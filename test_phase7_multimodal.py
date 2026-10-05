"""
Phase 7 Test Suite: Multimodal Employability Assessment & Fusion Platform
========================================================================
Comprehensive verification covering:
1. Module imports and class instantiations
2. Multimodal feature extraction from complete interview outputs
3. Direction-aware scale normalization across disparate metrics
4. Configurable weighted multimodal fusion
5. Missing CV modality detection & dynamic weight renormalization
6. Missing Speech modality handling without penalty
7. Missing both CV and Speech modalities (text & technical only)
8. Placement readiness classification and threshold boundary handling
9. Dynamic personalized recommendations and ethical language safeguards
10. End-to-end multimodal assessment, formatted reporting, and persistent storage
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# Ensure project root and subdirectories are on sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

eval_dir = project_root / "ai_ml" / "evaluation"
if str(eval_dir) not in sys.path:
    sys.path.append(str(eval_dir))

models_dir = project_root / "ai_ml" / "models"
if str(models_dir) not in sys.path:
    sys.path.append(str(models_dir))

rec_dir = project_root / "ai_ml" / "recomendation"
if str(rec_dir) not in sys.path:
    sys.path.append(str(rec_dir))


def test_01_imports():
    print("[TEST 1/10] Verifying Phase 7 module imports and instantiations...")
    from metrics import MultimodalFeatureExtractor
    from employability_model import EmployabilityModel, DEFAULT_MODALITY_WEIGHTS, DEFAULT_READINESS_THRESHOLDS
    from recommendation_engine import RecommendationEngine
    from evaluate_model import MultimodalEvaluator, run_employability_assessment

    extractor = MultimodalFeatureExtractor()
    model = EmployabilityModel()
    engine = RecommendationEngine()
    evaluator = MultimodalEvaluator()

    assert extractor is not None, "Failed to instantiate MultimodalFeatureExtractor"
    assert model is not None, "Failed to instantiate EmployabilityModel"
    assert engine is not None, "Failed to instantiate RecommendationEngine"
    assert evaluator is not None, "Failed to instantiate MultimodalEvaluator"
    assert callable(run_employability_assessment), "run_employability_assessment must be callable"

    assert "technical" in model.weights
    assert "hr_nlp" in model.weights
    assert "speech" in model.weights
    assert "computer_vision" in model.weights
    assert "resume_jd" in model.weights

    print("  [PASS] All Phase 7 modules successfully imported and instantiated.")


def test_02_feature_extraction():
    print("[TEST 2/10] Testing multimodal feature extraction with complete data...")
    from metrics import MultimodalFeatureExtractor

    sample_tech = {
        "overall_technical_score": 82.5,
        "average_score": 0.825,
        "total_questions": 5,
        "strong_topics": ["Python", "Algorithms"],
        "weak_topics": ["System Design"]
    }
    sample_hr = {
        "overall_hr_score": 78.0,
        "average_relevance": 85.0,
        "average_semantic_similarity": 0.81,
        "average_completeness": 75.0,
        "average_clarity": 80.0,
        "average_conciseness": 70.0,
        "average_star_score": 82.0
    }
    sample_cv = {
        "face_visibility_percentage": 94.0,
        "camera_facing_percentage": 88.0,
        "gaze_consistency_percentage": 85.0,
        "posture_consistency_percentage": 90.0,
        "movement_stability_percentage": 92.0,
        "gesture_frequency_percentage": 25.0,
        "reliability_status": "reliable"
    }
    sample_speech = {
        "speaking_rate_wpm": 138.0,
        "pause_count": 4,
        "average_pause_seconds": 0.75,
        "speech_active_percentage": 84.0,
        "fillers_per_100_words": 1.2,
        "energy_consistency_percentage": 86.0,
        "speech_continuity_percentage": 88.0
    }
    sample_resume_jd = {
        "job_match_score": 80.0,
        "matched_skills": ["Python", "FastAPI", "Docker"],
        "missing_skills": ["Kubernetes"]
    }

    features = MultimodalFeatureExtractor.extract_features(
        technical_results=sample_tech,
        hr_results=sample_hr,
        cv_results=sample_cv,
        speech_results=sample_speech,
        resume_jd_results=sample_resume_jd
    )

    avail = features["availability"]
    assert avail["technical"] is True, "Technical should be available"
    assert avail["hr_nlp"] is True, "HR NLP should be available"
    assert avail["computer_vision"] is True, "CV should be available"
    assert avail["speech"] is True, "Speech should be available"
    assert avail["resume_jd"] is True, "Resume/JD should be available"

    assert features["technical"]["overall_score"] == 82.5
    assert features["hr_nlp"]["clarity_score"] == 80.0
    assert features["computer_vision"]["face_visibility_percentage"] == 94.0
    assert features["speech"]["speaking_rate_wpm"] == 138.0
    assert features["resume_jd"]["job_match_score"] == 80.0

    print("  [PASS] Feature extraction structured all 5 modalities accurately.")


def test_03_normalization_rules():
    print("[TEST 3/10] Verifying direction-aware scale normalization across metrics...")
    from employability_model import EmployabilityModel

    # 1. Technical normalization (0-100 -> 0-1)
    assert EmployabilityModel.normalize_technical({"overall_score": 85.0}) == 0.85
    assert EmployabilityModel.normalize_technical({"overall_score": 110.0}) == 1.0  # clipped
    assert EmployabilityModel.normalize_technical({"overall_score": -10.0}) == 0.0  # clipped

    # 2. HR NLP normalization
    assert EmployabilityModel.normalize_hr_nlp({"overall_score": 75.0}) == 0.75

    # 3. Speech normalization: WPM curve
    optimal_speech = {
        "speaking_rate_wpm": 135.0,  # in optimal 110-165 range
        "fillers_per_100_words": 0.0,  # 0 fillers -> 1.0
        "average_pause_seconds": 0.6,  # <= 0.9s -> 1.0
        "energy_consistency_percentage": 100.0,
        "speech_continuity_percentage": 100.0
    }
    opt_speech_norm = EmployabilityModel.normalize_speech(optimal_speech)
    assert opt_speech_norm >= 0.95, f"Optimal speech should score near 1.0, got {opt_speech_norm}"

    # Excessive fillers should penalize
    high_filler_speech = dict(optimal_speech, fillers_per_100_words=8.0)
    high_filler_norm = EmployabilityModel.normalize_speech(high_filler_speech)
    assert high_filler_norm < opt_speech_norm, "High filler density must yield a lower normalized score"

    # Extreme slow pacing should penalize
    slow_speech = dict(optimal_speech, speaking_rate_wpm=45.0)
    slow_norm = EmployabilityModel.normalize_speech(slow_speech)
    assert slow_norm < opt_speech_norm, "Slow speech must yield a lower normalized score"

    # 4. Computer Vision normalization
    optimal_cv = {
        "face_visibility_percentage": 100.0,
        "camera_facing_percentage": 100.0,
        "posture_consistency_percentage": 100.0,
        "movement_stability_percentage": 100.0,
        "gesture_frequency_percentage": 30.0,
        "multiple_faces_detected": False,
        "reliability_status": "reliable"
    }
    opt_cv_norm = EmployabilityModel.normalize_computer_vision(optimal_cv)
    assert opt_cv_norm >= 0.95, f"Optimal CV should score near 1.0, got {opt_cv_norm}"

    unreliable_cv = dict(optimal_cv, multiple_faces_detected=True)
    unrel_norm = EmployabilityModel.normalize_computer_vision(unreliable_cv)
    assert unrel_norm < opt_cv_norm, "Multiple faces / unreliable status must discount CV score"

    print("  [PASS] Normalization handles scales, directionality, and outliers properly.")


def test_04_weighted_multimodal_fusion():
    print("[TEST 4/10] Verifying weighted multimodal fusion with all modalities...")
    from employability_model import EmployabilityModel

    raw_features = {
        "availability": {
            "technical": True,
            "hr_nlp": True,
            "computer_vision": True,
            "speech": True,
            "resume_jd": True
        },
        "technical": {"overall_score": 80.0},
        "hr_nlp": {"overall_score": 80.0},
        "computer_vision": {
            "face_visibility_percentage": 100.0,
            "camera_facing_percentage": 100.0,
            "posture_consistency_percentage": 100.0,
            "movement_stability_percentage": 100.0,
            "gesture_frequency_percentage": 25.0
        },
        "speech": {
            "speaking_rate_wpm": 130.0,
            "fillers_per_100_words": 0.0,
            "average_pause_seconds": 0.5,
            "energy_consistency_percentage": 100.0,
            "speech_continuity_percentage": 100.0
        },
        "resume_jd": {"job_match_score": 80.0}
    }

    model = EmployabilityModel()
    result = model.fuse_modalities(raw_features)

    assert "employability_score" in result
    assert "readiness_level" in result
    assert "confidence" in result
    assert result["confidence"] == 1.0, "All 5 modalities evaluated should give 1.0 confidence"
    assert len(result["active_modalities"]) == 5

    # Check active weights sum to 1.0
    active_weights = result["active_weights"]
    total_w = sum(active_weights.values())
    assert abs(total_w - 1.0) < 1e-4, f"Active weights must sum to 1.0, got {total_w}"

    # Fused score should be approximately 85-90% given optimal CV and speech with 80% tech/hr/resume
    assert 75.0 <= result["employability_score"] <= 95.0
    assert result["readiness_level"] in ["Ready", "Highly Ready"]

    print(f"  [PASS] Multimodal fusion score computed: {result['employability_score']:.1f}% ({result['readiness_level']}).")


def test_05_missing_cv_modality():
    print("[TEST 5/10] Testing missing CV modality handling and weight renormalization...")
    from employability_model import EmployabilityModel

    # CV is unavailable (e.g., candidate without camera)
    raw_features = {
        "availability": {
            "technical": True,
            "hr_nlp": True,
            "computer_vision": False,
            "speech": True,
            "resume_jd": True
        },
        "technical": {"overall_score": 80.0},
        "hr_nlp": {"overall_score": 80.0},
        "computer_vision": {},
        "speech": {
            "speaking_rate_wpm": 135.0,
            "fillers_per_100_words": 0.0,
            "average_pause_seconds": 0.6,
            "energy_consistency_percentage": 100.0,
            "speech_continuity_percentage": 100.0
        },
        "resume_jd": {"job_match_score": 80.0}
    }

    model = EmployabilityModel()
    result = model.fuse_modalities(raw_features)

    assert "computer_vision" not in result["active_modalities"], "CV must not be listed as active"
    assert result["confidence"] == 0.8, "4/5 modalities should give 0.8 confidence"

    # Active weights must sum to 1.0 (within rounding precision)
    w_sum = sum(result["active_weights"].values())
    assert abs(w_sum - 1.0) < 1e-3, f"Active weights must renormalize to 1.0, got {w_sum}"

    # Candidate should not be penalized to zero for missing CV
    assert result["employability_score"] >= 75.0, "Candidate must not receive zero penalty for missing camera"

    # Expected technical weight = 0.30 / 0.85 ≈ 0.353
    expected_tech_w = 0.30 / 0.85
    actual_tech_w = result["active_weights"]["technical"]
    assert abs(actual_tech_w - expected_tech_w) < 0.01, f"Expected tech weight ~{expected_tech_w:.3f}, got {actual_tech_w}"

    print(f"  [PASS] CV exclusion verified; renormalized weights sum to {w_sum:.2f}, score is {result['employability_score']:.1f}%.")


def test_06_missing_speech_modality():
    print("[TEST 6/10] Testing missing Speech modality handling...")
    from employability_model import EmployabilityModel

    # Speech is unavailable (e.g., text-only interview with camera)
    raw_features = {
        "availability": {
            "technical": True,
            "hr_nlp": True,
            "computer_vision": True,
            "speech": False,
            "resume_jd": True
        },
        "technical": {"overall_score": 75.0},
        "hr_nlp": {"overall_score": 75.0},
        "computer_vision": {
            "face_visibility_percentage": 90.0,
            "camera_facing_percentage": 85.0,
            "posture_consistency_percentage": 85.0,
            "movement_stability_percentage": 90.0,
            "gesture_frequency_percentage": 20.0
        },
        "speech": {},
        "resume_jd": {"job_match_score": 75.0}
    }

    model = EmployabilityModel()
    result = model.fuse_modalities(raw_features)

    assert "speech" not in result["active_modalities"]
    assert result["confidence"] == 0.8
    w_sum = sum(result["active_weights"].values())
    assert abs(w_sum - 1.0) < 1e-3, f"Active weights must renormalize to 1.0, got {w_sum}"
    assert result["employability_score"] >= 70.0

    print(f"  [PASS] Speech exclusion verified; score: {result['employability_score']:.1f}%.")


def test_07_missing_both_cv_and_speech():
    print("[TEST 7/10] Testing missing both CV and Speech modalities (text & technical only)...")
    from employability_model import EmployabilityModel

    raw_features = {
        "availability": {
            "technical": True,
            "hr_nlp": True,
            "computer_vision": False,
            "speech": False,
            "resume_jd": True
        },
        "technical": {"overall_score": 85.0},
        "hr_nlp": {"overall_score": 80.0},
        "computer_vision": {},
        "speech": {},
        "resume_jd": {"job_match_score": 75.0}
    }

    model = EmployabilityModel()
    result = model.fuse_modalities(raw_features)

    assert len(result["active_modalities"]) == 3
    assert result["confidence"] == 0.6  # 3/5
    w_sum = sum(result["active_weights"].values())
    assert abs(w_sum - 1.0) < 1e-4

    # Technical: 0.30/0.70 ≈ 0.429, HR: 0.25/0.70 ≈ 0.357, Resume: 0.15/0.70 ≈ 0.214
    expected_score = (0.85 * 0.30/0.70 + 0.80 * 0.25/0.70 + 0.75 * 0.15/0.70) * 100.0
    assert abs(result["employability_score"] - expected_score) < 0.5

    print(f"  [PASS] 3-modality fusion cleanly computed score {result['employability_score']:.1f}% without errors.")


def test_08_readiness_level_categories():
    print("[TEST 8/10] Testing placement readiness categorization across score thresholds...")
    from employability_model import EmployabilityModel

    model = EmployabilityModel()

    def get_level(score: float) -> str:
        dummy_feat = {
            "availability": {"technical": True},
            "technical": {"overall_score": score}
        }
        return model.fuse_modalities(dummy_feat)["readiness_level"]

    assert get_level(92.0) == "Highly Ready", "Score 92 should be Highly Ready"
    assert get_level(78.0) == "Ready", "Score 78 should be Ready"
    assert get_level(62.0) == "Developing", "Score 62 should be Developing"
    assert get_level(46.0) == "Needs Improvement", "Score 46 should be Needs Improvement"
    assert get_level(30.0) == "Early Stage", "Score 30 should be Early Stage"

    # Test custom threshold override
    custom_thresholds = [
        (80.0, "Tier 1 Ready", "Top readiness"),
        (0.0, "Tier 2 In Progress", "Developing readiness")
    ]
    custom_model = EmployabilityModel(readiness_thresholds=custom_thresholds)
    res = custom_model.fuse_modalities({"availability": {"technical": True}, "technical": {"overall_score": 85.0}})
    assert res["readiness_level"] == "Tier 1 Ready"

    print("  [PASS] Readiness levels and custom threshold boundaries fully verified.")


def test_09_dynamic_recommendations_and_ethics():
    print("[TEST 9/10] Verifying dynamic personalized feedback and ethical language...")
    from recommendation_engine import RecommendationEngine

    # Candidate 1: Strong technical, but weak acoustic delivery (high fillers, rapid speech)
    raw_1 = {
        "technical": {"weak_topics": [], "strong_topics": ["Distributed Systems", "Go"]},
        "resume_jd": {"missing_skills": [], "matched_skills": ["Go", "Docker"]},
        "hr_nlp": {"relevance_score": 85.0, "completeness_score": 80.0, "clarity_score": 85.0},
        "speech": {"speaking_rate_wpm": 195.0, "fillers_per_100_words": 6.2, "average_pause_seconds": 0.5},
        "computer_vision": {"camera_facing_percentage": 90.0, "posture_consistency_percentage": 85.0}
    }
    comp_1 = {"technical": 90.0, "resume_jd": 90.0, "hr_nlp": 85.0, "speech": 55.0, "computer_vision": 85.0}
    fb_1 = RecommendationEngine.generate_assessment(raw_1, comp_1, 80.0, "Ready")

    # Candidate 2: Low technical (weak in SQL, Kubernetes), missing skills, low posture consistency
    raw_2 = {
        "technical": {"weak_topics": ["SQL Queries", "Kubernetes Clustering"], "strong_topics": []},
        "resume_jd": {"missing_skills": ["Kubernetes", "PostgreSQL"], "matched_skills": []},
        "hr_nlp": {"relevance_score": 58.0, "completeness_score": 50.0, "clarity_score": 60.0},
        "speech": {"speaking_rate_wpm": 135.0, "fillers_per_100_words": 1.0, "average_pause_seconds": 0.6},
        "computer_vision": {"camera_facing_percentage": 50.0, "posture_consistency_percentage": 55.0}
    }
    comp_2 = {"technical": 52.0, "resume_jd": 45.0, "hr_nlp": 55.0, "speech": 92.0, "computer_vision": 55.0}
    fb_2 = RecommendationEngine.generate_assessment(raw_2, comp_2, 54.0, "Needs Improvement")

    # 1. Candidate specificity
    cand1_rec_text = " ".join(fb_1["recommendations"] + fb_1["improvement_areas"])
    cand2_rec_text = " ".join(fb_2["recommendations"] + fb_2["improvement_areas"])

    assert "filler" in cand1_rec_text.lower() or "speaking pace" in cand1_rec_text.lower()
    assert "sql" in cand2_rec_text.lower() or "kubernetes" in cand2_rec_text.lower()
    assert "posture" in cand2_rec_text.lower() or "camera" in cand2_rec_text.lower()

    # 2. Ethical Safeguards: ensure forbidden psychological terms are absent
    forbidden_terms = [
        "nervous", "anxiety", "dishonest", "deceptive", "deception",
        "liar", "personality", "mental state", "psychological", "guaranteed"
    ]
    for term in forbidden_terms:
        assert term not in cand1_rec_text.lower(), f"Forbidden psychological term '{term}' found in candidate 1 feedback!"
        assert term not in cand2_rec_text.lower(), f"Forbidden psychological term '{term}' found in candidate 2 feedback!"

    print("  [PASS] Feedback is strictly dynamic, candidate-specific, and ethically compliant.")


def test_10_end_to_end_assessment_and_persistence():
    print("[TEST 10/10] Verifying end-to-end multimodal assessment and persistence...")
    from evaluate_model import MultimodalEvaluator, run_employability_assessment

    with tempfile.TemporaryDirectory() as tmp_dir:
        evaluator = MultimodalEvaluator(results_dir=tmp_dir)

        sample_tech = {
            "overall_technical_score": 84.0,
            "strong_topics": ["Python", "Concurrency"],
            "weak_topics": ["Distributed Cache"],
            "candidate_resume": "Jane_Doe_Resume.pdf"
        }
        sample_hr = {
            "overall_hr_score": 82.0,
            "candidate_name": "Jane Doe",
            "average_relevance": 88.0,
            "average_completeness": 80.0,
            "average_clarity": 85.0
        }
        sample_cv = {
            "face_visibility_percentage": 95.0,
            "camera_facing_percentage": 90.0,
            "posture_consistency_percentage": 88.0,
            "movement_stability_percentage": 92.0,
            "gesture_frequency_percentage": 25.0
        }
        sample_speech = {
            "speaking_rate_wpm": 142.0,
            "pause_count": 3,
            "average_pause_seconds": 0.7,
            "fillers_per_100_words": 1.1,
            "speech_continuity_percentage": 90.0
        }
        sample_rjd = {
            "job_match_score": 85.0,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Redis"]
        }

        # Run assessment
        assessment = evaluator.evaluate(
            technical_results=sample_tech,
            hr_results=sample_hr,
            cv_results=sample_cv,
            speech_results=sample_speech,
            resume_jd_results=sample_rjd,
            candidate_id="Candidate_JaneDoe_001",
            save_results=True
        )

        assert assessment["candidate_id"] == "Candidate_JaneDoe_001"
        assert assessment["employability_score"] > 80.0
        assert assessment["readiness_level"] in ["Ready", "Highly Ready"]
        assert len(assessment["strengths"]) > 0
        assert len(assessment["recommendations"]) > 0

        # Verify formatted report text
        report = assessment["formatted_report"]
        assert "MULTIMODAL EMPLOYABILITY ASSESSMENT" in report
        assert "Candidate_JaneDoe_001" in report
        assert "Technical Performance" in report
        assert "KEY IDENTIFIED STRENGTHS:" in report

        # Verify persistent storage in temporary results directory
        storage_path = Path(tmp_dir) / "employability_assessments.json"
        assert storage_path.exists(), "employability_assessments.json must be written to disk"

        with open(storage_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            assert isinstance(records, list)
            assert len(records) == 1
            assert records[0]["candidate_id"] == "Candidate_JaneDoe_001"
            assert records[0]["employability_score"] == assessment["employability_score"]

        # Test convenience function run_employability_assessment()
        convenience_res = run_employability_assessment(
            technical_results=sample_tech,
            candidate_id="Candidate_JaneDoe_002",
            save_results=False
        )
        assert convenience_res["candidate_id"] == "Candidate_JaneDoe_002"
        assert convenience_res["confidence"] < 1.0  # partial modality

    print("  [PASS] End-to-end evaluation, formatted reporting, and JSON persistence verified.")


def main():
    print("============================================================")
    print("    STARTING PHASE 7 MULTIMODAL ASSESSMENT TEST SUITE      ")
    print("============================================================")

    tests = [
        test_01_imports,
        test_02_feature_extraction,
        test_03_normalization_rules,
        test_04_weighted_multimodal_fusion,
        test_05_missing_cv_modality,
        test_06_missing_speech_modality,
        test_07_missing_both_cv_and_speech,
        test_08_readiness_level_categories,
        test_09_dynamic_recommendations_and_ethics,
        test_10_end_to_end_assessment_and_persistence
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
    print(f"       PHASE 7 TEST RESULTS: {passed}/{total} PASSED       ")
    print("============================================================")

    if passed == total:
        print("[SUCCESS] All Phase 7 Multimodal Assessment tests passed successfully!")
        sys.exit(0)
    else:
        print(f"[FAILURE] {total - passed} tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
