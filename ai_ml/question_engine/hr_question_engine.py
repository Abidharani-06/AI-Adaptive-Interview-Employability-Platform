import os
import re
import sys
from pathlib import Path
import pandas as pd

# Resolve paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]

models_dir = str(project_root / "ai_ml" / "models")
if models_dir not in sys.path:
    sys.path.append(models_dir)

preprocessing_dir = str(project_root / "ai_ml" / "preprocessing")
if preprocessing_dir not in sys.path:
    sys.path.append(preprocessing_dir)

from candidate_profile import build_candidate_profile
from personalized_question_engine import parse_projects_from_text


# ============================================================
# 1. LOAD STATIC HR QUESTION BANK
# ============================================================

def load_hr_questions_dataset():
    """
    Load the HR and behavioral questions dataset.
    """
    path_candidates = [
        Path("ai_ml/data/hr_questions.csv"),
        project_root / "ai_ml" / "data" / "hr_questions.csv"
    ]
    for p in path_candidates:
        if p.exists():
            return pd.read_csv(p)

    raise FileNotFoundError("hr_questions.csv could not be found.")


# ============================================================
# 2. EXTRACT TARGET ROLE FROM JOB DESCRIPTION
# ============================================================

def extract_target_role_from_jd(jd_text):
    """
    Extract target role title from job description text.
    """
    if not jd_text:
        return "Software Engineer"

    # Look for role line e.g. "JOB ROLE: AI/ML Software Engineer"
    role_match = re.search(r"(?:JOB\s+ROLE|ROLE|POSITION|TITLE)\s*[:\-]\s*([^\n\r]+)", jd_text, re.IGNORECASE)
    if role_match:
        role = role_match.group(1).strip()
        role = re.sub(r"[^a-zA-Z0-9\s\/\-]", "", role)
        return role if role else "Software Engineer"

    # Secondary heuristic: look for developer/engineer patterns
    eng_match = re.search(r"\b([A-Za-z0-9\/\+\#\.\s]{3,30}\s+(?:Developer|Engineer|Scientist|Architect|Specialist))\b", jd_text)
    if eng_match:
        return eng_match.group(1).strip()

    return "Software Engineer"


# ============================================================
# 3. DYNAMIC RESUME-AWARE & JD-AWARE QUESTION BUILDER
# ============================================================

