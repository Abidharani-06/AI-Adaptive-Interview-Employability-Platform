"""
Comprehensive End-to-End Test Suite for Phase 4 (HR / Behavioral Interview Round)
Verifies:
1. Syntax & Import checks
2. HR question bank loading & schema
3. Resume-aware question generation (resume.pdf)
4. Balanced HR interview plan selection
5. Answer evaluation across strong, weak, and off-topic responses
6. Composite HR scoring (Relevance, Semantic Similarity, Completeness, Clarity, Concepts)
7. STAR analysis & missing component detection (no forced STAR on non-behavioral)
8. Personalized actionable feedback
9. Adaptive follow-up question generation (weak vs strong)
10. Dynamic support for different candidate/resume (Rakshana Resume.pdf)
11. Backwards compatibility with Phase 1-3 pipeline
"""

import sys
import unittest
from pathlib import Path

# Resolve project paths
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "ai_ml" / "preprocessing"))
sys.path.insert(0, str(project_root / "ai_ml" / "nlp"))
sys.path.insert(0, str(project_root / "ai_ml" / "models"))
sys.path.insert(0, str(project_root / "ai_ml" / "question_engine"))
sys.path.insert(0, str(project_root / "ai_ml" / "recomendation"))

from candidate_profile import build_candidate_profile
from hr_question_engine import (
    load_hr_questions_dataset,
    generate_personalized_hr_bank,
    select_hr_interview_plan,
    generate_adaptive_follow_up
)
from hr_evaluation_model import (
    evaluate_hr_answer,
    analyze_star_structure,
    generate_hr_feedback
)
from hr_adaptive_engine import run_hr_interview
from answer_relevance import calculate_relevance, calculate_semantic_similarity
from answer_completeness import evaluate_completeness, evaluate_clarity, evaluate_conciseness
from keyword_extraction import check_concept_coverage
from resume_parser import analyze_resume
from adaptive_engine import run_adaptive_interview, run_full_interview
from answer_evaluation_model import evaluate_answer


