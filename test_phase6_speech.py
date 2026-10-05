"""
Phase 6 Test Suite: Speech Analysis Module
==========================================
Comprehensive test suite verifying:
1. Speech module imports
2. Audio loading (WAV, formats, normalization)
3. Speech-to-text interface (real vs mocked distinction)
4. Speaking-rate calculation (WPM, pacing categories)
5. Pause detection & voice activity analysis
6. Filler word & phrase detection
7. Audio energy & volume consistency
8. Invalid audio & edge case handling
9. End-to-end speech analysis & formatted summary
10. HR Round + Speech integration & backward compatibility
"""

import os
import sys
import tempfile
from pathlib import Path
import numpy as np

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

speech_dir = project_root / "ai_ml" / "speech"
if str(speech_dir) not in sys.path:
    sys.path.append(str(speech_dir))

question_engine_dir = project_root / "ai_ml" / "question_engine"
if str(question_engine_dir) not in sys.path:
    sys.path.append(str(question_engine_dir))


def test_01_imports():
    print("[TEST 1/10] Checking speech module imports...")
    from speech_features import load_audio, AudioFeatureExtractor
    from pause_analyzer import PauseAnalyzer
    from filler_detector import FillerDetector
    from fluency_analysis import FluencyAnalyzer
    from speech_to_text import SpeechToTextTranscriber
    from speech_analyzer import SpeechAnalyzer

    afe = AudioFeatureExtractor()
    pa = PauseAnalyzer()
    fd = FillerDetector()
    fa = FluencyAnalyzer()
    stt = SpeechToTextTranscriber()
    sa = SpeechAnalyzer()

    assert afe is not None and pa is not None and fd is not None
    assert fa is not None and stt is not None and sa is not None
    print("  [PASS] All 6 speech analysis classes imported and instantiated.")


def test_02_audio_loading():
    print("[TEST 2/10] Testing audio loading and signal normalization...")
    from scipy.io import wavfile
    from speech_features import load_audio

    # Generate a temporary synthetic 2.0-second 16kHz sine wave
    sr = 16000
    t = np.linspace(0, 2.0, int(sr * 2.0), endpoint=False)
    sine_wave = np.sin(2 * np.pi * 440 * t) * 0.5  # 440Hz tone
    int16_data = np.int16(sine_wave * 32767)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        temp_wav = tf.name

    try:
        wavfile.write(temp_wav, sr, int16_data)
        samples, loaded_sr = load_audio(temp_wav)

        assert loaded_sr == sr, f"Expected sr={sr}, got {loaded_sr}"
        assert len(samples) == len(int16_data)
        assert -1.0 <= np.min(samples) <= 1.0
        assert -1.0 <= np.max(samples) <= 1.0
        print("  [PASS] Audio loading, format decoding, and normalization verified.")
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)


def test_03_speech_to_text_interface():
    print("[TEST 3/10] Testing speech-to-text interface (real vs mocked distinction)...")
    from speech_to_text import SpeechToTextTranscriber
    transcriber = SpeechToTextTranscriber()

    # 1. Non-existent file
    res_missing = transcriber.transcribe_file("path/to/nonexistent/sample_audio.wav")
    assert res_missing["status"] == "file_not_found"
    assert res_missing["transcript"] == ""

    # 2. Silent audio file
    sr = 16000
    silent_samples = np.zeros(int(sr * 1.5), dtype=np.int16)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        silent_wav = tf.name

    try:
        from scipy.io import wavfile
        wavfile.write(silent_wav, sr, silent_samples)
        res_silent = transcriber.transcribe_file(silent_wav)
        assert res_silent["status"] == "no_speech_detected"
        assert res_silent["transcript"] == ""

        # 3. Explicitly mocked transcript mode (tested in offline environments)
        res_mocked = transcriber.transcribe_file(
            silent_wav,
            mock_transcript="I developed a sign language converter using Python and OpenCV."
        )
        assert res_mocked["status"] == "mocked", "Expected status='mocked' for mocked input"
        assert res_mocked["word_count"] == 10
        assert "sign language" in res_mocked["transcript"].lower()
        print("  [PASS] STT status handling and mock vs real distinction verified.")
    finally:
        if os.path.exists(silent_wav):
            os.remove(silent_wav)


