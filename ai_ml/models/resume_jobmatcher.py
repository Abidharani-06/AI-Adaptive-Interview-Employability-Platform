import sys
from pathlib import Path

# Allow importing resume_parser.py
sys.path.append(
    str(Path(__file__).resolve().parents[1] / "preprocessing")
)

from resume_parser import extract_text_from_pdf, extract_skills


def extract_jd_skills(job_description):
    """
    Detect technical skills from a job description using the comprehensive skill catalog.
    """
    return extract_skills(job_description)


def calculate_skill_match(candidate_skills, required_skills):
    """
    Compare candidate skills with job-required skills.
    """

    candidate_set = set(candidate_skills)
    required_set = set(required_skills)

    matched_skills = sorted(candidate_set & required_set)
    missing_skills = sorted(required_set - candidate_set)

    if len(required_set) == 0:
        match_score = 0
    else:
        match_score = (
            len(matched_skills) / len(required_set)
        ) * 100

    return matched_skills, missing_skills, match_score


def match_resume_with_job(resume_path, job_description):
    """
    Complete resume and job-description matching pipeline.
    """

    resume_text = extract_text_from_pdf(resume_path)

    candidate_skills = extract_skills(resume_text)

    required_skills = extract_jd_skills(job_description)

    matched_skills, missing_skills, match_score = (
        calculate_skill_match(
            candidate_skills,
            required_skills
        )
    )

    return {
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score
    }


if __name__ == "__main__":

    resume_path = "resume.pdf"

    job_description = """
    We are looking for a Python Developer with knowledge of
    Python, SQL, Flask, Git, GitHub, Machine Learning,
    Pandas, NumPy and Docker.

    The candidate should also have knowledge of
    Data Structures, Algorithms and DBMS.
    """

    result = match_resume_with_job(
        resume_path,
        job_description
    )

    print("===================================")
    print("RESUME - JOB DESCRIPTION MATCHING")
    print("===================================")

    print("\nRequired Skills:")

    for skill in result["required_skills"]:
        print("-", skill)

    print("\nMatched Skills:")

    for skill in result["matched_skills"]:
        print("✓", skill)

    print("\nMissing Skills:")

    for skill in result["missing_skills"]:
        print("✗", skill)

    print("\n-----------------------------------")
    print(
        "Skill Match Score:",
        round(result["match_score"], 2),
        "%"
    )
    print("-----------------------------------")