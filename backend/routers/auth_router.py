"""
Authentication & Identity Verification Router
============================================
Handles registration, 6-digit email OTP verification, login,
session token generation, and candidate profile retrieval.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import hash_password, verify_password, create_access_token, get_current_user
from services.email_service import email_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------
class SendOtpRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirmPassword: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    yearOfStudy: Optional[str] = None
    graduationYear: Optional[str] = None
    city: Optional[str] = None
    targetRole: Optional[str] = None
    otp: Optional[str] = None
    rememberMe: Optional[bool] = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    rememberMe: Optional[bool] = True


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.post("/send-otp")
def send_registration_otp(req: SendOtpRequest, db: Session = Depends(get_db)):
    """
    Dispatches a secure 6-digit verification code to the candidate's email.
    Enforces duplicate email prevention and rate-limited resend cooldowns.
    """
    clean_email = req.email.strip().lower()

    # 1. Check if an active, already-verified account exists
    existing_user = db.query(models.User).filter(models.User.email == clean_email).first()
    if existing_user and existing_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead."
        )

    now = datetime.utcnow()

    # 2. Check resend cooldown
    if existing_user and existing_user.resend_cooldown_until and existing_user.resend_cooldown_until > now:
        remaining_secs = int((existing_user.resend_cooldown_until - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {max(1, remaining_secs)} seconds before requesting a new code."
        )

    # 3. Generate secure OTP and store hash
    otp_code = email_service.generate_otp()
    otp_hash = email_service.hash_otp(otp_code)
    expires_at = now + timedelta(minutes=5)
    cooldown_until = now + timedelta(seconds=60)

    if existing_user:
        existing_user.otp_hash = otp_hash
        existing_user.otp_expires_at = expires_at
        existing_user.otp_attempts = 0
        existing_user.resend_cooldown_until = cooldown_until
    else:
        # Create unverified user placeholder
        placeholder = models.User(
            email=clean_email,
            password_hash=hash_password(otp_code),  # temporary hash until registration finalized
            full_name="Candidate",
            is_verified=False,
            otp_hash=otp_hash,
            otp_expires_at=expires_at,
            otp_attempts=0,
            resend_cooldown_until=cooldown_until
        )
        db.add(placeholder)

    db.commit()

    # 4. Dispatch email
    dispatch_res = email_service.send_verification_email(clean_email, otp_code)

    return {
        "success": True,
        "message": "Verification code sent to your email.",
        "expiresInMinutes": 5,
        "devOtp": dispatch_res.get("dev_otp")  # Returned in dev mode for smooth automated testing
    }


@router.post("/verify-otp")
def verify_registration_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    """
    Validates candidate's entered 6-digit OTP against the stored cryptographic hash.
    Marks email verification status.
    """
    clean_email = req.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == clean_email).first()

    if not user or not user.otp_hash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending verification found for this email. Please request an OTP first."
        )

    # Check max attempts limit
    if user.otp_attempts >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded. Please request a new verification code."
        )

    # Check expiration
    if not user.otp_expires_at or datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )

    # Verify cryptographic hash
    if not email_service.verify_otp_hash(req.otp, user.otp_hash):
        user.otp_attempts += 1
        db.commit()
        remaining = max(0, 5 - user.otp_attempts)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. {remaining} attempt(s) remaining."
        )

    # Mark verified
    user.is_verified = True
    user.otp_hash = None
    user.otp_expires_at = None
    user.otp_attempts = 0
    db.commit()

    return {
        "success": True,
        "verified": True,
        "message": "Email verified successfully! You may now complete your registration."
    }


@router.post("/register")
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new candidate with verified credentials.
    Enforces password validation, profile attributes, and email verification.
    """
    clean_email = req.email.strip().lower()

    if req.confirmPassword and req.password != req.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password confirmation does not match password."
        )

    existing_user = db.query(models.User).filter(models.User.email == clean_email).first()

    # If user already registered and active
    if existing_user and existing_user.is_verified and existing_user.full_name != "Candidate":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead."
        )

    # If an OTP was provided in the payload, attempt verification
    if req.otp and existing_user and existing_user.otp_hash:
        if email_service.verify_otp_hash(req.otp, existing_user.otp_hash):
            existing_user.is_verified = True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP verification code. Please check and try again."
            )

    # Enforce verified status
    if not existing_user or not existing_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify your email address with the 6-digit code before completing registration."
        )

    # Hash final password
    hashed_pwd = hash_password(req.password)

    # Update or finalize user record
    user = existing_user
    user.password_hash = hashed_pwd
    user.full_name = req.name.strip()
    user.college = req.college.strip() if req.college else None
    user.degree = req.degree.strip() if req.degree else None
    user.department = req.department.strip() if req.department else None
    user.year_of_study = req.yearOfStudy.strip() if req.yearOfStudy else None
    user.graduation_year = req.graduationYear.strip() if req.graduationYear else None
    user.phone = req.phone.strip() if req.phone else None
    user.gender = req.gender.strip() if req.gender else None
    user.dob = req.dob.strip() if req.dob else None
    user.city = req.city.strip() if req.city else None
    user.location = req.city.strip() if req.city else None
    user.target_role = req.targetRole.strip() if req.targetRole else None
    user.is_verified = True
    user.otp_hash = None
    user.otp_expires_at = None

    db.commit()
    db.refresh(user)

    # Ensure profile record exists
    profile = db.query(models.Profile).filter(models.Profile.user_id == user.id).first()
    if not profile:
        profile = models.Profile(
            user_id=user.id,
            avatar_url=f"https://api.dicebear.com/7.x/initials/svg?seed={user.full_name}"
        )
        db.add(profile)
        db.commit()

    # Generate JWT token
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        remember_me=bool(req.rememberMe)
    )

    return {
        "success": True,
        "token": token,
        "user": user.to_dict()
    }


