"""
Observable Hand Gesture Analysis Module
---------------------------------------
Analyzes observable hand visibility, gesture frequency, and hand movement activity
using MediaPipe Hands.

IMPORTANT:
Does NOT diagnose psychological traits, nervousness, defensiveness, or deception.
Focuses strictly on measurable physical presence and motion of hands in the frame.
"""

import math
from typing import Dict, Optional, Tuple, Any, List


class GestureAnalyzer:
    """
    Analyzes observable hand presence and movement during an interview.
    Supports frame-based MediaPipe Hands tracking as well as direct landmark processing.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        gesture_movement_threshold: float = 0.015,
        excessive_movement_threshold: float = 0.09
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.gesture_movement_threshold = gesture_movement_threshold
        self.excessive_movement_threshold = excessive_movement_threshold
        self._hands = None
        self.reset()

    def _get_hands_detector(self):
        """Lazily initialize MediaPipe Hands detector."""
        if self._hands is None:
            try:
                import mediapipe as mp
                self._mp_hands = mp.solutions.hands
                self._hands = self._mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
            except Exception:
                self._hands = None
        return self._hands

    def reset(self):
        """Resets all session tracking metrics."""
        self.total_frames: int = 0
        self.hands_visible_frames: int = 0
        self.gesturing_frames: int = 0
        self.excessive_gesture_frames: int = 0
        self.excessive_movement_events: int = 0
        self._previous_wrists: List[Tuple[float, float]] = []
        self._consecutive_excessive_frames: int = 0

    def process_landmarks(
        self,
        hands_landmarks: List[Dict[str, Tuple[float, float]]]
    ) -> Dict[str, Any]:
        """
        Processes a list of detected hands, where each hand has key landmarks (e.g. wrist).

        Expected structure:
        hands_landmarks = [
            {"wrist": (x, y), "index_tip": (x, y)}, ...
        ]
        """
        self.total_frames += 1
        num_hands = len(hands_landmarks) if hands_landmarks else 0
        hands_visible = num_hands > 0

        current_wrists: List[Tuple[float, float]] = []
        is_gesturing = False
        is_excessive = False
        max_displacement = 0.0

        if hands_visible:
            self.hands_visible_frames += 1
            for hand in hands_landmarks:
                if "wrist" in hand:
                    current_wrists.append(hand["wrist"])

            # Compute displacement relative to previous frame
            if self._previous_wrists and current_wrists:
                # Match closest wrists between frames
                displacements = []
                for curr in current_wrists:
                    dists = [math.hypot(curr[0] - prev[0], curr[1] - prev[1]) for prev in self._previous_wrists]
                    displacements.append(min(dists))

                max_displacement = max(displacements) if displacements else 0.0

                if max_displacement >= self.gesture_movement_threshold:
                    is_gesturing = True
                    self.gesturing_frames += 1

                if max_displacement >= self.excessive_movement_threshold:
                    is_excessive = True
                    self.excessive_gesture_frames += 1
                    self._consecutive_excessive_frames += 1
                    if self._consecutive_excessive_frames == 10:
                        self.excessive_movement_events += 1
                else:
                    self._consecutive_excessive_frames = 0

            self._previous_wrists = current_wrists
        else:
            self._previous_wrists = []
            self._consecutive_excessive_frames = 0

        return {
            "hands_visible": hands_visible,
            "hands_count": num_hands,
            "is_gesturing": is_gesturing,
            "is_excessive": is_excessive,
            "wrist_displacement": round(max_displacement, 4)
        }

    def process_frame(self, frame_bgr) -> Dict[str, Any]:
        """
        Processes a BGR video frame using MediaPipe Hands.
        """
        detector = self._get_hands_detector()
        if detector is None:
            return self.process_landmarks([])

        try:
            import cv2
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)

            if not results.multi_hand_landmarks:
                return self.process_landmarks([])

            hands_data = []
            for hand_lms in results.multi_hand_landmarks:
                wrist = hand_lms.landmark[0]
                index_tip = hand_lms.landmark[8]
                hands_data.append({
                    "wrist": (wrist.x, wrist.y),
                    "index_tip": (index_tip.x, index_tip.y)
                })

            return self.process_landmarks(hands_data)
        except Exception:
            return self.process_landmarks([])

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Computes aggregate hand gesture metrics for the entire interview.
        """
        if self.total_frames == 0:
            return {
                "total_frames": 0,
                "hands_visible_frames": 0,
                "hand_visibility_ratio": 0.0,
                "gesture_frequency": 0.0,
                "excessive_movement_events": 0,
                "gesture_description": "No video frames analyzed."
            }

        vis_ratio = self.hands_visible_frames / self.total_frames
        gesture_freq = self.gesturing_frames / max(1, self.hands_visible_frames) if self.hands_visible_frames > 0 else 0.0
        overall_gesture_activity = self.gesturing_frames / self.total_frames

        if vis_ratio < 0.10:
            description = "Hands remained primarily below or outside the camera frame."
        elif overall_gesture_activity < 0.15:
            description = "Hands were periodically visible with minimal gesturing."
        elif overall_gesture_activity <= 0.50:
            description = "Moderate observable hand gestures accompanying spoken communication."
        else:
            description = "Frequent and continuous observable hand gesturing throughout responses."

        return {
            "total_frames": self.total_frames,
            "hands_visible_frames": self.hands_visible_frames,
            "hand_visibility_ratio": round(vis_ratio, 4),
            "hand_visibility_percentage": round(vis_ratio * 100, 1),
            "gesture_frequency": round(gesture_freq, 4),
            "gesture_frequency_percentage": round(gesture_freq * 100, 1),
            "overall_gesture_activity_ratio": round(overall_gesture_activity, 4),
            "excessive_movement_events": self.excessive_movement_events,
            "gesture_description": description
        }

    def close(self):
        """Release MediaPipe resources."""
        if self._hands:
            self._hands.close()
            self._hands = None
