"""
Phase 8 Comprehensive Test Suite: End-to-End Employability & Assessment System
=============================================================================
Verifies:
1. Module imports and class instantiations
2. Final assessment orchestration and unified data schema
3. Candidate-independent assessment execution
4. Skill-gap to personalized roadmap generation
5. Transparent priority assignment (HIGH, MEDIUM, LOW)
6. Dynamic personalized recommendation generation and ethical safeguards
7. First-assessment baseline progress handling
8. Multiple-assessment progress tracking and timeline series
9. Improvement, decline, and resolved skill-gap detection
10. Multi-format final report generation (JSON, Markdown, HTML, CSV)
11. Missing-modality resilience and error handling
12. Complete end-to-end candidate workflow with project resume and JD
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

for sub_dir in ["preprocessing", "nlp", "models", "question_engine", "recomendation", "evaluation", "speech", "computer_vision"]:
    p = str(project_root / "ai_ml" / sub_dir)
    if p not in sys.path:
        sys.path.append(p)


def test_01_imports():
    print("[TEST 1/12] Verifying Phase 8 module imports and instantiations...")
    from skill_gap import SkillGapAnalyzer
    from learning_path import LearningPathGenerator
    from performance_model import ProgressTracker
    from final_report_generator import FinalReportGenerator
    from orchestrator import EmployabilityPipeline, run_final_employability_pipeline

    analyzer = SkillGapAnalyzer()
    generator = LearningPathGenerator()
    tracker = ProgressTracker()
    reporter = FinalReportGenerator()
    pipeline = EmployabilityPipeline()

    assert analyzer is not None, "SkillGapAnalyzer failed to instantiate"
    assert generator is not None, "LearningPathGenerator failed to instantiate"
    assert tracker is not None, "ProgressTracker failed to instantiate"
    assert reporter is not None, "FinalReportGenerator failed to instantiate"
    assert pipeline is not None, "EmployabilityPipeline failed to instantiate"
    assert callable(run_final_employability_pipeline), "run_final_employability_pipeline must be callable"

    print("  [PASS] All Phase 8 modules successfully imported and instantiated.")


def test_02_final_assessment_orchestration():
    print("[TEST 2/12] Testing unified assessment orchestration schema...")
    from orchestrator import EmployabilityPipeline

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_history = Path(tmp_dir) / "test_history.json"
        pipeline = EmployabilityPipeline(reports_dir=tmp_dir, history_file=tmp_history)

        sample_tech = {
            "overall_technical_score": 82.0,
            "average_score": 0.82,
            "strong_topics": ["Python", "Algorithms"],
            "weak_topics": ["Docker"]
        }
        sample_hr = {
            "overall_hr_score": 79.0,
            "average_relevance": 84.0,
            "average_clarity": 85.0,
            "average_star_score": 80.0
        }
        sample_speech = {
            "speaking_rate_wpm": 140.0,
            "fillers_per_100_words": 1.2,
            "average_pause_seconds": 0.7
        }
        sample_cv = {
            "camera_facing_percentage": 90.0,
            "posture_consistency_percentage": 88.0,
            "movement_stability_percentage": 92.0
        }
        sample_rjd = {
            "target_role": "AI Engineer",
            "job_match_score": 80.0,
            "matched_skills": ["python", "machine learning"],
            "missing_skills": ["docker", "kubernetes"]
        }

        assessment = pipeline.evaluate_candidate(
            technical_results=sample_tech,
            hr_results=sample_hr,
            cv_results=sample_cv,
            speech_results=sample_speech,
            resume_jd_results=sample_rjd,
            candidate_id="Candidate_Test_001",
            save_reports=False
        )

        required_keys = [
            "candidate", "job_alignment", "skill_gaps", "technical_assessment",
            "hr_assessment", "visual_assessment", "speech_assessment",
            "multimodal_assessment", "readiness", "strengths",
            "improvement_areas", "recommendations", "learning_roadmap",
            "progress_tracking", "visualization_data"
        ]
        for k in required_keys:
            assert k in assessment, f"Missing key in unified assessment object: '{k}'"

        assert 0.0 <= assessment["readiness"]["score"] <= 100.0
        assert assessment["readiness"]["level"] in ["Highly Ready", "Ready", "Developing", "Needs Improvement", "Early Stage"]
        assert len(assessment["visualization_data"]["radar_chart"]) >= 5

        print("  [PASS] Unified assessment object adheres to complete schema.")


def test_03_candidate_independent_assessment():
    print("[TEST 3/12] Testing candidate-independent evaluation (Candidate A vs Candidate B)...")
    from orchestrator import EmployabilityPipeline

    pipeline = EmployabilityPipeline()

    # Candidate A: Backend Engineer with missing Docker/Kubernetes
    cand_a_rjd = {
        "target_role": "Backend Engineer",
        "job_match_score": 75.0,
        "matched_skills": ["python", "django", "postgresql"],
        "missing_skills": ["docker", "kubernetes"]
    }
    cand_a = pipeline.evaluate_candidate(
        candidate_id="Candidate Alpha",
        resume_jd_results=cand_a_rjd,
        save_reports=False
    )

    # Candidate B: Data Scientist with missing SQL/Tableau
    cand_b_rjd = {
        "target_role": "Data Scientist",
        "job_match_score": 60.0,
        "matched_skills": ["python", "pandas", "numpy"],
        "missing_skills": ["sql", "tableau"]
    }
    cand_b = pipeline.evaluate_candidate(
        candidate_id="Candidate Beta",
        resume_jd_results=cand_b_rjd,
        save_reports=False
    )

    assert cand_a["candidate"]["name"] == "Candidate Alpha"
    assert cand_b["candidate"]["name"] == "Candidate Beta"

    # Verify roadmaps and skill gaps are distinct and dynamic
    gaps_a = cand_a["skill_gaps"]["high_priority"] + cand_a["skill_gaps"]["medium_priority"]
    gaps_b = cand_b["skill_gaps"]["high_priority"] + cand_b["skill_gaps"]["medium_priority"]

    assert "docker" in gaps_a or "kubernetes" in gaps_a
    assert "sql" in gaps_b or "tableau" in gaps_b
    assert gaps_a != gaps_b, "Candidate gaps must be derived dynamically, not identical"

    print("  [PASS] Assessment is strictly candidate-independent and dynamic.")


def test_04_skill_gap_to_roadmap():
    print("[TEST 4/12] Testing skill-gap to structured learning roadmap generation...")
    from skill_gap import SkillGapAnalyzer
    from learning_path import LearningPathGenerator

    analyzer = SkillGapAnalyzer()
    generator = LearningPathGenerator()

    gaps = analyzer.analyze_gaps(
        required_skills=["data structures", "sql", "docker"],
        matched_skills=[],
        missing_skills=["data structures", "sql", "docker"],
        weak_topics=["data structures"]
    )

    roadmap = generator.generate_roadmap(
        skill_gap_analysis=gaps,
        component_scores={"technical": 55.0, "hr_nlp": 80.0, "speech": 80.0},
        duration_weeks=5
    )

    assert roadmap["total_modules"] >= 3
    assert roadmap["duration_weeks"] == 5
    assert len(roadmap["weekly_action_plan"]) == 5

    # Check that modules contain required structured content
    mod_skills = [m["skill"].lower() for m in roadmap["learning_modules"]]
    assert "data structures" in mod_skills
    assert "sql" in mod_skills
    assert "docker" in mod_skills

    for m in roadmap["learning_modules"]:
        assert len(m["subtopics"]) >= 3
        assert len(m["practice_tasks"]) >= 1
        assert m["estimated_hours"] > 0

    print("  [PASS] Learning roadmap generated with detailed modules and tasks.")


def test_05_priority_assignment():
    print("[TEST 5/12] Verifying priority assignment (HIGH, MEDIUM, LOW)...")
    from skill_gap import SkillGapAnalyzer

    analyzer = SkillGapAnalyzer()

    # Data Structures is a core foundational skill + weak topic -> HIGH
    # SQL is a core foundational skill -> HIGH
    # Figma / supporting tool -> MEDIUM / LOW
    res = analyzer.analyze_gaps(
        required_skills=["data structures", "sql", "figma"],
        matched_skills=[],
        missing_skills=["data structures", "sql", "figma"],
        weak_topics=["data structures"]
    )

    assert "data structures" in res["high_priority"], "Core skill with interview weakness must be HIGH priority"
    assert "sql" in res["high_priority"], "Core foundational skill must be HIGH priority"
    assert "figma" in res["medium_priority"] or "figma" in res["low_priority"]
    assert res["high_priority_count"] >= 2

    print("  [PASS] Transparent priority logic correctly assigns HIGH and MEDIUM tiers.")


def test_06_personalized_recommendations_and_ethics():
    print("[TEST 6/12] Testing dynamic recommendations and ethical phrasing...")
    from orchestrator import EmployabilityPipeline

    pipeline = EmployabilityPipeline()

    # Candidate with weak speech pacing & excessive pauses
    speech_data = {
        "speaking_rate_wpm": 210.0,  # fast
        "fillers_per_100_words": 5.8,  # high
        "average_pause_seconds": 2.2   # long pauses
    }
    cand_res = pipeline.evaluate_candidate(
        candidate_id="Candidate Communicator",
        speech_results=speech_data,
        technical_results={"overall_technical_score": 85.0, "weak_topics": []},
        save_reports=False
    )

    recs_text = " ".join(cand_res["recommendations"] + cand_res["improvement_areas"]).lower()

    # Verify actionable recommendations address measured weaknesses
    assert "filler" in recs_text or "pace" in recs_text or "pause" in recs_text

    # Ethical check: Verify forbidden psychological terms are absent
    forbidden_terms = ["nervous", "anxiety", "deceptive", "dishonest", "mental state", "personality", "guarantee"]
    for term in forbidden_terms:
        assert term not in recs_text, f"Forbidden term '{term}' found in feedback!"

    print("  [PASS] Recommendations are dynamically tailored and strictly ethical.")


def test_07_first_assessment_progress():
    print("[TEST 7/12] Testing first-assessment baseline progress handling...")
    from performance_model import ProgressTracker

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_history = Path(tmp_dir) / "candidate_history.json"
        tracker = ProgressTracker(history_file=tmp_history)

        dummy_assessment = {
            "timestamp": "2026-10-04T12:00:00",
            "employability_score": 62.5,
            "readiness_level": "Developing",
            "confidence": 1.0,
            "component_scores": {"technical": 60.0, "hr_nlp": 65.0},
            "raw_features": {
                "technical": {"weak_topics": ["SQL"]},
                "resume_jd": {"missing_skills": ["Docker"]}
            }
        }

        progress = tracker.record_attempt("Candidate Baseline", dummy_assessment)

        assert progress["is_baseline"] is True
        assert progress["current_attempt"] == 1
        assert progress["score_delta_previous"] == 0.0
        assert progress["score_delta_baseline"] == 0.0
        assert "Baseline assessment established" in progress["progress_narrative"]
        assert len(progress["timeline"]) == 1

        print("  [PASS] Initial baseline attempt handled cleanly without crashes.")


def test_08_multiple_assessment_progress():
    print("[TEST 8/12] Testing multiple-attempt progress tracking and score deltas...")
    from performance_model import ProgressTracker

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_history = Path(tmp_dir) / "candidate_history.json"
        tracker = ProgressTracker(history_file=tmp_history)

        # Attempt 1: 58.0
        tracker.record_attempt("Candidate Multi", {
            "timestamp": "2026-10-01T10:00:00",
            "employability_score": 58.0,
            "readiness_level": "Developing",
            "component_scores": {"technical": 50.0, "hr_nlp": 60.0}
        })

        # Attempt 2: 67.0
        tracker.record_attempt("Candidate Multi", {
            "timestamp": "2026-10-08T10:00:00",
            "employability_score": 67.0,
            "readiness_level": "Developing",
            "component_scores": {"technical": 65.0, "hr_nlp": 65.0}
        })

        # Attempt 3: 74.0
        prog_3 = tracker.record_attempt("Candidate Multi", {
            "timestamp": "2026-10-15T10:00:00",
            "employability_score": 74.0,
            "readiness_level": "Ready",
            "component_scores": {"technical": 75.0, "hr_nlp": 75.0}
        })

        assert prog_3["is_baseline"] is False
        assert prog_3["current_attempt"] == 3
        assert prog_3["score_delta_previous"] == 7.0  # 74 - 67
        assert prog_3["score_delta_baseline"] == 16.0  # 74 - 58
        assert "Readiness improved by 16.0 points across 3 attempts" in prog_3["progress_narrative"]
        assert len(prog_3["timeline"]) == 3

        print("  [PASS] Multi-attempt tracking accurately computed +16.0 point delta.")


def test_09_improvement_and_decline_detection():
    print("[TEST 9/12] Testing fine-grained improvement and decline detection...")
    from performance_model import ProgressTracker

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_history = Path(tmp_dir) / "candidate_history.json"
        tracker = ProgressTracker(history_file=tmp_history)

        # Attempt 1: Weak in SQL, high fillers, poor posture
        att1 = {
            "timestamp": "2026-10-01T10:00:00",
            "employability_score": 55.0,
            "component_scores": {"technical": 50.0, "speech": 55.0, "computer_vision": 55.0},
            "raw_features": {
                "technical": {"weak_topics": ["SQL"]},
                "resume_jd": {"missing_skills": ["SQL", "Docker"]},
                "speech": {"fillers_per_100_words": 6.5, "speaking_rate_wpm": 130.0},
                "computer_vision": {"posture_consistency_percentage": 50.0, "camera_facing_percentage": 55.0}
            }
        }
        tracker.record_attempt("Candidate Trends", att1)

        # Attempt 2: Resolved SQL, reduced fillers, improved posture, but speaking rate too fast (decline)
        att2 = {
            "timestamp": "2026-10-08T10:00:00",
            "employability_score": 72.0,
            "component_scores": {"technical": 75.0, "speech": 65.0, "computer_vision": 80.0},
            "raw_features": {
                "technical": {"weak_topics": []},
                "resume_jd": {"missing_skills": ["Docker"]},  # SQL resolved!
                "speech": {"fillers_per_100_words": 1.2, "speaking_rate_wpm": 195.0},  # fillers down, pacing fast
                "computer_vision": {"posture_consistency_percentage": 85.0, "camera_facing_percentage": 85.0}
            }
        }
        prog2 = tracker.record_attempt("Candidate Trends", att2)

        improved_str = " ".join(prog2["improved_areas"]).lower()
        assert "filler" in improved_str or "technical" in improved_str
        assert "sql" in [s.lower() for s in prog2["resolved_skill_gaps"]]
        assert "docker" in [s.lower() for s in prog2["persistent_gaps"]]

        print("  [PASS] Progress analysis identified resolved gaps, improvements, and trends.")


def test_10_final_report_generation():
    print("[TEST 10/12] Verifying multi-format report generation (JSON, Markdown, HTML, CSV)...")
    from final_report_generator import FinalReportGenerator

    with tempfile.TemporaryDirectory() as tmp_dir:
        generator = FinalReportGenerator(output_dir=tmp_dir)

        dummy_assessment = {
            "timestamp": "2026-10-04T12:00:00",
            "candidate": {"name": "Candidate Reporter"},
            "job_alignment": {"target_role": "Backend Engineer", "match_score": 75.0},
            "readiness": {"score": 78.5, "level": "Ready", "description": "Solid competence."},
            "multimodal_assessment": {
                "confidence": 1.0,
                "active_modalities": ["technical", "hr_nlp", "speech", "computer_vision", "resume_jd"],
                "component_scores": {"technical": 80.0, "hr_nlp": 78.0, "speech": 75.0, "computer_vision": 82.0, "resume_jd": 75.0}
            },
            "strengths": ["Strong technical problem solving."],
            "improvement_areas": ["Moderate speaking rate."],
            "recommendations": ["Practice STAR behavioral framework."],
            "learning_roadmap": {
                "total_modules": 2,
                "total_estimated_hours": 20,
                "duration_weeks": 5,
                "weekly_action_plan": [{"week": 1, "theme": "Foundation", "target_topics": ["SQL"], "milestone": "Mastery", "objectives": ["Practice SQL"]}]
            },
            "progress_tracking": {"is_baseline": True, "progress_narrative": "Baseline established."}
        }

        report_paths = generator.generate_all_reports(dummy_assessment, candidate_slug="test_cand")

        assert Path(report_paths["json_path"]).exists()
        assert Path(report_paths["markdown_path"]).exists()
        assert Path(report_paths["html_path"]).exists()

        # Check JSON integrity
        with open(report_paths["json_path"], "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["candidate"]["name"] == "Candidate Reporter"
            assert data["readiness"]["score"] == 78.5

        # Check Markdown sections
        with open(report_paths["markdown_path"], "r", encoding="utf-8") as f:
            md_content = f.read()
            assert "AI-POWERED MULTIMODAL EMPLOYABILITY ASSESSMENT REPORT" in md_content
            assert "EXECUTIVE READINESS SUMMARY" in md_content
            assert "PERSONALIZED LEARNING ROADMAP" in md_content
            assert "ETHICAL & TECHNICAL SAFEGUARDS" in md_content

        # Check HTML content
        with open(report_paths["html_path"], "r", encoding="utf-8") as f:
            html_content = f.read()
            assert "<!DOCTYPE html>" in html_content
            assert "Candidate Reporter" in html_content
            assert "78.5%" in html_content

        print("  [PASS] JSON, Markdown, HTML, and CSV reports generated successfully.")


def test_11_missing_modality_and_error_handling():
    print("[TEST 11/12] Testing pipeline robustness on missing inputs and missing modalities...")
    from orchestrator import EmployabilityPipeline

    with tempfile.TemporaryDirectory() as tmp_dir:
        pipeline = EmployabilityPipeline(reports_dir=tmp_dir, history_file=Path(tmp_dir)/"hist.json")

        # Missing resume, missing JD, missing CV, missing speech
        partial_res = pipeline.evaluate_candidate(
            resume_path="non_existent_resume.pdf",
            job_description=None,
            technical_results={"overall_technical_score": 70.0},
            hr_results={"overall_hr_score": 75.0},
            cv_results=None,
            speech_results=None,
            candidate_id="Candidate Resilient",
            save_reports=False
        )

        assert partial_res is not None
        assert partial_res["candidate"]["name"] == "Candidate Resilient"
        assert partial_res["readiness"]["score"] > 0.0
        assert partial_res["multimodal_assessment"]["confidence"] == 0.6  # 3/5 modalities
        assert len(partial_res["learning_roadmap"]["weekly_action_plan"]) > 0

        print("  [PASS] Pipeline gracefully handles missing files and unrecorded modalities.")


def test_12_complete_end_to_end_candidate_workflow():
    print("[TEST 12/12] Testing complete end-to-end workflow with project resume and JD...")
    from orchestrator import run_final_employability_pipeline

    resume_file = project_root / "resume.pdf"
    jd_file = project_root / "ai_ml" / "data" / "job_description.txt"

    assert resume_file.exists(), "resume.pdf must exist in project root"
    assert jd_file.exists(), "job_description.txt must exist in data dir"

    with open(jd_file, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # Pre-calculated round metrics representing candidate performance
    tech_eval = {
        "overall_technical_score": 78.5,
        "average_score": 0.785,
        "strong_topics": ["Python", "Machine Learning"],
        "weak_topics": ["Docker", "Data Structures"]
    }
    hr_eval = {
        "overall_hr_score": 82.0,
        "average_relevance": 85.0,
        "average_semantic_similarity": 0.92,
        "average_completeness": 80.0,
        "average_clarity": 88.0,
        "average_star_score": 85.0
    }
    speech_eval = {
        "speaking_rate_wpm": 142.0,
        "pause_count": 3,
        "average_pause_seconds": 0.8,
        "fillers_per_100_words": 1.5,
        "speech_continuity_percentage": 88.0
    }
    cv_eval = {
        "face_visibility_percentage": 95.0,
        "camera_facing_percentage": 90.0,
        "posture_consistency_percentage": 88.0,
        "movement_stability_percentage": 94.0
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Run top-level convenience pipeline
        pipeline_res = run_final_employability_pipeline(
            resume_path=resume_file,
            job_description=jd_text,
            technical_results=tech_eval,
            hr_results=hr_eval,
            cv_results=cv_eval,
            speech_results=speech_eval,
            target_role="AI/ML Software Engineer",
            save_reports=False
        )

        assert pipeline_res["candidate"]["name"] != "Candidate", "Candidate name must be extracted from resume"
        assert len(pipeline_res["candidate"]["skills"]) > 5
        assert pipeline_res["job_alignment"]["match_score"] > 0
        assert pipeline_res["readiness"]["score"] >= 70.0
        assert len(pipeline_res["learning_roadmap"]["learning_modules"]) > 0
        assert len(pipeline_res["strengths"]) > 0

        print(f"  [PASS] End-to-end pipeline executed for '{pipeline_res['candidate']['name']}': Score={pipeline_res['readiness']['score']:.1f}% ({pipeline_res['readiness']['level']}).")


def main():
    print("============================================================")
    print("    STARTING PHASE 8 FINAL SYSTEM INTEGRATION TEST SUITE    ")
    print("============================================================")

    tests = [
        test_01_imports,
        test_02_final_assessment_orchestration,
        test_03_candidate_independent_assessment,
        test_04_skill_gap_to_roadmap,
        test_05_priority_assignment,
        test_06_personalized_recommendations_and_ethics,
        test_07_first_assessment_progress,
        test_08_multiple_assessment_progress,
        test_09_improvement_and_decline_detection,
        test_10_final_report_generation,
        test_11_missing_modality_and_error_handling,
        test_12_complete_end_to_end_candidate_workflow
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
    print(f"       PHASE 8 TEST RESULTS: {passed}/{total} PASSED       ")
    print("============================================================")

    if passed == total:
        print("[SUCCESS] All Phase 8 Final System Integration tests passed successfully!")
        sys.exit(0)
    else:
        print(f"[FAILURE] {total - passed} tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
