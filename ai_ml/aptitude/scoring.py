"""
Aptitude Scoring & Diagnostic Engine
===================================
Evaluates candidate submissions, computes section-wise and overall metrics,
identifies strong and weak topics, and generates explainable diagnostic feedback.
"""

from typing import List, Dict, Any, Optional
from .difficulty import calculate_difficulty_metrics


def evaluate_aptitude_submission(
    user_answers: List[Dict[str, Any]],
    evaluation_keys: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates candidate responses against question evaluation keys.

    user_answers format:
    [
        {
            "question_id": "QA_PERC_001",
            "selected_option": "20%",
            "time_taken_seconds": 24.5
        }, ...
    ]
    """
    total_questions = len(evaluation_keys)
    total_attempted = 0
    total_correct = 0
    total_time_seconds = 0.0

    # Section-wise tracking
    sections = {
        "Quantitative Ability": {"total": 0, "attempted": 0, "correct": 0, "time": 0.0, "score": 0.0},
        "Logical Reasoning": {"total": 0, "attempted": 0, "correct": 0, "time": 0.0, "score": 0.0},
        "Verbal Ability": {"total": 0, "attempted": 0, "correct": 0, "time": 0.0, "score": 0.0}
    }

    # Topic-wise tracking
    topic_stats: Dict[str, Dict[str, int]] = {}

    # Answer log details
    answer_logs: List[Dict[str, Any]] = []

    # Map user answers by question_id for O(1) lookup
    user_ans_map = {ans["question_id"]: ans for ans in user_answers if "question_id" in ans}

    for q_id, q_info in evaluation_keys.items():
        sec = q_info["section"]
        topic = q_info["topic"]
        correct_ans = q_info["correct_answer"]
        diff = q_info["difficulty"]

        if sec in sections:
            sections[sec]["total"] += 1

        if topic not in topic_stats:
            topic_stats[topic] = {"section": sec, "total": 0, "correct": 0}
        topic_stats[topic]["total"] += 1

        ans_entry = user_ans_map.get(q_id)
        selected_opt = ans_entry.get("selected_option") if ans_entry else None
        time_taken = float(ans_entry.get("time_taken_seconds", 0.0)) if ans_entry else 0.0
        total_time_seconds += time_taken

        is_attempted = selected_opt is not None and str(selected_opt).strip() != ""
        is_correct = False

        if is_attempted:
            total_attempted += 1
            if sec in sections:
                sections[sec]["attempted"] += 1
                sections[sec]["time"] += time_taken

            if str(selected_opt).strip() == str(correct_ans).strip():
                is_correct = True
                total_correct += 1
                if sec in sections:
                    sections[sec]["correct"] += 1
                topic_stats[topic]["correct"] += 1

        answer_logs.append({
            "question_id": q_id,
            "section": sec,
            "topic": topic,
            "difficulty": diff,
            "selected_option": selected_opt,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "is_attempted": is_attempted,
            "time_taken_seconds": round(time_taken, 1),
            "explanation": q_info.get("explanation", "")
        })

    # Compute section scores and overall scores
    for sec_name, s_data in sections.items():
        if s_data["total"] > 0:
            s_data["score"] = round((s_data["correct"] / s_data["total"]) * 100.0, 1)
            s_data["accuracy"] = round((s_data["correct"] / max(1, s_data["attempted"])) * 100.0, 1)
            s_data["avg_time_per_q"] = round(s_data["time"] / max(1, s_data["attempted"]), 1)
        else:
            s_data["score"] = 0.0
            s_data["accuracy"] = 0.0
            s_data["avg_time_per_q"] = 0.0

    quant_score = sections["Quantitative Ability"]["score"]
    reasoning_score = sections["Logical Reasoning"]["score"]
    verbal_score = sections["Verbal Ability"]["score"]

    # Weighted overall aptitude score (Quantitative 40%, Reasoning 35%, Verbal 25%)
    overall_score = round(quant_score * 0.40 + reasoning_score * 0.35 + verbal_score * 0.25, 1)
    overall_accuracy = round((total_correct / max(1, total_attempted)) * 100.0, 1)
    avg_response_time = round(total_time_seconds / max(1, total_attempted), 1)

    # Classify strong and weak topics
    strong_topics = []
    weak_topics = []
    needs_improvement_topics = []

    for topic, stats in topic_stats.items():
        acc = (stats["correct"] / stats["total"]) * 100.0
        entry = {
            "topic": topic,
            "section": stats["section"],
            "accuracy": round(acc, 1),
            "correct": stats["correct"],
            "total": stats["total"]
        }
        if acc >= 75.0:
            strong_topics.append(entry)
        elif acc < 50.0:
            weak_topics.append(entry)
        else:
            needs_improvement_topics.append(entry)

    # Sort topics by accuracy ascending for weak areas
    weak_topics.sort(key=lambda x: x["accuracy"])
    strong_topics.sort(key=lambda x: x["accuracy"], reverse=True)

    # Difficulty performance
    diff_metrics = calculate_difficulty_metrics(answer_logs)

    # Diagnostic narrative & roadmap recommendation
    diagnostic_summary = []
    if quant_score >= 80:
        diagnostic_summary.append("Exceptional quantitative problem-solving fundamentals.")
    elif quant_score < 60:
        diagnostic_summary.append("Quantitative speed and arithmetic accuracy require focused review.")

    if reasoning_score >= 80:
        diagnostic_summary.append("Strong analytical deduction and structured logical reasoning.")
    elif reasoning_score < 60:
        diagnostic_summary.append("Logical deduction, series, and puzzle consistency need structured practice.")

    if verbal_score >= 80:
        diagnostic_summary.append("Clear verbal comprehension, grammatical accuracy, and professional vocabulary.")
    elif verbal_score < 60:
        diagnostic_summary.append("Sentence correction and contextual vocabulary need reinforcement.")

    weak_topic_names = [t["topic"] for t in weak_topics]
    roadmap_inputs = {
        "focus_areas": weak_topic_names[:3],
        "recommended_daily_problems": 15 if overall_score < 70 else 8,
        "primary_weakness": weak_topic_names[0] if weak_topic_names else "General speed optimization"
    }

    return {
        "overall_score": overall_score,
        "accuracy": overall_accuracy,
        "total_questions": total_questions,
        "attempted_count": total_attempted,
        "unattempted_count": total_questions - total_attempted,
        "correct_count": total_correct,
        "average_response_time": avg_response_time,
        "total_time_seconds": round(total_time_seconds, 1),
        "sections": {
            "quantitative": sections["Quantitative Ability"],
            "logical_reasoning": sections["Logical Reasoning"],
            "verbal_ability": sections["Verbal Ability"]
        },
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "needs_improvement_topics": needs_improvement_topics,
        "difficulty_performance": diff_metrics,
        "diagnostic_summary": diagnostic_summary,
        "roadmap_inputs": roadmap_inputs,
        "answer_logs": answer_logs
    }
