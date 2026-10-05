import os
import sys
from pathlib import Path

# Resolve project paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]

models_dir = str(project_root / "ai_ml" / "models")
if models_dir not in sys.path:
    sys.path.append(models_dir)

nlp_dir = str(project_root / "ai_ml" / "nlp")
if nlp_dir not in sys.path:
    sys.path.append(nlp_dir)

if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from hr_evaluation_model import evaluate_hr_answer
from hr_question_engine import (
    generate_personalized_hr_bank,
    select_hr_interview_plan,
    generate_adaptive_follow_up
)

cv_dir = str(project_root / "ai_ml" / "computer_vision")
if cv_dir not in sys.path:
    sys.path.append(cv_dir)

speech_dir = str(project_root / "ai_ml" / "speech")
if speech_dir not in sys.path:
    sys.path.append(speech_dir)

try:
    from cv_interview_analyzer import CVInterviewAnalyzer
except ImportError:
    CVInterviewAnalyzer = None

try:
    from speech_analyzer import SpeechAnalyzer
except ImportError:
    SpeechAnalyzer = None




def run_hr_interview(
    resume_path="resume.pdf",
    jd_path="ai_ml/data/job_description.txt",
    num_questions=5,
    interactive=True,
    answers_provider=None,
    enable_adaptive_followups=True,
    enable_camera=False,
    video_path=None,
    cv_analyzer=None,
    enable_speech=False,
    audio_path=None,
    speech_analyzer=None
):
    """
    Run an end-to-end AI-powered HR and Behavioral Interview Round.
    Features resume-aware question personalization, real-time NLP evaluation,
    STAR behavioral analysis, adaptive follow-ups, camera/video behavioral analysis,
    speech analysis, and comprehensive scoring.
    """
    resume_file = Path(resume_path)
    if not resume_file.exists():
        resume_file = project_root / resume_path
    if not resume_file.exists():
        raise FileNotFoundError(f"Resume file not found at: {resume_path}")

    # --------------------------------------------------------
    # STEP 1: RESUME & JD ANALYSIS
    # --------------------------------------------------------
    profile_data = generate_personalized_hr_bank(str(resume_file), jd_path)
    candidate_name = profile_data["candidate_name"]
    education = profile_data["education"]
    target_role = profile_data["target_role"]
    total_bank_size = len(profile_data["bank"])

    interview_plan = select_hr_interview_plan(profile_data, num_questions=num_questions)

    # Initialize Computer Vision Analyzer if enabled or video supplied
    active_cv = cv_analyzer
    if (enable_camera or video_path) and active_cv is None and CVInterviewAnalyzer is not None:
        active_cv = CVInterviewAnalyzer()

    if active_cv is not None and video_path:
        print("\n[Computer Vision] Processing interview video recording...")
        v_res = active_cv.process_video(video_path)
        if not v_res.get("success"):
            print(f"[Computer Vision Warning]: {v_res.get('error')}")

    # Initialize Speech Analyzer if enabled or audio supplied
    active_speech = speech_analyzer
    speech_eval_result = None
    if (enable_speech or audio_path) and active_speech is None and SpeechAnalyzer is not None:
        active_speech = SpeechAnalyzer()

    if active_speech is not None and audio_path:
        print("\n[Speech Analysis] Processing interview audio recording...")
        speech_eval_result = active_speech.analyze_audio_file(audio_path)
        if not speech_eval_result.get("success"):
            print(f"[Speech Analysis Warning]: {speech_eval_result.get('error')}")
    elif active_speech is not None and hasattr(active_speech, "get_summary"):
        speech_eval_result = active_speech.get_summary()


    # --------------------------------------------------------
    # STEP 2: DISPLAY CANDIDATE & SESSION HEADER
    # --------------------------------------------------------
    print("============================================================")
    print("      AI MULTIMODAL INTERVIEW - HR & BEHAVIORAL ROUND      ")
    print("============================================================")
    print(f"Candidate Name       : {candidate_name}")
    print(f"Resume Source        : {resume_file.name}")
    print(f"Academic Background  : {education}")
    print(f"Target Role (JD)     : {target_role}")
    print(f"Resume Projects      : {profile_data['projects_count']} detected")
    print(f"Personalized HR Bank : {total_bank_size} available questions")
    print(f"Scheduled Questions  : {len(interview_plan)} core questions")
    print(f"Adaptive Follow-ups  : {'Enabled' if enable_adaptive_followups else 'Disabled'}")
    print("============================================================\n")

    interview_history = []
    question_counter = 0

    # --------------------------------------------------------
    # STEP 3: INTERVIEW EXECUTION LOOP
    # --------------------------------------------------------
    for plan_idx, q_item in enumerate(interview_plan, start=1):
        question_counter += 1
        q_text = q_item["question_text"]
        cat = q_item["category"]
        requires_star = q_item["requires_star"]
        star_label = "[STAR BEHAVIORAL]" if requires_star else "[STANDARD HR]"

        # Display Question Header
        print("------------------------------------------------------------")
        print(f"QUESTION {question_counter} OF {len(interview_plan)}  {star_label}")
        print("------------------------------------------------------------")
        print(f"Category      : {cat}")
        print(f"Competencies  : {q_item.get('target_competencies', 'Communication')}")
        print(f"Question      : {q_text}")
        print("------------------------------------------------------------")

        # Capture Answer
        candidate_answer = ""
        if interactive:
            candidate_answer = input("\nYour Response: ").strip()
            while not candidate_answer:
                print("Answer cannot be empty. Please provide your response:")
                candidate_answer = input("Your Response: ").strip()
        else:
            if callable(answers_provider):
                candidate_answer = answers_provider(question_counter, q_text, cat)
            elif isinstance(answers_provider, list) and (question_counter - 1) < len(answers_provider):
                candidate_answer = answers_provider[question_counter - 1]
            else:
                candidate_answer = "In my academic and project experiences, I consistently communicate with teammates, take initiative on implementation, and ensure timely project completion."

        # Evaluate Answer
        eval_result = evaluate_hr_answer(q_item, candidate_answer)

        # Store Record
        record = {
            "question_index": question_counter,
            "is_followup": False,
            "question_id": q_item.get("question_id", f"HR_{question_counter}"),
            "question": q_text,
            "category": cat,
            "requires_star": requires_star,
            "candidate_answer": candidate_answer,
            "overall_score": eval_result["overall_score"],
            "overall_percentage": eval_result["overall_percentage"],
            "relevance_score": eval_result["relevance_score"],
            "semantic_similarity": eval_result.get("semantic_similarity", 0.0),
            "completeness_score": eval_result["completeness_score"],
            "clarity_score": eval_result["clarity_score"],
            "conciseness_score": eval_result["conciseness_score"],
            "concept_coverage": eval_result["concept_coverage"],
            "word_count": eval_result["word_count"],
            "star_result": eval_result["star_result"],
            "feedback": eval_result["feedback"]
        }
        interview_history.append(record)

        # Display Live NLP Evaluation
        print("\n--- AI HR EVALUATION ---")
        print(f"Overall Answer Score : {record['overall_percentage']}%")
        print(f"Relevance to Prompt  : {record['relevance_score'] * 100:.1f}%")
        print(f"Semantic Alignment   : {record['semantic_similarity'] * 100:.1f}%")
        print(f"Completeness & Depth : {record['completeness_score'] * 100:.1f}%")
        print(f"Clarity & Delivery   : {record['clarity_score'] * 100:.1f}%")

        if requires_star and record["star_result"]:
            star = record["star_result"]
            print(f"STAR Structure Score : {star['star_score'] * 100:.1f}%")
            comp_str = ", ".join([f"{k.capitalize()}: {'[YES]' if v else '[NO]'}" for k, v in star["components"].items()])
            print(f"STAR Components      : {comp_str}")

        print(f"Actionable Feedback  : {record['feedback']}\n")

        # ----------------------------------------------------
        # STEP 4: ADAPTIVE FOLLOW-UP QUESTIONING
        # ----------------------------------------------------
        if enable_adaptive_followups:
            followup = generate_adaptive_follow_up(q_item, eval_result)
            if followup:
                question_counter += 1
                f_text = followup["question_text"]
                f_star = followup["requires_star"]
                f_type = followup["type"].replace("_", " ").title()

                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(f"ADAPTIVE FOLLOW-UP [{f_type.upper()}]")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(f"Question      : {f_text}")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

                # Capture Follow-up Answer
                if interactive:
                    f_answer = input("\nYour Response: ").strip()
                    while not f_answer:
                        print("Response cannot be empty:")
                        f_answer = input("Your Response: ").strip()
                else:
                    if callable(answers_provider):
                        f_answer = answers_provider(question_counter, f_text, "Follow-Up")
                    elif isinstance(answers_provider, list) and (question_counter - 1) < len(answers_provider):
                        f_answer = answers_provider[question_counter - 1]
                    else:
                        f_answer = "I personally took responsibility for designing the core logic and debugging the system, which directly solved the bottleneck."

                # Evaluate Follow-up
                f_eval = evaluate_hr_answer(followup, f_answer)

                f_record = {
                    "question_index": question_counter,
                    "is_followup": True,
                    "question_id": f"FOLLOWUP_{question_counter}",
                    "parent_question": q_text,
                    "question": f_text,
                    "category": f"Follow-Up ({cat})",
                    "requires_star": f_star,
                    "candidate_answer": f_answer,
                    "overall_score": f_eval["overall_score"],
                    "overall_percentage": f_eval["overall_percentage"],
                    "relevance_score": f_eval["relevance_score"],
                    "semantic_similarity": f_eval.get("semantic_similarity", 0.0),
                    "completeness_score": f_eval["completeness_score"],
                    "clarity_score": f_eval["clarity_score"],
                    "conciseness_score": f_eval["conciseness_score"],
                    "concept_coverage": f_eval["concept_coverage"],
                    "word_count": f_eval["word_count"],
                    "star_result": f_eval["star_result"],
                    "feedback": f_eval["feedback"]
                }
                interview_history.append(f_record)

                print("\n--- FOLLOW-UP EVALUATION ---")
                print(f"Follow-up Score      : {f_record['overall_percentage']}%")
                print(f"Relevance to Prompt  : {f_record['relevance_score'] * 100:.1f}%")
                print(f"Semantic Alignment   : {f_record['semantic_similarity'] * 100:.1f}%")
                print(f"Actionable Feedback  : {f_record['feedback']}\n")

    # --------------------------------------------------------
    # STEP 5: COMPUTE AGGREGATE HR ANALYTICS
    # --------------------------------------------------------
    total_answered = len(interview_history)
    if total_answered == 0:
        return {"status": "no_questions_answered"}

    all_scores = [r["overall_score"] for r in interview_history]
    avg_overall = sum(all_scores) / total_answered
    avg_relevance = sum(r["relevance_score"] for r in interview_history) / total_answered
    avg_semantic = sum(r.get("semantic_similarity", 0.0) for r in interview_history) / total_answered
    avg_completeness = sum(r["completeness_score"] for r in interview_history) / total_answered
    avg_clarity = sum(r["clarity_score"] for r in interview_history) / total_answered
    avg_conciseness = sum(r["conciseness_score"] for r in interview_history) / total_answered

    star_records = [r for r in interview_history if r["requires_star"] and r["star_result"]]
    if star_records:
        avg_star = sum(r["star_result"]["star_score"] for r in star_records) / len(star_records)
    else:
        avg_star = 0.0

    # Category performance
    cat_scores = {}
    for r in interview_history:
        c = r["category"]
        cat_scores.setdefault(c, []).append(r["overall_score"])

    category_performance = {
        c: {
            "count": len(scs),
            "average_score": round(sum(scs) / len(scs), 4),
            "average_percentage": round((sum(scs) / len(scs)) * 100, 1)
        }
        for c, scs in cat_scores.items()
    }

    # Identify Strengths and Areas of Improvement
    dimension_scores = {
        "Relevance & Topic Focus": avg_relevance,
        "Semantic Similarity & Alignment": avg_semantic,
        "Completeness & Elaboration": avg_completeness,
        "Clarity & Professional Tone": avg_clarity,
        "Conciseness & Precision": avg_conciseness
    }
    if star_records:
        dimension_scores["STAR Behavioral Structure"] = avg_star

    strong_areas = [dim for dim, sc in dimension_scores.items() if sc >= 0.75]
    improvement_areas = [dim for dim, sc in dimension_scores.items() if sc < 0.75]

    summary = {
        "candidate_name": candidate_name,
        "target_role": target_role,
        "total_questions_answered": total_answered,
        "core_questions_count": len(interview_plan),
        "followup_questions_count": total_answered - len(interview_plan),
        "overall_hr_score": round(avg_overall * 100, 2),
        "average_relevance": round(avg_relevance * 100, 1),
        "average_semantic_similarity": round(avg_semantic * 100, 1),
        "average_completeness": round(avg_completeness * 100, 1),
        "average_clarity": round(avg_clarity * 100, 1),
        "average_conciseness": round(avg_conciseness * 100, 1),
        "average_star_score": round(avg_star * 100, 1) if star_records else None,
        "category_performance": category_performance,
        "strong_areas": strong_areas,
        "improvement_areas": improvement_areas,
        "camera_analysis": active_cv.get_aggregate_summary() if active_cv is not None else None,
        "speech_analysis": speech_eval_result if speech_eval_result is not None else (
            active_speech.get_summary() if (active_speech is not None and hasattr(active_speech, "get_summary")) else (
                active_speech if isinstance(active_speech, dict) else None
            )
        )
    }

    # --------------------------------------------------------
    # STEP 6: DISPLAY FINAL HR SUMMARY REPORT
    # --------------------------------------------------------
    print("============================================================")
    print("                HR INTERVIEW SUMMARY REPORT                 ")
    print("============================================================")
    print(f"Candidate Name           : {candidate_name}")
    print(f"Target Role              : {target_role}")
    print(f"Total Questions Answered : {total_answered} ({len(interview_plan)} core + {summary['followup_questions_count']} adaptive follow-up)")
    print(f"Overall HR Round Score   : {summary['overall_hr_score']}%")

    print("\n--- CORE NLP EVALUATION DIMENSIONS ---")
    print(f"- Relevance to Questions : {summary['average_relevance']}%")
    print(f"- Semantic Similarity    : {summary['average_semantic_similarity']}%")
    print(f"- Completeness & Depth   : {summary['average_completeness']}%")
    print(f"- Clarity & Delivery     : {summary['average_clarity']}%")
    print(f"- Conciseness            : {summary['average_conciseness']}%")
    if summary["average_star_score"] is not None:
        print(f"- STAR Behavioral Mastery: {summary['average_star_score']}% (from {len(star_records)} behavioral questions)")

    print("\n--- COMPETENCY PERFORMANCE BREAKDOWN ---")
    for cat, data in category_performance.items():
        print(f"- {cat:<32}: {data['average_percentage']}% ({data['count']} q)")

    print("\n--- CANDIDATE PROFILE ASSESSMENT ---")
    print(f"Strong HR Areas          : {', '.join(strong_areas) if strong_areas else 'None identified'}")
    print(f"Recommended Improvement  : {', '.join(improvement_areas) if improvement_areas else 'None - excellent performance across all dimensions'}")

    if summary.get("camera_analysis"):
        cv_s = summary["camera_analysis"]
        print("\n------------------------------------------------------------")
        print("      CAMERA ANALYSIS ASSESSMENT (OBSERVABLE SIGNALS)       ")
        print("------------------------------------------------------------")
        print(f"Face Visibility Rate     : {cv_s.get('face_visibility_percentage', 0.0):.1f}%")
        print(f"Camera Orientation       : {cv_s.get('camera_facing_percentage', 0.0):.1f}%")
        print(f"Gaze Consistency         : {cv_s.get('gaze_consistency_percentage', 0.0):.1f}%")
        print(f"Posture Consistency      : {cv_s.get('posture_consistency_percentage', 0.0):.1f}%")
        print(f"Movement Stability       : {cv_s.get('movement_stability_percentage', 100.0):.1f}%")
        print(f"Gesture Frequency        : {cv_s.get('gesture_frequency_percentage', 0.0):.1f}%")
        print(f"Analysis Reliability     : {cv_s.get('reliability_status', 'reliable').upper()}")
        print("\nObservable Visual Feedback:")
        for fb in cv_s.get("observable_feedback", []):
            print(f"- {fb}")
        if cv_s.get("warnings"):
            for w in cv_s["warnings"]:
                print(f"! [Notice]: {w}")

    if summary.get("speech_analysis"):
        sp_s = summary["speech_analysis"]
        print("\n------------------------------------------------------------")
        print("      SPEECH ANALYSIS ASSESSMENT (OBSERVABLE SIGNALS)       ")
        print("------------------------------------------------------------")
        if sp_s.get("transcript"):
            t_snip = sp_s["transcript"]
            if len(t_snip) > 80:
                t_snip = t_snip[:80] + "..."
            print(f"Transcript Snippet       : \"{t_snip}\"")
        print(f"Speaking Rate            : {sp_s.get('speaking_rate_wpm', 0.0)} WPM")
        print(f"Pause Frequency          : {sp_s.get('pause_count', 0)} pauses (Avg: {sp_s.get('average_pause_seconds', 0.0):.2f}s)")
        print(f"Speech Active Ratio      : {sp_s.get('speech_active_percentage', 0.0)}%")
        print(f"Filler Word Density      : {sp_s.get('fillers_per_100_words', 0.0)} per 100 words ({sp_s.get('filler_count', 0)} total)")
        print(f"Energy Consistency       : {sp_s.get('energy_consistency_percentage', 0.0):.1f}%")
        print(f"Speech Continuity        : {sp_s.get('speech_continuity_percentage', 0.0):.1f}%")
        print("\nObservable Acoustic & Verbal Feedback:")
        for fb in sp_s.get("observable_feedback", []):
            print(f"- {fb}")
        if sp_s.get("most_frequent_fillers"):
            f_str = ", ".join([f"'{k}': {v}x" for k, v in sp_s["most_frequent_fillers"][:3]])
            print(f"- Common Fillers         : {f_str}")

    print("============================================================\n")

    return summary


