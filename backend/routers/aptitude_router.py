"""
Aptitude Assessment Router
==========================
Handles Round 1 Aptitude Assessment:
- Section-wise question generation (Quantitative, Logical, Verbal)
- Dynamic submission evaluation and scoring
- Weak topic diagnostics & difficulty progression
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from ai_ml.aptitude.question_selector import select_aptitude_questions
from ai_ml.aptitude.scoring import evaluate_aptitude_submission

router = APIRouter(prefix="/api/aptitude", tags=["Aptitude Assessment"])


class StartAptitudeRequest(BaseModel):
    sessionId: Optional[int] = None
    questionsPerSection: Optional[int] = Field(default=5, ge=2, le=10)


class AnswerEntry(BaseModel):
    question_id: str
    selected_option: Optional[str] = None
    time_taken_seconds: Optional[float] = 0.0


class SubmitAptitudeRequest(BaseModel):
    attemptId: int
    answers: List[AnswerEntry]


@router.post("/start")
def start_aptitude_assessment(
    req: StartAptitudeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initializes a new Round 1 Aptitude Assessment for the candidate.
    Selects randomized questions across Quantitative, Logical, and Verbal sections.
    """
    client_questions, evaluation_keys = select_aptitude_questions(
        questions_per_section=req.questionsPerSection
    )

    new_attempt = models.AptitudeAttempt(
        user_id=current_user.id,
        session_id=req.sessionId,
        total_questions=len(client_questions),
        evaluation_keys_json=json.dumps(evaluation_keys),
        status="in_progress",
        created_at=datetime.utcnow()
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return {
        "success": True,
        "attemptId": new_attempt.id,
        "totalQuestions": len(client_questions),
        "questionsPerSection": req.questionsPerSection,
        "sections": ["Quantitative Ability", "Logical Reasoning", "Verbal Ability"],
        "questions": client_questions
    }


@router.get("/questions/{attempt_id}")
def get_attempt_questions(
    attempt_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves client-safe questions for an active attempt."""
    attempt = db.query(models.AptitudeAttempt).filter(
        models.AptitudeAttempt.id == attempt_id,
        models.AptitudeAttempt.user_id == current_user.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Aptitude attempt not found.")

    if not attempt.evaluation_keys_json:
        raise HTTPException(status_code=400, detail="No question data available for this attempt.")

    eval_keys = json.loads(attempt.evaluation_keys_json)
    # Reconstruct client questions without leaking correct answers
    client_qs = []
    for q_id, q_data in eval_keys.items():
        client_qs.append({
            "id": q_id,
            "order_index": q_data.get("order_index", 1),
            "section": q_data["section"],
            "topic": q_data["topic"],
            "difficulty": q_data["difficulty"],
            "question": q_data.get("question", ""),
            "options": q_data.get("options", [])
        })

    client_qs.sort(key=lambda x: x["order_index"])

    return {
        "success": True,
        "attemptId": attempt.id,
        "status": attempt.status,
        "questions": client_qs
    }


@router.post("/submit")
def submit_aptitude_assessment(
    req: SubmitAptitudeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits candidate answers for Round 1 Aptitude.
    Performs multi-dimensional scoring and weak-topic diagnostics.
    """
    attempt = db.query(models.AptitudeAttempt).filter(
        models.AptitudeAttempt.id == req.attemptId,
        models.AptitudeAttempt.user_id == current_user.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Aptitude attempt not found.")

    if not attempt.evaluation_keys_json:
        raise HTTPException(status_code=400, detail="Evaluation keys missing for this attempt.")

    eval_keys = json.loads(attempt.evaluation_keys_json)
    raw_answers = [a.dict() for a in req.answers]

    # Evaluate submission
    eval_result = evaluate_aptitude_submission(raw_answers, eval_keys)

    # Persist score and diagnostic summary to database
    attempt.overall_score = eval_result["overall_score"]
    attempt.accuracy = eval_result["accuracy"]
    attempt.attempted_count = eval_result["attempted_count"]
    attempt.correct_count = eval_result["correct_count"]
    attempt.average_response_time = eval_result["average_response_time"]
    attempt.total_time_seconds = eval_result["total_time_seconds"]

    attempt.quantitative_score = eval_result["sections"]["quantitative"]["score"]
    attempt.reasoning_score = eval_result["sections"]["logical_reasoning"]["score"]
    attempt.verbal_score = eval_result["sections"]["verbal_ability"]["score"]

    attempt.strong_topics_json = json.dumps(eval_result["strong_topics"])
    attempt.weak_topics_json = json.dumps(eval_result["weak_topics"])
    attempt.difficulty_performance_json = json.dumps(eval_result["difficulty_performance"])
    attempt.section_details_json = json.dumps(eval_result["sections"])
    attempt.roadmap_inputs_json = json.dumps(eval_result["roadmap_inputs"])
    attempt.diagnostic_summary_json = json.dumps(eval_result["diagnostic_summary"])

    attempt.status = "completed"
    attempt.completed_at = datetime.utcnow()

    # Clear existing logs if re-submitted
    db.query(models.AptitudeAnswerLog).filter(models.AptitudeAnswerLog.attempt_id == attempt.id).delete()

    # Save answer logs
    for log in eval_result["answer_logs"]:
        ans_log = models.AptitudeAnswerLog(
            attempt_id=attempt.id,
            question_id=log["question_id"],
            section=log["section"],
            topic=log["topic"],
            difficulty=log["difficulty"],
            selected_option=log["selected_option"],
            correct_answer=log["correct_answer"],
            is_correct=log["is_correct"],
            is_attempted=log["is_attempted"],
            time_taken_seconds=log["time_taken_seconds"],
            explanation=log["explanation"]
        )
        db.add(ans_log)

    db.commit()
    db.refresh(attempt)

    return {
        "success": True,
        "attempt": attempt.to_dict(),
        "evaluation": eval_result,
        "nextRound": {
            "round": 2,
            "title": "AI HR Interview",
            "message": "Round 1 Completed! Proceed to Round 2 — AI HR Interview."
        }
    }


@router.get("/results/{attempt_id}")
def get_aptitude_results(
    attempt_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves full evaluation report for an aptitude attempt."""
    attempt = db.query(models.AptitudeAttempt).filter(
        models.AptitudeAttempt.id == attempt_id,
        models.AptitudeAttempt.user_id == current_user.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Aptitude attempt not found.")

    answer_logs = [log.to_dict() for log in attempt.answer_logs]

    return {
        "success": True,
        "attempt": attempt.to_dict(),
        "answerLogs": answer_logs
    }


@router.get("/latest")
def get_latest_aptitude_result(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the candidate's latest completed aptitude assessment."""
    latest_attempt = db.query(models.AptitudeAttempt).filter(
        models.AptitudeAttempt.user_id == current_user.id,
        models.AptitudeAttempt.status == "completed"
    ).order_by(models.AptitudeAttempt.id.desc()).first()

    if not latest_attempt:
        return {"success": True, "attempt": None}

    return {
        "success": True,
        "attempt": latest_attempt.to_dict()
    }
