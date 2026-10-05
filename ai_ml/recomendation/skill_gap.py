"""
Skill Gap Analysis & Prioritization Module
------------------------------------------
Analyzes candidate skill gaps against target job descriptions and interview performance.
Assigns configurable, transparent priority levels (HIGH, MEDIUM, LOW) based on:
1. Core vs Supporting requirement in the job description
2. Candidate interview performance (demonstrated weaknesses)
3. Skill criticality for the target role

Does not make scientific or hiring guarantees; provides a structured, rule-based prioritization.
"""

from typing import Dict, List, Any, Optional, Set
import re


# Default skill classification for priority weighting
CORE_SKILL_CATEGORIES = {
    "languages": {"python", "java", "c++", "c", "javascript", "typescript", "go", "rust", "c#"},
    "foundations": {"data structures", "algorithms", "dbms", "operating systems", "computer networks", "system design", "sql"},
    "ai_ml_core": {"machine learning", "deep learning", "neural networks", "nlp", "computer vision", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"},
    "cloud_backend": {"docker", "kubernetes", "aws", "azure", "gcp", "flask", "django", "fastapi", "node.js", "react", "microservices"}
}


class SkillGapAnalyzer:
    """
    Analyzes and prioritizes candidate skill gaps based on JD requirements and interview metrics.
    """

    def __init__(self, core_categories: Optional[Dict[str, Set[str]]] = None):
        self.core_categories = core_categories or CORE_SKILL_CATEGORIES

    def is_core_skill(self, skill: str) -> bool:
        """Determines if a skill is a core foundational skill."""
        s_clean = skill.lower().strip()
        for cat_skills in self.core_categories.values():
            if s_clean in cat_skills:
                return True
        return False

    def analyze_gaps(
        self,
        required_skills: List[str],
        matched_skills: List[str],
        missing_skills: List[str],
        weak_topics: Optional[List[str]] = None,
        job_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates missing skills and interview weak topics, classifying them into HIGH, MEDIUM, and LOW priority.
        """
        weak_topics = [t.lower().strip() for t in (weak_topics or [])]
        req_clean = [s.lower().strip() for s in required_skills]
        matched_clean = [s.lower().strip() for s in matched_skills]
        missing_clean = [s.lower().strip() for s in missing_skills]

        prioritized_gaps = []
        high_priority = []
        medium_priority = []
        low_priority = []

        # 1. Process explicitly missing skills from JD
        for skill in missing_clean:
            is_core = self.is_core_skill(skill)
            # Check if candidate also demonstrated weakness in this area during interview
            interview_failed = any(skill in wt or wt in skill for wt in weak_topics)

            if is_core and interview_failed:
                priority = "HIGH"
                reason = "Mandatory foundational skill required by role and validated as weak during interview."
            elif is_core:
                priority = "HIGH"
                reason = "Core foundational skill required by role but not evidenced in candidate profile."
            elif interview_failed:
                priority = "MEDIUM"
                reason = "Demonstrated weakness during interview, relevant to role deliverables."
            else:
                priority = "MEDIUM"
                reason = "Required role skill missing from resume profile."

            gap_item = {
                "skill": skill,
                "priority": priority,
                "reason": reason,
                "is_core": is_core,
                "interview_weakness": interview_failed,
                "status": "missing"
            }
            prioritized_gaps.append(gap_item)

            if priority == "HIGH":
                high_priority.append(gap_item)
            elif priority == "MEDIUM":
                medium_priority.append(gap_item)
            else:
                low_priority.append(gap_item)

        # 2. Process interview weak topics that might already be "matched" on resume (theory vs practice gap)
        for topic in weak_topics:
            topic_matched = any(topic in ms or ms in topic for ms in matched_clean)
            already_covered = any(g["skill"] == topic for g in prioritized_gaps)

            if topic_matched and not already_covered:
                is_core = self.is_core_skill(topic)
                priority = "HIGH" if is_core else "MEDIUM"
                reason = "Listed on resume but candidate showed conceptual or implementation difficulty during interview."

                gap_item = {
                    "skill": topic,
                    "priority": priority,
                    "reason": reason,
                    "is_core": is_core,
                    "interview_weakness": True,
                    "status": "partial_mastery"
                }
                prioritized_gaps.append(gap_item)
                if priority == "HIGH":
                    high_priority.append(gap_item)
                else:
                    medium_priority.append(gap_item)

        # Sort gaps: HIGH first, then MEDIUM, then LOW
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        prioritized_gaps.sort(key=lambda x: priority_order.get(x["priority"], 3))

        total_gaps = len(prioritized_gaps)
        severity_ratio = (len(high_priority) * 1.0 + len(medium_priority) * 0.5) / max(1, len(required_skills))

        return {
            "total_gaps": total_gaps,
            "high_priority_count": len(high_priority),
            "medium_priority_count": len(medium_priority),
            "low_priority_count": len(low_priority),
            "prioritized_gaps": prioritized_gaps,
            "high_priority": [g["skill"] for g in high_priority],
            "medium_priority": [g["skill"] for g in medium_priority],
            "low_priority": [g["skill"] for g in low_priority],
            "gap_severity_index": round(min(1.0, severity_ratio), 2)
        }
