"""
Observable Posture Analysis Module
----------------------------------
Analyzes observable upper-body posture, shoulder alignment, torso orientation,
and posture consistency using MediaPipe Pose.

IMPORTANT:
Does NOT make claims about candidate confidence, emotional state, or personality.
Measures only physical landmark angles and alignments.
"""

import math
from typing import Dict, Optional, Tuple, Any, List


class PostureAnalyzer:
    """
    Analyzes upper-body posture, shoulder symmetry, and vertical orientation.
    Supports both direct video frame processing (via MediaPipe Pose) and direct landmark evaluation.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        max_tilt_threshold_deg: float = 10.0,
        lateral_lean_threshold: float = 0.08
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.max_tilt_threshold_deg = max_tilt_threshold_deg
        self.lateral_lean_threshold = lateral_lean_threshold
        self._pose = None
        self.reset()

    def _get_pose_detector(self):
        """Lazily initialize MediaPipe Pose detector."""
        if self._pose is None:
            try:
                import mediapipe as mp
                self._mp_pose = mp.solutions.pose
                self._pose = self._mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
            except Exception as e:
                self._pose = None
        return self._pose

    def reset(self):
        """Resets all accumulated session metrics."""
        self.total_frames: int = 0
        self.detected_frames: int = 0
        self.aligned_shoulder_frames: int = 0
        self.upright_frames: int = 0
        self.shoulder_tilt_angles: List[float] = []
        self.orientations_count: Dict[str, int] = {
            "upright": 0,
            "leaning_left": 0,
            "leaning_right": 0,
            "slouching": 0
        }
        self.excessive_lean_events: int = 0
        self._consecutive_lean_frames: int = 0

    def process_landmarks(
        self,
        landmarks: Dict[str, Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        Processes normalized landmark coordinates directly.

        Expected landmarks:
        - 'left_shoulder': (x, y)
        - 'right_shoulder': (x, y)
        - optional: 'nose': (x, y), 'left_hip': (x, y), 'right_hip': (x, y)
        """
        self.total_frames += 1

        if not landmarks or "left_shoulder" not in landmarks or "right_shoulder" not in landmarks:
            return {
                "detected": False,
                "shoulder_tilt_deg": 0.0,
                "is_shoulder_aligned": False,
                "orientation": "unknown",
                "is_upright": False
            }

        left_sh = landmarks["left_shoulder"]
        right_sh = landmarks["right_shoulder"]

        # Note: In mirrored/selfie camera, candidate's left shoulder is on right side of image or vice-versa.
        # dx and dy between the two shoulders
        dx = right_sh[0] - left_sh[0]
        dy = right_sh[1] - left_sh[1]

        if abs(dx) < 1e-4:
            tilt_deg = 90.0
        else:
            tilt_deg = math.degrees(math.atan2(dy, dx))
            # Normalize angle relative to horizontal (0 deg = level shoulders)
            if tilt_deg > 90.0:
                tilt_deg -= 180.0
            elif tilt_deg < -90.0:
                tilt_deg += 180.0

        abs_tilt = abs(tilt_deg)
        is_shoulder_aligned = abs_tilt <= self.max_tilt_threshold_deg

        # Determine torso orientation
        orientation = "upright"
        sh_center_x = (left_sh[0] + right_sh[0]) / 2.0
        sh_center_y = (left_sh[1] + right_sh[1]) / 2.0

        if "nose" in landmarks:
            nose = landmarks["nose"]
            horizontal_offset = nose[0] - sh_center_x
            vertical_dist = sh_center_y - nose[1]

            if horizontal_offset > self.lateral_lean_threshold:
                orientation = "leaning_right"
            elif horizontal_offset < -self.lateral_lean_threshold:
                orientation = "leaning_left"
            elif vertical_dist < 0.10:  # Head collapsed towards shoulder level
                orientation = "slouching"
            else:
                orientation = "upright"

        is_upright = (orientation == "upright")

        self.detected_frames += 1
        self.shoulder_tilt_angles.append(abs_tilt)
        if is_shoulder_aligned:
            self.aligned_shoulder_frames += 1
        if is_upright:
            self.upright_frames += 1

        self.orientations_count[orientation] = self.orientations_count.get(orientation, 0) + 1

        # Track sustained excessive lean events (> 15 consecutive frames)
        if not is_upright:
            self._consecutive_lean_frames += 1
            if self._consecutive_lean_frames == 15:
                self.excessive_lean_events += 1
        else:
            self._consecutive_lean_frames = 0

        return {
            "detected": True,
            "shoulder_tilt_deg": round(abs_tilt, 2),
            "is_shoulder_aligned": is_shoulder_aligned,
            "orientation": orientation,
            "is_upright": is_upright
        }

    def process_frame(self, frame_bgr) -> Dict[str, Any]:
        """
        Processes a raw BGR video frame using MediaPipe Pose.
        """
        detector = self._get_pose_detector()
        if detector is None:
            return self.process_landmarks({})

        try:
            import cv2
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)

            if not results.pose_landmarks:
                return self.process_landmarks({})

            lm = results.pose_landmarks.landmark
            landmarks = {
                "nose": (lm[0].x, lm[0].y),
                "left_shoulder": (lm[11].x, lm[11].y),
                "right_shoulder": (lm[12].x, lm[12].y)
            }
            if lm[23].visibility > 0.4 and lm[24].visibility > 0.4:
                landmarks["left_hip"] = (lm[23].x, lm[23].y)
                landmarks["right_hip"] = (lm[24].x, lm[24].y)

            return self.process_landmarks(landmarks)
        except Exception:
            return self.process_landmarks({})

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Computes aggregate posture consistency and alignment statistics.
        """
        if self.detected_frames == 0:
            return {
                "total_frames": self.total_frames,
                "detected_frames": 0,
                "posture_visibility_rate": 0.0,
                "shoulder_alignment_ratio": 0.0,
                "posture_consistency": 0.0,
                "dominant_orientation": "unknown",
                "excessive_lean_events": 0,
                "posture_description": "Upper-body / shoulders not visible in camera frame."
            }

        det = self.detected_frames
        vis_rate = det / max(1, self.total_frames)
        sh_aligned_ratio = self.aligned_shoulder_frames / det
        upright_ratio = self.upright_frames / det

        # Overall posture consistency: balance between aligned shoulders and upright torso
        consistency = (sh_aligned_ratio * 0.5) + (upright_ratio * 0.5)

        dominant_orientation = max(self.orientations_count.items(), key=lambda x: x[1])[0]
        avg_tilt = sum(self.shoulder_tilt_angles) / len(self.shoulder_tilt_angles) if self.shoulder_tilt_angles else 0.0

        if consistency >= 0.85:
            description = "Consistently upright and balanced shoulder posture maintained throughout."
        elif consistency >= 0.70:
            description = "Generally upright posture with occasional minor shifts or shoulder tilts."
        elif dominant_orientation in ("leaning_left", "leaning_right"):
            description = f"Frequent lateral leaning ({dominant_orientation.replace('_', ' ')}) observed."
        else:
            description = "Variable upper-body orientation with noticeable forward or side leaning."

        return {
            "total_frames": self.total_frames,
            "detected_frames": det,
            "posture_visibility_rate": round(vis_rate, 4),
            "shoulder_alignment_ratio": round(sh_aligned_ratio, 4),
            "upright_ratio": round(upright_ratio, 4),
            "posture_consistency": round(consistency, 4),
            "posture_consistency_percentage": round(consistency * 100, 1),
            "average_shoulder_tilt_deg": round(avg_tilt, 2),
            "dominant_orientation": dominant_orientation,
            "excessive_lean_events": self.excessive_lean_events,
            "posture_description": description
        }

    def close(self):
        """Release MediaPipe resources."""
        if self._pose:
            self._pose.close()
            self._pose = None
