import os
import sys
from pathlib import Path
import pandas as pd

# ============================================================
# RESOLVE PROJECT PATHS FOR ROBUST IMPORTS
# ============================================================

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]

# Allow imports whether executed directly or as a module
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

recomendation_dir = str(project_root / "ai_ml" / "recomendation")
if recomendation_dir not in sys.path:
    sys.path.append(recomendation_dir)

preprocessing_dir = str(project_root / "ai_ml" / "preprocessing")
if preprocessing_dir not in sys.path:
    sys.path.append(preprocessing_dir)

models_dir = str(project_root / "ai_ml" / "models")
if models_dir not in sys.path:
    sys.path.append(models_dir)


from difficulty_selector import select_next_difficulty
from question_generator import generate_questions
from personalized_question_engine import (
    generate_personalized_interview_bank,
    parse_projects_from_text,
    generate_skill_gap_question,
    generate_project_questions
)
from skill_matcher import (
    extract_required_skills,
    calculate_skill_match
)
from resume_parser import analyze_resume
from answer_evaluation_model import evaluate_answer
try:
    from hr_adaptive_engine import run_hr_interview
except ImportError:
    run_hr_interview = None


# ============================================================
# 1. ANALYZE JOB DESCRIPTION
# ============================================================

def analyze_job_match(resume_skills, job_description):
    """
    Compare candidate resume skills with job description requirements.
    """
    known_skills = [
        "python",
        "java",
        "c++",
        "javascript",
        "html",
        "css",
        "react",
        "node.js",
        "sql",
        "mysql",
        "mongodb",
        "aws",
        "azure",
        "docker",
        "git",
        "github",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "power bi",
        "figma",
        "flask",
        "data structures",
        "algorithms",
        "dbms",
        "computer vision",
        "natural language processing",
        "cloud computing"
    ]

    required_skills = extract_required_skills(
        job_description,
        known_skills
    )

    (
        matched_skills,
        missing_skills,
        match_score
    ) = calculate_skill_match(
        resume_skills,
        required_skills
    )

    return (
        required_skills,
        matched_skills,
        missing_skills,
        match_score
    )


# ============================================================
# 2. TOPIC MAPPING AND POOL CREATION
# ============================================================

TOPIC_MAPPING = {
    "sql": "SQL",
    "mysql": "SQL",
    "dbms": "DBMS",
    "algorithms": "Algorithms",
    "data structures": "Data Structures",
    "python": "Flask",
    "java": "OOP",
    "c++": "OOP",
    "machine learning": "Machine Learning",
    "deep learning": "Machine Learning",
    "computer vision": "Machine Learning",
    "natural language processing": "Machine Learning",
    "docker": "Docker",
    "aws": "Cloud Computing",
    "azure": "Cloud Computing",
    "cloud computing": "Cloud Computing",
    "flask": "Flask",
    "javascript": "Flask",
    "operating systems": "OS",
    "computer networks": "Computer Networks"
}


def select_topic_from_skill_gaps(missing_skills):
    """
    Fallback/single topic selection: picks first mapped topic from skill gaps.
    """
    for skill in missing_skills:
        skill_lower = skill.lower().strip()
        if skill_lower in TOPIC_MAPPING:
            return TOPIC_MAPPING[skill_lower]

    return "OOP"


