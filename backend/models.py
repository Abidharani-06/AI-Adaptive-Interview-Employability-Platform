import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    college = Column(String(255), nullable=True)
    degree = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    graduation_year = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Email verification & OTP security
    is_verified = Column(Boolean, default=False)
    otp_hash = Column(String(255), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    otp_attempts = Column(Integer, default=0)
    resend_cooldown_until = Column(DateTime, nullable=True)

    # Detailed candidate profile fields
    gender = Column(String(50), nullable=True)
    dob = Column(String(50), nullable=True)
    year_of_study = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)

    # Target role selected by user. Explicitly None until user picks one!
    target_role = Column(String(255), nullable=True, default=None)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    aptitude_attempts = relationship("AptitudeAttempt", back_populates="user", cascade="all, delete-orphan", order_by="AptitudeAttempt.id.desc()")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")
    progress_attempts = relationship("ProgressAttempt", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.full_name,
            "full_name": self.full_name,
            "isVerified": bool(self.is_verified),
            "college": self.college or "",
            "degree": self.degree or "",
            "department": self.department or "",
            "graduationYear": self.graduation_year or "",
            "yearOfStudy": self.year_of_study or "",
            "phone": self.phone or "",
            "gender": self.gender or "",
            "dob": self.dob or "",
            "city": self.city or "",
            "location": self.location or self.city or "",
            "targetRole": self.target_role,  # None if not chosen
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    skills_json = Column(Text, nullable=True)  # JSON serialized list
    projects_json = Column(Text, nullable=True)  # JSON serialized list
    internships_json = Column(Text, nullable=True)
    certifications_json = Column(Text, nullable=True)
    education_text = Column(String(500), nullable=True)

    user = relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "bio": self.bio or "",
            "avatarUrl": self.avatar_url or "",
            "skills": json.loads(self.skills_json) if self.skills_json else [],
            "projects": json.loads(self.projects_json) if self.projects_json else [],
            "internships": json.loads(self.internships_json) if self.internships_json else [],
            "certifications": json.loads(self.certifications_json) if self.certifications_json else [],
            "education": self.education_text or ""
        }


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=True)
    extracted_name = Column(String(255), nullable=True)
    extracted_education = Column(String(500), nullable=True)
    extracted_department = Column(String(255), nullable=True)
    extracted_skills_json = Column(Text, nullable=True)
    extracted_projects_json = Column(Text, nullable=True)
    extracted_internships_json = Column(Text, nullable=True)
    extracted_certifications_json = Column(Text, nullable=True)
    ai_suggested_role = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")

    def to_dict(self):
        return {
            "id": self.id,
            "fileName": self.filename,
            "uploadedAt": self.created_at.strftime("%Y-%m-%d") if self.created_at else None,
            "candidateName": self.extracted_name,
            "education": self.extracted_education,
            "department": self.extracted_department,
            "skills": json.loads(self.extracted_skills_json) if self.extracted_skills_json else [],
            "projects": json.loads(self.extracted_projects_json) if self.extracted_projects_json else [],
            "internships": json.loads(self.extracted_internships_json) if self.extracted_internships_json else [],
            "certifications": json.loads(self.extracted_certifications_json) if self.extracted_certifications_json else [],
            "aiSuggestedRole": self.ai_suggested_role
        }


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description_text = Column(Text, nullable=False)
    required_skills_json = Column(Text, nullable=True)
    matched_skills_json = Column(Text, nullable=True)
    missing_skills_json = Column(Text, nullable=True)
    match_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="job_descriptions")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.description_text,
            "requiredSkills": json.loads(self.required_skills_json) if self.required_skills_json else [],
            "matchedSkills": json.loads(self.matched_skills_json) if self.matched_skills_json else [],
            "missingSkills": json.loads(self.missing_skills_json) if self.missing_skills_json else [],
            "matchScore": round(self.match_score, 1)
        }


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    round_id = Column(String(100), default="full")
    round_type = Column(String(255), default="Full Mock Interview")
    target_role = Column(String(255), nullable=False)
    difficulty = Column(String(50), default="adaptive")
    question_count = Column(Integer, default=5)
    enable_camera = Column(Boolean, default=True)
    enable_microphone = Column(Boolean, default=True)
    status = Column(String(50), default="in_progress")  # in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.order_index")
    answers = relationship("InterviewAnswer", back_populates="session", cascade="all, delete-orphan")
    assessment = relationship("Assessment", back_populates="session", uselist=False)
    aptitude_attempt = relationship("AptitudeAttempt", back_populates="session", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "roundId": self.round_id,
            "roundType": self.round_type,
            "targetRole": self.target_role,
            "difficulty": self.difficulty,
            "questionCount": self.question_count,
            "enableCamera": self.enable_camera,
            "enableMicrophone": self.enable_microphone,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "questions": [q.to_dict() for q in self.questions]
        }


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, default=0)
    question_text = Column(Text, nullable=False)
    category = Column(String(255), nullable=True)
    question_type = Column(String(100), nullable=True)
    difficulty = Column(String(50), default="Medium")
    hint = Column(Text, nullable=True)
    expected_keywords = Column(Text, nullable=True)
    expected_answer = Column(Text, nullable=True)
    topic = Column(String(255), nullable=True)

    session = relationship("InterviewSession", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question_text,
            "category": self.category or "Technical Core",
            "type": self.question_type or "Adaptive",
            "difficulty": self.difficulty,
            "hint": self.hint or "",
            "topic": self.topic or ""
        }


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, nullable=True)
    question_text = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    answer_text = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="answers")

    def to_dict(self):
        return {
            "id": self.id,
            "questionId": self.question_id,
            "question": self.question_text,
            "category": self.category,
            "answer": self.answer_text,
            "wordCount": self.word_count,
            "score": self.score,
            "feedback": self.feedback
        }


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=True)
    overall_score = Column(Float, nullable=False)
    readiness_level = Column(String(100), nullable=False)
    readiness_description = Column(Text, nullable=True)
    technical_score = Column(Float, nullable=True)
    hr_score = Column(Float, nullable=True)
    speech_score = Column(Float, nullable=True)
    cv_score = Column(Float, nullable=True)
    resume_jd_score = Column(Float, nullable=True)
    strengths_json = Column(Text, nullable=True)
    improvement_areas_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    component_scores_json = Column(Text, nullable=True)
    raw_assessment_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assessments")
    session = relationship("InterviewSession", back_populates="assessment")

    def to_dict(self):
        if self.raw_assessment_json:
            try:
                data = json.loads(self.raw_assessment_json)
                data["id"] = self.id
                data["sessionId"] = self.session_id
                return data
            except Exception:
                pass

        return {
            "id": self.id,
            "sessionId": self.session_id,
            "readiness": {
                "score": round(self.overall_score, 1),
                "level": self.readiness_level,
                "description": self.readiness_description or ""
            },
            "multimodal_assessment": {
                "employability_score": round(self.overall_score, 1),
                "readiness_level": self.readiness_level,
                "readiness_description": self.readiness_description,
                "component_scores": json.loads(self.component_scores_json) if self.component_scores_json else {
                    "technical": self.technical_score,
                    "hr_nlp": self.hr_score,
                    "speech": self.speech_score,
                    "computer_vision": self.cv_score,
                    "resume_jd": self.resume_jd_score
                }
            },
            "strengths": json.loads(self.strengths_json) if self.strengths_json else [],
            "improvement_areas": json.loads(self.improvement_areas_json) if self.improvement_areas_json else [],
            "recommendations": json.loads(self.recommendations_json) if self.recommendations_json else [],
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, nullable=True)
    skill = Column(String(255), nullable=False)
    priority = Column(String(50), nullable=False)  # HIGH, MEDIUM, LOW
    reason = Column(Text, nullable=True)
    is_core = Column(Boolean, default=False)
    status = Column(String(50), default="open")  # open, resolved
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="skill_gaps")

    def to_dict(self):
        return {
            "id": self.id,
            "skill": self.skill,
            "priority": self.priority,
            "reason": self.reason or "",
            "is_core": self.is_core,
            "status": self.status
        }


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, nullable=True)
    duration_weeks = Column(Integer, default=5)
    total_estimated_hours = Column(Integer, default=80)
    weekly_action_plan_json = Column(Text, nullable=False)
    learning_modules_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roadmaps")

    def to_dict(self):
        return {
            "id": self.id,
            "duration_weeks": self.duration_weeks,
            "total_estimated_hours": self.total_estimated_hours,
            "weekly_action_plan": json.loads(self.weekly_action_plan_json) if self.weekly_action_plan_json else [],
            "learning_modules": json.loads(self.learning_modules_json) if self.learning_modules_json else []
        }