def test_04_speaking_rate_calculation():
    print("[TEST 4/10] Testing speaking-rate calculation (WPM and pacing categories)...")
    from fluency_analysis import FluencyAnalyzer
    analyzer = FluencyAnalyzer()

    # Case A: Standard conversational rate: 140 words in 60 seconds = 140 WPM
    sample_text = "word " * 140
    res_std = analyzer.analyze_fluency(sample_text, duration_seconds=60.0)
    assert res_std["word_count"] == 140
    assert abs(res_std["words_per_minute"] - 140.0) < 0.5
    assert res_std["pacing_category"] == "conversational_standard"

    # Case B: Deliberate/slow rate: 60 words in 60 seconds = 60 WPM
    slow_text = "word " * 60
    res_slow = analyzer.analyze_fluency(slow_text, duration_seconds=60.0)
    assert abs(res_slow["words_per_minute"] - 60.0) < 0.5
    assert res_slow["pacing_category"] == "deliberate_measured"

    # Case C: Rapid rate: 210 words in 60 seconds = 210 WPM
    fast_text = "word " * 210
    res_fast = analyzer.analyze_fluency(fast_text, duration_seconds=60.0)
    assert abs(res_fast["words_per_minute"] - 210.0) < 0.5
    assert res_fast["pacing_category"] == "rapid"

    # Case D: Zero duration / zero words (robustness against ZeroDivisionError)
    res_zero = analyzer.analyze_fluency("", duration_seconds=0.0)
    assert res_zero["words_per_minute"] == 0.0

    print("  [PASS] Speaking rate (WPM) and pacing classifications verified.")


def test_05_pause_detection():
    print("[TEST 5/10] Testing pause detection and voice activity analysis...")
    from pause_analyzer import PauseAnalyzer
    analyzer = PauseAnalyzer(min_pause_duration_s=0.30)

    # Construct synthetic audio signal:
    # 1.0s speech tone -> 0.8s silence -> 1.0s speech tone -> 0.8s silence -> 1.0s speech tone
    # Total duration = 4.6s with exactly 2 pauses of 0.8s each
    sr = 16000
    tone_1s = (np.sin(2 * np.pi * 300 * np.linspace(0, 1.0, sr, endpoint=False)) * 0.6).astype(np.float32)
    silence_08s = np.zeros(int(sr * 0.8), dtype=np.float32)

    signal = np.concatenate([tone_1s, silence_08s, tone_1s, silence_08s, tone_1s])

    res = analyzer.analyze_signal(signal, sr)
    assert res["pause_count"] == 2, f"Expected 2 pauses, got {res['pause_count']}"
    assert abs(res["average_pause_duration"] - 0.8) <= 0.15, f"Expected avg pause ~0.8s, got {res['average_pause_duration']}"
    assert 0.55 <= res["speech_active_ratio"] <= 0.75, f"Expected active ratio ~0.65, got {res['speech_active_ratio']}"
    assert "feedback" in res
    print("  [PASS] Pause detection, pause durations, and active ratio verified.")


def test_06_filler_detection():
    print("[TEST 6/10] Testing filler word and phrase detection...")
    from filler_detector import FillerDetector
    detector = FillerDetector()

    transcript = (
        "Um, in my last project, like, we actually faced a major bottleneck, "
        "you know, and basically resolved it on time."
    )

    res = detector.analyze(transcript)
    assert res["filler_count"] >= 5, f"Expected at least 5 fillers, got {res['filler_count']}"
    assert "you know" in res["detected_fillers"], "Expected multi-word filler 'you know' to be detected"
    assert "um" in res["detected_fillers"]
    assert "like" in res["detected_fillers"]
    assert "actually" in res["detected_fillers"]
    assert "basically" in res["detected_fillers"]
    assert res["fillers_per_100_words"] > 0.0
    assert len(res["most_frequent_fillers"]) > 0
    print("  [PASS] Multi-word and single-word filler detection verified.")