def build_interview_topic_pool(missing_skills, matched_skills, required_skills, has_projects=False):
    """
    Build an ordered priority list of topics for a multi-question interview.
    Prioritizes Candidate Projects, then skill gaps, then required core skills.
    """
    priority_topics = []

    # 1. Project Deep Dive (highest priority if candidate has projects)
    if has_projects:
        priority_topics.append("Resume Projects")

    # 2. Topics from missing skills (probes skill gaps)
    for skill in missing_skills:
        mapped = TOPIC_MAPPING.get(skill.lower().strip(), skill.title())
        if mapped and mapped not in priority_topics:
            priority_topics.append(mapped)

    # 3. Topics from required JD skills
    for skill in required_skills:
        mapped = TOPIC_MAPPING.get(skill.lower().strip(), skill.title())
        if mapped and mapped not in priority_topics:
            priority_topics.append(mapped)

    # 4. Topics from candidate matched skills
    for skill in matched_skills:
        mapped = TOPIC_MAPPING.get(skill.lower().strip(), skill.title())
        if mapped and mapped not in priority_topics:
            priority_topics.append(mapped)

    # 5. Standard CS fallback topics if list is short
    default_topics = [
        "OOP", "DBMS", "Algorithms", "Data Structures",
        "SQL", "OS", "Machine Learning", "Cloud Computing", "Docker"
    ]
    for topic in default_topics:
        if topic not in priority_topics:
            priority_topics.append(topic)

    return priority_topics


# ============================================================
# 3. QUESTION RETRIEVAL AND METADATA
# ============================================================

def get_questions_dataset():
    """
    Load questions dataset with path resolution.
    """
    path_candidates = [
        Path("ai_ml/data/questions.csv"),
        project_root / "ai_ml" / "data" / "questions.csv"
    ]
    for path in path_candidates:
        if path.exists():
            return pd.read_csv(path)

    raise FileNotFoundError("questions.csv could not be found.")


def get_expected_answer(question):
    """
    Retrieve expected answer for a specific question from CSV dataset.
    """
    data = get_questions_dataset()

    matching_rows = data[
        data["question"].str.strip().str.lower() == question.strip().lower()
    ]

    if matching_rows.empty:
        return None

    return str(matching_rows.iloc[0]["expected_answer"])


def get_question_metadata(question):
    """
    Retrieve full metadata (id, topic, difficulty, keywords, expected answer).
    """
    data = get_questions_dataset()

    matching_rows = data[
        data["question"].str.strip().str.lower() == question.strip().lower()
    ]

    if matching_rows.empty:
        return None

    row = matching_rows.iloc[0]
    return {
        "question_id": row.get("question_id", "N/A"),
        "topic": row.get("topic", "General"),
        "difficulty": row.get("difficulty", "Medium"),
        "expected_keywords": str(row.get("expected_keywords", "")),
        "expected_answer": str(row.get("expected_answer", "")),
        "source": "csv_bank"
    }


