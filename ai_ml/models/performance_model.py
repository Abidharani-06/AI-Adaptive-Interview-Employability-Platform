"""
Candidate Progress Tracking & Performance Model
-----------------------------------------------
Tracks, persists, and analyzes multiple interview attempts across time for the same candidate.
Computes real progression deltas:
- Readiness score and modality component changes
- Fine-grained acoustic, visual, and verbal metric shifts (WPM, fillers, pauses, posture)
- Skill-gap resolution (resolved skills vs persistent gaps vs new issues)
- Longitudinal trends (improved, declining, stable areas)

Handles:
- First-time baseline attempt (Attempt 1) without crashes
- Multiple sequential attempts (Attempt 2, 3...)
- Clean JSON persistence and frontend graph series export
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Resolve project paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]
default_history_file = project_root / "results" / "candidate_history.json"


class ProgressTracker:
    """
    Manages longitudinal candidate performance history and attempt-to-attempt progress analysis.
    """

    def __init__(self, history_file: Optional[Union[str, Path]] = None):
        self.history_file = Path(history_file or default_history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Loads all candidate assessment histories from JSON."""
        if not self.history_file.exists():
            return {}
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_history(self, history: Dict[str, List[Dict[str, Any]]]) -> None:
        """Saves candidate assessment histories to JSON."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"[Warning] Could not persist candidate history: {e}")

    def get_candidate_history(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Retrieves all past attempts for a given candidate."""
        history = self._load_history()
        return history.get(candidate_id, [])

    def record_attempt(
        self,
        candidate_id: str,
        assessment_summary: Dict[str, Any],
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Records a new assessment attempt and generates a comparative progress analysis.
        """
        history_db = self._load_history()
        cand_history = history_db.get(candidate_id, [])
        attempt_number = len(cand_history) + 1

        comp_scores = assessment_summary.get("component_scores", {})
        raw_feat = assessment_summary.get("raw_features", {})

        tech_feat = raw_feat.get("technical", {})
        speech_feat = raw_feat.get("speech", {})
        cv_feat = raw_feat.get("computer_vision", {})
        hr_feat = raw_feat.get("hr_nlp", {})
        rjd_feat = raw_feat.get("resume_jd", {})

        current_record = {
            "candidate_id": candidate_id,
            "attempt": attempt_number,
            "timestamp": assessment_summary.get("timestamp", datetime.now().isoformat()),
            "employability_score": float(assessment_summary.get("employability_score", 0.0)),
            "readiness_level": str(assessment_summary.get("readiness_level", "Early Stage")),
            "confidence": float(assessment_summary.get("confidence", 0.0)),
            "component_scores": {k: float(v) for k, v in comp_scores.items()},
            "weak_topics": list(tech_feat.get("weak_topics", [])),
            "missing_skills": list(rjd_feat.get("missing_skills", [])),
            "speech_metrics": {
                "wpm": float(speech_feat.get("speaking_rate_wpm", 0.0)),
                "fillers_per_100_words": float(speech_feat.get("fillers_per_100_words", 0.0)),
                "average_pause_seconds": float(speech_feat.get("average_pause_seconds", 0.0))
            },
            "cv_metrics": {
                "camera_facing_percentage": float(cv_feat.get("camera_facing_percentage", 0.0)),
                "posture_consistency_percentage": float(cv_feat.get("posture_consistency_percentage", 0.0)),
                "movement_stability_percentage": float(cv_feat.get("movement_stability_percentage", 100.0))
            },
            "hr_metrics": {
                "relevance_score": float(hr_feat.get("relevance_score", 0.0)),
                "clarity_score": float(hr_feat.get("clarity_score", 0.0)),
                "star_score": float(hr_feat.get("star_score", 0.0))
            }
        }

        # Analyze progress against previous attempts
        progress_analysis = self._compute_progress_deltas(current_record, cand_history)

        if save:
            cand_history.append(current_record)
            history_db[candidate_id] = cand_history
            self._save_history(history_db)

        return progress_analysis

    def _compute_progress_deltas(
        self,
        current: Dict[str, Any],
        past_attempts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates mathematical score differences, skill gap resolutions, and performance trends.
        """
        attempt_num = current["attempt"]

        # Case 1: First attempt (baseline establishment)
        if not past_attempts:
            return {
                "candidate_id": current["candidate_id"],
                "current_attempt": 1,
                "total_attempts": 1,
                "is_baseline": True,
                "score_delta_previous": 0.0,
                "score_delta_baseline": 0.0,
                "progress_narrative": f"Baseline assessment established at {current['employability_score']:.1f}% ({current['readiness_level']}). Subsequent attempts will track progression.",
                "improved_areas": [],
                "declining_areas": [],
                "stable_areas": ["All initial baseline metrics"],
                "resolved_skill_gaps": [],
                "persistent_gaps": current["missing_skills"],
                "new_issues": [],
                "timeline": [
                    {
                        "attempt": 1,
                        "date": current["timestamp"],
                        "score": current["employability_score"],
                        "readiness_level": current["readiness_level"],
                        "component_scores": current["component_scores"]
                    }
                ]
            }

        # Case 2: Multi-attempt comparison
        previous = past_attempts[-1]
        baseline = past_attempts[0]

        curr_score = current["employability_score"]
        prev_score = previous["employability_score"]
        base_score = baseline["employability_score"]

        delta_prev = round(curr_score - prev_score, 2)
        delta_base = round(curr_score - base_score, 2)

        improved = []
        declining = []
        stable = []

        # 1. Overall Readiness Trend
        if delta_prev > 1.5:
            improved.append(f"Overall Placement Readiness (+{delta_prev:.1f} pts)")
        elif delta_prev < -1.5:
            declining.append(f"Overall Placement Readiness ({delta_prev:.1f} pts)")
        else:
            stable.append("Overall Placement Readiness")

        # 2. Modality Component Changes
        curr_comps = current["component_scores"]
        prev_comps = previous.get("component_scores", {})
        for mod in set(curr_comps.keys()).union(prev_comps.keys()):
            c_val = curr_comps.get(mod, 0.0)
            p_val = prev_comps.get(mod, 0.0)
            diff = round(c_val - p_val, 1)

            mod_label = mod.replace("_", " ").title()
            if diff >= 3.0:
                improved.append(f"{mod_label} Performance (+{diff:.1f}%)")
            elif diff <= -3.0:
                declining.append(f"{mod_label} Performance ({diff:.1f}%)")
            else:
                stable.append(f"{mod_label} Performance")

        # 3. Fine-Grained Shifts (Speech & Acoustics)
        curr_sp = current.get("speech_metrics", {})
        prev_sp = previous.get("speech_metrics", {})
        if curr_sp and prev_sp:
            # Fillers: lower is better
            filler_diff = round(curr_sp.get("fillers_per_100_words", 0.0) - prev_sp.get("fillers_per_100_words", 0.0), 1)
            if filler_diff <= -1.0:
                improved.append(f"Filler Word Density ({filler_diff:.1f} per 100 words)")
            elif filler_diff >= 1.5:
                declining.append(f"Filler Word Density (+{filler_diff:.1f} per 100 words)")

            # Pauses: shorter is better if previous was high
            pause_diff = round(curr_sp.get("average_pause_seconds", 0.0) - prev_sp.get("average_pause_seconds", 0.0), 1)
            if prev_sp.get("average_pause_seconds", 0.0) > 1.2 and pause_diff <= -0.4:
                improved.append(f"Pause Duration Control ({pause_diff:.1f}s)")
            elif pause_diff >= 0.8:
                declining.append(f"Increased Pause Duration (+{pause_diff:.1f}s)")

        # 4. Fine-Grained Shifts (Visual Behavior)
        curr_cv = current.get("cv_metrics", {})
        prev_cv = previous.get("cv_metrics", {})
        if curr_cv and prev_cv:
            cam_diff = round(curr_cv.get("camera_facing_percentage", 0.0) - prev_cv.get("camera_facing_percentage", 0.0), 1)
            if cam_diff >= 5.0:
                improved.append(f"Camera-Facing Orientation (+{cam_diff:.1f}%)")
            elif cam_diff <= -5.0:
                declining.append(f"Camera-Facing Orientation ({cam_diff:.1f}%)")

            posture_diff = round(curr_cv.get("posture_consistency_percentage", 0.0) - prev_cv.get("posture_consistency_percentage", 0.0), 1)
            if posture_diff >= 5.0:
                improved.append(f"Shoulder & Posture Alignment (+{posture_diff:.1f}%)")
            elif posture_diff <= -5.0:
                declining.append(f"Shoulder & Posture Alignment ({posture_diff:.1f}%)")

        # 5. Skill Gap Evolution
        curr_missing = set(s.lower() for s in current.get("missing_skills", []))
        prev_missing = set(s.lower() for s in previous.get("missing_skills", []))
        curr_weak_topics = set(t.lower() for t in current.get("weak_topics", []))
        prev_weak_topics = set(t.lower() for t in previous.get("weak_topics", []))

        resolved_skills = sorted(list(prev_missing - curr_missing))
        resolved_topics = sorted(list(prev_weak_topics - curr_weak_topics))
        resolved_all = sorted(list(set(resolved_skills + resolved_topics)))

        persistent_skills = sorted(list(curr_missing.intersection(prev_missing)))
        new_issues = sorted(list((curr_missing - prev_missing).union(curr_weak_topics - prev_weak_topics)))

        for res_item in resolved_all:
            improved.append(f"Demonstrated Competency in: {res_item.title()}")

        # 6. Overall Narrative
        if delta_base > 0:
            narrative = f"Readiness improved by {delta_base:.1f} points across {attempt_num} attempts ({base_score:.1f}% -> {curr_score:.1f}%)."
        elif delta_base < 0:
            narrative = f"Readiness declined by {abs(delta_base):.1f} points across {attempt_num} attempts ({base_score:.1f}% -> {curr_score:.1f}%)."
        else:
            narrative = f"Readiness remained steady at {curr_score:.1f}% across {attempt_num} attempts."

        # 7. Timeline Series for Charts
        timeline = []
        for att in past_attempts + [current]:
            timeline.append({
                "attempt": att["attempt"],
                "date": att["timestamp"],
                "score": att["employability_score"],
                "readiness_level": att["readiness_level"],
                "component_scores": att.get("component_scores", {})
            })

        return {
            "candidate_id": current["candidate_id"],
            "current_attempt": attempt_num,
            "total_attempts": attempt_num,
            "is_baseline": False,
            "score_delta_previous": delta_prev,
            "score_delta_baseline": delta_base,
            "progress_narrative": narrative,
            "improved_areas": improved,
            "declining_areas": declining,
            "stable_areas": stable,
            "resolved_skill_gaps": resolved_all,
            "persistent_gaps": persistent_skills,
            "new_issues": new_issues,
            "timeline": timeline
        }