def test_07_energy_analysis():
    print("[TEST 7/10] Testing audio energy and volume consistency...")
    from speech_features import AudioFeatureExtractor
    extractor = AudioFeatureExtractor()

    sr = 16000
    # Signal A: Constant volume tone (high consistency)
    t = np.linspace(0, 2.0, sr * 2, endpoint=False)
    steady_signal = (np.sin(2 * np.pi * 400 * t) * 0.5).astype(np.float32)
    res_steady = extractor.analyze_audio(steady_signal, sr)
    assert res_steady["success"] is True
    assert res_steady["energy_consistency_score"] >= 0.70

    # Signal B: Signal with extreme volume spikes and dips (lower consistency)
    erratic_signal = np.copy(steady_signal)
    erratic_signal[:sr // 2] *= 0.02
    erratic_signal[sr: sr + sr // 4] *= 1.8
    res_erratic = extractor.analyze_audio(erratic_signal, sr)
    assert res_erratic["success"] is True
    assert res_erratic["energy_consistency_score"] <= res_steady["energy_consistency_score"]

    print("  [PASS] RMS energy, dynamics, and consistency score verified.")


def test_08_invalid_audio_and_edge_cases():
    print("[TEST 8/10] Testing robustness on invalid audio inputs and edge cases...")
    from speech_analyzer import SpeechAnalyzer
    analyzer = SpeechAnalyzer()

    # Case A: Nonexistent file path
    res_missing = analyzer.analyze_audio_file("path/to/missing_audio_recording.wav")
    assert res_missing["success"] is False
    assert "not found" in res_missing["error"].lower()

    # Case B: Empty numpy array
    res_empty = analyzer.analyze_signal(np.array([], dtype=np.float32), 16000)
    assert res_empty["success"] is False
    assert "empty" in res_empty["error"].lower()

    # Case C: Corrupt / non-audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tf.write(b"CORRUPT_NON_AUDIO_HEADER_DATA")
        corrupt_path = tf.name

    try:
        res_corrupt = analyzer.analyze_audio_file(corrupt_path)
        assert res_corrupt["success"] is False
        assert "failed" in res_corrupt["error"].lower()
    finally:
        if os.path.exists(corrupt_path):
            os.remove(corrupt_path)

    print("  [PASS] Missing file, empty buffer, and corrupt audio handled gracefully.")


def test_09_end_to_end_speech_analysis():
    print("[TEST 9/10] Testing end-to-end speech analysis and report generation...")
    from scipy.io import wavfile
    from speech_analyzer import SpeechAnalyzer
    analyzer = SpeechAnalyzer()

    # Create a 3.0s test audio file with vocal tones and pauses
    sr = 16000
    tone_1s = (np.sin(2 * np.pi * 350 * np.linspace(0, 1.0, sr, endpoint=False)) * 0.5).astype(np.float32)
    silence_05s = np.zeros(int(sr * 0.5), dtype=np.float32)
    test_signal = np.concatenate([tone_1s, silence_05s, tone_1s, silence_05s])

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        test_wav = tf.name

    try:
        int16_data = np.int16(test_signal * 32767)
        wavfile.write(test_wav, sr, int16_data)

        mock_text = "In my project, I basically designed the database architecture and like coordinated the team."
        summary = analyzer.analyze_audio_file(test_wav, mock_transcript=mock_text)

        assert summary["success"] is True
        assert summary["duration_seconds"] >= 2.9
        assert summary["word_count"] > 0
        assert summary["speaking_rate_wpm"] > 0.0
        assert summary["pause_count"] >= 1
        assert summary["filler_count"] >= 2  # 'basically', 'like'
        assert 0.0 <= summary["energy_consistency_percentage"] <= 100.0
        assert 0.0 <= summary["speech_continuity_percentage"] <= 100.0
        assert len(summary["observable_feedback"]) > 0

        # Check formatted report text
        report = summary["formatted_report"]
        assert "SPEECH ANALYSIS ASSESSMENT" in report
        assert "Speaking Rate" in report
        assert "Filler Word Count" in report

        # Verify NO forbidden psychological terms are present
        forbidden_terms = ["you were nervous", "anxious", "dishonest", "lacked confidence", "intelligence"]
        for term in forbidden_terms:
            assert term not in report.lower(), f"Forbidden psychological claim '{term}' found in report!"

        print("  [PASS] Full speech assessment pipeline and objective report verified.")
    finally:
        if os.path.exists(test_wav):
            os.remove(test_wav)


def test_10_hr_and_speech_integration():
    print("[TEST 10/10] Testing HR round + Speech integration & backward compatibility...")
    from scipy.io import wavfile
    from hr_adaptive_engine import run_hr_interview
    from speech_analyzer import SpeechAnalyzer

    # Generate test audio
    sr = 16000
    tone = (np.sin(2 * np.pi * 350 * np.linspace(0, 2.0, sr * 2, endpoint=False)) * 0.4).astype(np.float32)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        audio_wav = tf.name

    try:
        int16_data = np.int16(tone * 32767)
        wavfile.write(audio_wav, sr, int16_data)

        # Pre-instantiate speech analyzer with mock transcript
        speech_analyzer = SpeechAnalyzer()
        speech_analyzer.analyze_audio_file(
            audio_wav,
            mock_transcript="I led the software implementation and ensured reliable delivery."
        )

        mock_answers = [
            "In my college project, I coordinated tasks and handled core backend implementation.",
            "I resolve team conflicts through open communication and identifying shared objectives."
        ]

        # Part A: Run HR Interview with speech analysis attached
        res_with_speech = run_hr_interview(
            resume_path="resume.pdf",
            num_questions=2,
            interactive=False,
            answers_provider=mock_answers,
            enable_adaptive_followups=False,
            speech_analyzer=speech_analyzer
        )

        assert res_with_speech is not None
        assert "overall_hr_score" in res_with_speech
        assert "speech_analysis" in res_with_speech
        assert res_with_speech["speech_analysis"] is not None
        assert "speaking_rate_wpm" in res_with_speech["speech_analysis"]
        assert "pause_count" in res_with_speech["speech_analysis"]

        # Part B: Backward compatibility (speech disabled)
        res_no_speech = run_hr_interview(
            resume_path="resume.pdf",
            num_questions=2,
            interactive=False,
            answers_provider=mock_answers,
            enable_adaptive_followups=False,
            enable_speech=False,
            speech_analyzer=None
        )

        assert res_no_speech["speech_analysis"] is None, "Expected speech_analysis=None when disabled"
        assert "overall_hr_score" in res_no_speech
        print("  [PASS] HR + Speech pipeline integration and backward compatibility fully verified.")
    finally:
        if os.path.exists(audio_wav):
            os.remove(audio_wav)


def main():
    print("============================================================")
    print("      AI MULTIMODAL INTERVIEW - PHASE 6 SPEECH TEST SUITE   ")
    print("============================================================\n")

    tests = [
        test_01_imports,
        test_02_audio_loading,
        test_03_speech_to_text_interface,
        test_04_speaking_rate_calculation,
        test_05_pause_detection,
        test_06_filler_detection,
        test_07_energy_analysis,
        test_08_invalid_audio_and_edge_cases,
        test_09_end_to_end_speech_analysis,
        test_10_hr_and_speech_integration
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
    print(f"       PHASE 6 TEST RESULTS: {passed}/{total} PASSED       ")
    print("============================================================")

    if passed == total:
        print("[SUCCESS] All Phase 6 Speech Analysis tests passed successfully!")
        sys.exit(0)
    else:
        print(f"[FAILURE] {total - passed} tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