def generate_personalized_hr_bank(resume_path, jd_path=None):
    """
    Build an enriched, dynamic HR question bank customized for the specific
    candidate resume and target job description.
    """
    # 1. Parse Profile
    profile = build_candidate_profile(resume_path)
    name = profile.get("name", "Candidate")
    first_name = name.split()[0] if name != "Candidate" else "Candidate"
    education = profile.get("education", "Computer Science")
    skills = profile.get("skills", [])
    internships = profile.get("internships", [])
    certs = profile.get("certifications", [])

    parsed_projects = parse_projects_from_text(profile.get("projects", ""), skills)

    # 2. Parse Job Description
    target_role = "Software Engineer"
    if jd_path:
        jd_file = Path(jd_path)
        if not jd_file.exists():
            jd_file = project_root / jd_path
        if jd_file.exists():
            with open(jd_file, "r", encoding="utf-8") as f:
                target_role = extract_target_role_from_jd(f.read())

    personalized_bank = []

    # --------------------------------------------------------
    # Category A: Personalized Introduction & Background
    # --------------------------------------------------------
    intro_text = (
        f"Hello {first_name}, to start off, could you tell me about yourself "
        f"and what inspired you to pursue {education}?"
        if first_name != "Candidate"
        else f"To start off, could you walk me through your background and what led you to pursue {education}?"
    )
    personalized_bank.append({
        "question_id": "DYN_HR_INTRO",
        "category": "Introduction & Background",
        "question_text": intro_text,
        "target_competencies": "Self-Introduction; Communication; Career Motivation",
        "requires_star": False,
        "expected_themes": "background; education; technical journey; projects; interests; passion",
        "source": "dynamic_resume_intro",
        "follow_up_weak": f"What specific technical project or milestone during your time studying {education} solidified your interest in software engineering?",
        "follow_up_strong": "What unique perspective or strength does your academic journey give you as an engineer?"
    })

    # --------------------------------------------------------
    # Category B: Resume Project Motivation & Contribution (STAR)
    # --------------------------------------------------------
    if parsed_projects:
        for idx, proj in enumerate(parsed_projects[:3], start=1):
            p_name = proj["clean_name"]
            tech_context = ", ".join(proj["technologies"]) if proj["technologies"] else "modern tech"

            # Project Motivation & Role
            personalized_bank.append({
                "question_id": f"DYN_HR_PROJ_ROLE_{idx}",
                "category": "Project Experience & Impact",
                "question_text": f"In your resume, you developed '{p_name}'. What motivated you to choose this project, and what was your specific individual contribution?",
                "target_competencies": "Project Ownership; Technical Communication; Initiative",
                "requires_star": True,
                "expected_themes": f"motivation; objective; role; contribution; {p_name.lower()}; implementation; result",
                "source": "dynamic_project_ownership",
                "follow_up_weak": f"What specific module or technical component of '{p_name}' did you personally design and code?",
                "follow_up_strong": f"If you had another month to work on '{p_name}', what architectural enhancement or feature would you prioritize?"
            })

            # Project Roadblock & Problem Solving (STAR)
            personalized_bank.append({
                "question_id": f"DYN_HR_PROJ_CHALLENGE_{idx}",
                "category": "Overcoming Challenges",
                "question_text": f"During the development of '{p_name}', what was the most difficult technical or collaborative roadblock you encountered, and how did you resolve it?",
                "target_competencies": "Problem Solving; Resilience; Analytical Thinking",
                "requires_star": True,
                "expected_themes": "situation; roadblock; challenge; root cause; action; resolution; outcome; learning",
                "source": "dynamic_project_challenge",
                "follow_up_weak": "What exact diagnostic steps did you take to isolate the root cause of that problem?",
                "follow_up_strong": "How did overcoming that challenge change how you structure or test your code today?"
            })

    # --------------------------------------------------------
    # Category C: Internship / Practical Experience
    # --------------------------------------------------------
    if internships:
        intern_sample = internships[0]
        # Clean line
        clean_intern = re.sub(r"^(?:Selected for|Underwent|Completed)\s+", "", intern_sample, flags=re.IGNORECASE)
        personalized_bank.append({
            "question_id": "DYN_HR_INTERN",
            "category": "Professional Experience",
            "question_text": f"Your resume highlights experience with '{clean_intern}'. Can you describe a key deliverable you took ownership of and what working in that environment taught you?",
            "target_competencies": "Professional Growth; Ownership; Industry Readiness",
            "requires_star": True,
            "expected_themes": "experience; responsibility; deliverable; collaboration; learning; professional growth",
            "source": "dynamic_internship",
            "follow_up_weak": "What was the most challenging feedback you received during that experience, and how did you act on it?",
            "follow_up_strong": "How did that practical experience influence the standards you set for your own software projects?"
        })

    # --------------------------------------------------------
    # Category D: Achievements & Certifications
    # --------------------------------------------------------
    if certs:
        cert_sample = certs[0]
        personalized_bank.append({
            "question_id": "DYN_HR_ACHIEVE",
            "category": "Continuous Learning & Excellence",
            "question_text": f"I noticed your accomplishment regarding '{cert_sample}'. What motivated you to pursue this, and how have you applied what you gained from it?",
            "target_competencies": "Continuous Learning; Self-Direction; Applied Knowledge",
            "requires_star": False,
            "expected_themes": "motivation; dedication; certification; knowledge; application; impact",
            "source": "dynamic_achievement",
            "follow_up_weak": "Can you give a practical example where the skills from that certification solved a real problem?",
            "follow_up_strong": "What technical topic or skill are you planning to master next as your follow-up goal?"
        })

    # --------------------------------------------------------
    # Category E: Target Role & JD Alignment
    # --------------------------------------------------------
    personalized_bank.append({
        "question_id": "DYN_HR_JD_ALIGN",
        "category": "Motivation & Role Alignment",
        "question_text": f"We are actively hiring for an {target_role}. What makes you confident that your skills, background, and work ethic make you the right fit for this position?",
        "target_competencies": "Role Alignment; Value Proposition; Self-Awareness",
        "requires_star": False,
        "expected_themes": f"skills; {target_role.lower()}; value; dedication; fit; passion; team; impact",
        "source": "dynamic_jd_alignment",
        "follow_up_weak": f"What specific technical project of yours best demonstrates your ability to excel as an {target_role}?",
        "follow_up_strong": f"Where do you hope an {target_role} position will take your engineering career over the next 2-3 years?"
    })

    # --------------------------------------------------------
    # Category F: Core Behavioral Competencies from CSV Bank
    # --------------------------------------------------------
    try:
        csv_data = load_hr_questions_dataset()
        for _, row in csv_data.iterrows():
            personalized_bank.append({
                "question_id": str(row["question_id"]),
                "category": str(row["category"]),
                "question_text": str(row["question_text"]),
                "target_competencies": str(row.get("target_competencies", "")),
                "requires_star": bool(row.get("requires_star", False)),
                "expected_themes": str(row.get("expected_themes", "")),
                "source": "csv_bank",
                "follow_up_weak": str(row.get("follow_up_weak", "Could you provide a more specific example?")),
                "follow_up_strong": str(row.get("follow_up_strong", "What would you do differently if faced with that situation again?"))
            })
    except Exception as e:
        print(f"[Warning] Could not load static HR questions CSV: {e}")

    return {
        "candidate_name": name,
        "education": education,
        "target_role": target_role,
        "projects_count": len(parsed_projects),
        "bank": personalized_bank
    }


# ============================================================
# 4. SELECT ADAPTIVE HR QUESTIONS
# ============================================================