if __name__ == "__main__":
    print("============================================================")
    print("         AI-POWERED MULTIMODAL INTERVIEW PLATFORM          ")
    print("            MODULE: HR & BEHAVIORAL INTERVIEW               ")
    print("============================================================")

    user_resume_path = input("Enter resume PDF path (default: resume.pdf): ").strip()
    if not user_resume_path:
        user_resume_path = "resume.pdf"

    questions_input = input("Enter number of core questions (default: 5): ").strip()
    if questions_input.isdigit() and int(questions_input) > 0:
        total_q = int(questions_input)
    else:
        total_q = 5

    cam_input = input("Enable camera / video analysis? (y/n, default: n): ").strip().lower()
    enable_cam = cam_input in ("y", "yes")
    video_input = None
    if enable_cam:
        v_path = input("Enter video file path (or press Enter for live camera): ").strip()
        if v_path:
            video_input = v_path

    speech_input = input("Enable speech / audio analysis? (y/n, default: n): ").strip().lower()
    enable_sp = speech_input in ("y", "yes")
    audio_file_input = None
    if enable_sp:
        a_path = input("Enter audio file path (or press Enter for live microphone): ").strip()
        if a_path:
            audio_file_input = a_path

    try:
        run_hr_interview(
            resume_path=user_resume_path,
            jd_path="ai_ml/data/job_description.txt",
            num_questions=total_q,
            interactive=True,
            enable_adaptive_followups=True,
            enable_camera=enable_cam,
            video_path=video_input,
            enable_speech=enable_sp,
            audio_path=audio_file_input
        )
    except FileNotFoundError as fnf:
        print(f"\n[File Error]: {fnf}")
    except Exception as exc:
        print(f"\n[Runtime Error]: {exc}")
