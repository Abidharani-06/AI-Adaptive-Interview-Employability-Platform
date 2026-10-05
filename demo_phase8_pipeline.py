"""
End-to-End Programmatic Demonstration: Phase 8 Multimodal Assessment & Roadmap
=============================================================================
Demonstrates the complete candidate assessment and employability workflow:
1. Resume parsed (candidate name, education, skills, projects)
2. Skills extracted from resume
3. Job Description skill matching
4. Prioritized skill gaps identified (High, Medium, Low)
5. Adaptive technical interview results
6. HR / Behavioral STAR interview results
7. Speech & acoustic delivery results (observable signals)
8. Computer Vision observable behavior results
9. Phase 7 Multimodal fusion
10. Placement readiness estimation
11. Dynamic personalized recommendations
12. Candidate-specific learning roadmap (multi-week action plan)
13. Final report generated (JSON, Markdown, HTML, CSV)
"""

import sys
from pathlib import Path

# Resolve paths
project_root = Path(__file__).resolve().parent
for sub in ["preprocessing", "nlp", "models", "question_engine", "recomendation", "evaluation", "speech", "computer_vision"]:
    p = str(project_root / "ai_ml" / sub)
    if p not in sys.path:
        sys.path.append(p)

from orchestrator import run_final_employability_pipeline


def run_demo():
    print("============================================================")
    print(" AI-POWERED MULTIMODAL EMPLOYABILITY ASSESSMENT PLATFORM   ")
    print("            PHASE 8 END-TO-END DEMONSTRATION                ")
    print("============================================================\n")

    resume_path = project_root / "resume.pdf"
    jd_path = project_root / "ai_ml" / "data" / "job_description.txt"

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # Pre-calculated round evaluation dictionaries from interview session
    # Note: Audio & Video metrics are observable proxies from recorded interview
    tech_results = {
        "overall_technical_score": 76.5,
        "average_score": 0.765,
        "strong_topics": ["Python", "Machine Learning", "Git"],
        "weak_topics": ["Data Structures", "Docker"]
    }
    hr_results = {
        "overall_hr_score": 81.0,
        "average_relevance": 84.0,
        "average_semantic_similarity": 0.94,
        "average_completeness": 78.0,
        "average_clarity": 88.0,
        "average_star_score": 82.0
    }
    speech_results = {
        "speaking_rate_wpm": 138.0,  # Optimal conversational pace
        "pause_count": 4,
        "average_pause_seconds": 0.8,
        "fillers_per_100_words": 1.4,
        "energy_consistency_percentage": 90.0,
        "speech_continuity_percentage": 85.0
    }
    cv_results = {
        "face_visibility_percentage": 96.0,
        "camera_facing_percentage": 88.0,
        "posture_consistency_percentage": 90.0,
        "movement_stability_percentage": 92.0,
        "gesture_frequency_percentage": 25.0
    }

    # Execute complete orchestrator pipeline
    result = run_final_employability_pipeline(
        resume_path=resume_path,
        job_description=jd_text,
        technical_results=tech_results,
        hr_results=hr_results,
        cv_results=cv_results,
        speech_results=speech_results,
        target_role="AI/ML Software Engineer",
        save_reports=True
    )

    # 1. Candidate Information
    cand = result["candidate"]
    print(f"1. CANDIDATE PROFILE:")
    print(f"   - Name      : {cand['name']}")
    print(f"   - Education : {cand['education']}")
    print(f"   - Projects  : {len(cand['projects'])} projects detected from resume")

    # 2. Extracted Skills
    print(f"\n2. EXTRACTED RESUME SKILLS ({len(cand['skills'])} total):")
    print(f"   - {', '.join(cand['skills'][:10])}...")

    # 3. Job Description Match
    job = result["job_alignment"]
    print(f"\n3. JOB DESCRIPTION ALIGNMENT:")
    print(f"   - Target Role : {job['target_role']}")
    print(f"   - Match Score : {job['match_score']:.1f}%")
    print(f"   - Matched     : {', '.join(job['matched_skills'][:8])}...")

    # 4. Prioritized Skill Gaps
    gaps = result["skill_gaps"]
    print(f"\n4. PRIORITIZED SKILL GAPS:")
    print(f"   - High Priority   : {', '.join(gaps['high_priority'])}")
    print(f"   - Medium Priority : {', '.join(gaps['medium_priority'])}")

    # 5. Technical Interview Performance
    print(f"\n5. TECHNICAL EVALUATION:")
    print(f"   - Score        : {result['technical_assessment']['overall_technical_score']:.1f}%")
    print(f"   - Weak Topics  : {', '.join(result['technical_assessment']['weak_topics'])}")

    # 6. HR & Behavioral Performance
    print(f"\n6. HR NLP & STAR EVALUATION:")
    print(f"   - Score        : {result['hr_assessment']['overall_hr_score']:.1f}%")
    print(f"   - STAR Mastery : {result['hr_assessment']['average_star_score']:.1f}%")

    # 7. Speech & Acoustic Delivery
    print(f"\n7. SPEECH DELIVERY (OBSERVABLE SIGNALS):")
    print(f"   - Speaking Rate: {result['speech_assessment']['speaking_rate_wpm']} WPM")
    print(f"   - Filler Words : {result['speech_assessment']['fillers_per_100_words']} per 100 words")

    # 8. Computer Vision Behavior
    print(f"\n8. OBSERVABLE VISUAL BEHAVIOR:")
    print(f"   - Camera Facing: {result['visual_assessment']['camera_facing_percentage']}%")
    print(f"   - Posture Align: {result['visual_assessment']['posture_consistency_percentage']}%")

    # 9 & 10. Multimodal Fusion & Placement Readiness
    readiness = result["readiness"]
    print(f"\n9 & 10. MULTIMODAL FUSION & PLACEMENT READINESS:")
    print(f"   - Overall Score: {readiness['score']:.1f}%")
    print(f"   - Level        : {readiness['level']}")
    print(f"   - Description  : {readiness['description']}")

    # 11. Recommendations
    print(f"\n11. ACTIONABLE RECOMMENDATIONS:")
    for rec in result["recommendations"][:3]:
        print(f"   > {rec}")

    # 12. Learning Roadmap
    roadmap = result["learning_roadmap"]
    print(f"\n12. PERSONALIZED LEARNING ROADMAP ({roadmap['duration_weeks']} Weeks, {roadmap['total_estimated_hours']} Hours):")
    for wp in roadmap["weekly_action_plan"][:3]:
        print(f"   - Week {wp['week']}: {wp['theme']} (Focus: {', '.join(wp['target_topics'])})")

    # 13. Reports Generated
    reports = result.get("reports", {})
    print(f"\n13. GENERATED REPORT ARTIFACTS:")
    for r_type, r_path in reports.items():
        print(f"   - {r_type:<15}: {r_path}")

    print("\n============================================================")
    print("             DEMONSTRATION COMPLETED SUCCESSFULLY           ")
    print("============================================================")


if __name__ == "__main__":
    run_demo()
