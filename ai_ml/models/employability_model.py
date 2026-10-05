"""
Multimodal Employability Assessment & Fusion Model
--------------------------------------------------
Performs:
1. Feature normalization across disparate metric scales (scores, WPM, pauses, fillers).
2. Configurable weighted multimodal fusion.
3. Automatic missing-modality detection and dynamic weight renormalization.
4. Placement readiness classification and confidence estimation.

IMPORTANT:
- Does NOT claim to predict actual hiring decisions or guarantee job offers.
- Does NOT diagnose psychological states, true confidence, personality, or deception.
- Uses strictly observable performance proxies and transparent, calibrated fusion logic.
"""

import math
from typing import Dict, Any, Optional, List, Tuple

DEFAULT_MODALITY_WEIGHTS = {
    "technical": 0.30,
    "hr_nlp": 0.25,
    "speech": 0.15,
    "computer_vision": 0.15,
    "resume_jd": 0.15
}

DEFAULT_READINESS_THRESHOLDS = [
    (85.0, "Highly Ready", "Demonstrates strong, consistent readiness across evaluated dimensions."),
    (70.0, "Ready", "Demonstrates solid core competence with minor refinement opportunities."),
    (55.0, "Developing", "Demonstrates foundational capabilities with clear target areas for improvement."),
    (40.0, "Needs Improvement", "Shows emerging skills requiring structured practice across core areas."),
    (0.0, "Early Stage", "Requires foundational preparation and technical/communication practice.")
]


