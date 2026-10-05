"""
Observable Face and Head Orientation Analysis Module
----------------------------------------------------
Performs face detection, multi-face presence verification, head pose estimation
(yaw, pitch, roll, frontal-facing ratio), and observable facial expression cues.

IMPORTANT:
Does NOT diagnose psychological states, true emotions, personality, or confidence.
Classifies only observable landmark geometry (e.g. smile curvature, head tilt angles).
Flags multiple face detections as an unreliable analysis condition.
"""

import math
from typing import Dict, Optional, Tuple, Any, List


class FaceAnalyzer:
    """
    Analyzes face presence, multiple faces, head orientation angles, and observable facial cues.
    Supports both direct video frame processing (MediaPipe Face Mesh) and direct landmark evaluation.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        frontal_yaw_thresh_deg: float = 20.0,
        frontal_pitch_thresh_deg: float = 20.0,
        frontal_roll_thresh_deg: float = 20.0
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.frontal_yaw_thresh_deg = frontal_yaw_thresh_deg
        self.frontal_pitch_thresh_deg = frontal_pitch_thresh_deg
        self.frontal_roll_thresh_deg = frontal_roll_thresh_deg
        self._mesh = None
        self.reset()

    def _get_mesh_detector(self):
        """Lazily initialize MediaPipe Face Mesh detector with multi-face support."""
        if self._mesh is None:
            try:
                import mediapipe as mp
                self._mp_mesh = mp.solutions.face_mesh
                self._mesh = self._mp_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=3,  # Detect if multiple people are present
                    refine_landmarks=True,
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
            except Exception:
                self._mesh = None
        return self._mesh

    def reset(self):
        """Resets all accumulated session metrics."""
        self.total_frames: int = 0
        self.face_detected_frames: int = 0
        self.multiple_faces_frames: int = 0
        self.frontal_facing_frames: int = 0
        self.head_yaws: List[float] = []
        self.head_pitches: List[float] = []
        self.head_rolls: List[float] = []
        self.cue_counts: Dict[str, int] = {
            "neutral_cue": 0,
            "positive_cue": 0,
            "expressive_cue": 0
        }

    def estimate_head_pose_geometry(
        self,
        landmarks: Dict[int, Tuple[float, float, float]]
    ) -> Tuple[float, float, float]:
        """
        Estimates yaw, pitch, and roll in degrees using landmark geometry.
        Indices:
        - 1: nose tip
        - 152: chin
        - 33: left eye outer corner
        - 263: right eye outer corner
        - 61: mouth left corner
        - 291: mouth right corner
        """
        nose = landmarks[1]
        chin = landmarks[152]
        left_eye = landmarks[33]
        right_eye = landmarks[263]

        # Roll: angle between eyes relative to horizontal
        eye_dx = right_eye[0] - left_eye[0]
        eye_dy = right_eye[1] - left_eye[1]
        roll = math.degrees(math.atan2(eye_dy, eye_dx))

        # Yaw: asymmetry of nose tip relative to eye span
        eye_span = math.hypot(eye_dx, eye_dy)
        if eye_span > 1e-4:
            eye_mid_x = (left_eye[0] + right_eye[0]) / 2.0
            nose_offset_x = (nose[0] - eye_mid_x) / eye_span
            # Scale to approximate degrees (-45 to +45)
            yaw = float(nose_offset_x * 85.0)
        else:
            yaw = 0.0

        # Pitch: nose position relative to vertical eye-chin distance
        face_height = abs(chin[1] - (left_eye[1] + right_eye[1]) / 2.0)
        if face_height > 1e-4:
            eye_mid_y = (left_eye[1] + right_eye[1]) / 2.0
            nose_offset_y = (nose[1] - eye_mid_y) / face_height
            # Expected neutral nose is around ~0.25 of eye-chin height
            pitch = float((nose_offset_y - 0.25) * 60.0)
        else:
            pitch = 0.0

        return yaw, pitch, roll

    def extract_observable_facial_cue(
        self,
        landmarks: Dict[int, Tuple[float, float, float]]
    ) -> str:
        """
        Extracts observable landmark activity cues (neutral, positive, expressive).
        NOT an emotion classifier; describes mouth curvature and brow activity.
        """
        try:
            left_mouth = landmarks[61]
            right_mouth = landmarks[291]
            top_lip = landmarks[13]
            bottom_lip = landmarks[14]
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            left_brow = landmarks[107]
            right_brow = landmarks[336]

            mouth_w = math.hypot(right_mouth[0] - left_mouth[0], right_mouth[1] - left_mouth[1])
            eye_span = math.hypot(right_eye[0] - left_eye[0], right_eye[1] - left_eye[1])
            mouth_open = math.hypot(bottom_lip[0] - top_lip[0], bottom_lip[1] - top_lip[1])

            if eye_span < 1e-4:
                return "neutral_cue"

            mouth_ratio = mouth_w / eye_span
            open_ratio = mouth_open / mouth_w if mouth_w > 1e-4 else 0.0

            # Observable smile cue: widened mouth with slight upward corner curvature
            mouth_mid_y = (left_mouth[1] + right_mouth[1]) / 2.0
            if mouth_ratio > 0.58 and (mouth_mid_y - top_lip[1]) > 0.01:
                return "positive_cue"

            # Observable expressive/speaking cue: active mouth opening
            if open_ratio > 0.25:
                return "expressive_cue"

            return "neutral_cue"
        except Exception:
            return "neutral_cue"

    def process_landmarks_data(
        self,
        faces_landmarks: List[Dict[int, Tuple[float, float, float]]]
    ) -> Dict[str, Any]:
        """
        Processes extracted landmark points for one or more faces.
        """
        self.total_frames += 1
        num_faces = len(faces_landmarks) if faces_landmarks else 0

        if num_faces == 0:
            return {
                "face_detected": False,
                "multiple_faces": False,
                "face_count": 0,
                "head_orientation": {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_frontal": False},
                "facial_cue": "no_face",
                "warning": "No face detected in frame."
            }

        if num_faces > 1:
            self.multiple_faces_frames += 1
            # Clearly mark as unreliable rather than picking random person
            return {
                "face_detected": True,
                "multiple_faces": True,
                "face_count": num_faces,
                "head_orientation": {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_frontal": False},
                "facial_cue": "unreliable_multi_face",
                "warning": f"Multiple faces ({num_faces}) detected in frame - analysis unreliable."
            }

        # Single face detected
        self.face_detected_frames += 1
        lms = faces_landmarks[0]

        yaw, pitch, roll = self.estimate_head_pose_geometry(lms)
        is_frontal = (
            abs(yaw) <= self.frontal_yaw_thresh_deg and
            abs(pitch) <= self.frontal_pitch_thresh_deg and
            abs(roll) <= self.frontal_roll_thresh_deg
        )

        if is_frontal:
            self.frontal_facing_frames += 1

        self.head_yaws.append(yaw)
        self.head_pitches.append(pitch)
        self.head_rolls.append(roll)

        cue = self.extract_observable_facial_cue(lms)
        self.cue_counts[cue] = self.cue_counts.get(cue, 0) + 1

        return {
            "face_detected": True,
            "multiple_faces": False,
            "face_count": 1,
            "head_orientation": {
                "yaw": round(yaw, 2),
                "pitch": round(pitch, 2),
                "roll": round(roll, 2),
                "is_frontal": is_frontal
            },
            "facial_cue": cue,
            "warning": None
        }

    def process_frame(self, frame_bgr) -> Dict[str, Any]:
        """
        Processes a video frame with MediaPipe Face Mesh.
        """
        detector = self._get_mesh_detector()
        if detector is None:
            return self.process_landmarks_data([])

        try:
            import cv2
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)

            if not results.multi_face_landmarks:
                return self.process_landmarks_data([])

            faces_data = []
            for face_lms in results.multi_face_landmarks:
                lm_dict = {}
                for idx in [1, 152, 33, 263, 61, 291, 13, 14, 107, 336, 159, 386, 468, 473]:
                    if idx < len(face_lms.landmark):
                        p = face_lms.landmark[idx]
                        lm_dict[idx] = (p.x, p.y, p.z)
                faces_data.append(lm_dict)

            return self.process_landmarks_data(faces_data)
        except Exception:
            return self.process_landmarks_data([])

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Computes aggregate metrics for face visibility, head orientation, and facial activity.
        """
        if self.total_frames == 0:
            return {
                "total_frames": 0,
                "face_visibility_rate": 0.0,
                "frontal_facing_ratio": 0.0,
                "multiple_faces_detected": False,
                "multiple_faces_ratio": 0.0,
                "facial_cue_breakdown": dict(self.cue_counts),
                "face_description": "No frames evaluated."
            }

        vis_rate = self.face_detected_frames / self.total_frames
        multi_ratio = self.multiple_faces_frames / self.total_frames
        frontal_ratio = self.frontal_facing_frames / max(1, self.face_detected_frames)

        avg_yaw = sum(self.head_yaws) / len(self.head_yaws) if self.head_yaws else 0.0
        avg_pitch = sum(self.head_pitches) / len(self.head_pitches) if self.head_pitches else 0.0
        avg_roll = sum(self.head_rolls) / len(self.head_rolls) if self.head_rolls else 0.0

        is_multi_problematic = multi_ratio > 0.10

        # Non-psychological feedback descriptions
        if is_multi_problematic:
            desc = "Multiple faces detected for over 10% of frames; interview visual analysis is flagged as unreliable."
        elif vis_rate >= 0.90:
            desc = "Face was consistently visible and properly framed throughout the interview."
        elif vis_rate >= 0.70:
            desc = "Face was visible for most of the interview with occasional intermittent frame dropouts."
        else:
            desc = "Frequent loss of face visibility detected during the interview session."

        if frontal_ratio >= 0.80:
            head_desc = "Head orientation was predominantly frontal and camera-facing."
        elif frontal_ratio >= 0.50:
            head_desc = "Head orientation was generally camera-facing with periodic side or downward turns."
        else:
            head_desc = "Head was frequently turned away from the primary camera orientation."

        return {
            "total_frames": self.total_frames,
            "face_detected_frames": self.face_detected_frames,
            "face_visibility_rate": round(vis_rate, 4),
            "face_visibility_percentage": round(vis_rate * 100, 1),
            "frontal_facing_ratio": round(frontal_ratio, 4),
            "frontal_facing_percentage": round(frontal_ratio * 100, 1),
            "multiple_faces_detected": is_multi_problematic,
            "multiple_faces_frames": self.multiple_faces_frames,
            "multiple_faces_ratio": round(multi_ratio, 4),
            "average_yaw_deg": round(avg_yaw, 2),
            "average_pitch_deg": round(avg_pitch, 2),
            "average_roll_deg": round(avg_roll, 2),
            "facial_cue_breakdown": dict(self.cue_counts),
            "face_description": desc,
            "head_pose_description": head_desc
        }

    def close(self):
        """Release MediaPipe resources."""
        if self._mesh:
            self._mesh.close()
            self._mesh = None