def select_adaptive_question(topic, difficulty, asked_questions, topic_pool, dynamic_bank=None):
    """
    Select an unasked question matching the target topic and difficulty.
    Prioritizes dynamic AI questions from dynamic_bank, then falls back
    to static CSV questions and adjacent difficulties/topics.
    """
    asked_normalized = {q.strip().lower() for q in asked_questions}

    # ---------------------------------------------------------
    # STEP A: Check Dynamic AI Question Bank First
    # ---------------------------------------------------------
    if dynamic_bank:
        # A1. Exact topic and exact difficulty in dynamic bank
        for q_item in dynamic_bank:
            q_text = q_item["question"].strip()
            if q_text.lower() not in asked_normalized:
                if q_item["topic"].lower() == topic.lower() and q_item["difficulty"].lower() == difficulty.lower():
                    return q_text, q_item["topic"], q_item["difficulty"], q_item

        # A2. Exact topic, any difficulty in dynamic bank
        for q_item in dynamic_bank:
            q_text = q_item["question"].strip()
            if q_text.lower() not in asked_normalized:
                if q_item["topic"].lower() == topic.lower():
                    return q_text, q_item["topic"], q_item["difficulty"], q_item

    # ---------------------------------------------------------
    # STEP B: Check Questions CSV Bank
    # ---------------------------------------------------------
    data = get_questions_dataset()

    def find_unasked_csv(subset):
        for _, row in subset.iterrows():
            q_text = str(row["question"]).strip()
            if q_text.lower() not in asked_normalized:
                meta = {
                    "question_id": str(row.get("question_id", "N/A")),
                    "topic": str(row.get("topic", "General")),
                    "difficulty": str(row.get("difficulty", "Medium")),
                    "expected_keywords": str(row.get("expected_keywords", "")),
                    "expected_answer": str(row.get("expected_answer", "")),
                    "source": "csv_bank"
                }
                return q_text, meta["topic"], meta["difficulty"], meta
        return None

    # B1: Exact topic and exact difficulty in CSV
    exact_matches = data[
        (data["topic"].str.lower() == topic.lower()) &
        (data["difficulty"].str.lower() == difficulty.lower())
    ]
    res = find_unasked_csv(exact_matches)
    if res:
        return res

    # B2: Same topic, other difficulties
    difficulty_order = ["Medium", "Easy", "Hard"]
    for diff in difficulty_order:
        if diff.lower() != difficulty.lower():
            diff_matches = data[
                (data["topic"].str.lower() == topic.lower()) &
                (data["difficulty"].str.lower() == diff.lower())
            ]
            res = find_unasked_csv(diff_matches)
            if res:
                return res

    # B3: Fallback to next topics in topic pool
    for fallback_topic in topic_pool:
        if fallback_topic.lower() == topic.lower():
            continue

        # Check dynamic bank for fallback topic
        if dynamic_bank:
            for q_item in dynamic_bank:
                q_text = q_item["question"].strip()
                if q_text.lower() not in asked_normalized and q_item["topic"].lower() == fallback_topic.lower():
                    return q_text, q_item["topic"], q_item["difficulty"], q_item

        pool_matches = data[
            (data["topic"].str.lower() == fallback_topic.lower()) &
            (data["difficulty"].str.lower() == difficulty.lower())
        ]
        res = find_unasked_csv(pool_matches)
        if res:
            return res

        pool_any = data[data["topic"].str.lower() == fallback_topic.lower()]
        res = find_unasked_csv(pool_any)
        if res:
            return res

    # B4: Final global fallback
    global_res = find_unasked_csv(data)
    if global_res:
        return global_res

    return None, None, None, None


# ============================================================
# 4. SINGLE QUESTION WRAPPER (BACKWARD COMPATIBILITY)
# ============================================================

def get_next_questions(missing_skills, previous_score, number_of_questions=1):
    """
    Backward-compatible single-question selector used in early prototypes.
    """
    topic = select_topic_from_skill_gaps(missing_skills)
    next_difficulty = select_next_difficulty(previous_score)
    questions = generate_questions(topic, next_difficulty, number_of_questions)

    return topic, next_difficulty, questions


# ============================================================
# 5. PERSONALIZED FEEDBACK GENERATION
# ============================================================

def generate_personalized_feedback(ml_score, semantic_score, final_score, expected_keywords, candidate_answer):
    """
    Generate actionable, constructive feedback for a technical answer.
    """
    feedback_parts = []

    # 1. Performance Tier Feedback
    if final_score >= 0.80:
        feedback_parts.append(
            "Strong answer. You accurately captured the fundamental principles and key terminology."
        )
    elif final_score >= 0.60:
        feedback_parts.append(
            "Satisfactory answer. The core concept is understood, but adding formal definitions or specific examples would improve clarity."
        )
    elif final_score >= 0.40:
        feedback_parts.append(
            "Partial understanding. The answer touches on the concept but lacks technical depth and precision."
        )
    else:
        feedback_parts.append(
            "Needs significant improvement. The answer did not address the required technical concepts."
        )

    # 2. Keyword/Concept Coverage Feedback
    if expected_keywords:
        raw_keywords = [
            kw.strip()
            for kw in expected_keywords.replace(";", ",").split(",")
            if kw.strip()
        ]
        answer_lower = candidate_answer.lower()
        missing_terms = [
            kw for kw in raw_keywords
            if kw.lower() not in answer_lower
        ]

        if missing_terms:
            sample_missing = missing_terms[:3]
            feedback_parts.append(
                f"Consider incorporating key concepts such as: {', '.join(sample_missing)}."
            )

    return " ".join(feedback_parts)


