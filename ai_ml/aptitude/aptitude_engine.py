"""
Aptitude Engine Orchestrator
============================
Orchestrates Round 1 of the assessment platform:
- Prepares randomized sections (Quantitative -> Logical -> Verbal)
- Manages evaluation and difficulty analytics
- Feeds diagnostic weak areas into the downstream Employability Pipeline
"""

from typing import Dict, List, Any, Optional
from .question_selector import select_aptitude_questions
from .scoring import evaluate_aptitude_submission


class AptitudeEngine:
    def __init__(self, questions_per_section: int = 5):
        self.questions_per_section = questions_per_section

    def create_assessment_session(self) -> Dict[str, Any]:
        """
        Creates a new candidate session with balanced, randomized questions.
        Returns:
            {
                "client_questions": list of client-safe questions with shuffled options,
                "evaluation_keys": dictionary with secret keys for scoring
            }
        """
        client_questions, evaluation_keys = select_aptitude_questions(
            questions_per_section=self.questions_per_section
        )
        return {
            "client_questions": client_questions,
            "evaluation_keys": evaluation_keys,
            "total_questions": len(client_questions)
        }

    def evaluate_session(
        self,
        user_answers: List[Dict[str, Any]],
        evaluation_keys: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates submitted candidate answers and returns structured report.
        """
        return evaluate_aptitude_submission(user_answers, evaluation_keys)


def run_aptitude_assessment(
    user_answers: List[Dict[str, Any]],
    evaluation_keys: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Functional convenience wrapper."""
    engine = AptitudeEngine()
    return engine.evaluate_session(user_answers, evaluation_keys)
