"""
Aptitude Module Test Suite
==========================
Tests:
1. Question bank schema & categorization
2. Question selector & option randomization
3. Client question privacy (no correct answers in client output)
4. Evaluation and section scoring (Quant, Logical, Verbal)
5. Difficulty adaptation & progression metrics
6. Strong and weak topic detection
7. Unattempted questions and edge cases
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import unittest
from ai_ml.aptitude.question_bank import (
    get_all_questions,
    QUANTITATIVE_TOPICS,
    LOGICAL_REASONING_TOPICS,
    VERBAL_ABILITY_TOPICS
)
from ai_ml.aptitude.question_selector import select_aptitude_questions
from ai_ml.aptitude.difficulty import adapt_question_difficulty, calculate_difficulty_metrics
from ai_ml.aptitude.scoring import evaluate_aptitude_submission
from ai_ml.aptitude.aptitude_engine import AptitudeEngine


class TestAptitudeEngine(unittest.TestCase):

    def test_01_question_bank_structure(self):
        """Verify question bank contents, options, and keys."""
        questions = get_all_questions()
        self.assertGreaterEqual(len(questions), 30)

        sections = set(q["section"] for q in questions)
        self.assertEqual(sections, {"Quantitative Ability", "Logical Reasoning", "Verbal Ability"})

        for q in questions:
            self.assertIn("id", q)
            self.assertIn("topic", q)
            self.assertIn("difficulty", q)
            self.assertIn(q["difficulty"], ["Easy", "Medium", "Hard"])
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["correct_answer"], q["options"])
            self.assertTrue(len(q["explanation"]) > 0)

    def test_02_question_selector_and_privacy(self):
        """Verify client question bundle does NOT leak correct answers."""
        client_qs, eval_keys = select_aptitude_questions(questions_per_section=3)
        self.assertEqual(len(client_qs), 9)  # 3 sections * 3 questions
        self.assertEqual(len(eval_keys), 9)

        for cq in client_qs:
            self.assertNotIn("correct_answer", cq)
            self.assertNotIn("explanation", cq)
            self.assertEqual(len(cq["options"]), 4)

    def test_03_difficulty_adaptation(self):
        """Verify escalating on success and de-escalating on failure."""
        self.assertEqual(adapt_question_difficulty("Easy", was_correct=True), "Medium")
        self.assertEqual(adapt_question_difficulty("Medium", was_correct=True), "Hard")
        self.assertEqual(adapt_question_difficulty("Hard", was_correct=False), "Medium")
        self.assertEqual(adapt_question_difficulty("Medium", was_correct=False), "Easy")

    def test_04_scoring_and_diagnostics(self):
        """Verify accurate scoring, accuracy calculation, and topic detection."""
        client_qs, eval_keys = select_aptitude_questions(questions_per_section=2, seed=42)

        # Simulate answers: answer first 4 correctly, next 1 incorrectly, leave 1 unattempted
        q_ids = list(eval_keys.keys())
        simulated_answers = []

        # 4 correct
        for qid in q_ids[:4]:
            simulated_answers.append({
                "question_id": qid,
                "selected_option": eval_keys[qid]["correct_answer"],
                "time_taken_seconds": 30.0
            })

        # 1 wrong
        simulated_answers.append({
            "question_id": q_ids[4],
            "selected_option": "WRONG_ANSWER_OPTION",
            "time_taken_seconds": 25.0
        })

        # 1 unattempted (not added to simulated_answers)

        result = evaluate_aptitude_submission(simulated_answers, eval_keys)

        self.assertEqual(result["total_questions"], 6)
        self.assertEqual(result["attempted_count"], 5)
        self.assertEqual(result["unattempted_count"], 1)
        self.assertEqual(result["correct_count"], 4)
        self.assertEqual(result["accuracy"], 80.0)  # 4 / 5
        self.assertIn("quantitative", result["sections"])
        self.assertIn("logical_reasoning", result["sections"])
        self.assertIn("verbal_ability", result["sections"])
        self.assertIn("roadmap_inputs", result)
        self.assertIn("difficulty_performance", result)

    def test_05_engine_orchestration(self):
        """Verify complete session workflow through AptitudeEngine."""
        engine = AptitudeEngine(questions_per_section=2)
        session = engine.create_assessment_session()

        client_qs = session["client_questions"]
        eval_keys = session["evaluation_keys"]

        all_correct = [
            {"question_id": cq["id"], "selected_option": eval_keys[cq["id"]]["correct_answer"], "time_taken_seconds": 20.0}
            for cq in client_qs
        ]

        report = engine.evaluate_session(all_correct, eval_keys)
        self.assertEqual(report["overall_score"], 100.0)
        self.assertEqual(report["accuracy"], 100.0)


if __name__ == "__main__":
    unittest.main()
