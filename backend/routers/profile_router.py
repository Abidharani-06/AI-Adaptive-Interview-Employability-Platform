from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/profile", tags=["Profile"])


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    graduationYear: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    targetRole: Optional[str] = None
    bio: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str


@router.get("")
def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full profile details for the authenticated user."""
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    
    active_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.id.desc()).first()

    return {
        "success": True,
        "user": current_user.to_dict(),
        "profile": profile.to_dict() if profile else {},
        "resume": active_resume.to_dict() if active_resume else None
    }


@router.put("")
def update_profile(
    req: UpdateProfileRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile information for the authenticated user only."""
    if req.name is not None and req.name.strip():
        current_user.full_name = req.name.strip()
    if req.college is not None:
        current_user.college = req.college.strip()
    if req.degree is not None:
        current_user.degree = req.degree.strip()
    if req.department is not None:
        current_user.department = req.department.strip()
    if req.graduationYear is not None:
        current_user.graduation_year = req.graduationYear.strip()
    if req.phone is not None:
        current_user.phone = req.phone.strip()
    if req.location is not None:
        current_user.location = req.location.strip()
    if req.targetRole is not None:
        current_user.target_role = req.targetRole.strip()

    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if profile and req.bio is not None:
        profile.bio = req.bio.strip()

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": current_user.to_dict()
    }


@router.put("/password")
def change_password(
    req: ChangePasswordRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Securely update the candidate's password."""
    if not verify_password(req.oldPassword, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )

    if len(req.newPassword) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long."
        )

    current_user.password_hash = hash_password(req.newPassword)
    db.commit()

    return {"success": True, "message": "Password changed successfully."}
