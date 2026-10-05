"""
Recommendation & Explainability Engine
--------------------------------------
Generates transparent, observable explanations (Strengths & Areas for Improvement)
and candidate-specific actionable recommendations across all interview modalities.

IMPORTANT:
- Strict Ethical Compliance: Contains NO psychological assumptions (no claims of nervousness, anxiety, or confidence).
- Fully Dynamic: Explanations and recommendations are directly derived from actual candidate metrics, missing skills, and weak topics.
"""

from typing import Dict, List, Any, Optional


class RecommendationEngine:
    """
    Produces explainable assessments and tailored improvement recommendations.
    """

    @staticmethod
    def generate_assessment(
        raw_features: Dict[str, Any],
        component_scores: Dict[str, float],
        employability_score: float,
        readiness_level: str
    ) -> Dict[str, Any]:
        """
        Synthesizes strengths, areas for improvement, and actionable recommendations.
        """
        strengths: List[str] = []
        improvements: List[str] = []
        recommendations: List[str] = []

        tech = raw_features.get("technical", {})
        hr = raw_features.get("hr_nlp", {})
        cv = raw_features.get("computer_vision", {})
        speech = raw_features.get("speech", {})
        rjd = raw_features.get("resume_jd", {})

        # ----------------------------------------------------
        # 1. Technical Evaluation Breakdown
        # ----------------------------------------------------
        if "technical" in component_scores:
            t_score = component_scores["technical"]
            weak_topics = tech.get("weak_topics", [])
            strong_topics = tech.get("strong_topics", [])

            if t_score >= 70.0:
                strengths.append(f"Strong overall technical problem solving ({t_score:.1f}%).")
                if strong_topics:
                    strengths.append(f"Demonstrated solid mastery in: {', '.join(strong_topics[:3])}.")
            else:
                improvements.append(f"Technical interview performance scored below target ({t_score:.1f}%).")
                if weak_topics:
                    improvements.append(f"Identified conceptual gaps in: {', '.join(weak_topics[:3])}.")
                    recommendations.append(f"Prioritize focused coding and architectural review for: {', '.join(weak_topics[:3])}.")
                else:
                    recommendations.append("Strengthen core data structures and algorithmic complexity analysis.")

        # ----------------------------------------------------
        # 2. Resume / JD Skill Match Breakdown
        # ----------------------------------------------------
        if "resume_jd" in component_scores:
            m_score = component_scores["resume_jd"]
            missing_skills = rjd.get("missing_skills", [])
            matched_skills = rjd.get("matched_skills", [])

            if m_score >= 70.0:
                strengths.append(f"High resume-to-role alignment with job description ({m_score:.1f}% match).")
            else:
                improvements.append(f"Resume shows noticeable skill gaps against job requirements ({m_score:.1f}% match).")
                if missing_skills:
                    improvements.append(f"Key missing skills detected: {', '.join(missing_skills[:4])}.")
                    recommendations.append(f"Acquire hands-on project experience in target skills: {', '.join(missing_skills[:4])}.")

        # ----------------------------------------------------
        # 3. HR NLP Verbal Communication Breakdown
        # ----------------------------------------------------
        if "hr_nlp" in component_scores:
            hr_score = component_scores["hr_nlp"]
            rel = hr.get("relevance_score", 0.0)
            comp = hr.get("completeness_score", 0.0)
            clar = hr.get("clarity_score", 0.0)
            conc = hr.get("conciseness_score", 0.0)
            star = hr.get("star_score", 0.0)

            if hr_score >= 75.0:
                strengths.append(f"Clear and structured behavioral communication ({hr_score:.1f}%).")
            if rel >= 75.0:
                strengths.append("High direct answer relevance to interview prompts.")
            elif rel < 65.0:
                improvements.append("Responses occasionally drifted from the core question focus.")
                recommendations.append("Practice directly answering the specific interview prompt before adding broader context.")

            if comp < 65.0:
                improvements.append("Several responses lacked thorough elaboration or specific examples.")
                recommendations.append("Structure behavioral responses using the STAR method (Situation, Task, Action, Result).")

            if conc < 50.0:
                improvements.append("Responses exhibited wordiness with opportunity for greater precision.")
                recommendations.append("Practice concise delivery by limiting introductory framing and focusing on concrete actions.")

        # ----------------------------------------------------
        # 4. Speech Delivery & Acoustic Pacing Breakdown
        # ----------------------------------------------------
        if "speech" in component_scores:
            sp_score = component_scores["speech"]
            wpm = speech.get("speaking_rate_wpm", 0.0)
            fillers = speech.get("fillers_per_100_words", 0.0)
            avg_pause = speech.get("average_pause_seconds", 0.0)
            energy_cons = speech.get("energy_consistency_percentage", 0.0)

            if 115.0 <= wpm <= 165.0:
                strengths.append(f"Natural conversational speaking rate maintained ({wpm:.1f} WPM).")
            elif wpm > 175.0:
                improvements.append(f"Speaking rate was unusually rapid ({wpm:.1f} WPM).")
                recommendations.append("Moderate speaking pace to approximately 130–150 WPM for maximum clarity.")
            elif 0.0 < wpm < 100.0:
                improvements.append(f"Speaking rate was relatively slow with extended pauses ({wpm:.1f} WPM).")
                recommendations.append("Practice fluid transition phrases to sustain a conversational pace.")

            if fillers <= 1.5:
                strengths.append(f"Minimal filler word density observed ({fillers:.1f} per 100 words).")
            elif fillers >= 4.0:
                improvements.append(f"Noticeable filler word density detected ({fillers:.1f} per 100 words).")
                recommendations.append("Incorporate brief silent pauses instead of verbal fillers ('um', 'like', 'actually') when organizing thoughts.")

            if avg_pause >= 2.0:
                improvements.append(f"Extended pauses detected between spoken phrases (avg: {avg_pause:.1f}s).")
                recommendations.append("Prepare standard narrative anchors in advance to reduce intra-sentence pauses.")

            if energy_cons >= 80.0:
                strengths.append("Consistent vocal volume and steady speech energy maintained throughout.")

        # ----------------------------------------------------
        # 5. Computer Vision & Observable Behavior Breakdown
        # ----------------------------------------------------
        if "computer_vision" in component_scores:
            cv_score = component_scores["computer_vision"]
            face_vis = cv.get("face_visibility_percentage", 0.0)
            cam_facing = cv.get("camera_facing_percentage", 0.0)
            posture = cv.get("posture_consistency_percentage", 0.0)
            stability = cv.get("movement_stability_percentage", 100.0)

            if face_vis >= 85.0 and cam_facing >= 75.0:
                strengths.append(f"Consistent camera orientation and visual engagement maintained ({cam_facing:.1f}%).")
            elif cam_facing < 60.0:
                improvements.append(f"Gaze and head orientation were frequently directed away from the camera ({cam_facing:.1f}%).")
                recommendations.append("Maintain observable eye alignment toward the camera lens during virtual responses.")

            if posture >= 80.0:
                strengths.append("Consistently upright upper-body posture and shoulder alignment.")
            elif posture < 65.0:
                improvements.append("Noticeable shoulder tilt or lateral leaning observed across frames.")
                recommendations.append("Ensure webcam is at eye level and maintain centered, upright seated posture.")

            if stability < 70.0:
                improvements.append("Frequent physical position adjustments and body displacement detected.")
                recommendations.append("Maintain a stable seated position with grounded posture during responses.")

        # Fallback if lists are short
        if not strengths:
            strengths.append("Candidate completed the interview assessment with recorded data.")
        if not recommendations:
            recommendations.append("Continue regular technical practice and mock interview rehearsal.")

        return {
            "strengths": strengths,
            "improvement_areas": improvements,
            "recommendations": recommendations
        }