def select_hr_interview_plan(personalized_bank, num_questions=5):
    """
    Select a balanced, structured set of HR questions covering:
    1. Introduction & Background (Personalized)
    2. Project Motivation & Ownership (Personalized, STAR)
    3. Overcoming Roadblocks / Problem Solving (Personalized, STAR)
    4. Teamwork & Conflict Resolution / Leadership (STAR)
    5. Role / Company Alignment & Vision
    """
    bank = personalized_bank["bank"]
    selected = []
    used_ids = set()

    def add_from_filter(predicate):
        for q in bank:
            if q["question_id"] not in used_ids and predicate(q):
                selected.append(q)
                used_ids.add(q["question_id"])
                return True
        return False

    # 1. Introduction
    add_from_filter(lambda q: q["category"] == "Introduction & Background")

    # 2. Project Ownership (STAR)
    add_from_filter(lambda q: q["category"] == "Project Experience & Impact")

    # 3. Overcoming Challenges / Roadblock (STAR)
    add_from_filter(lambda q: q["category"] == "Overcoming Challenges")

    # 4. Teamwork / Conflict Resolution / Leadership (STAR)
    add_from_filter(lambda q: q["category"] in [
        "Teamwork & Conflict Resolution",
        "Leadership & Initiative",
        "Pressure & Deadline Management"
    ])

    # 5. Role Alignment
    add_from_filter(lambda q: q["category"] == "Motivation & Role Alignment")

    # Fill remaining if num_questions > 5 or if any category was missing
    for q in bank:
        if len(selected) >= num_questions:
            break
        if q["question_id"] not in used_ids:
            selected.append(q)
            used_ids.add(q["question_id"])

    return selected[:num_questions]


# ============================================================
# 5. ADAPTIVE FOLLOW-UP GENERATOR
# ============================================================

def generate_adaptive_follow_up(question_obj, eval_result):
    """
    Generate an intelligent, contextual follow-up question based on the
    candidate's score and identified missing components.
    """
    overall_score = eval_result["overall_score"]
    star_res = eval_result.get("star_result")
    missing_star = star_res.get("missing_components", []) if star_res else []

    # Scenario 1: Behavioral question with missing Action
    if "Action" in missing_star and overall_score < 0.65:
        return {
            "is_followup": True,
            "type": "probe_action",
            "question_text": "What specific technical or individual actions did YOU personally take to address that situation?",
            "requires_star": True,
            "expected_themes": "action; individual contribution; initiative; implementation; decision",
            "parent_question_id": question_obj.get("question_id", "N/A")
        }

    # Scenario 2: Behavioral question with missing Result
    if "Result" in missing_star and overall_score < 0.65:
        return {
            "is_followup": True,
            "type": "probe_result",
            "question_text": "What was the measurable outcome or final impact of your solution, and what key lesson did you learn from it?",
            "requires_star": True,
            "expected_themes": "result; outcome; impact; metrics; learning; success; delivery",
            "parent_question_id": question_obj.get("question_id", "N/A")
        }

    # Scenario 3: General low score / shallow response (< 0.55)
    if overall_score < 0.55:
        weak_prompt = question_obj.get("follow_up_weak")
        if not weak_prompt:
            weak_prompt = "Could you elaborate with a specific real-world example from your academic or project experience?"
        return {
            "is_followup": True,
            "type": "probe_depth",
            "question_text": weak_prompt,
            "requires_star": question_obj.get("requires_star", False),
            "expected_themes": question_obj.get("expected_themes", ""),
            "parent_question_id": question_obj.get("question_id", "N/A")
        }

    # Scenario 4: High performance (>= 0.78) -> Probe deeper architectural or strategic insight
    if overall_score >= 0.78:
        strong_prompt = question_obj.get("follow_up_strong")
        if not strong_prompt:
            strong_prompt = "Looking back, what is one key decision in that experience that you would approach differently today?"
        return {
            "is_followup": True,
            "type": "probe_reflection",
            "question_text": strong_prompt,
            "requires_star": False,
            "expected_themes": "reflection; decision; improvement; trade-offs; learning; foresight",
            "parent_question_id": question_obj.get("question_id", "N/A")
        }

    return None


if __name__ == "__main__":
    print("=== DYNAMIC HR QUESTION ENGINE TEST ===")
    res = generate_personalized_hr_bank("resume.pdf", "ai_ml/data/job_description.txt")
    print("Candidate Name :", res["candidate_name"])
    print("Education      :", res["education"])
    print("Target Role    :", res["target_role"])
    print("Total Bank Size:", len(res["bank"]))

    plan = select_hr_interview_plan(res, num_questions=5)
    print(f"\n--- Selected Plan ({len(plan)} questions) ---")
    for i, q in enumerate(plan, 1):
        star_tag = "[STAR]" if q["requires_star"] else "[STANDARD]"
        print(f"{i}. {star_tag} [{q['category']}]")
        print(f"   {q['question_text']}")
