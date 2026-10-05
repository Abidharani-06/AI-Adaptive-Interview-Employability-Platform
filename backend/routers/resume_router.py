import os
import re
import json
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from services.ai_service import AIService

router = APIRouter(prefix="/api/resumes", tags=["Resume Analysis"])

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class TextResumeRequest(BaseModel):
    rawText: str
    fileName: Optional[str] = "Pasted_Resume.txt"


def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters from uploaded filenames."""
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
    return clean[:100]


@router.post("/upload")
async def upload_resume_pdf(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handles PDF resume uploads.
    Saves file to isolated storage, executes Python Phase 2 parser (PyPDF2),
    extracts candidate profile, skills, projects, and generates AI role suggestion.
    """
    # 1. Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".txt", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF or text document."
        )

    # 2. Sanitize and save file
    safe_name = sanitize_filename(file.filename)
    user_file_name = f"user_{current_user.id}_{safe_name}"
    dest_path = UPLOAD_DIR / user_file_name

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Check file size
    if dest_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10 MB limit."
        )

    # 3. Parse using AI/ML Phase 2 engine
    try:
        profile = AIService.parse_resume(file_path=str(dest_path))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resume PDF: {str(e)}"
        )

    # 4. Deactivate previous active resumes for this user
    db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).update({"is_active": False})

    # 5. Store Resume record
    new_resume = models.Resume(
        user_id=current_user.id,
        filename=safe_name,
        file_path=str(dest_path),
        raw_text=profile.get("resume_text", ""),
        extracted_name=profile.get("name"),
        extracted_education=profile.get("education"),
        extracted_department=profile.get("department"),
        extracted_skills_json=json.dumps(profile.get("skills", [])),
        extracted_projects_json=json.dumps(profile.get("projects", [])),
        extracted_internships_json=json.dumps(profile.get("internships", [])),
        extracted_certifications_json=json.dumps(profile.get("certifications", [])),
        ai_suggested_role=profile.get("ai_suggested_role", "Software Engineer"),
        is_active=True
    )
    db.add(new_resume)

    # 6. Update user's profile with extracted education/dept if empty
    if not current_user.department and profile.get("department"):
        current_user.department = profile.get("department")
    if not current_user.college and profile.get("education"):
        current_user.college = profile.get("education")

    db.commit()
    db.refresh(new_resume)

    return {
        "success": True,
        "message": f"Resume '{safe_name}' analyzed successfully.",
        "resume": new_resume.to_dict(),
        "aiSuggestedRole": new_resume.ai_suggested_role,
        "currentUserTargetRole": current_user.target_role  # Explicitly shown to maintain separation
    }


@router.post("/parse-text")
def parse_text_resume(
    req: TextResumeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parses pasted resume text into structured candidate competencies.
    """
    if not req.rawText.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty."
        )

    profile = AIService.parse_resume(raw_text=req.rawText)

    # Deactivate previous active resumes
    db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).update({"is_active": False})

    new_resume = models.Resume(
        user_id=current_user.id,
        filename=req.fileName or "Pasted_Resume.txt",
        raw_text=req.rawText,
        extracted_name=profile.get("name"),
        extracted_education=profile.get("education"),
        extracted_department=profile.get("department"),
        extracted_skills_json=json.dumps(profile.get("skills", [])),
        extracted_projects_json=json.dumps(profile.get("projects", [])),
        extracted_internships_json=json.dumps(profile.get("internships", [])),
        extracted_certifications_json=json.dumps(profile.get("certifications", [])),
        ai_suggested_role=profile.get("ai_suggested_role", "Software Engineer"),
        is_active=True
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "success": True,
        "message": "Resume text parsed successfully.",
        "resume": new_resume.to_dict(),
        "aiSuggestedRole": new_resume.ai_suggested_role,
        "currentUserTargetRole": current_user.target_role
    }


@router.get("/current")
def get_current_resume(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the authenticated candidate's active resume."""
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.id.desc()).first()

    if not resume:
        return {"success": True, "resume": None}

    return {"success": True, "resume": resume.to_dict()}


@router.get("/{resume_id}")
def get_resume_by_id(
    resume_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves a specific resume, enforcing strict candidate data isolation."""
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or unauthorized."
        )

    return {"success": True, "resume": resume.to_dict()}