class EmployabilityModel:
    """
    Transparent, calibrated multimodal fusion and employability assessment model.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        readiness_thresholds: Optional[List[Tuple[float, str, str]]] = None
    ):
        self.weights = dict(weights or DEFAULT_MODALITY_WEIGHTS)
        self.thresholds = list(readiness_thresholds or DEFAULT_READINESS_THRESHOLDS)
        # Ensure thresholds are sorted descending
        self.thresholds.sort(key=lambda x: x[0], reverse=True)

    # --------------------------------------------------------
    # 1. FEATURE NORMALIZATION RULES
    # --------------------------------------------------------

    @staticmethod
    def normalize_technical(raw_tech: Dict[str, Any]) -> float:
        """
        Normalizes technical interview score to [0.0, 1.0].
        Direction: Higher is better.
        """
        if not raw_tech:
            return 0.0
        score = raw_tech.get("overall_score", 0.0)
        return max(0.0, min(1.0, score / 100.0))

    @staticmethod
    def normalize_hr_nlp(raw_hr: Dict[str, Any]) -> float:
        """
        Normalizes HR NLP score from relevance, semantic similarity, completeness, clarity, conciseness, and STAR.
        Direction: Higher is better.
        """
        if not raw_hr:
            return 0.0

        if "overall_score" in raw_hr:
            return max(0.0, min(1.0, raw_hr["overall_score"] / 100.0))

        # Composite fallback from dimensions if overall not present
        rel = raw_hr.get("relevance_score", 50.0) / 100.0
        comp = raw_hr.get("completeness_score", 50.0) / 100.0
        clar = raw_hr.get("clarity_score", 50.0) / 100.0
        conc = raw_hr.get("conciseness_score", 50.0) / 100.0
        star = raw_hr.get("star_score", 70.0) / 100.0

        score = (rel * 0.25) + (comp * 0.25) + (clar * 0.20) + (conc * 0.15) + (star * 0.15)
        return max(0.0, min(1.0, score))

    @staticmethod
    def normalize_computer_vision(raw_cv: Dict[str, Any]) -> float:
        """
        Normalizes observable visual behavior features to [0.0, 1.0].
        Evaluates face visibility, camera orientation, posture consistency, and movement stability.
        Direction: Higher is better.
        """
        if not raw_cv:
            return 0.0

        face_vis = raw_cv.get("face_visibility_percentage", 0.0) / 100.0
        cam_facing = raw_cv.get("camera_facing_percentage", 0.0) / 100.0
        posture = raw_cv.get("posture_consistency_percentage", 0.0) / 100.0
        stability = raw_cv.get("movement_stability_percentage", 100.0) / 100.0

        # Hand gesture activity: moderate activity (15-50%) is standard; 0% is calm; excessive >80% is slightly penalized
        gest_raw = raw_cv.get("gesture_frequency_percentage", 0.0)
        if gest_raw <= 60.0:
            gesture_score = 1.0
        else:
            gesture_score = max(0.60, 1.0 - ((gest_raw - 60.0) / 100.0))

        cv_composite = (face_vis * 0.30) + (cam_facing * 0.25) + (posture * 0.25) + (stability * 0.15) + (gesture_score * 0.05)

        # Reliability discount if multiple faces detected
        if raw_cv.get("multiple_faces_detected") or raw_cv.get("reliability_status") == "unreliable":
            cv_composite *= 0.70

        return max(0.0, min(1.0, cv_composite))

    @staticmethod
    def normalize_speech(raw_speech: Dict[str, Any]) -> float:
        """
        Normalizes acoustic and verbal delivery features to [0.0, 1.0].
        Pacing (WPM): optimal 120-160 WPM.
        Filler density: lower is better (0 fillers -> 1.0, 10+ fillers/100 words -> 0.0).
        Pauses: optimal average pause 0.5-1.0s; excessive pauses penalize.
        Energy and continuity: higher is better.
        """
        if not raw_speech:
            return 0.0

        # 1. Speaking rate (WPM)
        wpm = raw_speech.get("speaking_rate_wpm", 0.0)
        if wpm <= 0.0:
            wpm_score = 0.50
        elif 110.0 <= wpm <= 165.0:
            wpm_score = 1.0
        elif wpm < 110.0:
            wpm_score = max(0.20, wpm / 110.0)
        else:
            wpm_score = max(0.20, 1.0 - ((wpm - 165.0) / 100.0))

        # 2. Filler density per 100 words (lower is better)
        fillers = raw_speech.get("fillers_per_100_words", 0.0)
        filler_score = max(0.0, min(1.0, 1.0 - (fillers / 10.0)))

        # 3. Average pause duration
        avg_pause = raw_speech.get("average_pause_seconds", 0.0)
        if avg_pause <= 0.90:
            pause_score = 1.0
        else:
            pause_score = max(0.10, min(1.0, 1.0 - ((avg_pause - 0.90) / 2.5)))

        # 4. Energy consistency & speech continuity
        energy_score = raw_speech.get("energy_consistency_percentage", 80.0) / 100.0
        continuity_score = raw_speech.get("speech_continuity_percentage", 75.0) / 100.0

        speech_composite = (
            (wpm_score * 0.25) +
            (filler_score * 0.25) +
            (pause_score * 0.20) +
            (energy_score * 0.15) +
            (continuity_score * 0.15)
        )
        return max(0.0, min(1.0, speech_composite))

    @staticmethod
    def normalize_resume_jd(raw_rjd: Dict[str, Any]) -> float:
        """
        Normalizes resume-JD skill match score to [0.0, 1.0].
        Direction: Higher is better.
        """
        if not raw_rjd:
            return 0.0
        score = raw_rjd.get("job_match_score", 0.0)
        return max(0.0, min(1.0, score / 100.0))

    # --------------------------------------------------------
    # 2. MULTIMODAL FUSION & DYNAMIC WEIGHT RENORMALIZATION
    # --------------------------------------------------------

    def fuse_modalities(self, raw_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs missing-modality detection, weight renormalization,
        and weighted linear fusion into an overall placement readiness estimate.
        """
        avail = raw_features.get("availability", {})
        active_modalities = [m for m, is_avail in avail.items() if is_avail]

        # Calculate normalized scores for each modality
        norm_scores: Dict[str, float] = {}
        if avail.get("technical"):
            norm_scores["technical"] = self.normalize_technical(raw_features.get("technical", {}))
        if avail.get("hr_nlp"):
            norm_scores["hr_nlp"] = self.normalize_hr_nlp(raw_features.get("hr_nlp", {}))
        if avail.get("computer_vision"):
            norm_scores["computer_vision"] = self.normalize_computer_vision(raw_features.get("computer_vision", {}))
        if avail.get("speech"):
            norm_scores["speech"] = self.normalize_speech(raw_features.get("speech", {}))
        if avail.get("resume_jd"):
            norm_scores["resume_jd"] = self.normalize_resume_jd(raw_features.get("resume_jd", {}))

        # Handle complete omission edge case
        if not active_modalities or not norm_scores:
            return {
                "employability_score": 0.0,
                "readiness_level": "Early Stage",
                "readiness_description": "No evaluated modality data available.",
                "confidence": 0.0,
                "component_scores": {},
                "active_weights": {},
                "active_modalities": []
            }

        # Dynamic weight renormalization over active modalities
        total_active_weight = sum(self.weights.get(m, 0.0) for m in norm_scores)
        if total_active_weight <= 1e-6:
            # Fallback to equal weighting if custom weights summed to zero
            renorm_weights = {m: 1.0 / len(norm_scores) for m in norm_scores}
        else:
            renorm_weights = {
                m: self.weights.get(m, 0.0) / total_active_weight
                for m in norm_scores
            }

        # Compute fused score
        fused_score_0_1 = sum(norm_scores[m] * renorm_weights[m] for m in norm_scores)
        employability_score = round(max(0.0, min(100.0, fused_score_0_1 * 100.0)), 2)

        # Readiness Level Categorization
        readiness_level = "Early Stage"
        readiness_desc = "Foundational preparation required."
        for min_score, label, desc in self.thresholds:
            if employability_score >= min_score:
                readiness_level = label
                readiness_desc = desc
                break

        # Confidence Estimation: proportion of evaluated modalities (5 total)
        confidence = round(len(norm_scores) / len(DEFAULT_MODALITY_WEIGHTS), 2)

        component_percentages = {
            m: round(norm_scores[m] * 100.0, 1)
            for m in norm_scores
        }

        return {
            "employability_score": employability_score,
            "readiness_level": readiness_level,
            "readiness_description": readiness_desc,
            "confidence": confidence,
            "component_scores": component_percentages,
            "active_weights": {m: round(w, 4) for m, w in renorm_weights.items()},
            "active_modalities": list(norm_scores.keys())
        }