# ============================================================
# 6. MULTI-QUESTION ADAPTIVE INTERVIEW PIPELINE
# ============================================================

def run_adaptive_interview(
    resume_path="resume.pdf",
    jd_path="ai_ml/data/job_description.txt",
    num_questions=5,
    interactive=True,
    answers_provider=None
):
    """
    Run an end-to-end multi-question adaptive technical interview
    with Dynamic AI Question Generation.
    """

    # --------------------------------------------------------
    # STEP 1: RESUME & JD ANALYSIS
    # --------------------------------------------------------
    resume_file = Path(resume_path)
    if not resume_file.exists():
        raise FileNotFoundError(f"Resume file not found at: {resume_path}")

    resume_text, resume_skills, resume_sections, resume_projects = analyze_resume(str(resume_file))

    # Read Job Description
    resolved_jd = Path(jd_path)
    if not resolved_jd.exists():
        resolved_jd = project_root / jd_path

    if not resolved_jd.exists():
        raise FileNotFoundError(f"Job description file not found at: {jd_path}")

    with open(resolved_jd, "r", encoding="utf-8") as f:
        job_description = f.read()

    required_skills, matched_skills, missing_skills, match_score = analyze_job_match(
        resume_skills,
        job_description
    )

    # Parse candidate projects
    parsed_projects = parse_projects_from_text(resume_projects, resume_skills)
    has_projects = len(parsed_projects) > 0

    # Build topic rotation pool based on projects, skill gaps & JD
    topic_pool = build_interview_topic_pool(
        missing_skills,
        matched_skills,
        required_skills,
        has_projects=has_projects
    )

    # --------------------------------------------------------
    # STEP 2: GENERATE DYNAMIC PERSONALIZED QUESTION BANK
    # --------------------------------------------------------
    dynamic_bank = generate_personalized_interview_bank(
        resume_skills=resume_skills,
        projects_text=resume_projects,
        missing_skills=missing_skills,
        required_skills=required_skills,
        difficulty="Medium"
    )

    # --------------------------------------------------------
    # STEP 3: DISPLAY CANDIDATE PROFILE & JD MATCH
    # --------------------------------------------------------
    print("============================================================")
    print("     AI MULTIMODAL INTERVIEW — ADAPTIVE TECHNICAL ROUND    ")
    print("============================================================")
    print(f"Candidate Resume    : {resume_file.name}")
    print(f"Total Skills Found  : {len(resume_skills)}")
    print(f"Detected Skills     : {', '.join(resume_skills) if resume_skills else 'None'}")
    print(f"Candidate Projects  : {len(parsed_projects)} detected")
    for p in parsed_projects[:3]:
        print(f"  • {p['clean_name']} [{p['context']}]")
    print(f"Required JD Skills  : {', '.join(required_skills)}")
    print(f"Matched Skills      : {', '.join(matched_skills) if matched_skills else 'None'}")
    print(f"Skill Gaps (Missing): {', '.join(missing_skills) if missing_skills else 'None'}")
    print(f"Resume-JD Match     : {round(match_score, 2)}%")
    print(f"AI Dynamic Bank     : {len(dynamic_bank)} personalized questions generated")
    print(f"Interview Topic Pool: {', '.join(topic_pool[:6])}")
    print("============================================================\n")

    # --------------------------------------------------------
    # STEP 4: INITIALIZE ADAPTIVE SESSION STATE
    # --------------------------------------------------------
    current_difficulty = "Medium"
    previous_score = 0.50
    asked_questions = []
    interview_history = []

    # --------------------------------------------------------
    # STEP 5: MULTI-QUESTION ADAPTIVE LOOP
    # --------------------------------------------------------
    for q_idx in range(1, num_questions + 1):
        # Rotate topic from the pool (modulo topic_pool length)
        topic_idx = (q_idx - 1) % len(topic_pool)
        target_topic = topic_pool[topic_idx]

        # Select adaptive question (checks dynamic bank first, then CSV)
        question_text, actual_topic, actual_difficulty, metadata = select_adaptive_question(
            topic=target_topic,
            difficulty=current_difficulty,
            asked_questions=asked_questions,
            topic_pool=topic_pool,
            dynamic_bank=dynamic_bank
        )

        if not question_text:
            print(f"\n[Warning] No further unique questions available. Concluding session.")
            break

        asked_questions.append(question_text)
        expected_answer = metadata.get("expected_answer", "") if metadata else get_expected_answer(question_text)
        expected_keywords = metadata.get("expected_keywords", "") if metadata else ""
        source_type = metadata.get("source", "csv_bank") if metadata else "csv_bank"

        # Display Question Header
        print(f"------------------------------------------------------------")
        print(f"QUESTION {q_idx} OF {num_questions}  [{source_type.replace('_', ' ').upper()}]")
        print(f"------------------------------------------------------------")
        print(f"Topic        : {actual_topic}")
        print(f"Difficulty   : {actual_difficulty}")
        print(f"Question     : {question_text}")
        print(f"------------------------------------------------------------")

        # Capture Candidate Answer
        candidate_answer = ""
        if interactive:
            candidate_answer = input("\nYour Answer: ").strip()
            while not candidate_answer:
                print("Answer cannot be empty. Please provide an answer:")
                candidate_answer = input("Your Answer: ").strip()
        else:
            if callable(answers_provider):
                candidate_answer = answers_provider(q_idx, question_text, actual_topic)
            elif isinstance(answers_provider, list) and (q_idx - 1) < len(answers_provider):
                candidate_answer = answers_provider[q_idx - 1]
            else:
                candidate_answer = "Default automated test answer covering key concepts."

        # Evaluate Answer using ML & Semantic Model
        ml_score, semantic_score, final_score = evaluate_answer(
            expected_answer,
            candidate_answer
        )

        # Generate Actionable Educational Feedback
        feedback = generate_personalized_feedback(
            ml_score=ml_score,
            semantic_score=semantic_score,
            final_score=final_score,
            expected_keywords=expected_keywords,
            candidate_answer=candidate_answer
        )

        # Select Next Difficulty Adaptively
        next_difficulty = select_next_difficulty(final_score)

        # Store Question Record
        record = {
            "question_number": q_idx,
            "question_id": metadata.get("question_id", f"Q{q_idx:03d}") if metadata else f"Q{q_idx:03d}",
            "question": question_text,
            "topic": actual_topic,
            "difficulty": actual_difficulty,
            "source": source_type,
            "candidate_answer": candidate_answer,
            "ml_score": round(float(ml_score), 4),
            "semantic_score": round(float(semantic_score), 4),
            "final_score": round(float(final_score), 4),
            "feedback": feedback,
            "next_difficulty": next_difficulty
        }
        interview_history.append(record)

        # Display Per-Question Results
        print("\n--- AI EVALUATION ---")
        print(f"ML Model Score      : {record['ml_score']:.4f}")
        print(f"Semantic Similarity : {record['semantic_score']:.4f}")
        print(f"Final Question Score: {record['final_score']:.4f} ({(record['final_score'] * 100):.1f}%)")
        print(f"Actionable Feedback : {feedback}")
        print(f"Adaptive Decision   : Next Difficulty -> [{next_difficulty}]\n")

        # Update difficulty for the next question
        current_difficulty = next_difficulty
        previous_score = final_score

    # --------------------------------------------------------
    # STEP 6: COMPUTE OVERALL INTERVIEW ANALYTICS
    # --------------------------------------------------------
    total_answered = len(interview_history)
    if total_answered == 0:
        return {"status": "no_questions_answered"}

    all_scores = [rec["final_score"] for rec in interview_history]
    average_score = sum(all_scores) / total_answered
    overall_technical_score = round(average_score * 100, 2)

    # Topic-wise performance
    topic_scores = {}
    for rec in interview_history:
        top = rec["topic"]
        topic_scores.setdefault(top, []).append(rec["final_score"])

    topic_performance = {
        top: {
            "count": len(scores),
            "average_score": round(sum(scores) / len(scores), 4),
            "average_percentage": round((sum(scores) / len(scores)) * 100, 1)
        }
        for top, scores in topic_scores.items()
    }

    # Difficulty-wise performance
    difficulty_scores = {}
    for rec in interview_history:
        diff = rec["difficulty"]
        difficulty_scores.setdefault(diff, []).append(rec["final_score"])

    difficulty_performance = {
        diff: {
            "count": len(scores),
            "average_score": round(sum(scores) / len(scores), 4),
            "average_percentage": round((sum(scores) / len(scores)) * 100, 1)
        }
        for diff, scores in difficulty_scores.items()
    }

    # Question sources breakdown
    source_counts = {}
    for rec in interview_history:
        src = rec["source"]
        source_counts[src] = source_counts.get(src, 0) + 1

    # Strong & Weak Topics identification (Threshold: 70%)
    strong_topics = [
        top for top, data in topic_performance.items()
        if data["average_score"] >= 0.70
    ]
    weak_topics = [
        top for top, data in topic_performance.items()
        if data["average_score"] < 0.70
    ]

    summary = {
        "candidate_resume": resume_file.name,
        "resume_skills": resume_skills,
        "job_match_score": round(match_score, 2),
        "total_questions": total_answered,
        "average_score": round(average_score, 4),
        "overall_technical_score": overall_technical_score,
        "source_breakdown": source_counts,
        "topic_performance": topic_performance,
        "difficulty_performance": difficulty_performance,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "interview_history": interview_history
    }

    # --------------------------------------------------------
    # STEP 7: DISPLAY FINAL ASSESSMENT REPORT
    # --------------------------------------------------------
    print("============================================================")
    print("             TECHNICAL INTERVIEW SUMMARY REPORT             ")
    print("============================================================")
    print(f"Questions Answered       : {total_answered} of {num_questions}")
    print(f"Overall Technical Score  : {overall_technical_score}%")
    print(f"Average Answer Score     : {round(average_score, 4)}")
    print(f"Resume-JD Match Score    : {round(match_score, 2)}%")

    print("\n--- QUESTION SOURCES BREAKDOWN ---")
    for src, count in source_counts.items():
        print(f"- {src.replace('_', ' ').title():<25}: {count} question/s")

    print("\n--- TOPIC-WISE PERFORMANCE ---")
    for top, data in topic_performance.items():
        print(f"- {top:<20}: {data['average_percentage']}% (from {data['count']} question/s)")

    print("\n--- DIFFICULTY-WISE PERFORMANCE ---")
    for diff, data in difficulty_performance.items():
        print(f"- {diff:<10}: {data['average_percentage']}% (from {data['count']} question/s)")

    print("\n--- STRENGTHS & WEAKNESSES ---")
    print(f"Strong Topics : {', '.join(strong_topics) if strong_topics else 'None'}")
    print(f"Weak Topics   : {', '.join(weak_topics) if weak_topics else 'None'}")

    print("============================================================\n")

    return summary


