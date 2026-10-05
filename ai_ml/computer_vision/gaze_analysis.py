"""
Observable Gaze Analysis Module
-------------------------------
Analyzes observable eye orientation and gaze consistency relative to the camera.
Tracks approximate gaze direction (center, left, right, up, down), camera-facing ratio,
and off-camera gaze events.

IMPORTANT:
Does NOT claim psychological eye-contact measurement or assess honesty, nervousness, or confidence.
Only measures observable iris/pupil positioning relative to eye corners and head orientation.
"""

import math
from typing import Dict, Optional, Tuple, Any, List


class GazeAnalyzer:
    """
    Estimates observable gaze orientation towards the camera using eye landmarks and iris positions.
    """

    def __init__(
        self,
        center_ratio_min: float = 0.35,
        center_ratio_max: float = 0.65,
        head_yaw_limit_deg: float = 20.0,
        head_pitch_limit_deg: float = 20.0
    ):
        self.center_ratio_min = center_ratio_min
        self.center_ratio_max = center_ratio_max
        self.head_yaw_limit_deg = head_yaw_limit_deg
        self.head_pitch_limit_deg = head_pitch_limit_deg
        self.reset()

    def reset(self):
        """Resets all gaze tracking session counters."""
        self.total_frames: int = 0
        self.valid_frames: int = 0
        self.camera_facing_frames: int = 0
        self.off_camera_frames: int = 0
        self.off_camera_episodes: int = 0
        self._in_off_camera_episode: bool = False
        self._consecutive_off_camera: int = 0
        self.direction_counts: Dict[str, int] = {
            "center": 0,
            "left": 0,
            "right": 0,
            "up": 0,
            "down": 0
        }

    def process_eye_landmarks(
        self,
        left_eye: Optional[Dict[str, Tuple[float, float]]] = None,
        right_eye: Optional[Dict[str, Tuple[float, float]]] = None,
        head_yaw: float = 0.0,
        head_pitch: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates observable gaze direction for a frame.

        Parameters:
        - left_eye: {'inner': (x, y), 'outer': (x, y), 'iris': (x, y), 'top': (x, y), 'bottom': (x, y)}
        - right_eye: {'inner': (x, y), 'outer': (x, y), 'iris': (x, y), 'top': (x, y), 'bottom': (x, y)}
        - head_yaw: Head yaw angle in degrees (- = left, + = right).
        - head_pitch: Head pitch angle in degrees (- = down, + = up).
        """
        self.total_frames += 1

        if not left_eye and not right_eye:
            return {
                "valid": False,
                "direction": "unknown",
                "is_camera_facing": False,
                "confidence": 0.0
            }

        # If head is turned significantly away, gaze is observable as off-camera
        if abs(head_yaw) > self.head_yaw_limit_deg or abs(head_pitch) > self.head_pitch_limit_deg:
            if abs(head_yaw) > abs(head_pitch):
                direction = "right" if head_yaw > 0 else "left"
            else:
                direction = "up" if head_pitch > 0 else "down"

            self._record_frame(direction, is_camera_facing=False)
            return {
                "valid": True,
                "direction": direction,
                "is_camera_facing": False,
                "confidence": 0.90
            }

        # Inspect iris relative position inside eye bounding box
        horizontal_ratios: List[float] = []
        vertical_ratios: List[float] = []

        for eye_data in [left_eye, right_eye]:
            if not eye_data or "iris" not in eye_data:
                continue
            iris = eye_data["iris"]
            if "inner" in eye_data and "outer" in eye_data:
                p_in = eye_data["inner"]
                p_out = eye_data["outer"]
                min_x = min(p_in[0], p_out[0])
                max_x = max(p_in[0], p_out[0])
                width = max_x - min_x
                if width > 1e-4:
                    h_ratio = (iris[0] - min_x) / width
                    horizontal_ratios.append(h_ratio)

            if "top" in eye_data and "bottom" in eye_data:
                p_top = eye_data["top"]
                p_bot = eye_data["bottom"]
                min_y = min(p_top[1], p_bot[1])
                max_y = max(p_top[1], p_bot[1])
                height = max_y - min_y
                if height > 1e-4:
                    v_ratio = (iris[1] - min_y) / height
                    vertical_ratios.append(v_ratio)

        # Average available ratios
        avg_h = sum(horizontal_ratios) / len(horizontal_ratios) if horizontal_ratios else 0.5
        avg_v = sum(vertical_ratios) / len(vertical_ratios) if vertical_ratios else 0.5

        # Classify gaze direction
        is_camera = True
        direction = "center"

        if avg_h < self.center_ratio_min:
            direction = "left"
            is_camera = False
        elif avg_h > self.center_ratio_max:
            direction = "right"
            is_camera = False
        elif avg_v < 0.30:
            direction = "up"
            is_camera = False
        elif avg_v > 0.70:
            direction = "down"
            is_camera = False

        self._record_frame(direction, is_camera_facing=is_camera)

        return {
            "valid": True,
            "direction": direction,
            "is_camera_facing": is_camera,
            "horizontal_ratio": round(avg_h, 3),
            "vertical_ratio": round(avg_v, 3),
            "confidence": 0.85
        }

    def _record_frame(self, direction: str, is_camera_facing: bool):
        """Updates internal counters based on frame result."""
        self.valid_frames += 1
        self.direction_counts[direction] = self.direction_counts.get(direction, 0) + 1

        if is_camera_facing:
            self.camera_facing_frames += 1
            self._consecutive_off_camera = 0
            self._in_off_camera_episode = False
        else:
            self.off_camera_frames += 1
            self._consecutive_off_camera += 1
            # Episode triggers when gaze remains off-camera for at least 3 frames
            if self._consecutive_off_camera == 3 and not self._in_off_camera_episode:
                self.off_camera_episodes += 1
                self._in_off_camera_episode = True

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Computes aggregate gaze consistency and off-camera statistics.
        """
        if self.valid_frames == 0:
            return {
                "total_frames": self.total_frames,
                "valid_frames": 0,
                "gaze_consistency": 0.0,
                "camera_facing_ratio": 0.0,
                "camera_facing_percentage": 0.0,
                "off_camera_gaze_frequency": 0,
                "off_camera_duration_ratio": 0.0,
                "dominant_gaze_direction": "unknown",
                "gaze_description": "Insufficient face or eye data to evaluate observable gaze."
            }

        camera_ratio = self.camera_facing_frames / self.valid_frames
        off_ratio = self.off_camera_frames / self.valid_frames
        dominant_direction = max(self.direction_counts.items(), key=lambda x: x[1])[0]

        if camera_ratio >= 0.80:
            description = "Observable gaze was consistently oriented toward the camera for most of the session."
        elif camera_ratio >= 0.60:
            description = "Gaze was generally camera-facing with intermittent off-camera visual shifts."
        elif camera_ratio >= 0.40:
            description = f"Frequent off-camera gaze observed (primarily directed {dominant_direction})."
        else:
            description = f"Substantial duration of off-camera gaze detected throughout responses (predominantly {dominant_direction})."

        return {
            "total_frames": self.total_frames,
            "valid_frames": self.valid_frames,
            "gaze_consistency": round(camera_ratio, 4),
            "camera_facing_ratio": round(camera_ratio, 4),
            "camera_facing_percentage": round(camera_ratio * 100, 1),
            "off_camera_gaze_frequency": self.off_camera_episodes,
            "off_camera_duration_ratio": round(off_ratio, 4),
            "dominant_gaze_direction": dominant_direction,
            "direction_breakdown": dict(self.direction_counts),
            "gaze_description": description
        }
