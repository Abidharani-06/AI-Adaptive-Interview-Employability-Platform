"""
Phase 5 Test Suite: Computer Vision / Camera Analysis Module
============================================================
Comprehensive test suite verifying:
1. Module imports (OpenCV, MediaPipe, CV modules)
2. Face detection & multiple-face handling
3. Head orientation & observable facial cues
4. Observable gaze & eye-contact estimation
5. Upper-body posture & shoulder alignment
6. Hand gesture presence & activity tracking
7. Movement displacement & stability analysis
8. Edge cases (no face, invalid video, missing camera)
9. Pre-recorded/synthetic video processing & summary report
10. HR Round + CV integration & backward compatibility
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

cv_dir = project_root / "ai_ml" / "computer_vision"
if str(cv_dir) not in sys.path:
    sys.path.append(str(cv_dir))

question_engine_dir = project_root / "ai_ml" / "question_engine"
if str(question_engine_dir) not in sys.path:
    sys.path.append(str(question_engine_dir))


def test_01_imports():
    print("[TEST 1/10] Checking imports (OpenCV, MediaPipe, and CV analyzers)...")
    import cv2
    import mediapipe as mp
    from face_analysis import FaceAnalyzer
    from gaze_analysis import GazeAnalyzer
    from posture_analysis import PostureAnalyzer
    from gesture_analysis import GestureAnalyzer
    from movement_analyzer import MovementAnalyzer
    from cv_interview_analyzer import CVInterviewAnalyzer

    assert cv2.__version__ is not None, "OpenCV failed to import"
    assert mp.__version__ is not None, "MediaPipe failed to import"

    fa = FaceAnalyzer()
    ga = GazeAnalyzer()
    pa = PostureAnalyzer()
    gea = GestureAnalyzer()
    ma = MovementAnalyzer()
    cva = CVInterviewAnalyzer()

    assert fa is not None and ga is not None and pa is not None
    assert gea is not None and ma is not None and cva is not None
    print("  [PASS] All 6 CV analyzers and dependencies imported successfully.")


def test_02_face_detection_and_multi_face():
    print("[TEST 2/10] Testing face detection and multi-face detection handling...")
    from face_analysis import FaceAnalyzer
    analyzer = FaceAnalyzer()

    # Case A: No face
    empty_res = analyzer.process_landmarks_data([])
    assert empty_res["face_detected"] is False, "Expected face_detected=False for empty input"
    assert empty_res["multiple_faces"] is False

    # Case B: Single face
    face_1 = {
        1: (0.50, 0.45, 0.0),    # nose
        152: (0.50, 0.65, 0.0),  # chin
        33: (0.42, 0.40, 0.0),   # left eye outer
        263: (0.58, 0.40, 0.0),  # right eye outer
        61: (0.45, 0.55, 0.0),   # left mouth
        291: (0.55, 0.55, 0.0),  # right mouth
        13: (0.50, 0.53, 0.0),   # upper lip
        14: (0.50, 0.56, 0.0)    # lower lip
    }
    single_res = analyzer.process_landmarks_data([face_1])
    assert single_res["face_detected"] is True, "Expected face_detected=True for single face"
    assert single_res["multiple_faces"] is False
    assert single_res["face_count"] == 1
    assert single_res["warning"] is None

    # Case C: Multiple faces (must flag as unreliable)
    face_2 = dict(face_1)
    multi_res = analyzer.process_landmarks_data([face_1, face_2])
    assert multi_res["multiple_faces"] is True, "Expected multiple_faces=True"
    assert multi_res["face_count"] == 2
    assert "unreliable" in multi_res["warning"].lower()

    # Aggregate check
    agg = analyzer.get_aggregate_metrics()
    assert agg["total_frames"] == 3
    assert agg["multiple_faces_frames"] == 1
    print("  [PASS] Single face, no-face, and multi-face edge cases handled properly.")


def test_03_head_orientation_and_cues():
    print("[TEST 3/10] Testing head orientation estimation and observable facial cues...")
    from face_analysis import FaceAnalyzer
    analyzer = FaceAnalyzer()

    # Frontal face
    frontal_face = {
        1: (0.50, 0.45, 0.0),    # nose centered
        152: (0.50, 0.65, 0.0),  # chin
        33: (0.42, 0.40, 0.0),   # left eye
        263: (0.58, 0.40, 0.0),  # right eye
        61: (0.45, 0.55, 0.0),
        291: (0.55, 0.55, 0.0),
        13: (0.50, 0.53, 0.0),
        14: (0.50, 0.55, 0.0)
    }
    res_front = analyzer.process_landmarks_data([frontal_face])
    yaw = res_front["head_orientation"]["yaw"]
    assert abs(yaw) < 10.0, f"Expected yaw near 0 for frontal face, got {yaw}"
    assert res_front["head_orientation"]["is_frontal"] is True

    # Turned head (nose shifted significantly right)
    turned_face = dict(frontal_face)
    turned_face[1] = (0.56, 0.45, 0.0)  # nose shifted right
    res_turned = analyzer.process_landmarks_data([turned_face])
    assert res_turned["head_orientation"]["is_frontal"] is False, "Expected is_frontal=False for turned head"

    # Smiling / upturned mouth observable cue
    smile_face = dict(frontal_face)
    smile_face[61] = (0.42, 0.53, 0.0)  # widened and upturned
    smile_face[291] = (0.58, 0.53, 0.0)
    res_smile = analyzer.process_landmarks_data([smile_face])
    assert res_smile["facial_cue"] in ("positive_cue", "expressive_cue", "neutral_cue")
    print("  [PASS] Head orientation angles and observable landmark cues verified.")


def test_04_gaze_analysis():
    print("[TEST 4/10] Testing observable gaze and camera-facing consistency...")
    from gaze_analysis import GazeAnalyzer
    analyzer = GazeAnalyzer()

    # Frame 1: Center gaze (looking at camera)
    left_eye_center = {
        "inner": (0.46, 0.40), "outer": (0.40, 0.40),
        "iris": (0.43, 0.40), "top": (0.43, 0.38), "bottom": (0.43, 0.42)
    }
    right_eye_center = {
        "inner": (0.54, 0.40), "outer": (0.60, 0.40),
        "iris": (0.57, 0.40), "top": (0.57, 0.38), "bottom": (0.57, 0.42)
    }
    res_center = analyzer.process_eye_landmarks(left_eye_center, right_eye_center, head_yaw=0.0, head_pitch=0.0)
    assert res_center["is_camera_facing"] is True
    assert res_center["direction"] == "center"

    # Frame 2: Off-camera gaze due to significant head yaw turn
    res_off = analyzer.process_eye_landmarks(left_eye_center, right_eye_center, head_yaw=30.0, head_pitch=0.0)
    assert res_off["is_camera_facing"] is False
    assert res_off["direction"] == "right"

    # Aggregate metrics
    agg = analyzer.get_aggregate_metrics()
    assert agg["total_frames"] == 2
    assert agg["camera_facing_ratio"] == 0.5
    assert agg["camera_facing_percentage"] == 50.0
    assert "gaze_description" in agg
    print("  [PASS] Gaze direction, camera-facing ratio, and descriptions verified.")


def test_05_posture_analysis():
    print("[TEST 5/10] Testing observable posture analysis and shoulder alignment...")
    from posture_analysis import PostureAnalyzer
    analyzer = PostureAnalyzer(max_tilt_threshold_deg=10.0)

    # Frame 1: Perfectly aligned level shoulders
    lms_aligned = {
        "left_shoulder": (0.35, 0.60),
        "right_shoulder": (0.65, 0.60),
        "nose": (0.50, 0.35)
    }
    res1 = analyzer.process_landmarks(lms_aligned)
    assert res1["detected"] is True
    assert res1["is_shoulder_aligned"] is True
    assert res1["orientation"] == "upright"
    assert res1["shoulder_tilt_deg"] == 0.0

    # Frame 2: Tilted shoulders (shoulder tilt angle > 10 deg)
    lms_tilted = {
        "left_shoulder": (0.35, 0.55),
        "right_shoulder": (0.65, 0.65),  # vertical delta 0.10 over dx 0.30 => ~18 deg
        "nose": (0.50, 0.35)
    }
    res2 = analyzer.process_landmarks(lms_tilted)
    assert res2["is_shoulder_aligned"] is False
    assert res2["shoulder_tilt_deg"] > 10.0

    # Frame 3: Lateral lean
    lms_lean = {
        "left_shoulder": (0.25, 0.60),
        "right_shoulder": (0.55, 0.60),
        "nose": (0.55, 0.35)  # head shifted significantly right of shoulder center (0.40)
    }
    res3 = analyzer.process_landmarks(lms_lean)
    assert res3["orientation"] in ("leaning_right", "leaning_left")

    agg = analyzer.get_aggregate_metrics()
    assert agg["detected_frames"] == 3
    assert 0.0 <= agg["posture_consistency"] <= 1.0
    assert "posture_description" in agg
    print("  [PASS] Posture alignment, torso orientation, and consistency verified.")


def test_06_gesture_analysis():
    print("[TEST 6/10] Testing hand gesture tracking and activity metrics...")
    from gesture_analysis import GestureAnalyzer
    analyzer = GestureAnalyzer()

    # Frame 1: Hands not visible
    res1 = analyzer.process_landmarks([])
    assert res1["hands_visible"] is False
    assert res1["is_gesturing"] is False

    # Frame 2: Hand appears in frame
    res2 = analyzer.process_landmarks([{"wrist": (0.40, 0.70), "index_tip": (0.40, 0.60)}])
    assert res2["hands_visible"] is True
    assert res2["hands_count"] == 1

    # Frame 3: Hand moves significantly (gesturing)
    res3 = analyzer.process_landmarks([{"wrist": (0.45, 0.65), "index_tip": (0.45, 0.55)}])
    assert res3["hands_visible"] is True
    assert res3["is_gesturing"] is True

    agg = analyzer.get_aggregate_metrics()
    assert agg["total_frames"] == 3
    assert agg["hands_visible_frames"] == 2
    assert agg["hand_visibility_percentage"] == round((2/3)*100, 1)
    assert "gesture_description" in agg
    print("  [PASS] Hand visibility and gesture activity tracking verified.")


def test_07_movement_analysis():
    print("[TEST 7/10] Testing movement displacement and stability scoring...")
    from movement_analyzer import MovementAnalyzer
    analyzer = MovementAnalyzer(excessive_threshold=0.08)

    # Frame 1: Stationary anchor
    res1 = analyzer.process_frame({"nose": (0.50, 0.50)})
    assert res1["displacement"] == 0.0
    assert res1["is_excessive"] is False

    # Frame 2: Minor natural movement
    res2 = analyzer.process_frame({"nose": (0.505, 0.505)})
    assert res2["displacement"] > 0.0
    assert res2["is_excessive"] is False

    # Frame 3: Rapid large displacement (exceeds threshold)
    res3 = analyzer.process_frame({"nose": (0.65, 0.65)})
    assert res3["is_excessive"] is True

    agg = analyzer.get_aggregate_metrics()
    assert agg["valid_frames"] == 2
    assert agg["excessive_movement_events"] >= 1
    assert 0.0 <= agg["movement_stability_score"] <= 1.0
    assert "movement_description" in agg
    print("  [PASS] Movement rate, stability score, and excessive events verified.")


def test_08_invalid_video_and_camera_edge_cases():
    print("[TEST 8/10] Testing robustness on invalid inputs and edge cases...")
    from cv_interview_analyzer import CVInterviewAnalyzer
    analyzer = CVInterviewAnalyzer()

    # Case A: Nonexistent video path
    res_missing = analyzer.process_video("path/to/nonexistent/interview_sample_99.mp4")
    assert res_missing["success"] is False
    assert "invalid video file path" in res_missing["error"].lower()

    # Case B: Empty / invalid video file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(b"NOT_A_REAL_VIDEO_DATA")
        invalid_path = tf.name

    try:
        res_corrupt = analyzer.process_video(invalid_path)
        assert res_corrupt["success"] is False
        assert "failed to open video file" in res_corrupt["error"].lower()
    finally:
        if os.path.exists(invalid_path):
            os.remove(invalid_path)

    # Case C: Invalid camera device index (should fail gracefully)
    res_cam = analyzer.process_webcam(device_index=99999, duration_seconds=1.0)
    assert res_cam["success"] is False
    assert "camera device" in res_cam["error"].lower()

    print("  [PASS] Invalid video path, corrupt file, and unavailable camera handled gracefully.")


def test_09_synthetic_video_processing_and_summary():
    print("[TEST 9/10] Testing end-to-end video processing and summary generation...")
    import cv2
    import numpy as np
    from cv_interview_analyzer import CVInterviewAnalyzer

    analyzer = CVInterviewAnalyzer()

    # Create a synthetic 15-frame video file
    temp_dir = tempfile.gettempdir()
    video_path = os.path.join(temp_dir, "synthetic_interview_test.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 10.0, (320, 240))

    try:
        for i in range(15):
            # Draw synthetic background with moving circle simulating face
            frame = np.full((240, 320, 3), 40, dtype=np.uint8)
            cx = 160 + int(np.sin(i * 0.3) * 10)
            cy = 120 + int(np.cos(i * 0.3) * 5)
            cv2.circle(frame, (cx, cy), 45, (200, 180, 160), -1)
            # Eyes
            cv2.circle(frame, (cx - 15, cy - 10), 5, (255, 255, 255), -1)
            cv2.circle(frame, (cx + 15, cy - 10), 5, (255, 255, 255), -1)
            # Mouth
            cv2.line(frame, (cx - 15, cy + 20), (cx + 15, cy + 20), (50, 50, 200), 2)
            out.write(frame)
        out.release()

        # Process through analyzer
        res = analyzer.process_video(video_path, sample_fps=10)
        assert res["success"] is True, f"Video processing failed: {res.get('error')}"
        assert res["total_frames_processed"] > 0

        summary = res["summary"]
        assert "face_visibility_percentage" in summary
        assert "camera_facing_percentage" in summary
        assert "gaze_consistency_percentage" in summary
        assert "posture_consistency_percentage" in summary
        assert "movement_stability_percentage" in summary
        assert "gesture_frequency_percentage" in summary
        assert "reliability_status" in summary
        assert len(summary["observable_feedback"]) > 0

        # Check formatted report text
        report_text = summary["formatted_report"]
        assert "COMPUTER VISION ASSESSMENT" in report_text
        assert "Face Visibility" in report_text

        # Ensure NO unsupported psychological claims exist
        forbidden_terms = ["you were nervous", "dishonest", "anxious", "low confidence as fact", "intelligence"]
        for term in forbidden_terms:
            assert term not in report_text.lower(), f"Forbidden psychological term '{term}' found in report!"

        print("  [PASS] Video processing and objective, non-psychological CV summary verified.")
    finally:
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception:
                pass


def test_10_hr_and_cv_integration():
    print("[TEST 10/10] Testing HR round + CV analyzer integration & backward compatibility...")
    from hr_adaptive_engine import run_hr_interview
    from cv_interview_analyzer import CVInterviewAnalyzer

    # Create CV analyzer with pre-recorded visual metrics
    cv_analyzer = CVInterviewAnalyzer()
    for _ in range(5):
        cv_analyzer.movement_analyzer.process_frame({"nose": (0.50, 0.50)})
        cv_analyzer.posture_analyzer.process_landmarks({
            "left_shoulder": (0.35, 0.60),
            "right_shoulder": (0.65, 0.60),
            "nose": (0.50, 0.35)
        })

    mock_answers = [
        "In my previous project, we faced a tight deadline. I coordinated tasks and delivered on time.",
        "When disagreements arise in a team, I listen to all perspectives and find common ground.",
        "I stay updated on new technologies through online courses and open-source contributions.",
        "One challenge was debugging a distributed system bottleneck, which I resolved with targeted profiling.",
        "I align my personal career goals with the team vision to deliver meaningful impact."
    ]

    # Part A: Run HR Interview with CV analyzer integrated
    result_with_cv = run_hr_interview(
        resume_path="resume.pdf",
        num_questions=2,
        interactive=False,
        answers_provider=mock_answers,
        enable_adaptive_followups=False,
        cv_analyzer=cv_analyzer
    )

    assert result_with_cv is not None, "HR interview returned None"
    assert "overall_hr_score" in result_with_cv
    assert "average_relevance" in result_with_cv
    assert "average_clarity" in result_with_cv
    assert result_with_cv["camera_analysis"] is not None, "Expected camera_analysis to be present in result"
    assert "face_visibility_percentage" in result_with_cv["camera_analysis"]

    # Part B: Backward compatibility (enable_camera=False, no cv_analyzer)
    result_without_cv = run_hr_interview(
        resume_path="resume.pdf",
        num_questions=2,
        interactive=False,
        answers_provider=mock_answers,
        enable_adaptive_followups=False,
        enable_camera=False,
        cv_analyzer=None
    )

    assert result_without_cv["camera_analysis"] is None, "Expected camera_analysis=None when disabled"
    assert "overall_hr_score" in result_without_cv
    print("  [PASS] HR + CV pipeline integration and backward compatibility fully verified.")


def main():
    print("============================================================")
    print("       AI MULTIMODAL INTERVIEW - PHASE 5 CV TEST SUITE       ")
    print("============================================================\n")

    tests = [
        test_01_imports,
        test_02_face_detection_and_multi_face,
        test_03_head_orientation_and_cues,
        test_04_gaze_analysis,
        test_05_posture_analysis,
        test_06_gesture_analysis,
        test_07_movement_analysis,
        test_08_invalid_video_and_camera_edge_cases,
        test_09_synthetic_video_processing_and_summary,
        test_10_hr_and_cv_integration
    ]

    passed = 0
    total = len(tests)

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test_fn.__name__} raised an exception: {e}")
            import traceback
            traceback.print_exc()

    print("\n============================================================")
    print(f"       PHASE 5 TEST RESULTS: {passed}/{total} PASSED       ")
    print("============================================================")

    if passed == total:
        print("[SUCCESS] All Phase 5 Computer Vision tests passed successfully!")
        sys.exit(0)
    else:
        print(f"[FAILURE] {total - passed} tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
