"""
Aptitude Question Selector
==========================
Randomizes and balances question selection across sections:
1. Quantitative Ability
2. Logical Reasoning
3. Verbal Ability
Shuffles options and prepares client-facing vs evaluation bundles.
"""

import random
from typing import List, Dict, Any, Tuple
from .question_bank import get_all_questions, QUANTITATIVE_TOPICS, LOGICAL_REASONING_TOPICS, VERBAL_ABILITY_TOPICS


def select_aptitude_questions(
    questions_per_section: int = 5,
    difficulty_mix: str = "adaptive",
    seed: Any = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Selects a balanced set of aptitude questions across Quantitative, Logical, and Verbal.
    
    Returns:
    - client_questions: List of questions with shuffled options without answers.
    - evaluation_keys: Dictionary mapping question ID to correct answer and explanation.
    """
    if seed is not None:
        random.seed(seed)

    all_qs = get_all_questions()

    quant_qs = [q for q in all_qs if q["section"] == "Quantitative Ability"]
    logic_qs = [q for q in all_qs if q["section"] == "Logical Reasoning"]
    verbal_qs = [q for q in all_qs if q["section"] == "Verbal Ability"]

    def sample_from_pool(pool: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        if not pool:
            return []
        if count >= len(pool):
            shuffled = pool.copy()
            random.shuffle(shuffled)
            return shuffled
        return random.sample(pool, count)

    selected_quant = sample_from_pool(quant_qs, questions_per_section)
    selected_logic = sample_from_pool(logic_qs, questions_per_section)
    selected_verbal = sample_from_pool(verbal_qs, questions_per_section)

    all_selected = selected_quant + selected_logic + selected_verbal

    client_questions = []
    evaluation_keys = {}

    order_index = 1
    for q in all_selected:
        # Clone options and shuffle them
        shuffled_options = q["options"].copy()
        random.shuffle(shuffled_options)

        evaluation_keys[q["id"]] = {
            "id": q["id"],
            "section": q["section"],
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "correct_answer": q["correct_answer"],
            "explanation": q.get("explanation", ""),
            "order_index": order_index
        }

        # Client version strips the secret answer and explanation
        client_q = {
            "id": q["id"],
            "order_index": order_index,
            "section": q["section"],
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "options": shuffled_options
        }
        client_questions.append(client_q)
        order_index += 1

    return client_questions, evaluation_keys
