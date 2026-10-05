import re
import sys
from pathlib import Path

# Allow importing resume_parser.py
sys.path.append(
    str(Path(__file__).resolve().parents[1] / "preprocessing")
)

from resume_parser import (
    extract_text_from_pdf,
    extract_skills,
    extract_sections,
    extract_projects
)


def extract_candidate_name(text):
    """
    Extract candidate name from header lines of resume text.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    header_blocklist = {
        "resume", "curriculum", "vitae", "biodata", "contact",
        "profile", "objective", "email", "phone", "address", "career"
    }

    for line in lines[:5]:
        clean = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        words = clean.split()
        if 1 <= len(words) <= 4 and not any(w.lower() in header_blocklist for w in words):
            if "@" not in line and not re.search(r"\d{5,}", line) and "http" not in line.lower():
                return " ".join(w.capitalize() for w in words)

    return "Candidate"


def extract_candidate_education(text):
    """
    Extract degree and major if mentioned in resume.
    Avoids hardcoding computer science when other disciplines (VLSI, ECE, EEE, AI, etc.) are present.
    """
    deg_matches = re.findall(
        r"(?:Bachelor\s+of\s+Engineering|Bachelor\s+of\s+Technology|Master\s+of\s+Technology|B\.?\s*Tech|B\.?\s*E|B\.?\s*Sc|M\.?\s*Tech|M\.?\s*S|Bachelor|Master)[^\n,;]{0,80}",
        text,
        re.IGNORECASE
    )
    if deg_matches:
        raw_edu = deg_matches[0].strip()
        cleaned_edu = re.sub(r"[^\x00-\x7F]+", " - ", raw_edu)
        cleaned_edu = re.sub(r"[\(\)\[\]\u2022\uf0b7\-\*]+", " ", cleaned_edu)
        cleaned_edu = re.sub(r"\s+", " ", cleaned_edu).strip()
        return cleaned_edu

    # Heuristic department fallback if degree match not found
    dept = extract_candidate_department(text)
    if dept and dept != "Engineering":
        return f"Bachelor of Engineering in {dept}"

    return "Bachelor of Engineering"


def extract_candidate_department(text):
    """
    Detect candidate department / specialization from resume text.
    """
    t_lower = text.lower()
    
    if any(k in t_lower for k in ["vlsi", "very large scale integration", "electronics and communication", "electronics & communication", "ece"]):
        return "Electronics & Communication (VLSI)"
    if any(k in t_lower for k in ["artificial intelligence", "data science", "ai & ds", "ai and data science"]):
        return "Artificial Intelligence and Data Science"
    if any(k in t_lower for k in ["electrical and electronics", "electrical & electronics", "eee"]):
        return "Electrical & Electronics Engineering"
    if any(k in t_lower for k in ["computer science", "cse", "computer engineering"]):
        return "Computer Science & Engineering"
    if any(k in t_lower for k in ["information technology", "it"]):
        return "Information Technology"
    if any(k in t_lower for k in ["mechanical engineering", "mechanical"]):
        return "Mechanical Engineering"
    
    return "Engineering"


def suggest_role_from_profile(profile):
    """
    Suggest an appropriate career role based on extracted resume skills and projects.
    Distinguished from the user's chosen target_role.
    """
    skills = [s.lower() for s in profile.get("skills", [])]
    text = profile.get("resume_text", "").lower()

    # 1. VLSI & Hardware Design
    vlsi_keywords = {"verilog", "systemverilog", "vhdl", "rtl", "rtl design", "fpga", "asic", "vlsi", "cadence", "synopsys", "vivado", "digital electronics"}
    if any(k in skills for k in vlsi_keywords) or any(k in text for k in ["vlsi", "verilog", "vhdl", "rtl design", "digital electronics", "fpga design"]):
        return "VLSI Design Engineer"

    # 2. Embedded Systems
    embedded_keywords = {"embedded c", "microcontroller", "arm", "arduino", "rtos", "embedded systems", "pcb design", "microprocessor"}
    if any(k in skills for k in embedded_keywords) or "embedded systems" in text:
        return "Embedded Systems Engineer"

    # 3. Cloud & DevOps
    cloud_keywords = {"docker", "kubernetes", "aws", "terraform", "ansible", "jenkins", "ci/cd", "gcp", "prometheus", "grafana"}
    cloud_matches = [k for k in cloud_keywords if k in skills]
    if len(cloud_matches) >= 2 or "devops engineer" in text or "cloud engineer" in text:
        return "Cloud & DevOps Engineer"

    # 4. AI & Machine Learning
    ai_keywords = {"machine learning", "deep learning", "tensorflow", "pytorch", "keras", "computer vision", "natural language processing", "nlp"}
    if any(k in skills for k in ai_keywords) or "artificial intelligence" in text or "deep learning" in text:
        return "AI/ML Engineer"

    # 5. Data Science / Analytics
    data_keywords = {"pandas", "numpy", "power bi", "tableau", "spark", "hadoop"}
    if any(k in skills for k in data_keywords) and "sql" in skills:
        return "Data Scientist"

    # 6. Frontend Developer
    frontend_keywords = {"react", "angular", "vue", "javascript", "typescript", "html", "css"}
    if "react" in skills or ("javascript" in skills and "html" in skills and "css" in skills):
        if not any(k in skills for k in ["django", "flask", "fastapi", "spring boot", "node.js"]):
            return "Frontend Developer"

    # 7. Backend Developer
    backend_keywords = {"node.js", "express", "django", "flask", "fastapi", "spring boot"}
    if any(k in skills for k in backend_keywords):
        return "Backend Developer"

    # Default general software role
    return "Software Engineer"


def extract_internships_and_experience(text):
    """
    Extract internship or work experience lines from resume text.
    """
    internships = []
    objective_filter = {"seeking", "to secure", "looking for", "opportunity where", "aspiring"}

    for line in text.splitlines():
        clean = re.sub(r"^[•▪◦\-\*\d\.\)\s]+", "", line).strip()
        clean = re.sub(r"[\ufffd\uf0b7]+", " ", clean).strip()
        l_lower = clean.lower()

        if not clean or len(clean) < 8 or len(clean) > 120:
            continue

        if any(term in l_lower for term in objective_filter):
            continue

        if any(k in l_lower for k in ["internship", "intern", "trainee", "developer role", "worked as"]):
            if clean not in internships:
                internships.append(clean)

    return internships


def extract_certifications_and_achievements(text):
    """
    Extract certificates, achievements, and competitive accolades.
    """
    certs = []
    blocklist = {"achievements / activities", "certifications", "achievements", "activities"}

    for line in text.splitlines():
        clean = re.sub(r"^[•▪◦\-\*\d\.\)\s]+", "", line).strip()
        clean = re.sub(r"[\ufffd\uf0b7]+", " ", clean).strip()
        l_lower = clean.lower()

        if not clean or len(clean) < 8 or len(clean) > 120 or l_lower in blocklist:
            continue

        if any(k in l_lower for k in ["certified", "certification", "hackathon", "sih", "nptel", "coursera", "badge", "award", "rank", "winner", "runner"]):
            if clean not in certs:
                certs.append(clean)

    return certs


def build_candidate_profile(resume_path=None, raw_text=None):
    """
    Build a comprehensive structured candidate profile from a resume PDF or text.
    Preserves full backwards compatibility with Phase 1-3.
    """
    if raw_text:
        resume_text = raw_text
    elif resume_path and Path(resume_path).exists():
        resume_text = extract_text_from_pdf(resume_path)
    else:
        resume_text = ""

    skills = extract_skills(resume_text)
    sections = extract_sections(resume_text)
    projects = extract_projects(resume_text)

    name = extract_candidate_name(resume_text)
    education = extract_candidate_education(resume_text)
    department = extract_candidate_department(resume_text)
    internships = extract_internships_and_experience(resume_text)
    certifications = extract_certifications_and_achievements(resume_text)

    profile = {
        "name": name,
        "education": education,
        "department": department,
        "skills": skills,
        "sections": sections,
        "projects": projects,
        "internships": internships,
        "certifications": certifications,
        "resume_text": resume_text
    }

    profile["ai_suggested_role"] = suggest_role_from_profile(profile)

    return profile


if __name__ == "__main__":
    resume_path = "resume.pdf"
    profile = build_candidate_profile(resume_path)

    print("===================================")
    print("AI ENRICHED CANDIDATE PROFILE")
    print("===================================")
    print("Candidate Name :", profile["name"])
    print("Education      :", profile["education"])
    print("Total Skills   :", len(profile["skills"]))
    print("Skills Sample  :", ", ".join(profile["skills"][:6]))
    print("Internships    :", len(profile["internships"]))
    for it in profile["internships"]:
        print(f"  • {it}")
    print("Certifications :", len(profile["certifications"]))
    for cr in profile["certifications"]:
        print(f"  • {cr}")
    print("Resume Sections:", sum(1 for v in profile["sections"].values() if v))
    print("===================================")