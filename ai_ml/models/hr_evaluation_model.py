import re
import sys
from pathlib import Path

# Resolve project paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]
nlp_dir = str(project_root / "ai_ml" / "nlp")
if nlp_dir not in sys.path:
    sys.path.append(nlp_dir)

from answer_relevance import calculate_relevance, calculate_semantic_similarity
from answer_completeness import (
    evaluate_completeness,
    evaluate_clarity,
    evaluate_conciseness,
    count_words
)
from keyword_extraction import check_concept_coverage, extract_keywords


# ============================================================
# 1. BEHAVIORAL / STAR LINGUISTIC DETECTOR
# ============================================================

STAR_PATTERNS = {
    "situation": [
        r"\b(?:when\s+i\s+was|during\s+my|in\s+my\s+previous|while\s+working\s+on|in\s+our\s+project)\b",
        r"\b(?:the\s+situation\s+was|at\s+the\s+time|we\s+faced|our\s+team\s+had|we\s+were\s+building)\b",
        r"\b(?:hackathon|internship|college|client|system|company|deadline|problem\s+started)\b",
        r"\b(?:context|background|project\s+called|scenario)\b"
    ],
    "task": [
        r"\b(?:my\s+task\s+was|my\s+responsibility\s+was|i\s+was\s+responsible\s+for)\b",
        r"\b(?:i\s+needed\s+to|i\s+had\s+to|my\s+goal\s+was|the\s+objective\s+was)\b",
        r"\b(?:assigned\s+to|tasked\s+with|required\s+to|aimed\s+to|expected\s+to)\b",
        r"\b(?:challenge\s+was\s+to|deliverable|scope)\b"
    ],
    "action": [
        r"\b(?:i\s+implemented|i\s+developed|i\s+designed|i\s+created|i\s+built|i\s+coded)\b",
        r"\b(?:i\s+decided|i\s+analyzed|i\s+researched|i\s+investigated|i\s+identified)\b",
        r"\b(?:i\s+communicated|i\s+organized|i\s+coordinated|i\s+suggested|i\s+proposed)\b",
        r"\b(?:i\s+refactored|i\s+debugged|i\s+optimized|i\s+solved|i\s+stepped\s+in)\b",
        r"\b(?:to\s+solve\s+this\s+i|my\s+approach\s+was|i\s+took\s+the\s+initiative)\b"
    ],
    "result": [
        r"\b(?:as\s+a\s+result|in\s+the\s+end|finally|ultimately|consequently)\b",
        r"\b(?:achieved|improved|reduced|increased|optimized\s+by|saved|decreased)\b",
        r"\b(?:\d+%\s*|\d+\s*(?:percent|hours|days|times|users|faster|increase))\b",
        r"\b(?:successfully\s+(?:delivered|deployed|launched|completed|resolved))\b",
        r"\b(?:what\s+i\s+learned|the\s+key\s+takeaway|outcome\s+was|positive\s+feedback)\b",
        r"\b(?:awarded|selected|won|completed\s+on\s+time)\b"
    ]
}


def analyze_star_structure(answer_text):
    """
    Analyze candidate response for STAR (Situation, Task, Action, Result)
    elements using structural and linguistic markers.
    """
    if not answer_text or len(answer_text.strip()) < 10:
        return {
            "is_applicable": True,
            "star_score": 0.0,
            "components": {
                "situation": False,
                "task": False,
                "action": False,
                "result": False
            },
            "missing_components": ["Situation", "Task", "Action", "Result"],
            "feedback": "No structured behavioral answer provided."
        }

    text_lower = answer_text.lower()
    components = {}

    for comp, patterns in STAR_PATTERNS.items():
        found = False
        for p in patterns:
            if re.search(p, text_lower):
                found = True
                break
        components[comp] = found

    # Individual action pronoun verification ("I" vs "We" check)
    i_actions = len(re.findall(r"\bi\s+(?:implemented|did|built|coded|designed|led|solved|debugged|analyzed|took)\b", text_lower))
    we_only = len(re.findall(r"\bwe\s+", text_lower)) > 2 and i_actions == 0
    if we_only and components["action"]:
        # Moderate action credit if candidate only spoke in collective 'we' without personal contribution
        action_clarification = True
    else:
        action_clarification = False

    present_count = sum(1 for v in components.values() if v)
    star_score = round(present_count / 4.0, 4)

    missing = [c.capitalize() for c, pres in components.items() if not pres]

    # Generate specific STAR feedback
    star_feedback_parts = []
    if "Situation" in missing:
        star_feedback_parts.append("Set the stage by clearly defining the Situation or project context.")
    if "Task" in missing:
        star_feedback_parts.append("Clarify your specific Task or the core goal you were expected to achieve.")
    if "Action" in missing:
        star_feedback_parts.append("Detail the concrete Actions YOU personally took rather than speaking only about the team.")
    elif action_clarification:
        star_feedback_parts.append("Highlight your individual contribution—you described what the team did, but clarify your personal role.")
    if "Result" in missing:
        star_feedback_parts.append("Clearly state the measurable Result, outcome, or lessons learned from the experience.")

    if not missing and not action_clarification:
        star_feedback_parts.append("Excellent execution of the STAR framework with clear context, action, and results.")

    return {
        "is_applicable": True,
        "star_score": star_score,
        "components": components,
        "missing_components": missing,
        "feedback": " ".join(star_feedback_parts)
    }