# ============================================================
# 7. UNIFIED FULL INTERVIEW RUNNER (TECHNICAL + HR)
# ============================================================

def run_full_interview(
    resume_path="resume.pdf",
    jd_path="ai_ml/data/job_description.txt",
    tech_questions=5,
    hr_questions=5,
    interactive=True,
    tech_answers_provider=None,
    hr_answers_provider=None
):
    """
    Execute a comprehensive multi-round interview:
    Round 1: Adaptive Technical & Project Round (Phases 2 & 3)
    Round 2: HR & Behavioral Round (Phase 4)
    Consolidated Assessment Report
    """
    print("\n" + "#" * 60)
    print("      AI MULTIMODAL INTERVIEW - COMPLETE EVALUATION")
    print("#" * 60 + "\n")

    # Round 1: Technical Interview
    tech_summary = run_adaptive_interview(
        resume_path=resume_path,
        jd_path=jd_path,
        num_questions=tech_questions,
        interactive=interactive,
        answers_provider=tech_answers_provider
    )

    hr_summary = None
    if run_hr_interview:
        print("\n" + "#" * 60)
        print("      PROCEEDING TO ROUND 2: HR & BEHAVIORAL ROUND")
        print("#" * 60 + "\n")

        # Round 2: HR Interview
        hr_summary = run_hr_interview(
            resume_path=resume_path,
            jd_path=jd_path,
            num_questions=hr_questions,
            interactive=interactive,
            answers_provider=hr_answers_provider
        )

    # Consolidated Scoring
    tech_score = tech_summary.get("overall_technical_score", 0.0) if tech_summary else 0.0
    hr_score = hr_summary.get("overall_hr_score", 0.0) if hr_summary else 0.0
    combined_score = round((tech_score * 0.6) + (hr_score * 0.4), 2)

    print("\n" + "=" * 60)
    print("             CONSOLIDATED INTERVIEW ASSESSMENT")
    print("=" * 60)
    print(f"Technical Round Score (Phase 2 & 3) : {tech_score}% (Weight: 60%)")
    print(f"HR / Behavioral Score (Phase 4)     : {hr_score}% (Weight: 40%)")
    print(f"Combined Candidate Interview Score   : {combined_score}%")
    print("=" * 60 + "\n")

    return {
        "technical_summary": tech_summary,
        "hr_summary": hr_summary,
        "combined_score": combined_score
    }


