"""
Aptitude Difficulty Adaptation Engine
====================================
Dynamically adjusts question difficulty based on sequential answer accuracy
and computes difficulty progression analytics.
"""

from typing import List, Dict, Any


DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]


def adapt_question_difficulty(
    current_difficulty: str,
    was_correct: bool,
    consecutive_correct: int = 1,
    consecutive_incorrect: int = 1
) -> str:
    """
    Returns the next recommended difficulty level:
    - If correct and consecutive streak >= 1: escalate (Easy -> Medium -> Hard)
    - If incorrect: de-escalate (Hard -> Medium -> Easy)
    """
    if was_correct:
        if current_difficulty == "Easy":
            return "Medium"
        elif current_difficulty == "Medium" and consecutive_correct >= 1:
            return "Hard"
        return "Hard"
    else:
        if current_difficulty == "Hard":
            return "Medium"
        elif current_difficulty == "Medium" and consecutive_incorrect >= 1:
            return "Easy"
        return "Easy"


def calculate_difficulty_metrics(answer_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes candidate accuracy and volume across Easy, Medium, and Hard tiers.
    """
    breakdown = {
        "Easy": {"total": 0, "correct": 0, "accuracy": 0.0},
        "Medium": {"total": 0, "correct": 0, "accuracy": 0.0},
        "Hard": {"total": 0, "correct": 0, "accuracy": 0.0}
    }

    for log in answer_logs:
        diff = log.get("difficulty", "Medium")
        if diff not in breakdown:
            diff = "Medium"
        breakdown[diff]["total"] += 1
        if log.get("is_correct", False):
            breakdown[diff]["correct"] += 1

    for diff, stats in breakdown.items():
        if stats["total"] > 0:
            stats["accuracy"] = round((stats["correct"] / stats["total"]) * 100.0, 1)

    # Compute a weighted difficulty capability index (0-100)
    # Weights: Easy = 0.25, Medium = 0.35, Hard = 0.40
    cap_index = (
        breakdown["Easy"]["accuracy"] * 0.25 +
        breakdown["Medium"]["accuracy"] * 0.35 +
        breakdown["Hard"]["accuracy"] * 0.40
    )

    return {
        "breakdown": breakdown,
        "capability_index": round(cap_index, 1)
    }
