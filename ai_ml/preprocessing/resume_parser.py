import re
import PyPDF2


# ============================================================
# 1. EXTRACT TEXT FROM PDF
# ============================================================

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a resume PDF.
    """

    text = ""

    with open(pdf_path, "rb") as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# ============================================================
# 2. EXTRACT TECHNICAL SKILLS
# ============================================================

def extract_skills(text):
    """
    Extract known technical skills from resume text.
    Supports Software, AI/ML, VLSI/Hardware, Embedded Systems, Cloud/DevOps, and Data Engineering.
    """

    skills_list = [
        # VLSI & Hardware Design
        "verilog", "systemverilog", "vhdl", "rtl", "rtl design", "digital electronics",
        "fpga", "asic", "vlsi", "cadence", "synopsys", "vivado", "modelsim", "quartus",
        "analog electronics", "microcontroller", "embedded c", "embedded systems", "arm",
        "microprocessor", "pcb design", "matlab", "simulink", "spice", "ltspice",

        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "ci/cd", "linux", "bash", "git", "github", "gitlab",
        "prometheus", "grafana", "cloud computing",

        # Programming Languages & Core Computer Science
        "python", "java", "c++", "c", "c#", ".net", "javascript", "typescript",
        "html", "css", "data structures", "algorithms", "dbms", "operating systems",
        "computer networks", "system design",

        # Web & Frameworks
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "fastapi", "spring boot", "rest api", "graphql", "sql", "mysql",
        "postgresql", "mongodb", "redis",

        # AI / ML / Data
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "pandas", "numpy", "power bi", "tableau", "spark",
        "hadoop", "kafka", "opencv", "computer vision", "natural language processing",
        "nlp",

        # Cybersecurity & Tools
        "cryptography", "network security", "penetration testing", "wireshark",
        "ethical hacking", "firewall", "figma"
    ]

    text_lower = text.lower()
    detected_skills = []

    # Sort longest first to avoid partial conflicts (e.g. 'digital electronics' before 'electronics')
    skills_sorted = sorted(skills_list, key=lambda s: len(s), reverse=True)

    for skill in skills_sorted:
        # Match using word boundaries or character delimiters
        pattern = r"(?<![a-zA-Z0-9_])" + re.escape(skill) + r"(?![a-zA-Z0-9_])"
        if re.search(pattern, text_lower):
            if skill not in detected_skills:
                detected_skills.append(skill)

    return detected_skills


# ============================================================
# 3. DETECT RESUME SECTIONS
# ============================================================

def extract_sections(text):
    """
    Detect important resume sections.
    """

    sections = {}

    section_names = [
        "objective",
        "education",
        "skills",
        "projects",
        "internship",
        "experience",
        "certifications",
        "achievements",
        "declaration"
    ]

    text_lower = text.lower()

    for section in section_names:

        pattern = r"\b" + re.escape(section) + r"\b"

        if re.search(pattern, text_lower):

            sections[section] = True

        else:

            sections[section] = False

    return sections


# ============================================================
# 4. EXTRACT PROJECTS
# ============================================================

def extract_projects(text):
    """
    Extract projects from the Projects section.

    Handles formats such as:

    Projects
    • Project 1
    • Project 2

    and:

    Projects • Project 1
    • Project 2
    """

    lines = text.splitlines()

    project_lines = []

    inside_projects = False

    end_sections = [
        "declaration",
        "achievements",
        "certifications",
        "education",
        "skills",
        "internship",
        "experience",
        "objective"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Normalize spaces
        normalized_line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        normalized_lower = normalized_line.lower()

        # ====================================================
        # Check whether this line contains the Projects heading
        # ====================================================

        projects_match = re.search(
            r"\bprojects\b",
            normalized_lower
        )

        if projects_match and not inside_projects:

            # Make sure this is actually a section heading.
            # It should normally appear near the beginning
            # of the line.
            before_projects = normalized_lower[
                :projects_match.start()
            ].strip()

            if before_projects == "":

                inside_projects = True

                # Get everything after "Projects"
                remaining_text = normalized_line[
                    projects_match.end():
                ].strip()

                # Remove leading spaces / bullets
                remaining_text = re.sub(
                    r"^[•▪◦\-\*]+\s*",
                    "",
                    remaining_text
                ).strip()

                if remaining_text:

                    project_lines.append(
                        remaining_text
                    )

                continue

        # ====================================================
        # Stop at the next section
        # ====================================================

        if inside_projects:

            if normalized_lower in end_sections:

                break

            # If another section heading appears at the
            # beginning of the line, stop.
            section_match = re.match(
                r"^(declaration|achievements|certifications|"
                r"education|skills|internship|experience|objective)"
                r"\b",
                normalized_lower
            )

            if section_match:

                break

            # =================================================
            # Remove bullet symbols
            # =================================================

            cleaned_line = re.sub(
                r"^[•▪◦\-\*]+\s*",
                "",
                normalized_line
            ).strip()

            if not cleaned_line:
                continue

            # Ignore section heading
            if cleaned_line.lower() in [
                "project",
                "projects"
            ]:
                continue

            # Ignore declaration text
            if cleaned_line.lower().startswith(
                "i hereby declare"
            ):
                continue

            project_lines.append(
                cleaned_line
            )

    return "\n".join(project_lines)


# ============================================================
# 5. COMPLETE RESUME ANALYSIS
# ============================================================

def analyze_resume(resume_path):
    """
    Perform complete resume analysis.
    """

    resume_text = extract_text_from_pdf(
        resume_path
    )

    skills = extract_skills(
        resume_text
    )

    sections = extract_sections(
        resume_text
    )

    projects = extract_projects(
        resume_text
    )

    return (
        resume_text,
        skills,
        sections,
        projects
    )


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print("AI RESUME ANALYSIS")
    print("===================================")

    resume_path = input(
        "\nEnter the resume PDF path: "
    ).strip()

    try:

        (
            resume_text,
            skills,
            sections,
            projects
        ) = analyze_resume(
            resume_path
        )

        # ====================================================
        # DISPLAY SKILLS
        # ====================================================

        print("\nDetected Skills:")

        if skills:

            for skill in skills:

                print("-", skill)

        else:

            print(
                "No known technical skills detected."
            )

        # ====================================================
        # DISPLAY SECTIONS
        # ====================================================

        print("\nResume Sections:")

        for section, found in sections.items():

            if found:

                print("-", section)

        # ====================================================
        # DISPLAY PROJECTS
        # ====================================================

        print("\nExtracted Projects:")

        if projects:

            for project in projects.splitlines():

                print("-", project)

        else:

            print(
                "No Projects Section Found."
            )

        print("\n===================================")
        print("RESUME ANALYSIS COMPLETED")
        print("===================================")

    except FileNotFoundError:

        print(
            "\nERROR: Resume file was not found."
        )

        print(
            "Please check the PDF path and try again."
        )

    except Exception as error:

        print(
            "\nERROR while processing resume:"
        )

        print(error)