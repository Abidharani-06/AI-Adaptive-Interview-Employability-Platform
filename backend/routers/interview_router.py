import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from services.ai_service import AIService

router = APIRouter(prefix="/api/interviews", tags=["Interview Management"])

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class SetupSessionRequest(BaseModel):
    roundId: Optional[str] = "full"
    roundType: Optional[str] = "Full Mock Interview"
    targetRole: Optional[str] = None
    questionCount: Optional[int] = 5
    difficulty: Optional[str] = "adaptive"
    enableCamera: Optional[bool] = True
    enableMicrophone: Optional[bool] = True


class AnswerRecord(BaseModel):
    questionId: Optional[int] = None
    question: str
    category: Optional[str] = None
    answer: str


class CompleteInterviewRequest(BaseModel):
    answers: List[AnswerRecord]
    cvResults: Optional[Dict[str, Any]] = None
    speechResults: Optional[Dict[str, Any]] = None
    aptitudeAttemptId: Optional[int] = None


class LiveHREvalRequest(BaseModel):
    question: str
    answer: str
    category: Optional[str] = "HR Behavioral"


class SpeechMetricsRequest(BaseModel):
    transcript: str
    durationSeconds: float
    pauseCount: Optional[int] = 0



@router.post("/setup")
def setup_interview_session(
    req: SetupSessionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configures and creates a new isolated interview session for the candidate.
    Generates personalized questions dynamically based on:
    - Current candidate's resume projects
    - Candidate's target role
    - Identified JD skill gaps
    - Difficulty configuration
    """
    # 1. Resolve target role
    target_role = req.targetRole or current_user.target_role or "Software Engineer"
    if req.targetRole and not current_user.target_role:
        current_user.target_role = req.targetRole
        db.commit()

    # 2. Fetch current candidate's active resume and JD
    active_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.id.desc()).first()

    active_jd = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.id,
        models.JobDescription.is_active == True
    ).order_by(models.JobDescription.id.desc()).first()

    candidate_data = {
        "skills": json.loads(active_resume.extracted_skills_json) if active_resume and active_resume.extracted_skills_json else [],
        "projects": json.loads(active_resume.extracted_projects_json) if active_resume and active_resume.extracted_projects_json else []
    }

    missing_skills = []
    if active_jd and active_jd.missing_skills_json:
        try:
            missing_skills = json.loads(active_jd.missing_skills_json)
        except Exception:
            missing_skills = []

    # 3. Dynamically generate personalized questions using Phase 1, 3, 4 engines
    q_count = req.questionCount or 5
    raw_questions = AIService.generate_interview_questions(
        candidate_data=candidate_data,
        target_role=target_role,
        round_type=req.roundType or "Full Mock Interview",
        question_count=q_count,
        difficulty=req.difficulty or "Medium",
        missing_skills=missing_skills
    )

    # 4. Create InterviewSession in database
    new_session = models.InterviewSession(
        user_id=current_user.id,
        round_id=req.roundId or "full",
        round_type=req.roundType or "Full Mock Interview",
        target_role=target_role,
        difficulty=req.difficulty or "adaptive",
        question_count=len(raw_questions),
        enable_camera=bool(req.enableCamera),
        enable_microphone=bool(req.enableMicrophone),
        status="in_progress"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # 5. Save generated InterviewQuestion rows
    for idx, q_dict in enumerate(raw_questions):
        q_row = models.InterviewQuestion(
            session_id=new_session.id,
            order_index=idx,
            question_text=q_dict.get("question", ""),
            category=q_dict.get("category", "Technical Core"),
            question_type=q_dict.get("type", "Adaptive"),
            difficulty=q_dict.get("difficulty", "Medium"),
            hint=q_dict.get("hint", ""),
            expected_keywords=q_dict.get("expected_keywords", ""),
            expected_answer=q_dict.get("expected_answer", ""),
            topic=q_dict.get("topic", "")
        )
        db.add(q_row)

    db.commit()
    db.refresh(new_session)

    return {
        "success": True,
        "session": new_session.to_dict()
    }


@router.get("/{session_id}")
def get_interview_session(
    session_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves session details and questions, enforcing user isolation."""
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found or unauthorized."
        )

    return {
        "success": True,
        "session": session.to_dict()
    }


