"""
Master Multimodal Evaluator & Assessment Orchestrator
----------------------------------------------------
Coordinates multimodal feature extraction, normalization, weighted fusion,
placement readiness estimation, explainable recommendations, and persistent storage.

Supports any combination of available modalities (Technical, HR NLP, CV, Speech, Resume/JD).
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Resolve internal imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]

models_dir = str(project_root / "ai_ml" / "models")
if models_dir not in sys.path:
    sys.path.append(models_dir)

rec_dir = str(project_root / "ai_ml" / "recomendation")
if rec_dir not in sys.path:
    sys.path.append(rec_dir)

if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from metrics import MultimodalFeatureExtractor
from employability_model import EmployabilityModel
from recommendation_engine import RecommendationEngine


class MultimodalEvaluator:
    """
    Central evaluator producing end-to-end multimodal employability assessments.
    """

    def __init__(
        self,
        custom_weights: Optional[Dict[str, float]] = None,
        results_dir: Optional[Union[str, Path]] = None
    ):
        self.model = EmployabilityModel(weights=custom_weights)
        self.results_dir = Path(results_dir or (project_root / "results"))
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.results_dir / "employability_assessments.json"

    def evaluate(
        self,
        technical_results: Optional[Dict[str, Any]] = None,
        hr_results: Optional[Dict[str, Any]] = None,
        cv_results: Optional[Dict[str, Any]] = None,
        speech_results: Optional[Dict[str, Any]] = None,
        resume_jd_results: Optional[Dict[str, Any]] = None,
        candidate_id: Optional[str] = None,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete multimodal employability assessment pipeline.
        """
        # Step 1: Feature Extraction
        raw_features = MultimodalFeatureExtractor.extract_features(
            technical_results=technical_results,
            hr_results=hr_results,
            cv_results=cv_results,
            speech_results=speech_results,
            resume_jd_results=resume_jd_results
        )

        # Step 2: Multimodal Weighted Fusion & Readiness Prediction
        fusion_result = self.model.fuse_modalities(raw_features)

        employability_score = fusion_result["employability_score"]
        readiness_level = fusion_result["readiness_level"]
        component_scores = fusion_result["component_scores"]

        # Step 3: Explainable Assessment & Personalized Recommendations
        assessment_exp = RecommendationEngine.generate_assessment(
            raw_features=raw_features,
            component_scores=component_scores,
            employability_score=employability_score,
            readiness_level=readiness_level
        )

        # Derive candidate identifier
        c_id = candidate_id
        if not c_id:
            if hr_results and hr_results.get("candidate_name"):
                c_id = hr_results["candidate_name"]
            elif technical_results and technical_results.get("candidate_resume"):
                c_id = technical_results["candidate_resume"]
            else:
                c_id = "Candidate"

        summary = {
            "candidate_id": c_id,
            "timestamp": datetime.now().isoformat(),
            "employability_score": employability_score,
            "readiness_level": readiness_level,
            "readiness_description": fusion_result["readiness_description"],
            "confidence": fusion_result["confidence"],
            "component_scores": component_scores,
            "active_weights": fusion_result["active_weights"],
            "active_modalities": fusion_result["active_modalities"],
            "modality_availability": raw_features["availability"],
            "strengths": assessment_exp["strengths"],
            "improvement_areas": assessment_exp["improvement_areas"],
            "recommendations": assessment_exp["recommendations"],
            "raw_features": raw_features
        }

        summary["formatted_report"] = self.generate_report_text(summary)

        # Step 4: Persistent Storage
        if save_results:
            self._save_assessment(summary)

        return summary

    def generate_report_text(self, summary: Dict[str, Any]) -> str:
        """
        Formats assessment summary into clean, readable text report.
        """
        comp_scores = summary.get("component_scores", {})
        avail = summary.get("modality_availability", {})

        mod_names = {
            "technical": "Technical Performance",
            "hr_nlp": "HR / NLP Quality",
            "speech": "Speech Delivery",
            "computer_vision": "Observable Visual Behavior",
            "resume_jd": "Resume / JD Skill Match"
        }

        lines = [
            "============================================================",
            "            MULTIMODAL EMPLOYABILITY ASSESSMENT             ",
            "============================================================",
            f"Candidate Identifier : {summary.get('candidate_id', 'Candidate')}",
            f"Overall Score        : {summary.get('employability_score', 0.0):.1f}%",
            f"Readiness Level      : {summary.get('readiness_level', 'Developing')}",
            f"Assessment Confidence: {int(summary.get('confidence', 0.0) * 100)}% ({len(summary.get('active_modalities', []))} of 5 modalities evaluated)",
            "------------------------------------------------------------",
            "MODALITY PERFORMANCE BREAKDOWN:"
        ]

        for mod_key, label in mod_names.items():
            if mod_key in comp_scores:
                weight_pct = int(summary.get("active_weights", {}).get(mod_key, 0.0) * 100)
                lines.append(f"- {label:<28}: {comp_scores[mod_key]:.1f}% (Weight: {weight_pct}%)")

        lines.append("------------------------------------------------------------")
        lines.append("MODALITY AVAILABILITY:")
        for mod_key, label in mod_names.items():
            is_present = avail.get(mod_key, False)
            lines.append(f"- {label:<28}: {'[YES]' if is_present else '[NOT RECORDED]'}")

        lines.append("------------------------------------------------------------")
        lines.append("KEY IDENTIFIED STRENGTHS:")
        for s in summary.get("strengths", []):
            lines.append(f"+ {s}")

        lines.append("------------------------------------------------------------")
        lines.append("AREAS FOR IMPROVEMENT:")
        for imp in summary.get("improvement_areas", []):
            lines.append(f"- {imp}")

        lines.append("------------------------------------------------------------")
        lines.append("ACTIONABLE RECOMMENDATIONS:")
        for r in summary.get("recommendations", []):
            lines.append(f"> {r}")

        lines.append("============================================================\n")
        return "\n".join(lines)

    def _save_assessment(self, summary: Dict[str, Any]):
        """
        Appends assessment record to results/employability_assessments.json.
        """
        try:
            records = []
            if self.storage_file.exists():
                try:
                    with open(self.storage_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            records = data
                except Exception:
                    records = []

            # Save clean record without recursive structures
            record = {
                "candidate_id": summary.get("candidate_id"),
                "timestamp": summary.get("timestamp"),
                "employability_score": summary.get("employability_score"),
                "readiness_level": summary.get("readiness_level"),
                "confidence": summary.get("confidence"),
                "component_scores": summary.get("component_scores"),
                "active_modalities": summary.get("active_modalities"),
                "strengths": summary.get("strengths"),
                "improvement_areas": summary.get("improvement_areas"),
                "recommendations": summary.get("recommendations")
            }
            records.append(record)

            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            # Graceful logging, don't fail interview evaluation
            print(f"[Warning] Failed to persist employability assessment record: {e}")


def run_employability_assessment(
    technical_results: Optional[Dict[str, Any]] = None,
    hr_results: Optional[Dict[str, Any]] = None,
    cv_results: Optional[Dict[str, Any]] = None,
    speech_results: Optional[Dict[str, Any]] = None,
    resume_jd_results: Optional[Dict[str, Any]] = None,
    candidate_id: Optional[str] = None,
    save_results: bool = True
) -> Dict[str, Any]:
    """
    Convenience function providing a programmatic interface to the multimodal evaluator.
    """
    evaluator = MultimodalEvaluator()
    return evaluator.evaluate(
        technical_results=technical_results,
        hr_results=hr_results,
        cv_results=cv_results,
        speech_results=speech_results,
        resume_jd_results=resume_jd_results,
        candidate_id=candidate_id,
        save_results=save_results
    )
