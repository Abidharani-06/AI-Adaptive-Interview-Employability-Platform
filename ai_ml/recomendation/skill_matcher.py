import re


def normalize_skill(skill):
    """Normalize skill names for comparison."""
    return re.sub(r"\s+", " ", skill.lower().strip())


def extract_required_skills(job_description, known_skills):
    """
    Detect required skills mentioned in the job description.
    """

    jd_text = job_description.lower()

    required_skills = []

    for skill in known_skills:
        if skill.lower() in jd_text:
            required_skills.append(skill)

    return required_skills


def calculate_skill_match(resume_skills, required_skills):
    """
    Compare resume skills with job-required skills.
    """

    resume_set = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    required_set = {
        normalize_skill(skill)
        for skill in required_skills
    }

    matched_skills = sorted(
        resume_set.intersection(required_set)
    )

    missing_skills = sorted(
        required_set.difference(resume_set)
    )

    if len(required_set) > 0:
        match_score = (
            len(matched_skills) /
            len(required_set)
        ) * 100
    else:
        match_score = 0

    return matched_skills, missing_skills, match_score


if __name__ == "__main__":

    print("===================================")
    print("AI JOB DESCRIPTION SKILL MATCHING")
    print("===================================")

    # Skills detected from the candidate's resume
    resume_skills = [
        "python",
        "java",
        "c++",
        "javascript",
        "html",
        "css",
        "mongodb",
        "git",
        "github",
        "machine learning",
        "deep learning",
        "pandas",
        "numpy",
        "power bi"
    ]

    # Read Job Description
    with open(
        "ai_ml/data/job_description.txt",
        "r",
        encoding="utf-8"
    ) as file:

        job_description = file.read()

    # Skills that our system knows how to detect
    known_skills = [
        "python",
        "java",
        "c++",
        "javascript",
        "html",
        "css",
        "react",
        "node.js",
        "sql",
        "mysql",
        "mongodb",
        "aws",
        "azure",
        "docker",
        "git",
        "github",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "power bi",
        "figma",
        "flask",
        "data structures",
        "algorithms",
        "dbms",
        "computer vision",
        "natural language processing",
        "cloud computing"
    ]

    # Detect required skills from JD
    required_skills = extract_required_skills(
        job_description,
        known_skills
    )

    # Compare resume and JD
    matched_skills, missing_skills, match_score = (
        calculate_skill_match(
            resume_skills,
            required_skills
        )
    )

    print("\nRequired Skills:")
    for skill in required_skills:
        print("-", skill)

    print("\nMatched Skills:")
    for skill in matched_skills:
        print("-", skill)

    print("\nMissing Skills:")
    for skill in missing_skills:
        print("-", skill)

    print(
        "\nSkill Match Score:",
        round(match_score, 2),
        "%"
    )

    print("\n===================================")