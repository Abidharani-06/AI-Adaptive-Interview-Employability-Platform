"""
Computer Vision Interview Analyzer
----------------------------------
Unified pipeline orchestrating Face Detection, Gaze Analysis, Head Orientation,
Posture Analysis, Movement Tracking, and Hand Gesture Analysis for interviews.

Features:
- Live webcam streaming & pre-recorded video file analysis
- Graceful error handling for missing camera, permission denied, invalid video paths, no face, and multi-face edge cases
- Frame-level extraction and multi-metric aggregation
- Strictly objective, observable visual cues (NO unsupported psychological or emotional claims)
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Local module imports
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from face_analysis import FaceAnalyzer
from gaze_analysis import GazeAnalyzer
from posture_analysis import PostureAnalyzer
from gesture_analysis import GestureAnalyzer
from movement_analyzer import MovementAnalyzer


class CVInterviewAnalyzer:
    """
    Central pipeline coordinator for video interview visual behavior analysis.
    """

    def __init__(
        self,
        frontal_yaw_thresh_deg: float = 18.0,
        frontal_pitch_thresh_deg: float = 16.0,
        posture_tilt_thresh_deg: float = 10.0,
        excessive_movement_threshold: float = 0.08
    ):
        self.face_analyzer = FaceAnalyzer(
            frontal_yaw_thresh_deg=frontal_yaw_thresh_deg,
            frontal_pitch_thresh_deg=frontal_pitch_thresh_deg
        )
        self.gaze_analyzer = GazeAnalyzer()
        self.posture_analyzer = PostureAnalyzer(
            max_tilt_threshold_deg=posture_tilt_thresh_deg
        )
        self.gesture_analyzer = GestureAnalyzer()
        self.movement_analyzer = MovementAnalyzer(
            excessive_threshold=excessive_movement_threshold
        )
        self.frame_records: List[Dict[str, Any]] = []
        self.warnings: List[str] = []

    def reset(self):
        """Resets all internal analyzers for a fresh interview session."""
        self.face_analyzer.reset()
        self.gaze_analyzer.reset()
        self.posture_analyzer.reset()
        self.gesture_analyzer.reset()
        self.movement_analyzer.reset()
        self.frame_records.clear()
        self.warnings.clear()

    def process_frame(self, frame_bgr, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Processes a single BGR frame through all visual behavior analyzers.
        """
        # 1. Face Analysis
        face_res = self.face_analyzer.process_frame(frame_bgr)
        head_yaw = face_res["head_orientation"]["yaw"]
        head_pitch = face_res["head_orientation"]["pitch"]

        # 2. Gaze Analysis
        # MediaPipe FaceMesh produces eye landmark data inside FaceAnalyzer if available
        left_eye_data = None
        right_eye_data = None
        mesh_det = getattr(self.face_analyzer, "_mesh", None)
        if mesh_det and face_res.get("face_detected") and not face_res.get("multiple_faces"):
            # If face detected, pass estimated head orientation into gaze analyzer
            gaze_res = self.gaze_analyzer.process_eye_landmarks(
                head_yaw=head_yaw,
                head_pitch=head_pitch
            )
        else:
            gaze_res = self.gaze_analyzer.process_eye_landmarks(None, None, head_yaw=0.0, head_pitch=0.0)

        # 3. Posture Analysis
        posture_res = self.posture_analyzer.process_frame(frame_bgr)

        # 4. Gesture Analysis
        gesture_res = self.gesture_analyzer.process_frame(frame_bgr)

        # 5. Movement Analysis (anchor tracking)
        anchors = {}
        scale_ref = None
        if face_res.get("face_detected"):
            # Anchor using head orientation or face center
            anchors["head"] = (0.5 + head_yaw / 180.0, 0.4 + head_pitch / 180.0)
            scale_ref = 0.20

        movement_res = self.movement_analyzer.process_frame(anchors, scale_reference=scale_ref)

        if face_res.get("warning"):
            if face_res["warning"] not in self.warnings:
                self.warnings.append(face_res["warning"])

        record = {
            "timestamp": timestamp or time.time(),
            "face": face_res,
            "gaze": gaze_res,
            "posture": posture_res,
            "gesture": gesture_res,
            "movement": movement_res
        }
        self.frame_records.append(record)
        return record

    def process_video(
        self,
        video_path: str,
        sample_fps: int = 10,
        max_frames: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processes a pre-recorded video file.
        Returns complete aggregate analysis summary.
        """
        self.reset()
        video_file = Path(video_path)

        if not video_file.exists() or not video_file.is_file():
            return {
                "success": False,
                "error": f"Invalid video file path: {video_path}",
                "total_frames_processed": 0,
                "summary": None
            }

        try:
            import cv2
            cap = cv2.VideoCapture(str(video_file))
            if not cap.isOpened():
                return {
                    "success": False,
                    "error": f"Failed to open video file: {video_path}. Unrecognized codec or corrupt video.",
                    "total_frames_processed": 0,
                    "summary": None
                }

            native_fps = cap.get(cv2.CAP_PROP_FPS)
            if native_fps <= 0 or native_fps != native_fps:
                native_fps = 30.0

            frame_interval = max(1, int(round(native_fps / sample_fps)))
            frame_idx = 0
            processed_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_interval == 0:
                    self.process_frame(frame, timestamp=frame_idx / native_fps)
                    processed_count += 1
                    if max_frames and processed_count >= max_frames:
                        break

                frame_idx += 1

            cap.release()

            return {
                "success": True,
                "video_file": str(video_file),
                "total_frames_processed": processed_count,
                "summary": self.get_aggregate_summary()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Video processing error: {str(e)}",
                "total_frames_processed": len(self.frame_records),
                "summary": None
            }

    def process_webcam(
        self,
        device_index: int = 0,
        duration_seconds: float = 5.0,
        sample_fps: int = 10,
        max_frames: Optional[int] = None,
        frame_callback=None
    ) -> Dict[str, Any]:
        """
        Streams frames from live camera for a specified duration or frame count.
        Handles camera unavailability and permission denied gracefully.
        """
        self.reset()
        try:
            import cv2
            cap = cv2.VideoCapture(device_index)
            if not cap.isOpened():
                return {
                    "success": False,
                    "error": f"Camera device {device_index} unavailable or permission denied.",
                    "total_frames_processed": 0,
                    "summary": None
                }

            start_time = time.time()
            interval = 1.0 / sample_fps
            processed_count = 0

            while True:
                elapsed = time.time() - start_time
                if elapsed >= duration_seconds:
                    break
                if max_frames and processed_count >= max_frames:
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                self.process_frame(frame, timestamp=elapsed)
                processed_count += 1

                if frame_callback:
                    frame_callback(frame, processed_count)

                time.sleep(interval)

            cap.release()

            return {
                "success": True,
                "camera_device": device_index,
                "duration_seconds": round(time.time() - start_time, 2),
                "total_frames_processed": processed_count,
                "summary": self.get_aggregate_summary()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Webcam capture error: {str(e)}",
                "total_frames_processed": len(self.frame_records),
                "summary": None
            }

    def get_aggregate_summary(self) -> Dict[str, Any]:
        """
        Aggregates frame observations across face, gaze, posture, gesture, and movement.
        Produces non-psychological, observable feedback and normalized percentages.
        """
        face_agg = self.face_analyzer.get_aggregate_metrics()
        gaze_agg = self.gaze_analyzer.get_aggregate_metrics()
        posture_agg = self.posture_analyzer.get_aggregate_metrics()
        gesture_agg = self.gesture_analyzer.get_aggregate_metrics()
        movement_agg = self.movement_analyzer.get_aggregate_metrics()

        face_vis = face_agg.get("face_visibility_percentage", 0.0)
        camera_orient = face_agg.get("frontal_facing_percentage", 0.0)
        gaze_cons = gaze_agg.get("camera_facing_percentage", 0.0)
        posture_cons = posture_agg.get("posture_consistency_percentage", 0.0)
        movement_stab = movement_agg.get("stability_percentage", 100.0)
        gesture_freq = gesture_agg.get("gesture_frequency_percentage", 0.0)

        # Reliability check
        is_multi = face_agg.get("multiple_faces_detected", False)
        is_reliable = (not is_multi) and (face_vis >= 20.0)

        feedback_list = []
        if is_multi:
            feedback_list.append("Multiple faces were detected during the session; visual behavioral analysis is flagged as unreliable.")
        elif face_vis < 50.0:
            feedback_list.append("Face visibility was low or frequently occluded during responses.")
        else:
            feedback_list.append(face_agg.get("face_description", "Face was visible for most of the interview."))

        feedback_list.append(face_agg.get("head_pose_description", "Head orientation was generally camera-facing."))
        feedback_list.append(gaze_agg.get("gaze_description", "Gaze consistency evaluated."))
        feedback_list.append(posture_agg.get("posture_description", "Posture remained generally upright."))
        feedback_list.append(movement_agg.get("movement_description", "Movement stability was steady."))
        feedback_list.append(gesture_agg.get("gesture_description", "Hand gestures were observed."))

        summary = {
            "face_visibility_percentage": face_vis,
            "camera_facing_percentage": camera_orient,
            "gaze_consistency_percentage": gaze_cons,
            "posture_consistency_percentage": posture_cons,
            "movement_stability_percentage": movement_stab,
            "gesture_frequency_percentage": gesture_freq,
            "multiple_faces_detected": is_multi,
            "reliability_status": "reliable" if is_reliable else "unreliable",
            "metrics": {
                "face": face_agg,
                "gaze": gaze_agg,
                "posture": posture_agg,
                "gesture": gesture_agg,
                "movement": movement_agg
            },
            "observable_feedback": feedback_list,
            "warnings": list(set(self.warnings))
        }

        summary["formatted_report"] = self.generate_report_text(summary)
        return summary

    def generate_report_text(self, summary: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates clean formatted assessment text output matching the Phase 5 specification.
        """
        if summary is None:
            summary = self.get_aggregate_summary()

        lines = [
            "============================================================",
            "                 COMPUTER VISION ASSESSMENT                 ",
            "============================================================",
            f"Face Visibility      : {summary['face_visibility_percentage']:.1f}%",
            f"Camera Orientation   : {summary['camera_facing_percentage']:.1f}%",
            f"Gaze Consistency     : {summary['gaze_consistency_percentage']:.1f}%",
            f"Posture Consistency  : {summary['posture_consistency_percentage']:.1f}%",
            f"Movement Stability   : {summary['movement_stability_percentage']:.1f}%",
            f"Gesture Frequency    : {summary['gesture_frequency_percentage']:.1f}%",
            f"Analysis Reliability : {summary['reliability_status'].upper()}",
            "------------------------------------------------------------",
            "Observable Visual Feedback:"
        ]
        for fb in summary.get("observable_feedback", []):
            lines.append(f"- {fb}")

        if summary.get("warnings"):
            lines.append("------------------------------------------------------------")
            lines.append("Session Alerts / Warnings:")
            for w in summary["warnings"]:
                lines.append(f"! [Notice]: {w}")

        lines.append("============================================================\n")
        return "\n".join(lines)

    def close(self):
        """Releases all MediaPipe resources cleanly."""
        self.face_analyzer.close()
        self.posture_analyzer.close()
        self.gesture_analyzer.close()