class TestPhase4HRInterview(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 65)
        print("   STARTING PHASE 4: HR & BEHAVIORAL INTERVIEW TEST SUITE")
        print("=" * 65)

    def test_01_syntax_and_imports(self):
        """Test 1: Verify all Phase 4 and NLP modules import cleanly."""
        print("\n[Test 1] Verifying syntax and module imports...")
        self.assertTrue(callable(build_candidate_profile))
        self.assertTrue(callable(generate_personalized_hr_bank))
        self.assertTrue(callable(select_hr_interview_plan))
        self.assertTrue(callable(generate_adaptive_follow_up))
        self.assertTrue(callable(evaluate_hr_answer))
        self.assertTrue(callable(analyze_star_structure))
        self.assertTrue(callable(run_hr_interview))
        self.assertTrue(callable(calculate_relevance))
        self.assertTrue(callable(calculate_semantic_similarity))
        print("[PASS] All Phase 4 modules and NLP dependencies imported successfully.")

    def test_02_hr_question_bank(self):
        """Test 2: Verify HR question dataset loads with proper schema."""
        print("\n[Test 2] Verifying HR question bank dataset...")
        df = load_hr_questions_dataset()
        self.assertGreaterEqual(len(df), 10)
        required_cols = {"question_id", "category", "question_text", "requires_star", "expected_themes"}
        self.assertTrue(required_cols.issubset(set(df.columns)))
        print(f"[PASS] HR questions dataset verified with {len(df)} curated questions.")

    def test_03_resume_aware_question_generation(self):
        """Test 3: Verify dynamic resume-aware personalization with resume.pdf."""
        print("\n[Test 3] Verifying resume-aware questions for resume.pdf (Candidate 1)...")
        resume_path = project_root / "resume.pdf"
        self.assertTrue(resume_path.exists(), "resume.pdf must exist")

        res = generate_personalized_hr_bank(str(resume_path), "ai_ml/data/job_description.txt")
        self.assertIn("Abidharani", res["candidate_name"])
        self.assertIn("COMPUTER SCIENCE", res["education"].upper())
        self.assertGreater(len(res["bank"]), 15)

        # Verify intro question is personalized with candidate's actual name & degree
        intro_q = next(q for q in res["bank"] if q["question_id"] == "DYN_HR_INTRO")
        self.assertIn("Abidharani", intro_q["question_text"])
        self.assertIn(res["education"], intro_q["question_text"])
        self.assertFalse(intro_q["requires_star"])

        # Verify project questions reference actual parsed projects (not noise)
        proj_q = next((q for q in res["bank"] if "DYN_HR_PROJ_ROLE" in q["question_id"]), None)
        self.assertIsNotNone(proj_q)
        self.assertTrue(proj_q["requires_star"])
        self.assertNotIn("Cloud Computing | Web D", proj_q["question_text"])
        print(f"[PASS] Candidate: {res['candidate_name']} | Projects detected: {res['projects_count']}")
        print(f"[PASS] Sample Project Question: {proj_q['question_text']}")

    def test_04_balanced_interview_plan_selection(self):
        """Test 4: Verify balanced interview plan covers all core competency categories."""
        print("\n[Test 4] Verifying balanced HR interview plan selection...")
        res = generate_personalized_hr_bank("resume.pdf", "ai_ml/data/job_description.txt")
        plan = select_hr_interview_plan(res, num_questions=5)

        self.assertEqual(len(plan), 5)
        categories = [q["category"] for q in plan]
        self.assertIn("Introduction & Background", categories)
        self.assertIn("Project Experience & Impact", categories)
        self.assertIn("Motivation & Role Alignment", categories)

        star_count = sum(1 for q in plan if q["requires_star"])
        std_count = sum(1 for q in plan if not q["requires_star"])
        self.assertGreaterEqual(star_count, 2, "Must contain behavioral STAR questions")
        self.assertGreaterEqual(std_count, 1, "Must contain standard HR questions")
        print(f"[PASS] Interview plan selected: {len(plan)} questions ({star_count} STAR, {std_count} Standard).")

    def test_05_and_06_answer_evaluation_and_scoring(self):
        """Test 5 & 6: Verify HR answer evaluation and composite scoring dimensions."""
        print("\n[Test 5 & 6] Verifying HR answer evaluation across answer qualities...")
        q_obj = {
            "question_text": "Tell me about a difficult challenge you faced in a project and how you solved it.",
            "expected_themes": "situation; challenge; action; solution; outcome; learning",
            "requires_star": True
        }

        # Strong comprehensive STAR answer
        ans_strong = (
            "During my final year project on an Automatic Medicine Vending Machine, our team faced a severe "
            "hardware-software communication latency issue that halted dispensing. My task was to optimize "
            "the serial communication protocol. I analyzed the baud rates, refactored the Python driver to "
            "use asynchronous threading, and implemented a buffer queue. As a result, we reduced the sensor "
            "response time by 65% and successfully completed the live demonstration on schedule."
        )

        # Weak vague answer
        ans_weak = "We had a bug in our project and it was tough. We stayed late and fixed it."

        # Completely off-topic answer
        ans_offtopic = "I enjoy playing cricket on weekends and eating biryani with my friends in the hostel."

        eval_strong = evaluate_hr_answer(q_obj, ans_strong)
        eval_weak = evaluate_hr_answer(q_obj, ans_weak)
        eval_offtopic = evaluate_hr_answer(q_obj, ans_offtopic)

        # Assert composite scoring dimensions are present
        for res_dict in [eval_strong, eval_weak, eval_offtopic]:
            self.assertIn("overall_score", res_dict)
            self.assertIn("relevance_score", res_dict)
            self.assertIn("semantic_similarity", res_dict)
            self.assertIn("completeness_score", res_dict)
            self.assertIn("clarity_score", res_dict)
            self.assertIn("conciseness_score", res_dict)
            self.assertIn("concept_coverage", res_dict)
            self.assertIn("feedback", res_dict)

        # Score hierarchy verification
        self.assertGreaterEqual(eval_strong["overall_percentage"], 75.0, "Strong answer should score >= 75%")
        self.assertLess(eval_weak["overall_percentage"], eval_strong["overall_percentage"])
        self.assertLess(eval_offtopic["overall_percentage"], 45.0, "Off-topic answer should score < 45%")
        self.assertLess(eval_offtopic["relevance_score"], 0.40, "Off-topic relevance should be < 40%")

        print(f"[PASS] Strong Answer Score   : {eval_strong['overall_percentage']}% (Relevance: {eval_strong['relevance_score']*100:.1f}%, Semantic Sim: {eval_strong['semantic_similarity']*100:.1f}%)")
        print(f"[PASS] Weak Answer Score     : {eval_weak['overall_percentage']}% (Relevance: {eval_weak['relevance_score']*100:.1f}%)")
        print(f"[PASS] Off-Topic Answer Score: {eval_offtopic['overall_percentage']}% (Relevance: {eval_offtopic['relevance_score']*100:.1f}%)")

    def test_07_star_analysis_and_missing_components(self):
        """Test 7: Verify STAR analysis, missing component detection, and no forced STAR on non-behavioral."""
        print("\n[Test 7] Verifying STAR behavioral analysis & component detection...")

        # 1. Complete STAR
        ans_all_star = "During my project, my task was to fix latency. I refactored the Python driver. As a result, response time improved by 50%."
        star_all = analyze_star_structure(ans_all_star)
        self.assertTrue(star_all["is_applicable"])
        self.assertEqual(len(star_all["missing_components"]), 0)
        self.assertEqual(star_all["star_score"], 1.0)

        # 2. Missing Result
        ans_no_result = "During my project, my task was to optimize the database. I analyzed queries and created indexes."
        star_no_res = analyze_star_structure(ans_no_result)
        self.assertIn("Result", star_no_res["missing_components"])
        self.assertIn("measurable Result", star_no_res["feedback"])

        # 3. Missing Action
        ans_no_action = "During my internship, the objective was to improve test coverage. Finally test coverage reached 80%."
        star_no_act = analyze_star_structure(ans_no_action)
        self.assertIn("Action", star_no_act["missing_components"])

        # 4. Standard non-STAR question verification (e.g. "Tell me about yourself")
        q_intro = {
            "question_text": "Tell me about yourself and your journey in technology.",
            "requires_star": False
        }
        eval_intro = evaluate_hr_answer(q_intro, "I am a passionate software engineer who enjoys backend systems.")
        self.assertIsNone(eval_intro["star_result"], "STAR analysis must NOT be forced on standard questions")
        print("[PASS] STAR components properly detected; missing components correctly identified.")
        print("[PASS] Non-STAR questions correctly bypass STAR analysis.")

    def test_08_personalized_feedback(self):
        """Test 8: Verify personalized feedback reflects actual candidate answers."""
        print("\n[Test 8] Verifying personalized feedback generation...")
        q_obj = {
            "question_text": "Describe a difficult problem you faced and how you solved it.",
            "expected_themes": "challenge; action; solution; result",
            "requires_star": True
        }

        # Answer missing action
        ans_missing_action = "In my project there was a huge bottleneck. In the end, we achieved 99% accuracy."
        res = evaluate_hr_answer(q_obj, ans_missing_action)
        self.assertIn("Actions YOU personally took", res["feedback"])

        # Answer with filler words
        ans_fillers = "Um, basically, like, you know, I fixed the database and literally optimized queries."
        res_fillers = evaluate_hr_answer(q_obj, ans_fillers)
        self.assertIn("filler phrases", res_fillers["feedback"].lower())
        print(f"[PASS] Feedback adapts specifically to candidate text: '{res_fillers['feedback'][:80]}...'")

    def test_09_adaptive_follow_up_questions(self):
        """Test 9: Verify intelligent adaptive follow-ups for weak vs strong responses."""
        print("\n[Test 9] Verifying adaptive follow-up question logic...")
        q_item = {
            "question_id": "HR_PROJ_CHALLENGE",
            "question_text": "What was the most difficult roadblock in your project?",
            "requires_star": True,
            "follow_up_weak": "What exact diagnostic steps did you take to isolate the root cause?",
            "follow_up_strong": "How did overcoming that challenge change how you structure your code today?"
        }

        # Case A: Missing Action -> Probes Action
        eval_no_action = {
            "overall_score": 0.58,
            "star_result": {"missing_components": ["Action"]}
        }
        fu_action = generate_adaptive_follow_up(q_item, eval_no_action)
        self.assertEqual(fu_action["type"], "probe_action")
        self.assertIn("actions did YOU personally take", fu_action["question_text"])

        # Case B: Missing Result -> Probes Result
        eval_no_res = {
            "overall_score": 0.55,
            "star_result": {"missing_components": ["Result"]}
        }
        fu_res = generate_adaptive_follow_up(q_item, eval_no_res)
        self.assertEqual(fu_res["type"], "probe_result")
        self.assertIn("measurable outcome", fu_res["question_text"])

        # Case C: High score -> Probes strategic reflection / architectural growth
        eval_strong = {
            "overall_score": 0.88,
            "star_result": {"missing_components": []}
        }
        fu_strong = generate_adaptive_follow_up(q_item, eval_strong)
        self.assertEqual(fu_strong["type"], "probe_reflection")
        self.assertEqual(fu_strong["question_text"], q_item["follow_up_strong"])
        print("[PASS] Adaptive follow-ups dynamically target missing STAR components and deep reflection.")

    def test_10_dynamic_support_for_different_candidates(self):
        """Test 10: Verify the engine dynamically adapts to different resumes (Candidate 2: Rakshana B)."""
        print("\n[Test 10] Verifying dynamic adaptation for different candidate (Rakshana Resume.pdf)...")
        resume_cand2 = project_root / "Rakshana Resume.pdf"
        self.assertTrue(resume_cand2.exists(), "Rakshana Resume.pdf must exist")

        res2 = generate_personalized_hr_bank(str(resume_cand2), "ai_ml/data/job_description.txt")
        self.assertEqual(res2["candidate_name"], "Rakshana B")
        self.assertIn("Artificial Intelligence", res2["education"])

        plan2 = select_hr_interview_plan(res2, num_questions=5)
        # Check intro mentions Rakshana
        intro_q = plan2[0]
        self.assertIn("Rakshana", intro_q["question_text"])
        self.assertIn("Artificial Intelligence", intro_q["question_text"])

        # Check project question mentions Rakshana's project (Smart Curriculum Activity & Attendance App)
        proj_q = plan2[1]
        self.assertIn("Smart Curriculum Activity", proj_q["question_text"])
        self.assertNotIn("Abidharani", str(plan2))
        print(f"[PASS] Successfully adapted to Candidate 2: {res2['candidate_name']}")
        print(f"[PASS] Project question customized to: '{proj_q['question_text']}'")

    def test_11_pipeline_integration_and_phase_1_to_3_compatibility(self):
        """Test 11: Verify backwards compatibility with Phase 1-3 and full pipeline execution."""
        print("\n[Test 11] Verifying Phase 1-3 compatibility and consolidated interview execution...")

        # 1. Phase 1 Resume Parser verification
        text, skills, sections, projects = analyze_resume("resume.pdf")
        self.assertGreater(len(skills), 0)
        self.assertTrue(sections["projects"])

        # 2. Phase 2 & 3 Technical Evaluation verification
        ml_sc, sem_sc, final_sc = evaluate_answer(
            "Inheritance allows child classes to reuse attributes and methods.",
            "Child classes inherit methods and attributes from parent classes."
        )
        self.assertGreaterEqual(final_sc, 0.60)

        # 3. Phase 4 End-to-end HR Interview (Programmatic automated execution)
        def hr_test_provider(q_num, q_text, cat):
            q_lower = q_text.lower()
            if "project" in q_lower or "challenge" in q_lower or "action" in q_lower or "roadblock" in q_lower:
                return (
                    "During my project on Sign Language to Voice Converter, our team faced high latency in frame processing. "
                    "My task was to optimize the computer vision pipeline. I implemented asynchronous threading and refactored "
                    "the Python driver to use buffer queues. As a result, we increased throughput by 65% and successfully "
                    "delivered the live demonstration on schedule."
                )
            elif "yourself" in q_lower or "pursue" in q_lower:
                return (
                    "I am a computer science engineering student passionate about artificial intelligence, backend systems, "
                    "and building scalable software applications. Throughout my academic journey, I have taken initiative to "
                    "design, develop, and deliver impactful projects."
                )
            else:
                return (
                    "I manage tight deadlines by breaking complex deliverables into daily agile tasks, maintaining proactive "
                    "communication with stakeholders, and focusing on high-impact code modules to ensure quality delivery."
                )

        hr_summary = run_hr_interview(
            resume_path="resume.pdf",
            jd_path="ai_ml/data/job_description.txt",
            num_questions=3,
            interactive=False,
            answers_provider=hr_test_provider,
            enable_adaptive_followups=True
        )

        self.assertEqual(hr_summary["candidate_name"], "Abidharani A")
        self.assertGreaterEqual(hr_summary["overall_hr_score"], 60.0)
        self.assertIn("average_semantic_similarity", hr_summary)
        self.assertIn("strong_areas", hr_summary)
        self.assertIn("category_performance", hr_summary)

        # 4. Multi-round consolidated pipeline (Technical + HR)
        def tech_test_provider(q_idx, q_txt, topic):
            return "Object oriented programming encapsulates state and logic inside classes and objects."

        full_summary = run_full_interview(
            resume_path="resume.pdf",
            jd_path="ai_ml/data/job_description.txt",
            tech_questions=2,
            hr_questions=2,
            interactive=False,
            tech_answers_provider=tech_test_provider,
            hr_answers_provider=hr_test_provider
        )

        self.assertIn("technical_summary", full_summary)
        self.assertIn("hr_summary", full_summary)
        self.assertIn("combined_score", full_summary)
        print(f"[PASS] Consolidated Score: {full_summary['combined_score']}% (Tech: {full_summary['technical_summary']['overall_technical_score']}%, HR: {full_summary['hr_summary']['overall_hr_score']}%)")
        print("[PASS] All 11 Phase 4 requirements and Phase 1-3 compatibility checks PASSED.")


if __name__ == "__main__":
    unittest.main()
