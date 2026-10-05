import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/assessments", tags=["Assessments & Analytics"])


@router.get("/latest")
def get_latest_assessment(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the current candidate's latest completed assessment.
    Returns null if no interview has been completed yet (no fake default).
    """
    latest = db.query(models.Assessment).filter(
        models.Assessment.user_id == current_user.id
    ).order_by(models.Assessment.id.desc()).first()

    if not latest:
        return {"success": True, "assessment": None}

    return {"success": True, "assessment": latest.to_dict()}


@router.get("/skill-gaps")
def get_skill_gaps(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves dynamically computed skill gaps for the authenticated candidate.
    Categorized into HIGH, MEDIUM, and LOW priority.
    """
    gaps = db.query(models.SkillGap).filter(
        models.SkillGap.user_id == current_user.id
    ).order_by(models.SkillGap.id.desc()).all()

    prioritized = [g.to_dict() for g in gaps]
    high = [g["skill"] for g in prioritized if g["priority"] == "HIGH"]
    medium = [g["skill"] for g in prioritized if g["priority"] == "MEDIUM"]
    low = [g["skill"] for g in prioritized if g["priority"] == "LOW"]

    return {
        "success": True,
        "skillGaps": {
            "total_gaps": len(prioritized),
            "high_priority_count": len(high),
            "medium_priority_count": len(medium),
            "low_priority_count": len(low),
            "prioritized_gaps": prioritized,
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low
        }
    }


@router.get("/roadmap")
def get_learning_roadmap(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves candidate's personalized multi-week learning roadmap.
    Returns null if no assessment completed yet.
    """
    roadmap = db.query(models.LearningRoadmap).filter(
        models.LearningRoadmap.user_id == current_user.id
    ).order_by(models.LearningRoadmap.id.desc()).first()

    if not roadmap:
        return {"success": True, "roadmap": None}

    return {"success": True, "roadmap": roadmap.to_dict()}


@router.get("/feedback")
def get_ai_feedback(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves candidate-specific AI feedback (strengths, improvement areas, recommendations).
    """
    latest = db.query(models.Assessment).filter(
        models.Assessment.user_id == current_user.id
    ).order_by(models.Assessment.id.desc()).first()

    if not latest:
        return {
            "success": True,
            "feedback": None
        }

    return {
        "success": True,
        "feedback": {
            "strengths": json.loads(latest.strengths_json) if latest.strengths_json else [],
            "improvement_areas": json.loads(latest.improvement_areas_json) if latest.improvement_areas_json else [],
            "recommendations": json.loads(latest.recommendations_json) if latest.recommendations_json else [],
            "readiness": {
                "score": latest.overall_score,
                "level": latest.readiness_level,
                "description": latest.readiness_description
            }
        }
    }


@router.get("/progress")
def get_progress_timeline(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves longitudinal interview attempt history for the authenticated candidate only.
    """
    attempts = db.query(models.ProgressAttempt).filter(
        models.ProgressAttempt.user_id == current_user.id
    ).order_by(models.ProgressAttempt.attempt_number.asc()).all()

    timeline = [a.to_dict() for a in attempts]

    return {
        "success": True,
        "totalAttempts": len(timeline),
        "timeline": timeline,
        "latestScore": timeline[-1]["score"] if timeline else None,
        "initialScore": timeline[0]["score"] if timeline else None,
        "overallDelta": round(timeline[-1]["score"] - timeline[0]["score"], 1) if len(timeline) > 1 else 0.0
    }


@router.get("/reports")
def get_reports_list(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists available report artifacts generated for the candidate."""
    reports = db.query(models.Report).filter(
        models.Report.user_id == current_user.id
    ).order_by(models.Report.id.desc()).all()

    return {
        "success": True,
        "reports": [r.to_dict() for r in reports]
    }


@router.get("/reports/download/{report_format}")
def download_report_file(
    report_format: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Downloads candidate report artifact (json, markdown, html, csv).
    Ensures candidate can only download their own reports.
    """
    fmt_clean = report_format.lower().strip()
    report = db.query(models.Report).filter(
        models.Report.user_id == current_user.id,
        models.Report.report_type == fmt_clean
    ).order_by(models.Report.id.desc()).first()

    if not report or not report.file_path or not Path(report.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report format '{report_format}' not found for your account."
        )

    return FileResponse(
        path=report.file_path,
        filename=Path(report.file_path).name,
        media_type="application/octet-stream"
    )