# ============================================================
# 2. PERSONALIZED FEEDBACK GENERATOR
# ============================================================

def generate_hr_feedback(
    relevance_score,
    completeness_score,
    clarity_score,
    conciseness_score,
    concept_coverage,
    missing_concepts,
    fillers,
    star_result=None,
    is_star=False
):
    """
    Generate tailored, actionable educational feedback grounded in
    observable textual characteristics.
    """
    feedback = []

    # 1. Relevance Feedback
    if relevance_score >= 0.75:
        feedback.append("Direct, relevant response that clearly addresses the interviewer's question.")
    elif relevance_score >= 0.50:
        feedback.append("Partially addresses the question, but could focus more directly on the core topic.")
    else:
        feedback.append("The answer diverges from the main question. Make sure to address the specific prompt directly.")

    # 2. Structural & STAR Feedback
    if is_star and star_result:
        if star_result["missing_components"]:
            feedback.append(star_result["feedback"])
        else:
            feedback.append("Strong narrative structure covering background, individual action, and outcome.")

    # 3. Conciseness / Length Feedback
    if conciseness_score < 0.60:
        if completeness_score < 0.50:
            feedback.append("Response is too brief. Elaborate with a specific example or explanation.")
        else:
            feedback.append("Response is somewhat lengthy. Aim for a tighter, more concise delivery.")

    # 4. Clarity & Filler Words
    if fillers:
        top_filler, count = fillers[0]
        feedback.append(f"Minimize filler phrases (e.g., '{top_filler}' appeared {count} time{'s' if count > 1 else ''}) to sound more articulate.")

    # 5. Missing Conceptual Depth
    if missing_concepts and len(missing_concepts) > 2 and relevance_score >= 0.50:
        sample_missing = missing_concepts[:2]
        feedback.append(f"Consider touching on themes such as: {', '.join(sample_missing)}.")

    return " ".join(feedback)


# ============================================================
# 3. COMPREHENSIVE HR ANSWER EVALUATOR
# ============================================================

