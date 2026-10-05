import json
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from services.ai_service import AIService

router = APIRouter(prefix="/api/jobs", tags=["Job Description & Target Role"])


class MatchJobRequest(BaseModel):
    title: Optional[str] = None
    descriptionText: str
    targetRole: Optional[str] = None


class UpdateTargetRoleRequest(BaseModel):
    targetRole: str


@router.post("/match")
def match_job_description(
    req: MatchJobRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compares candidate's active resume skills against a Job Description.
    Calculates matched skills, missing skills, match percentage, and updates the target role.
    """
    # 1. Fetch current candidate's active resume
    active_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.id.desc()).first()

    candidate_skills = []
    if active_resume and active_resume.extracted_skills_json:
        try:
            candidate_skills = json.loads(active_resume.extracted_skills_json)
        except Exception:
            candidate_skills = []

    # 2. Determine target role
    target_role = req.targetRole or req.title or current_user.target_role
    if not target_role:
        target_role = active_resume.ai_suggested_role if active_resume else "Software Engineer"

    # Update user's target role if user explicitly supplied it
    if req.targetRole:
        current_user.target_role = req.targetRole.strip()

    # 3. Perform Phase 2/3 skill matching
    match_result = AIService.match_job_description(
        candidate_skills=candidate_skills,
        job_description_text=req.descriptionText,
        target_role=target_role
    )

    # 4. Deactivate previous active JDs for this candidate
    db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.id
    ).update({"is_active": False})

    # 5. Save JobDescription record
    new_jd = models.JobDescription(
        user_id=current_user.id,
        title=req.title or target_role,
        description_text=req.descriptionText,
        required_skills_json=json.dumps(match_result["required_skills"]),
        matched_skills_json=json.dumps(match_result["matched_skills"]),
        missing_skills_json=json.dumps(match_result["missing_skills"]),
        match_score=match_result["match_score"],
        is_active=True
    )
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)

    return {
        "success": True,
        "jobDescription": new_jd.to_dict(),
        "targetRole": current_user.target_role,
        "matchScore": match_result["match_score"],
        "matchedSkills": match_result["matched_skills"],
        "missingSkills": match_result["missing_skills"]
    }


@router.put("/target-role")
def update_target_role(
    req: UpdateTargetRoleRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Explicitly updates the candidate's chosen target role.
    Stored against the current authenticated user's profile.
    """
    role = req.targetRole.strip()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target role cannot be blank."
        )

    current_user.target_role = role
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": f"Target role updated to '{role}'.",
        "targetRole": current_user.target_role
    }


@router.get("/current")
def get_current_job(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the candidate's active Job Description and chosen target role.
    Returns targetRole: null if unselected.
    """
    active_jd = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.id,
        models.JobDescription.is_active == True
    ).order_by(models.JobDescription.id.desc()).first()

    return {
        "success": True,
        "targetRole": current_user.target_role,
        "jobDescription": active_jd.to_dict() if active_jd else None
    }
