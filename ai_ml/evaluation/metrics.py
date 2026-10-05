"""
Multimodal Feature Extraction Module
------------------------------------
Extracts structured numerical and categorical features across all interview modalities:
1. Technical Interview Performance
2. HR / Behavioral NLP Evaluation
3. Computer Vision Observable Behavior
4. Speech & Acoustic Delivery
5. Resume-JD Skill Match Alignment

Handles missing, partial, or unrecorded modalities gracefully without throwing errors.
"""

from typing import Dict, Any, Optional, List


class MultimodalFeatureExtractor:
    """
    Extracts standardized raw feature dictionaries across available modalities.
    """

    @staticmethod
    def extract_features(
        technical_results: Optional[Dict[str, Any]] = None,
        hr_results: Optional[Dict[str, Any]] = None,
        cv_results: Optional[Dict[str, Any]] = None,
        speech_results: Optional[Dict[str, Any]] = None,
        resume_jd_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extracts structured raw features and identifies modality availability.
        """
        # Determine modality presence
        # Note: In hr_results, camera_analysis and speech_analysis may be nested
        cv_data = cv_results
        speech_data = speech_results
        if hr_results and isinstance(hr_results, dict):
            if cv_data is None and hr_results.get("camera_analysis"):
                cv_data = hr_results["camera_analysis"]
            if speech_data is None and hr_results.get("speech_analysis"):
                speech_data = hr_results["speech_analysis"]

        has_tech = bool(technical_results and isinstance(technical_results, dict) and len(technical_results) > 0)
        has_hr = bool(hr_results and isinstance(hr_results, dict) and "overall_hr_score" in hr_results)
        has_cv = bool(cv_data and isinstance(cv_data, dict) and (cv_data.get("face_visibility_percentage") is not None or cv_data.get("reliability_status")))
        has_speech = bool(speech_data and isinstance(speech_data, dict) and (speech_data.get("speaking_rate_wpm") is not None or speech_data.get("pause_count") is not None))
        has_resume_jd = bool(
            (resume_jd_results and isinstance(resume_jd_results, dict) and "job_match_score" in resume_jd_results) or
            (technical_results and isinstance(technical_results, dict) and "job_match_score" in technical_results)
        )

        features: Dict[str, Any] = {
            "availability": {
                "technical": has_tech,
                "hr_nlp": has_hr,
                "computer_vision": has_cv,
                "speech": has_speech,
                "resume_jd": has_resume_jd
            },
            "technical": {},
            "hr_nlp": {},
            "computer_vision": {},
            "speech": {},
            "resume_jd": {}
        }

        # 1. Technical Features
        if has_tech:
            t = technical_results
            features["technical"] = {
                "overall_score": float(t.get("overall_technical_score", t.get("average_score", 0.0) * 100)),
                "average_score": float(t.get("average_score", 0.0)),
                "total_questions": int(t.get("total_questions", 0)),
                "strong_topics_count": len(t.get("strong_topics", [])),
                "weak_topics_count": len(t.get("weak_topics", [])),
                "strong_topics": list(t.get("strong_topics", [])),
                "weak_topics": list(t.get("weak_topics", []))
            }

        # 2. HR NLP Features
        if has_hr:
            h = hr_results
            features["hr_nlp"] = {
                "overall_score": float(h.get("overall_hr_score", 0.0)),
                "relevance_score": float(h.get("average_relevance", 0.0)),
                "semantic_similarity": float(h.get("average_semantic_similarity", 0.0)),
                "completeness_score": float(h.get("average_completeness", 0.0)),
                "clarity_score": float(h.get("average_clarity", 0.0)),
                "conciseness_score": float(h.get("average_conciseness", 0.0)),
                "star_score": float(h.get("average_star_score") if h.get("average_star_score") is not None else 70.0),
                "has_star_evaluated": h.get("average_star_score") is not None
            }

        # 3. Computer Vision Features
        if has_cv:
            c = cv_data
            features["computer_vision"] = {
                "face_visibility_percentage": float(c.get("face_visibility_percentage", 0.0)),
                "camera_facing_percentage": float(c.get("camera_facing_percentage", 0.0)),
                "gaze_consistency_percentage": float(c.get("gaze_consistency_percentage", 0.0)),
                "posture_consistency_percentage": float(c.get("posture_consistency_percentage", 0.0)),
                "movement_stability_percentage": float(c.get("movement_stability_percentage", 100.0)),
                "gesture_frequency_percentage": float(c.get("gesture_frequency_percentage", 0.0)),
                "reliability_status": str(c.get("reliability_status", "reliable")).lower(),
                "multiple_faces_detected": bool(c.get("multiple_faces_detected", False))
            }

        # 4. Speech Features
        if has_speech:
            s = speech_data
            features["speech"] = {
                "speaking_rate_wpm": float(s.get("speaking_rate_wpm", 0.0)),
                "pause_count": int(s.get("pause_count", 0)),
                "average_pause_seconds": float(s.get("average_pause_seconds", 0.0)),
                "speech_active_percentage": float(s.get("speech_active_percentage", 0.0)),
                "filler_count": int(s.get("filler_count", 0)),
                "fillers_per_100_words": float(s.get("fillers_per_100_words", 0.0)),
                "energy_consistency_percentage": float(s.get("energy_consistency_percentage", 0.0)),
                "speech_continuity_percentage": float(s.get("speech_continuity_percentage", 0.0))
            }

        # 5. Resume / JD Match Features
        r_jd = resume_jd_results if (resume_jd_results and "job_match_score" in resume_jd_results) else technical_results
        if has_resume_jd and r_jd:
            features["resume_jd"] = {
                "job_match_score": float(r_jd.get("job_match_score", 0.0)),
                "matched_skills": list(r_jd.get("matched_skills", r_jd.get("resume_skills", []))),
                "missing_skills": list(r_jd.get("missing_skills", r_jd.get("weak_topics", []))),
                "matched_count": len(r_jd.get("matched_skills", r_jd.get("resume_skills", []))),
                "missing_count": len(r_jd.get("missing_skills", r_jd.get("weak_topics", [])))
            }

        return features