def evaluate_hr_answer(question_obj, candidate_answer):
    """
    Comprehensive evaluation of an HR / Behavioral answer.
    Combines Relevance, Completeness, Clarity, Concept Coverage,
    Semantic Similarity, and optional STAR analysis.
    """
    q_text = question_obj.get("question_text", question_obj.get("question", ""))
    expected_themes = question_obj.get("expected_themes", "")
    requires_star = question_obj.get("requires_star", False)

    # Handle string boolean in CSV
    if isinstance(requires_star, str):
        requires_star = requires_star.strip().lower() in ["true", "1", "yes"]

    # 1. Word Count & Length
    word_count = count_words(candidate_answer)

    # 2. STAR Analysis if applicable (Situation, Task, Action, Result)
    star_result = None
    star_score = None
    star_comps = None
    if requires_star:
        star_result = analyze_star_structure(candidate_answer)
        star_score = star_result["star_score"]
        star_comps = star_result.get("components")

    # 3. Relevance & Semantic Similarity via SBERT
    relevance_score = calculate_relevance(q_text, candidate_answer, expected_themes, star_components=star_comps)
    semantic_similarity_score = calculate_semantic_similarity(q_text, candidate_answer)

    # 4. Completeness & Depth
    completeness_score, _ = evaluate_completeness(candidate_answer)

    # 5. Clarity & Filler Words
    clarity_score, fillers = evaluate_clarity(candidate_answer)

    # 6. Conciseness
    conciseness_score = evaluate_conciseness(candidate_answer)

    # 7. Concept Coverage
    concept_ratio, matched_concepts, missing_concepts = check_concept_coverage(
        candidate_answer,
        expected_themes,
        star_components=star_comps
    )

    # 8. Composite Overall HR Answer Score (0.0 to 1.0)
    if requires_star:
        # Balanced behavioral weights: Relevance (20%), Semantic Sim (10%), STAR (25%), Completeness (20%), Clarity (15%), Concepts (10%)
        overall_score = (
            (relevance_score * 0.20) +
            (semantic_similarity_score * 0.10) +
            (star_score * 0.25) +
            (completeness_score * 0.20) +
            (clarity_score * 0.15) +
            (concept_ratio * 0.10)
        )
    else:
        # Standard HR weights: Relevance (25%), Semantic Sim (15%), Completeness (25%), Clarity (20%), Concepts (15%)
        overall_score = (
            (relevance_score * 0.25) +
            (semantic_similarity_score * 0.15) +
            (completeness_score * 0.25) +
            (clarity_score * 0.20) +
            (concept_ratio * 0.15)
        )

    overall_score = round(max(0.0, min(1.0, overall_score)), 4)

    # 9. Actionable Feedback
    feedback = generate_hr_feedback(
        relevance_score=relevance_score,
        completeness_score=completeness_score,
        clarity_score=clarity_score,
        conciseness_score=conciseness_score,
        concept_coverage=concept_ratio,
        missing_concepts=missing_concepts,
        fillers=fillers,
        star_result=star_result,
        is_star=requires_star
    )

    return {
        "overall_score": overall_score,
        "overall_percentage": round(overall_score * 100, 1),
        "relevance_score": relevance_score,
        "semantic_similarity": semantic_similarity_score,
        "completeness_score": completeness_score,
        "clarity_score": clarity_score,
        "conciseness_score": conciseness_score,
        "concept_coverage": concept_ratio,
        "word_count": word_count,
        "fillers_detected": fillers,
        "requires_star": requires_star,
        "star_result": star_result,
        "feedback": feedback
    }


if __name__ == "__main__":
    q_star = {
        "question_text": "Tell me about a difficult challenge you faced in a project and how you solved it.",
        "expected_themes": "situation; challenge; action; solution; outcome; learning",
        "requires_star": True
    }

    ans_star_complete = """
    During my final year project on an Automatic Medicine Vending Machine, our team faced a severe 
    hardware-software communication latency issue that halted dispensing. My task was to optimize 
    the serial communication protocol. I analyzed the baud rates, refactored the Python driver to 
    use asynchronous threading, and implemented a buffer queue. As a result, we reduced the sensor 
    response time by 65% and successfully completed the live demonstration on schedule.
    """

    ans_star_weak = "We had a bug in our project and it was tough. We stayed late and fixed it."

    print("=== HR ANSWER EVALUATION DEMO ===")
    res_good = evaluate_hr_answer(q_star, ans_star_complete)
    print("\n--- Complete STAR Answer ---")
    print(f"Overall HR Score: {res_good['overall_percentage']}%")
    print(f"Relevance       : {res_good['relevance_score'] * 100:.1f}%")
    print(f"Completeness    : {res_good['completeness_score'] * 100:.1f}%")
    print(f"Clarity         : {res_good['clarity_score'] * 100:.1f}%")
    if res_good['star_result']:
        print(f"STAR Score      : {res_good['star_result']['star_score'] * 100:.1f}%")
        print(f"STAR Components : {res_good['star_result']['components']}")
    print(f"Feedback        : {res_good['feedback']}")

    res_weak = evaluate_hr_answer(q_star, ans_star_weak)
    print("\n--- Weak STAR Answer ---")
    print(f"Overall HR Score: {res_weak['overall_percentage']}%")
    print(f"Feedback        : {res_weak['feedback']}")