@router.post("/{session_id}/complete")
def complete_interview_session(
    session_id: int,
    req: CompleteInterviewRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalizes the interview session.
    Triggers the complete Phase 4-8 Multimodal AI Evaluation pipeline:
    - Technical and HR NLP assessment
    - Speech acoustic analysis
    - Computer Vision observable presentation analysis
    - Multimodal readiness estimation
    - Prioritized skill gaps
    - Dynamic personalized 5-week roadmap
    - Multi-attempt progress tracking
    - Report generation
    Saves all metrics in user-isolated database records.
    """
    # 1. Validate session ownership
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or unauthorized."
        )

    # 2. Save individual answers to database
    formatted_answers = []
    for ans in req.answers:
        words = ans.answer.strip().split()
        ans_row = models.InterviewAnswer(
            session_id=session.id,
            question_id=ans.questionId,
            question_text=ans.question,
            category=ans.category,
            answer_text=ans.answer,
            word_count=len(words)
        )
        db.add(ans_row)
        formatted_answers.append({
            "question": ans.question,
            "category": ans.category,
            "answer": ans.answer
        })

    # 3. Retrieve resume and JD context
    active_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.id.desc()).first()

    active_jd = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.id,
        models.JobDescription.is_active == True
    ).order_by(models.JobDescription.id.desc()).first()

    resume_path = active_resume.file_path if active_resume and active_resume.file_path and Path(active_resume.file_path).exists() else None
    jd_text = active_jd.description_text if active_jd else None

    # 4. Create user-specific reports directory
    user_reports_dir = REPORTS_DIR / f"user_{current_user.id}"
    user_reports_dir.mkdir(parents=True, exist_ok=True)

    # 4b. Retrieve candidate's aptitude attempt if available
    aptitude_attempt = None
    if req.aptitudeAttemptId:
        aptitude_attempt = db.query(models.AptitudeAttempt).filter(
            models.AptitudeAttempt.id == req.aptitudeAttemptId,
            models.AptitudeAttempt.user_id == current_user.id
        ).first()
    if not aptitude_attempt:
        aptitude_attempt = db.query(models.AptitudeAttempt).filter(
            models.AptitudeAttempt.user_id == current_user.id,
            models.AptitudeAttempt.status == "completed"
        ).order_by(models.AptitudeAttempt.id.desc()).first()

    if aptitude_attempt and not aptitude_attempt.session_id:
        aptitude_attempt.session_id = session.id
        db.commit()

    aptitude_data = aptitude_attempt.to_dict() if aptitude_attempt else None

    # 5. Run full Phase 4-8 AI Evaluation Pipeline
    assessment_data = AIService.evaluate_candidate_interview(
        candidate_name=current_user.full_name,
        target_role=session.target_role,
        resume_path=str(resume_path) if resume_path else None,
        job_description_text=jd_text,
        answers=formatted_answers,
        cv_metrics=req.cvResults,
        speech_metrics=req.speechResults,
        aptitude_results=aptitude_data,
        reports_dir=str(user_reports_dir)
    )

    # 6. Mark session completed
    session.status = "completed"
    session.completed_at = datetime.utcnow()

    # 7. Persist Assessment record
    readiness = assessment_data.get("readiness", {})
    comp_scores = assessment_data.get("multimodal_assessment", {}).get("component_scores", {})
    
    new_assessment = models.Assessment(
        user_id=current_user.id,
        session_id=session.id,
        overall_score=readiness.get("score", 75.0),
        readiness_level=readiness.get("level", "Ready"),
        readiness_description=readiness.get("description", ""),
        technical_score=comp_scores.get("technical", 70.0),
        hr_score=comp_scores.get("hr_nlp", 70.0),
        speech_score=comp_scores.get("speech", 70.0),
        cv_score=comp_scores.get("computer_vision", 70.0),
        resume_jd_score=comp_scores.get("resume_jd", 70.0),
        strengths_json=json.dumps(assessment_data.get("strengths", [])),
        improvement_areas_json=json.dumps(assessment_data.get("improvement_areas", [])),
        recommendations_json=json.dumps(assessment_data.get("recommendations", [])),
        component_scores_json=json.dumps(comp_scores),
        raw_assessment_json=json.dumps(assessment_data)
    )
    db.add(new_assessment)

    # 8. Persist SkillGaps
    gaps_info = assessment_data.get("skill_gaps", {})
    for g in gaps_info.get("prioritized_gaps", []):
        sg = models.SkillGap(
            user_id=current_user.id,
            session_id=session.id,
            skill=g.get("skill", ""),
            priority=g.get("priority", "MEDIUM"),
            reason=g.get("reason", ""),
            is_core=bool(g.get("is_core", False)),
            status="open"
        )
        db.add(sg)

    # 9. Persist LearningRoadmap
    roadmap_info = assessment_data.get("learning_roadmap", {})
    if roadmap_info:
        lr = models.LearningRoadmap(
            user_id=current_user.id,
            session_id=session.id,
            duration_weeks=roadmap_info.get("duration_weeks", 5),
            total_estimated_hours=roadmap_info.get("total_estimated_hours", 80),
            weekly_action_plan_json=json.dumps(roadmap_info.get("weekly_action_plan", [])),
            learning_modules_json=json.dumps(roadmap_info.get("learning_modules", []))
        )
        db.add(lr)

    # 10. Persist ProgressAttempt
    prev_attempts_count = db.query(models.ProgressAttempt).filter(
        models.ProgressAttempt.user_id == current_user.id
    ).count()

    prev_latest = db.query(models.ProgressAttempt).filter(
        models.ProgressAttempt.user_id == current_user.id
    ).order_by(models.ProgressAttempt.attempt_number.desc()).first()

    delta = round(readiness.get("score", 75.0) - prev_latest.score, 1) if prev_latest else 0.0

    attempt_record = models.ProgressAttempt(
        user_id=current_user.id,
        session_id=session.id,
        attempt_number=prev_attempts_count + 1,
        date_str=datetime.utcnow().strftime("%Y-%m-%d"),
        score=readiness.get("score", 75.0),
        readiness_level=readiness.get("level", "Ready"),
        score_delta_previous=delta,
        component_scores_json=json.dumps(comp_scores)
    )
    db.add(attempt_record)

    # 11. Persist Reports
    for r_type, r_path in assessment_data.get("reports", {}).items():
        rep = models.Report(
            user_id=current_user.id,
            session_id=session.id,
            report_type=r_type,
            file_path=str(r_path)
        )
        db.add(rep)

    db.commit()
    db.refresh(new_assessment)

    return {
        "success": True,
        "message": "Interview session completed and evaluated successfully.",
        "assessment": assessment_data
    }


@router.post("/evaluate-hr-answer")
def evaluate_hr_answer_endpoint(
    req: LiveHREvalRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Evaluates a candidate's HR / behavioral response in real time using Phase 4 NLP models.
    Returns composite score, STAR breakdown, clarity, and adaptive follow-up question if applicable.
    """
    res = AIService.evaluate_hr_answer_live(
        question_text=req.question,
        answer_text=req.answer,
        category=req.category or "HR Behavioral"
    )
    return {
        "success": True,
        "evaluation": res["evaluation"],
        "adaptiveFollowup": res["adaptive_followup"]
    }


@router.post("/speech-metrics")
def compute_speech_metrics_endpoint(
    req: SpeechMetricsRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Computes observable speech acoustic features (Phase 6):
    speaking rate (WPM), pause density, filler word density, continuity, and fluency.
    """
    metrics = AIService.compute_speech_metrics_from_text(
        transcript=req.transcript,
        duration_seconds=req.durationSeconds,
        pause_count=req.pauseCount or 0
    )
    return {
        "success": True,
        "metrics": metrics
    }