class ProgressAttempt(Base):
    __tablename__ = "progress_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, nullable=True)
    attempt_number = Column(Integer, nullable=False)
    date_str = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    readiness_level = Column(String(100), nullable=False)
    score_delta_previous = Column(Float, default=0.0)
    component_scores_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_attempts")

    def to_dict(self):
        return {
            "id": self.id,
            "attempt": self.attempt_number,
            "date": self.date_str,
            "score": round(self.score, 1),
            "readiness_level": self.readiness_level,
            "delta": round(self.score_delta_previous, 1) if self.score_delta_previous is not None else 0.0,
            "component_scores": json.loads(self.component_scores_json) if self.component_scores_json else {}
        }


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, nullable=True)
    report_type = Column(String(50), nullable=False)  # json, markdown, html, csv
    file_path = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reports")

    def to_dict(self):
        return {
            "id": self.id,
            "reportType": self.report_type,
            "filePath": self.file_path,
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }


class AptitudeAttempt(Base):
    __tablename__ = "aptitude_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True)

    total_questions = Column(Integer, default=15)
    attempted_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    overall_score = Column(Float, default=0.0)
    quantitative_score = Column(Float, default=0.0)
    reasoning_score = Column(Float, default=0.0)
    verbal_score = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    total_time_seconds = Column(Float, default=0.0)

    # Detailed serialized diagnostics
    strong_topics_json = Column(Text, nullable=True)
    weak_topics_json = Column(Text, nullable=True)
    difficulty_performance_json = Column(Text, nullable=True)
    section_details_json = Column(Text, nullable=True)
    roadmap_inputs_json = Column(Text, nullable=True)
    diagnostic_summary_json = Column(Text, nullable=True)

    # Evaluation key store for validation during test taking
    evaluation_keys_json = Column(Text, nullable=True)

    status = Column(String(50), default="in_progress")  # in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="aptitude_attempts")
    session = relationship("InterviewSession", back_populates="aptitude_attempt")
    answer_logs = relationship("AptitudeAnswerLog", back_populates="attempt", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "sessionId": self.session_id,
            "overallScore": round(self.overall_score, 1),
            "quantitativeScore": round(self.quantitative_score, 1),
            "reasoningScore": round(self.reasoning_score, 1),
            "verbalScore": round(self.verbal_score, 1),
            "accuracy": round(self.accuracy, 1),
            "totalQuestions": self.total_questions,
            "attemptedCount": self.attempted_count,
            "unattemptedCount": max(0, self.total_questions - self.attempted_count),
            "correctCount": self.correct_count,
            "averageResponseTime": round(self.average_response_time, 1),
            "totalTimeSeconds": round(self.total_time_seconds, 1),
            "strongTopics": json.loads(self.strong_topics_json) if self.strong_topics_json else [],
            "weakTopics": json.loads(self.weak_topics_json) if self.weak_topics_json else [],
            "difficultyPerformance": json.loads(self.difficulty_performance_json) if self.difficulty_performance_json else {},
            "sections": json.loads(self.section_details_json) if self.section_details_json else {},
            "diagnosticSummary": json.loads(self.diagnostic_summary_json) if self.diagnostic_summary_json else [],
            "roadmapInputs": json.loads(self.roadmap_inputs_json) if self.roadmap_inputs_json else {},
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None
        }


class AptitudeAnswerLog(Base):
    __tablename__ = "aptitude_answer_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attempt_id = Column(Integer, ForeignKey("aptitude_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(100), nullable=False)
    section = Column(String(100), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="Medium")
    selected_option = Column(String(500), nullable=True)
    correct_answer = Column(String(500), nullable=True)
    is_correct = Column(Boolean, default=False)
    is_attempted = Column(Boolean, default=False)
    time_taken_seconds = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)

    attempt = relationship("AptitudeAttempt", back_populates="answer_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "questionId": self.question_id,
            "section": self.section,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "selectedOption": self.selected_option,
            "correctAnswer": self.correct_answer,
            "isCorrect": self.is_correct,
            "isAttempted": self.is_attempted,
            "timeTakenSeconds": round(self.time_taken_seconds, 1),
            "explanation": self.explanation
        }

