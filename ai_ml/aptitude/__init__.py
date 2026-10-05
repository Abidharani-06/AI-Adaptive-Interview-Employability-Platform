"""
AI Aptitude Assessment Engine
==============================
Provides structured, adaptive assessment across:
1. Quantitative Ability
2. Logical Reasoning
3. Verbal Ability
"""

from .aptitude_engine import AptitudeEngine, run_aptitude_assessment
from .question_bank import (
    QUANTITATIVE_TOPICS,
    LOGICAL_REASONING_TOPICS,
    VERBAL_ABILITY_TOPICS,
    get_all_questions
)
from .question_selector import select_aptitude_questions
from .scoring import evaluate_aptitude_submission
from .difficulty import adapt_question_difficulty

__all__ = [
    "AptitudeEngine",
    "run_aptitude_assessment",
    "QUANTITATIVE_TOPICS",
    "LOGICAL_REASONING_TOPICS",
    "VERBAL_ABILITY_TOPICS",
    "get_all_questions",
    "select_aptitude_questions",
    "evaluate_aptitude_submission",
    "adapt_question_difficulty"
]
