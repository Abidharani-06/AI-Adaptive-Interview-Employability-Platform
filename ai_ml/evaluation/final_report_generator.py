"""
Final Employability Assessment Report Generator
-----------------------------------------------
Generates comprehensive, multi-format assessment reports:
1. JSON Report: Machine-readable data structure for API and UI consumption
2. Markdown / Text Report: Formatted executive summary
3. HTML Report: Polished browser-viewable document with styled badges and visual charts
4. CSV Summary: Single-row tabular append for enterprise candidate tracking

Enforces ethical distinctions:
- OBSERVED / MEASURED vs MODEL-DERIVED
- Zero psychological claims or hiring guarantees
"""

import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Resolve project paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]
default_reports_dir = project_root / "results" / "reports"


class FinalReportGenerator:
    """
    Synthesizes all multimodal interview signals, roadmap modules, and progress tracking
    into publication-quality reports.
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        self.output_dir = Path(output_dir or default_reports_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.csv_summary_file = project_root / "results" / "assessment_summary.csv"

    def generate_all_reports(
        self,
        final_assessment: Dict[str, Any],
        candidate_slug: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generates and saves JSON, Markdown, HTML, and CSV outputs.
        Returns paths to created report artifacts.
        """
        c_id = final_assessment.get("candidate", {}).get("name", "Candidate")
        slug = candidate_slug or c_id.replace(" ", "_").replace("/", "_").lower()
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{slug}_{timestamp_str}"

        # 1. Generate JSON
        json_path = self.output_dir / f"{base_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(final_assessment, f, indent=2)

        # 2. Generate Markdown
        md_text = self.generate_markdown(final_assessment)
        md_path = self.output_dir / f"{base_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        # 3. Generate HTML
        html_text = self.generate_html(final_assessment)
        html_path = self.output_dir / f"{base_name}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_text)

        # 4. Append to CSV Summary
        self._append_to_csv(final_assessment)

        return {
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "html_path": str(html_path),
            "csv_path": str(self.csv_summary_file)
        }

    def generate_markdown(self, assessment: Dict[str, Any]) -> str:
        """
        Builds a clean, professional Markdown report.
        """
        cand = assessment.get("candidate", {})
        job = assessment.get("job_alignment", {})
        readiness = assessment.get("readiness", {})
        multimodal = assessment.get("multimodal_assessment", {})
        comp_scores = multimodal.get("component_scores", {})
        strengths = assessment.get("strengths", [])
        improvements = assessment.get("improvement_areas", [])
        recommendations = assessment.get("recommendations", [])
        roadmap = assessment.get("learning_roadmap", {})
        progress = assessment.get("progress_tracking", {})

        lines = [
            "# AI-POWERED MULTIMODAL EMPLOYABILITY ASSESSMENT REPORT",
            f"**Candidate:** {cand.get('name', 'Candidate')} | **Role Target:** {job.get('target_role', 'Software Engineer')} | **Date:** {assessment.get('timestamp', datetime.now().isoformat())[:10]}",
            "",
            "---",
            "",
            "## 1. EXECUTIVE READINESS SUMMARY",
            f"- **Placement Readiness Score:** **{readiness.get('score', 0.0):.1f}%**",
            f"- **Readiness Level:** **{readiness.get('level', 'Developing')}**",
            f"- **Assessment Confidence:** **{int(multimodal.get('confidence', 0.0) * 100)}%** ({len(multimodal.get('active_modalities', []))} of 5 evaluated modalities)",
            f"- **Evaluation Summary:** {readiness.get('description', '')}",
            "",
            "### Modality Performance Breakdown",
            "| Evaluation Dimension | Measured Score | Active Weight | Status |",
            "|:---|:---:|:---:|:---:|"
        ]

        mod_names = [
            ("technical", "Technical Problem Solving"),
            ("hr_nlp", "HR / Behavioral NLP Quality"),
            ("speech", "Speech & Acoustic Delivery"),
            ("computer_vision", "Observable Visual Behavior"),
            ("resume_jd", "Resume / JD Skill Alignment")
        ]

        weights = multimodal.get("active_weights", {})
        avail = multimodal.get("modality_availability", {})

        for m_key, m_label in mod_names:
            score = comp_scores.get(m_key)
            w = weights.get(m_key, 0.0)
            is_pres = avail.get(m_key, False)
            score_str = f"{score:.1f}%" if score is not None else "N/A"
            w_str = f"{int(w * 100)}%" if is_pres else "0%"
            stat_str = "Evaluated" if is_pres else "Not Recorded"
            lines.append(f"| {m_label} | {score_str} | {w_str} | {stat_str} |")

        lines.extend([
            "",
            "---",
            "",
            "## 2. MEASURED PERFORMANCE DETAILS (OBSERVED SIGNALS)",
            "",
            "### Technical Round",
            f"- **Overall Technical Score:** {assessment.get('technical_assessment', {}).get('overall_technical_score', assessment.get('technical_assessment', {}).get('overall_score', comp_scores.get('technical', 'N/A')))}%",
            f"- **Strong Topics:** {', '.join(assessment.get('technical_assessment', {}).get('strong_topics', [])) or 'None identified'}",
            f"- **Weak Topics:** {', '.join(assessment.get('technical_assessment', {}).get('weak_topics', [])) or 'None identified'}",
            "",
            "### Behavioral / HR Round",
            f"- **Overall HR Score:** {assessment.get('hr_assessment', {}).get('overall_hr_score', assessment.get('hr_assessment', {}).get('overall_score', comp_scores.get('hr_nlp', 'N/A')))}%",
            f"- **Answer Relevance:** {assessment.get('hr_assessment', {}).get('average_relevance', assessment.get('hr_assessment', {}).get('relevance_score', 'N/A'))}%",
            f"- **Clarity & Delivery:** {assessment.get('hr_assessment', {}).get('average_clarity', assessment.get('hr_assessment', {}).get('clarity_score', 'N/A'))}%",
            f"- **STAR Structure Mastery:** {assessment.get('hr_assessment', {}).get('average_star_score', assessment.get('hr_assessment', {}).get('star_score', 'N/A'))}%",
            "",
            "### Speech & Acoustic Observations",
            f"- **Speaking Rate:** {assessment.get('speech_assessment', {}).get('speaking_rate_wpm', 'N/A')} WPM (Optimal: 120–160 WPM)",
            f"- **Filler Word Density:** {assessment.get('speech_assessment', {}).get('fillers_per_100_words', 'N/A')} fillers per 100 words",
            f"- **Average Pause Duration:** {assessment.get('speech_assessment', {}).get('average_pause_seconds', 'N/A')} seconds",
            "",
            "### Visual & Posture Observations",
            f"- **Camera-Facing Consistency:** {assessment.get('visual_assessment', {}).get('camera_facing_percentage', 'N/A')}%",
            f"- **Posture Consistency:** {assessment.get('visual_assessment', {}).get('posture_consistency_percentage', 'N/A')}%",
            f"- **Movement Stability:** {assessment.get('visual_assessment', {}).get('movement_stability_percentage', 'N/A')}%",
            "",
            "---",
            "",
            "## 3. EXPLAINABLE ASSESSMENT",
            "",
            "### Key Strengths",
            "\n".join([f"+ {s}" for s in strengths]) if strengths else "+ Completed comprehensive multimodal evaluation.",
            "",
            "### Areas for Improvement",
            "\n".join([f"- {imp}" for imp in improvements]) if improvements else "- Baseline requirements fulfilled.",
            "",
            "### Prioritized Skill Gaps",
            f"- **High Priority:** {', '.join(assessment.get('skill_gaps', {}).get('high_priority', [])) or 'None'}",
            f"- **Medium Priority:** {', '.join(assessment.get('skill_gaps', {}).get('medium_priority', [])) or 'None'}",
            "",
            "### Actionable Recommendations",
            "\n".join([f"> {r}" for r in recommendations]) if recommendations else "> Continue regular problem solving and mock interview rehearsal.",
            "",
            "---",
            "",
            "## 4. PERSONALIZED LEARNING ROADMAP & ACTION PLAN",
            f"**Total Modules:** {roadmap.get('total_modules', 0)} | **Estimated Total Effort:** {roadmap.get('total_estimated_hours', 0)} hours | **Schedule Duration:** {roadmap.get('duration_weeks', 5)} weeks",
            ""
        ])

        for wp in roadmap.get("weekly_action_plan", []):
            lines.extend([
                f"### Week {wp.get('week')}: {wp.get('theme')}",
                f"- **Target Focus:** {', '.join(wp.get('target_topics', []))}",
                f"- **Milestone Goal:** {wp.get('milestone', '')}",
                "- **Key Objectives:**"
            ])
            for obj in wp.get("objectives", []):
                lines.append(f"  * {obj}")
            lines.append("")

        # Progress history if available
        if progress and not progress.get("is_baseline", True):
            lines.extend([
                "---",
                "",
                "## 5. LONGITUDINAL PROGRESS TRACKING",
                f"- **Current Attempt:** #{progress.get('current_attempt', 1)}",
                f"- **Progress Narrative:** {progress.get('progress_narrative', '')}",
                f"- **Change from Previous Attempt:** {progress.get('score_delta_previous', 0.0):+0.1f} points",
                f"- **Change from Initial Baseline:** {progress.get('score_delta_baseline', 0.0):+0.1f} points",
                f"- **Newly Resolved Competencies:** {', '.join(progress.get('resolved_skill_gaps', [])) or 'None in this attempt'}",
                f"- **Demonstrated Improvements:** {', '.join(progress.get('improved_areas', [])) or 'Stable'}",
                ""
            ])

        lines.extend([
            "---",
            "",
            "## 6. ETHICAL & TECHNICAL SAFEGUARDS",
            "- **Nature of Assessment:** The Placement Readiness Estimate is a calibrated prototype score indicating readiness against observable benchmark metrics.",
            "- **Non-Diagnostic Scope:** This platform does NOT measure or claim to diagnose nervousness, anxiety, personality, honesty, deception, or mental health.",
            "- **No Hiring Guarantee:** Score outputs reflect technical mastery and observable interview communication proxies; they do not guarantee employment or hiring offers.",
            ""
        ])

        return "\n".join(lines)

    def generate_html(self, assessment: Dict[str, Any]) -> str:
        """
        Builds a styled, modern HTML report with cards and badges.
        """
        cand = assessment.get("candidate", {})
        readiness = assessment.get("readiness", {})
        score = readiness.get("score", 0.0)
        level = readiness.get("level", "Developing")
        multimodal = assessment.get("multimodal_assessment", {})
        comp_scores = multimodal.get("component_scores", {})
        roadmap = assessment.get("learning_roadmap", {})
        progress = assessment.get("progress_tracking", {})

        # Color theme according to readiness level
        level_colors = {
            "Highly Ready": "#10b981",
            "Ready": "#3b82f6",
            "Developing": "#f59e0b",
            "Needs Improvement": "#ef4444",
            "Early Stage": "#6b7280"
        }
        badge_color = level_colors.get(level, "#3b82f6")

        mod_cards_html = ""
        mod_names = [
            ("technical", "Technical Problem Solving"),
            ("hr_nlp", "HR / Behavioral NLP"),
            ("speech", "Speech & Acoustic Delivery"),
            ("computer_vision", "Observable Visual Behavior"),
            ("resume_jd", "Resume / JD Alignment")
        ]
        for key, title in mod_names:
            val = comp_scores.get(key)
            val_str = f"{val:.1f}%" if val is not None else "Not Recorded"
            pct = val if val is not None else 0
            mod_cards_html += f"""
            <div class="card">
                <div class="card-title">{title}</div>
                <div class="card-value">{val_str}</div>
                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {pct}%;"></div></div>
            </div>
            """

        roadmap_weeks_html = ""
        for wp in roadmap.get("weekly_action_plan", []):
            objectives_li = "".join(f"<li>{obj}</li>" for obj in wp.get("objectives", []))
            roadmap_weeks_html += f"""
            <div class="week-card">
                <div class="week-header">
                    <span class="week-pill">Week {wp.get('week')}</span>
                    <span class="week-theme">{wp.get('theme')}</span>
                </div>
                <div class="week-milestone"><strong>Milestone:</strong> {wp.get('milestone')}</div>
                <ul class="week-objectives">{objectives_li}</ul>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Employability Report - {cand.get('name', 'Candidate')}</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 960px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
    .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 24px; margin-bottom: 32px; }}
    .title {{ font-size: 24px; font-weight: 700; color: #e2e8f0; }}
    .subtitle {{ font-size: 14px; color: #94a3b8; margin-top: 4px; }}
    .badge {{ background: {badge_color}; color: #ffffff; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; display: inline-block; }}
    .score-hero {{ display: flex; align-items: center; gap: 32px; background: #0f172a; border-radius: 12px; padding: 24px; margin-bottom: 32px; }}
    .score-circle {{ font-size: 48px; font-weight: 800; color: {badge_color}; min-width: 120px; text-align: center; }}
    .score-desc {{ font-size: 15px; color: #cbd5e1; line-height: 1.5; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }}
    .card {{ background: #0f172a; border-radius: 10px; padding: 16px; border: 1px solid #334155; }}
    .card-title {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }}
    .card-value {{ font-size: 24px; font-weight: 700; color: #f8fafc; margin: 8px 0; }}
    .progress-bar-bg {{ background: #334155; height: 6px; border-radius: 3px; overflow: hidden; }}
    .progress-bar-fill {{ background: {badge_color}; height: 100%; border-radius: 3px; }}
    .section-title {{ font-size: 18px; font-weight: 700; color: #e2e8f0; margin: 32px 0 16px; border-left: 4px solid {badge_color}; padding-left: 12px; }}
    .week-card {{ background: #0f172a; border-radius: 10px; padding: 16px; margin-bottom: 16px; border: 1px solid #334155; }}
    .week-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
    .week-pill {{ background: #334155; color: #e2e8f0; font-size: 12px; font-weight: 700; padding: 4px 8px; border-radius: 6px; }}
    .week-theme {{ font-size: 15px; font-weight: 600; color: #f8fafc; }}
    .week-milestone {{ font-size: 13px; color: #38bdf8; margin-bottom: 8px; }}
    .week-objectives {{ font-size: 13px; color: #cbd5e1; margin: 0; padding-left: 20px; }}
    .week-objectives li {{ margin-bottom: 4px; }}
    .disclaimer {{ background: #0f172a; border-radius: 8px; padding: 16px; font-size: 12px; color: #64748b; margin-top: 40px; border: 1px solid #1e293b; line-height: 1.5; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <div class="title">AI Employability & Readiness Assessment</div>
            <div class="subtitle">Candidate: <strong>{cand.get('name', 'Candidate')}</strong> | Target: <strong>{assessment.get('job_alignment', {}).get('target_role', 'Software Engineer')}</strong></div>
        </div>
        <div class="badge">{level}</div>
    </div>

    <div class="score-hero">
        <div class="score-circle">{score:.1f}%</div>
        <div class="score-desc">
            <strong>Placement Readiness Estimate:</strong> {readiness.get('description', '')}
            <br><small style="color: #94a3b8;">Confidence Level: {int(multimodal.get('confidence', 0.0) * 100)}% based on {len(multimodal.get('active_modalities', []))} active evaluation streams.</small>
        </div>
    </div>

    <div class="section-title">Modality Performance Breakdown</div>
    <div class="grid">
        {mod_cards_html}
    </div>

    <div class="section-title">Personalized Learning Roadmap & Action Plan</div>
    <div class="roadmap-list">
        {roadmap_weeks_html}
    </div>

    <div class="disclaimer">
        <strong>Ethical & Technical Safeguard Notice:</strong> This score represents an objective engineering evaluation derived from observed technical responses, resume alignment, acoustic delivery, and computer vision indicators. It does NOT claim to assess psychological attributes (confidence, nervousness, personality, or deception) and does not guarantee employment.
    </div>
</div>
</body>
</html>"""
        return html

    def _append_to_csv(self, assessment: Dict[str, Any]) -> None:
        """
        Appends single row summary to assessment_summary.csv.
        """
        try:
            file_exists = self.csv_summary_file.exists()
            self.csv_summary_file.parent.mkdir(parents=True, exist_ok=True)

            cand = assessment.get("candidate", {})
            readiness = assessment.get("readiness", {})
            multimodal = assessment.get("multimodal_assessment", {})
            comp = multimodal.get("component_scores", {})

            row = {
                "timestamp": assessment.get("timestamp", datetime.now().isoformat()),
                "candidate_name": cand.get("name", "Candidate"),
                "target_role": assessment.get("job_alignment", {}).get("target_role", "Software Engineer"),
                "employability_score": readiness.get("score", 0.0),
                "readiness_level": readiness.get("level", "Developing"),
                "confidence": multimodal.get("confidence", 0.0),
                "technical_score": comp.get("technical", ""),
                "hr_score": comp.get("hr_nlp", ""),
                "speech_score": comp.get("speech", ""),
                "cv_score": comp.get("computer_vision", ""),
                "skill_match_score": comp.get("resume_jd", "")
            }

            fieldnames = [
                "timestamp", "candidate_name", "target_role",
                "employability_score", "readiness_level", "confidence",
                "technical_score", "hr_score", "speech_score", "cv_score", "skill_match_score"
            ]

            with open(self.csv_summary_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            print(f"[Warning] Failed to write assessment CSV summary: {e}")