# ============================================================
# 8. MAIN INTERACTIVE EXECUTION
# ============================================================

if __name__ == "__main__":
    print("============================================================")
    print("         AI-POWERED MULTIMODAL INTERVIEW PLATFORM          ")
    print("     PHASE 2/3: TECHNICAL | PHASE 4: HR & BEHAVIORAL       ")
    print("============================================================")
    print("1. Technical Round Only (Phases 2 & 3)")
    print("2. HR & Behavioral Round Only (Phase 4)")
    print("3. Full Interview (Technical + HR Combined)")

    round_choice = input("\nSelect interview mode (1, 2, or 3, default: 1): ").strip()
    if round_choice not in ["1", "2", "3"]:
        round_choice = "1"

    # 1. Candidate Resume Path
    user_resume_path = input("Enter resume PDF path (default: resume.pdf): ").strip()
    if not user_resume_path:
        user_resume_path = "resume.pdf"

    # 2. Number of Questions
    questions_input = input("Enter number of questions per round (default: 5): ").strip()
    if questions_input.isdigit() and int(questions_input) > 0:
        total_q = int(questions_input)
    else:
        total_q = 5

    try:
        if round_choice == "1":
            run_adaptive_interview(
                resume_path=user_resume_path,
                jd_path="ai_ml/data/job_description.txt",
                num_questions=total_q,
                interactive=True
            )
        elif round_choice == "2":
            if run_hr_interview:
                run_hr_interview(
                    resume_path=user_resume_path,
                    jd_path="ai_ml/data/job_description.txt",
                    num_questions=total_q,
                    interactive=True
                )
            else:
                print("[Error] HR interview module not available.")
        else:
            run_full_interview(
                resume_path=user_resume_path,
                jd_path="ai_ml/data/job_description.txt",
                tech_questions=total_q,
                hr_questions=total_q,
                interactive=True
            )
    except FileNotFoundError as fnf:
        print(f"\n[File Error]: {fnf}")
    except Exception as exc:
        print(f"\n[Runtime Error]: {exc}")