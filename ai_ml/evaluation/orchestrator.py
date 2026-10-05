"""
Master End-to-End Employability Pipeline Orchestrator
---------------------------------------------------
Connects all components of the AI-Powered Multimodal Adaptive Interview platform:
1. Dynamic Resume Parsing & Candidate Profile
2. Job Description Skill Matching & Gap Analysis
3. Adaptive Technical Interview Performance
4. HR / Behavioral STAR Interview Round
5. Computer Vision Observable Behavior Analysis
6. Speech & Acoustic Delivery Analysis
7. Phase 7 Multimodal Fusion & Placement Readiness Estimation
8. Phase 8 Dynamic Learning Roadmap Generation
9. Phase 8 Multi-Attempt Progress Tracking
10. Phase 8 Multi-Format Report Generation (JSON, Markdown, HTML, CSV)

Maintains candidate independence, robust error handling, and strict ethical safeguards.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Resolve internal directories
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]

# Append relevant module directories to sys.path
for sub_dir in ["preprocessing", "nlp", "models", "question_engine", "recomendation", "evaluation", "speech", "computer_vision"]:
    p = str(project_root / "ai_ml" / sub_dir)
    if p not in sys.path:
        sys.path.append(p)

from candidate_profile import build_candidate_profile
from resume_jobmatcher import extract_jd_skills, calculate_skill_match
from skill_gap import SkillGapAnalyzer
from learning_path import LearningPathGenerator
from performance_model import ProgressTracker
from final_report_generator import FinalReportGenerator
from evaluate_model import MultimodalEvaluator


class EmployabilityPipeline:
    """
    Central pipeline orchestrator executing or assembling the entire candidate assessment lifecycle.
    """

    def __init__(
        self,
        reports_dir: Optional[Union[str, Path]] = None,
        history_file: Optional[Union[str, Path]] = None
    ):
        self.gap_analyzer = SkillGapAnalyzer()
        self.roadmap_generator = LearningPathGenerator()
        self.progress_tracker = ProgressTracker(history_file=history_file)
        self.report_generator = FinalReportGenerator(output_dir=reports_dir)
        self.multimodal_evaluator = MultimodalEvaluator()

    def evaluate_candidate(
        self,
        resume_path: Optional[Union[str, Path]] = None,
        job_description: Optional[str] = None,
        technical_results: Optional[Dict[str, Any]] = None,
        hr_results: Optional[Dict[str, Any]] = None,
        cv_results: Optional[Dict[str, Any]] = None,
        speech_results: Optional[Dict[str, Any]] = None,
        resume_jd_results: Optional[Dict[str, Any]] = None,
        aptitude_results: Optional[Dict[str, Any]] = None,
        candidate_id: Optional[str] = None,
        target_role: Optional[str] = None,
        save_reports: bool = True
    ) -> Dict[str, Any]:
        """
        Synthesizes candidate profile, JD alignment, interview modalities,
        roadmap, progress tracking, and final reports.
        """
        # 1. Candidate Profile Extraction (if resume available)
        cand_profile = {}
        candidate_name = candidate_id or "Candidate"
        if resume_path and Path(resume_path).exists():
            try:
                cand_profile = build_candidate_profile(str(resume_path))
                if cand_profile.get("name") and cand_profile["name"] != "Candidate" and not candidate_id:
                    candidate_name = cand_profile["name"]
            except Exception as e:
                print(f"[Warning] Resume parsing error handled: {e}")
                cand_profile = {"name": candidate_name, "skills": [], "education": "", "projects": []}
        else:
            cand_profile = {"name": candidate_name, "skills": [], "education": "", "projects": []}

        # 2. Resume / JD Skill Matching
        if resume_jd_results:
            rjd = resume_jd_results
        elif job_description and cand_profile.get("skills"):
            req_skills = extract_jd_skills(job_description)
            matched_s, missing_s, m_score = calculate_skill_match(cand_profile["skills"], req_skills)
            rjd = {
                "job_match_score": round(m_score, 2),
                "matched_skills": matched_s,
                "missing_skills": missing_s,
                "required_skills": req_skills,
                "target_role": target_role or "Software Engineer"
            }
        else:
            rjd = {
                "job_match_score": 70.0,
                "matched_skills": cand_profile.get("skills", []),
                "missing_skills": [],
                "target_role": target_role or "Software Engineer"
            }

        # 3. Multimodal Assessment & Placement Readiness Fusion (Phase 7)
        multimodal_summary = self.multimodal_evaluator.evaluate(
            technical_results=technical_results,
            hr_results=hr_results,
            cv_results=cv_results,
            speech_results=speech_results,
            resume_jd_results=rjd,
            candidate_id=candidate_name,
            save_results=False  # Handled in Phase 8 unified storage
        )

        component_scores = multimodal_summary.get("component_scores", {})
        weak_topics = list(technical_results.get("weak_topics", [])) if technical_results else []

        # Merge weak aptitude areas into gap detection so roadmap prescribes targeted aptitude practice
        if aptitude_results and aptitude_results.get("weak_topics"):
            for wt in aptitude_results["weak_topics"]:
                topic_title = wt.get("topic") if isinstance(wt, dict) else str(wt)
                if topic_title and f"Aptitude: {topic_title}" not in weak_topics:
                    weak_topics.append(f"Aptitude: {topic_title}")

        if aptitude_results and "overall_score" in aptitude_results:
            component_scores["aptitude"] = aptitude_results["overall_score"]

        # 4. Skill Gap Prioritization (Phase 8)
        skill_gap_analysis = self.gap_analyzer.analyze_gaps(
            required_skills=rjd.get("required_skills", rjd.get("matched_skills", []) + rjd.get("missing_skills", [])),
            matched_skills=rjd.get("matched_skills", []),
            missing_skills=rjd.get("missing_skills", []),
            weak_topics=weak_topics,
            job_role=rjd.get("target_role", "Software Engineer")
        )

        # 5. Dynamic Personalized Learning Roadmap (Phase 8)
        roadmap = self.roadmap_generator.generate_roadmap(
            skill_gap_analysis=skill_gap_analysis,
            component_scores=component_scores,
            duration_weeks=5
        )

        # 6. Longitudinal Progress Tracking (Phase 8)
        progress_data = self.progress_tracker.record_attempt(
            candidate_id=candidate_name,
            assessment_summary=multimodal_summary,
            save=save_reports
        )

        # 7. Visualization Data Preparation for UI
        vis_radar = {
            "technical": component_scores.get("technical", 0.0),
            "hr_nlp": component_scores.get("hr_nlp", 0.0),
            "speech": component_scores.get("speech", 0.0),
            "visual": component_scores.get("computer_vision", 0.0),
            "skill_match": component_scores.get("resume_jd", 0.0),
            "aptitude": aptitude_results.get("overall_score") if aptitude_results else None,
            "overall_readiness": multimodal_summary.get("employability_score", 0.0)
        }

        # Assemble Master Unified Assessment Object
        final_assessment = {
            "timestamp": datetime.now().isoformat(),
            "candidate": {
                "name": candidate_name,
                "education": cand_profile.get("education", ""),
                "skills": cand_profile.get("skills", []),
                "projects": cand_profile.get("projects", []),
                "internships": cand_profile.get("internships", []),
                "certifications": cand_profile.get("certifications", [])
            },
            "job_alignment": {
                "target_role": rjd.get("target_role", "Software Engineer"),
                "match_score": rjd.get("job_match_score", 0.0),
                "matched_skills": rjd.get("matched_skills", []),
                "missing_skills": rjd.get("missing_skills", [])
            },
            "skill_gaps": skill_gap_analysis,
            "aptitude_assessment": aptitude_results or {},
            "technical_assessment": technical_results or {},
            "hr_assessment": hr_results or {},
            "visual_assessment": cv_results or multimodal_summary.get("raw_features", {}).get("computer_vision", {}),
            "speech_assessment": speech_results or multimodal_summary.get("raw_features", {}).get("speech", {}),
            "multimodal_assessment": multimodal_summary,
            "readiness": {
                "score": multimodal_summary.get("employability_score", 0.0),
                "level": multimodal_summary.get("readiness_level", "Developing"),
                "description": multimodal_summary.get("readiness_description", "")
            },
            "strengths": multimodal_summary.get("strengths", []),
            "improvement_areas": multimodal_summary.get("improvement_areas", []),
            "recommendations": multimodal_summary.get("recommendations", []),
            "learning_roadmap": roadmap,
            "progress_tracking": progress_data,
            "visualization_data": {
                "radar_chart": vis_radar,
                "progress_timeline": progress_data.get("timeline", [])
            }
        }

        # 8. Report Generation & Persistence
        if save_reports:
            created_files = self.report_generator.generate_all_reports(
                final_assessment=final_assessment,
                candidate_slug=candidate_name.replace(" ", "_").lower()
            )
            final_assessment["reports"] = created_files
        else:
            final_assessment["reports"] = {}

        return final_assessment


def run_final_employability_pipeline(
    resume_path: Optional[Union[str, Path]] = None,
    job_description: Optional[str] = None,
    technical_results: Optional[Dict[str, Any]] = None,
    hr_results: Optional[Dict[str, Any]] = None,
    cv_results: Optional[Dict[str, Any]] = None,
    speech_results: Optional[Dict[str, Any]] = None,
    resume_jd_results: Optional[Dict[str, Any]] = None,
    aptitude_results: Optional[Dict[str, Any]] = None,
    candidate_id: Optional[str] = None,
    target_role: Optional[str] = None,
    save_reports: bool = True
) -> Dict[str, Any]:
    """
    Convenience function providing a top-level programmatic interface to the Phase 8 pipeline.
    """
    pipeline = EmployabilityPipeline()
    return pipeline.evaluate_candidate(
        resume_path=resume_path,
        job_description=job_description,
        technical_results=technical_results,
        hr_results=hr_results,
        cv_results=cv_results,
        speech_results=speech_results,
        resume_jd_results=resume_jd_results,
        aptitude_results=aptitude_results,
        candidate_id=candidate_id,
        target_role=target_role,
        save_reports=save_reports
    )
