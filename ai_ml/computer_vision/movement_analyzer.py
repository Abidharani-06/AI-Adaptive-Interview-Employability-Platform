"""
Observable Movement Analysis Module
-----------------------------------
Measures physical, observable movement between video frames (head and body displacement).
Produces objective metrics such as movement rate, stability score, and excessive movement events.

IMPORTANT:
Does NOT diagnose psychological states such as anxiety, nervousness, or confidence.
Only tracks observable landmark displacement.
"""

import math
from typing import Dict, List, Optional, Tuple, Any


class MovementAnalyzer:
    """
    Analyzes observable inter-frame displacement of head and upper-body landmarks.
    """

    def __init__(self, excessive_threshold: float = 0.08, min_event_gap_frames: int = 10):
        """
        Parameters:
        - excessive_threshold: Normalized Euclidean displacement threshold considered excessive motion.
        - min_event_gap_frames: Minimum frame gap between counted excessive movement events to avoid multi-counting.
        """
        self.excessive_threshold = excessive_threshold
        self.min_event_gap_frames = min_event_gap_frames
        self.reset()

    def reset(self):
        """Resets all accumulated movement tracking metrics."""
        self.previous_anchors: Optional[Dict[str, Tuple[float, float]]] = None
        self.total_frames: int = 0
        self.valid_frames: int = 0
        self.displacements: List[float] = []
        self.excessive_frames_count: int = 0
        self.excessive_movement_events: int = 0
        self.last_excessive_frame_idx: int = -self.min_event_gap_frames

    def process_frame(
        self,
        anchors: Optional[Dict[str, Tuple[float, float]]] = None,
        scale_reference: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Processes anchor points for a single frame.

        Parameters:
        - anchors: Dictionary of landmark coordinates, e.g. {"nose": (x, y), "left_shoulder": (x, y), ...}
                   Coordinates should be normalized [0.0, 1.0].
        - scale_reference: Distance between reference points (e.g. inter-eye or shoulder width) to normalize displacement.
                           If None, default normalization is used.

        Returns:
        - Frame-level movement result dict.
        """
        self.total_frames += 1

        if not anchors:
            self.previous_anchors = None
            return {
                "frame_index": self.total_frames,
                "displacement": 0.0,
                "is_excessive": False,
                "valid": False
            }

        if self.previous_anchors is None:
            self.previous_anchors = dict(anchors)
            return {
                "frame_index": self.total_frames,
                "displacement": 0.0,
                "is_excessive": False,
                "valid": False
            }

        # Calculate average displacement across common tracked anchors
        common_keys = [k for k in anchors if k in self.previous_anchors]
        if not common_keys:
            self.previous_anchors = dict(anchors)
            return {
                "frame_index": self.total_frames,
                "displacement": 0.0,
                "is_excessive": False,
                "valid": False
            }

        displacements_list = []
        for key in common_keys:
            curr_pt = anchors[key]
            prev_pt = self.previous_anchors[key]
            dx = curr_pt[0] - prev_pt[0]
            dy = curr_pt[1] - prev_pt[1]
            dist = math.sqrt(dx * dx + dy * dy)
            displacements_list.append(dist)

        raw_avg_disp = sum(displacements_list) / len(displacements_list)

        # Scale normalization: if scale reference provided (e.g., face width or shoulder width),
        # adjust so distance changes don't distort movement.
        norm_factor = scale_reference if (scale_reference and scale_reference > 0.05) else 0.20
        normalized_disp = raw_avg_disp / (norm_factor / 0.20)

        is_excessive = normalized_disp >= self.excessive_threshold

        self.valid_frames += 1
        self.displacements.append(normalized_disp)

        if is_excessive:
            self.excessive_frames_count += 1
            if (self.total_frames - self.last_excessive_frame_idx) >= self.min_event_gap_frames:
                self.excessive_movement_events += 1
                self.last_excessive_frame_idx = self.total_frames

        self.previous_anchors = dict(anchors)

        return {
            "frame_index": self.total_frames,
            "displacement": round(normalized_disp, 4),
            "is_excessive": is_excessive,
            "valid": True
        }

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Computes aggregate movement statistics over the entire recorded session.
        """
        if self.valid_frames == 0 or not self.displacements:
            return {
                "total_frames": self.total_frames,
                "valid_frames": self.valid_frames,
                "average_movement_rate": 0.0,
                "movement_stability_score": 1.0,
                "excessive_movement_ratio": 0.0,
                "excessive_movement_events": 0,
                "stability_percentage": 100.0,
                "movement_description": "Insufficient movement data detected."
            }

        avg_displacement = sum(self.displacements) / len(self.displacements)
        excessive_ratio = self.excessive_frames_count / self.valid_frames

        # Stability score: 1.0 is completely stable and steady; drops as excessive ratio or high jitter increases
        # Using a smooth bounded formulation:
        stability = max(0.0, min(1.0, 1.0 - (excessive_ratio * 1.5 + min(1.0, avg_displacement * 4.0) * 0.3)))

        if excessive_ratio < 0.05 and avg_displacement < 0.025:
            description = "Steady and composed physical presence with minimal displacement."
        elif excessive_ratio < 0.15:
            description = "Natural physical movement within standard expected interview range."
        elif excessive_ratio < 0.30:
            description = "Noticeable upper-body movement and position adjustments observed."
        else:
            description = "Frequent and marked movement observed throughout the session."

        return {
            "total_frames": self.total_frames,
            "valid_frames": self.valid_frames,
            "average_movement_rate": round(avg_displacement, 4),
            "movement_stability_score": round(stability, 4),
            "excessive_movement_ratio": round(excessive_ratio, 4),
            "excessive_movement_events": self.excessive_movement_events,
            "stability_percentage": round(stability * 100, 1),
            "movement_description": description
        }