@router.post("/login")
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates candidate with email and password.
    Returns signed session token on success.
    """
    clean_email = req.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == clean_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. No account found with this email."
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Incorrect password."
        )

    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        remember_me=bool(req.rememberMe)
    )

    return {
        "success": True,
        "token": token,
        "user": user.to_dict()
    }


@router.post("/logout")
def logout_user(current_user: models.User = Depends(get_current_user)):
    """Stateless logout confirmation."""
    return {"success": True, "message": "Successfully logged out."}


@router.get("/me")
def get_current_user_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the authenticated candidate's active account details, assessment, and aptitude data."""
    active_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.id.desc()).first()

    active_jd = db.query(models.JobDescription).filter(
        models.JobDescription.user_id == current_user.id,
        models.JobDescription.is_active == True
    ).order_by(models.JobDescription.id.desc()).first()

    latest_assessment = db.query(models.Assessment).filter(
        models.Assessment.user_id == current_user.id
    ).order_by(models.Assessment.id.desc()).first()

    latest_aptitude = db.query(models.AptitudeAttempt).filter(
        models.AptitudeAttempt.user_id == current_user.id,
        models.AptitudeAttempt.status == "completed"
    ).order_by(models.AptitudeAttempt.id.desc()).first()

    history = db.query(models.ProgressAttempt).filter(
        models.ProgressAttempt.user_id == current_user.id
    ).order_by(models.ProgressAttempt.attempt_number.asc()).all()

    user_dict = current_user.to_dict()
    user_dict["resume"] = active_resume.to_dict() if active_resume else None
    user_dict["jobDescription"] = active_jd.to_dict() if active_jd else None
    user_dict["currentAssessment"] = latest_assessment.to_dict() if latest_assessment else None
    user_dict["latestAptitude"] = latest_aptitude.to_dict() if latest_aptitude else None
    user_dict["interviewHistory"] = [h.to_dict() for h in history]

    return {
        "success": True,
        "user": user_dict
    }
