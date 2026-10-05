import re
import sys
from pathlib import Path
import pandas as pd

# Add current directory to path for local module imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parents[1]

if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from question_generator import generate_questions


# ============================================================
# 1. PARSE CANDIDATE PROJECTS & RESUME ENTITIES
# ============================================================

def parse_projects_from_text(projects_text, resume_skills=None):
    """
    Parse project strings or multiline text into structured project entities.
    Extracts project title, context (hackathon, internship, course),
    and identified technologies.
    """
    if not projects_text:
        return []

    if isinstance(projects_text, list):
        raw_lines = projects_text
    else:
        raw_lines = projects_text.splitlines()

    known_technologies = [
        "python", "java", "c++", "javascript", "react", "node.js",
        "sql", "mysql", "mongodb", "aws", "docker", "machine learning",
        "deep learning", "computer vision", "nlp", "pandas", "numpy",
        "power bi", "flask", "django", "opencv", "tensorflow", "pytorch",
        "html", "css"
    ]

    header_noise = {
        "/ training", "domain", "projects", "academic projects",
        "personal projects", "internships", "experience"
    }

    parsed_projects = []

    for raw in raw_lines:
        line = raw.strip()
        if not line or len(line) < 4:
            continue

        clean_line = re.sub(r"^[•▪◦\-\*\d\.\)]+\s*", "", line).strip()
        clean_lower = clean_line.lower()

        if clean_lower in header_noise or clean_lower.startswith("domain") or clean_lower.startswith("/ training"):
            continue

        # Skip multi-domain catalog headers (e.g. Cloud Computing | Web Development | AI)
        if "|" in clean_line and any(term in clean_lower for term in ["cloud computing", "artificial intelligence", "data science", "web development"]):
            continue

        # Extract context if present (e.g. Hackathon, Internship)
        context = "Personal/Academic Project"
        context_match = re.search(r"\(([^)]+)\)", clean_line)
        if context_match:
            context = context_match.group(1).strip()

        # Identify mentioned technologies
        detected_tech = []
        for tech in known_technologies:
            if re.search(r"\b" + re.escape(tech) + r"\b", clean_lower):
                detected_tech.append(tech.title())

        # If resume_skills provided and no tech explicitly in project title,
        # associate relevant skills from the candidate's profile
        if not detected_tech and resume_skills:
            if any(term in clean_lower for term in ["ai", "learning", "model", "vending", "detection"]):
                detected_tech = [s.title() for s in resume_skills if s.lower() in ["python", "machine learning", "pandas", "numpy"]][:2]
            elif any(term in clean_lower for term in ["web", "app", "form", "attendance", "portal"]):
                detected_tech = [s.title() for s in resume_skills if s.lower() in ["html", "css", "javascript", "flask", "react"]][:2]

        parsed_projects.append({
            "title": clean_line,
            "clean_name": re.sub(r"\([^)]+\)", "", clean_line).strip(),
            "technologies": detected_tech if detected_tech else ["Python/Software Development"],
            "context": context
        })

    return parsed_projects


# ============================================================
# 2. DYNAMIC PROJECT-BASED QUESTION GENERATION
# ============================================================

def generate_project_questions(project, difficulty="Medium"):
    """
    Generate in-depth architectural and technical questions tailored
    to a candidate's specific resume project.
    """
    p_name = project.get("clean_name", project.get("title", "your project"))
    techs = project.get("technologies", ["core technologies"])
    primary_tech = techs[0] if techs else "chosen technology"
    context = project.get("context", "project")

    questions_bank = {
        "Easy": [
            {
                "question": f"Can you give an overview of your project '{p_name}' and explain the primary objective it solves?",
                "topic": "Resume Projects",
                "difficulty": "Easy",
                "expected_keywords": f"objective, user, workflow, {primary_tech.lower()}, solution",
                "expected_answer": f"The candidate should describe the motivation behind '{p_name}', its primary end-users, core functionality, and how {primary_tech} was utilized to build the solution."
            },
            {
                "question": f"In '{p_name}', why did you choose {primary_tech} as part of your tech stack?",
                "topic": "Resume Projects",
                "difficulty": "Easy",
                "expected_keywords": f"{primary_tech.lower()}, libraries, suitability, alternative, performance",
                "expected_answer": f"The candidate should justify choosing {primary_tech} based on ease of development, ecosystem support, performance requirements, and compatibility with '{p_name}'."
            }
        ],
        "Medium": [
            {
                "question": f"Walk me through the system architecture and data pipeline of '{p_name}'. How do individual components communicate?",
                "topic": "Resume Projects",
                "difficulty": "Medium",
                "expected_keywords": f"architecture, pipeline, input, processing, output, {primary_tech.lower()}, data flow",
                "expected_answer": f"The candidate should detail the architectural layers of '{p_name}', tracing data flow from input/ingestion through processing components to the final output or UI."
            },
            {
                "question": f"What data preprocessing or input validation steps did you implement in '{p_name}' before feeding data into the core logic?",
                "topic": "Resume Projects",
                "difficulty": "Medium",
                "expected_keywords": "validation, preprocessing, cleaning, missing values, normalization, error handling",
                "expected_answer": "The candidate should specify concrete data cleaning techniques, edge-case validation, formatting, or feature transformations executed prior to processing."
            },
            {
                "question": f"What was the most challenging technical roadblock or bug you encountered while building '{p_name}', and how did you resolve it?",
                "topic": "Resume Projects",
                "difficulty": "Medium",
                "expected_keywords": "challenge, roadblock, debugging, root cause, resolution, trade-off",
                "expected_answer": "The candidate should clearly articulate a specific technical difficulty, the debugging or diagnostic method used to identify the root cause, and the engineering resolution implemented."
            }
        ],
        "Hard": [
            {
                "question": f"If you had to scale '{p_name}' to support 100,000 concurrent users or process a 100x larger dataset, what architectural bottlenecks would arise and how would you redesign it?",
                "topic": "Resume Projects",
                "difficulty": "Hard",
                "expected_keywords": "concurrency, scalability, caching, load balancing, asynchronous, database indexing, bottlenecks",
                "expected_answer": f"The candidate should identify performance bottlenecks in '{p_name}' (e.g. database locks, compute limits, synchronous operations) and propose horizontal scaling, caching (Redis), message queues, or distributed processing."
            },
            {
                "question": f"How did you evaluate the performance, correctness, or accuracy of '{p_name}'? What testing strategies or quantitative metrics did you use?",
                "topic": "Resume Projects",
                "difficulty": "Hard",
                "expected_keywords": "metrics, evaluation, unit testing, validation, benchmark, performance, accuracy",
                "expected_answer": "The candidate should describe their evaluation framework, such as quantitative metrics (accuracy, latency, throughput), unit/integration tests, or user acceptance benchmarks."
            }
        ]
    }

    # Return list of questions for requested difficulty, fallback to Medium if empty
    diff_key = difficulty.capitalize() if difficulty.capitalize() in questions_bank else "Medium"
    return questions_bank.get(diff_key, questions_bank["Medium"])


# ============================================================
# 3. DYNAMIC SKILL-GAP QUESTION GENERATION
# ============================================================

SKILL_QUESTION_TEMPLATES = {
    "sql": {
        "Easy": ("What is SQL and what is the difference between DDL and DML commands?", "SQL, DDL, DML, database, create, insert", "SQL is used to manage relational databases. DDL (Data Definition Language) defines schema like CREATE/ALTER, whereas DML (Data Manipulation Language) manages records like SELECT/INSERT/UPDATE."),
        "Medium": ("Explain indexing in relational databases. How does a B-Tree index optimize SQL query execution?", "index, B-Tree, search, lookup, binary, performance, execution plan", "Indexes allow the database engine to locate records without a full table scan. B-Trees keep keys sorted, reducing search time complexity from O(n) to O(log n)."),
        "Hard": ("How would you optimize a slow SQL query involving multi-table joins on tables with millions of rows?", "execution plan, EXPLAIN, indexing, join order, partitioning, caching", "Analyze the query plan with EXPLAIN, ensure join and filter columns are indexed, eliminate unnecessary columns/subqueries, and consider partitioning or denormalization if appropriate.")
    },
    "docker": {
        "Easy": ("What is Docker and how does containerization differ from traditional virtualization?", "Docker, container, virtualization, OS kernel, lightweight, image", "Docker packages applications with dependencies into isolated containers sharing the host OS kernel, making them significantly lighter and faster than virtual machines."),
        "Medium": ("Explain the difference between a Dockerfile, an Image, and a Container. What is the role of docker-compose?", "Dockerfile, image, container, instance, compose, multi-container", "A Dockerfile is a text recipe, an image is a compiled immutable blueprint, and a container is an active running instance. Docker Compose coordinates multi-container services."),
        "Hard": ("How do you implement multi-stage Docker builds to minimize production image size and enhance security?", "multi-stage, build stage, production image, dependencies, security, attack surface", "Multi-stage builds use multiple FROM directives in a single Dockerfile, compiling dependencies in an initial builder stage and copying only compiled artifacts to a minimal production base image.")
    },
    "aws": {
        "Easy": ("What is AWS and what are core services like EC2, S3, and RDS used for?", "AWS, cloud, EC2, S3, RDS, compute, storage, database", "AWS is a cloud platform. EC2 provides resizable virtual compute servers, S3 offers scalable object storage, and RDS is a managed relational database service."),
        "Medium": ("Explain the difference between horizontal and vertical scaling in AWS, and how Auto Scaling Groups work.", "scaling, EC2, auto scaling, horizontal, vertical, load balancer, traffic", "Vertical scaling upgrades instance capacity (CPU/RAM), while horizontal scaling adds more instances. Auto Scaling automatically adjusts instance count based on CloudWatch metrics."),
        "Hard": ("How would you design a fault-tolerant, highly available architecture on AWS across multiple Availability Zones?", "high availability, multi-AZ, ALB, load balancer, failover, redundancy, disaster recovery", "Deploy redundant EC2 instances across multiple AZs behind an Application Load Balancer, use Multi-AZ RDS for automated database failover, and store static assets in S3 with CloudFront CDN.")
    },
    "machine learning": {
        "Easy": ("What is the difference between supervised, unsupervised, and reinforcement learning?", "supervised, unsupervised, reinforcement, labeled data, clustering, reward", "Supervised learning trains on labeled input-output pairs, unsupervised learning finds patterns in unlabeled data, and reinforcement learning trains agents via rewards and penalties."),
        "Medium": ("How do you detect and handle overfitting in a machine learning model?", "overfitting, cross-validation, regularization, L1, L2, dropout, pruning", "Overfitting occurs when a model memorizes training noise. It is detected via train-validation divergence and mitigated using regularization (L1/L2, Dropout), cross-validation, or simpler models."),
        "Hard": ("Explain the bias-variance tradeoff mathematically and how ensemble methods like Random Forest and Gradient Boosting address it.", "bias, variance, tradeoff, ensemble, random forest, boosting, bagging", "Bias is error from erroneous assumptions; variance is sensitivity to training fluctuations. Random Forests reduce variance via bagging, while Gradient Boosting iteratively reduces bias.")
    },
    "algorithms": {
        "Easy": ("What is Big-O notation and why is analyzing time complexity important in software engineering?", "Big-O, time complexity, space complexity, asymptotic, efficiency, worst-case", "Big-O notation describes the upper bound of algorithm runtime as input size scales, enabling engineers to compare algorithmic efficiency independently of hardware."),
        "Medium": ("Compare Dynamic Programming with Divide and Conquer. What conditions must a problem satisfy to use DP?", "dynamic programming, divide and conquer, memoization, overlapping subproblems, optimal substructure", "Both divide problems into subproblems. Dynamic programming requires overlapping subproblems and optimal substructure, caching intermediate results via memoization or tabulation to avoid redundant compute."),
        "Hard": ("Explain Dijkstra's shortest path algorithm. How does using a min-heap priority queue affect its time complexity?", "Dijkstra, graph, shortest path, priority queue, min-heap, relaxation, O((V+E) log V)", "Dijkstra finds the shortest path in non-negative weighted graphs using greedy edge relaxation. A min-heap reduces complexity from O(V^2) to O((V + E) log V) by speeding up minimum-distance vertex selection.")
    }
}


def generate_skill_gap_question(skill, difficulty="Medium"):
    """
    Generate a dynamic technical interview question targeting a missing JD skill.
    """
    skill_clean = skill.lower().strip()
    diff_key = difficulty.capitalize() if difficulty.capitalize() in ["Easy", "Medium", "Hard"] else "Medium"

    # Match specific known template
    if skill_clean in SKILL_QUESTION_TEMPLATES:
        q_text, kws, exp_ans = SKILL_QUESTION_TEMPLATES[skill_clean][diff_key]
        return {
            "question": q_text,
            "topic": skill.title(),
            "difficulty": diff_key,
            "expected_keywords": kws,
            "expected_answer": exp_ans,
            "source": "skill_gap_dynamic"
        }

    # Dynamic fallback template for any arbitrary missing technical skill
    generic_templates = {
        "Easy": (
            f"What is {skill.title()} and what primary problems does it solve in modern software development?",
            f"{skill.lower()}, purpose, architecture, advantage, development",
            f"The candidate should describe the core definition, primary use case, and key benefits of using {skill.title()}."
        ),
        "Medium": (
            f"How is {skill.title()} typically integrated into an end-to-end production tech stack, and what are its key features?",
            f"{skill.lower()}, integration, workflow, configuration, production, best practices",
            f"The candidate should outline common integration workflows, architectural role, and configuration practices when working with {skill.title()}."
        ),
        "Hard": (
            f"What performance bottlenecks or architectural challenges commonly arise when scaling applications built with {skill.title()}, and how do you resolve them?",
            f"{skill.lower()}, bottlenecks, scalability, optimization, troubleshooting, architecture",
            f"The candidate should discuss advanced architectural considerations, latency/concurrency limits, and optimization techniques specific to {skill.title()}."
        )
    }

    q_text, kws, exp_ans = generic_templates[diff_key]
    return {
        "question": q_text,
        "topic": skill.title(),
        "difficulty": diff_key,
        "expected_keywords": kws,
        "expected_answer": exp_ans,
        "source": "skill_gap_dynamic"
    }


# ============================================================
# 4. COMPREHENSIVE PERSONALIZED INTERVIEW BANK GENERATOR
# ============================================================

def generate_personalized_interview_bank(
    resume_skills,
    projects_text,
    missing_skills,
    required_skills,
    difficulty="Medium"
):
    """
    Construct a complete dynamic question bank specifically tailored to the
    candidate's exact resume projects, detected skills, and missing JD requirements.
    """
    bank = []

    # 1. Project-Specific Questions (Customized to this candidate's projects)
    parsed_projects = parse_projects_from_text(projects_text, resume_skills)

    for proj in parsed_projects:
        for diff in ["Easy", "Medium", "Hard"]:
            proj_qs = generate_project_questions(proj, difficulty=diff)
            for q in proj_qs:
                q["source"] = "resume_project_dynamic"
                q["project_name"] = proj["clean_name"]
                bank.append(q)

    # 2. Skill-Gap Probing Questions (Customized to missing JD skills)
    for skill in missing_skills:
        for diff in ["Easy", "Medium", "Hard"]:
            skill_q = generate_skill_gap_question(skill, difficulty=diff)
            bank.append(skill_q)

    # 3. Candidate Core Skill Verification Questions
    for skill in resume_skills:
        skill_clean = skill.lower().strip()
        if skill_clean in SKILL_QUESTION_TEMPLATES:
            for diff in ["Easy", "Medium", "Hard"]:
                q_text, kws, exp_ans = SKILL_QUESTION_TEMPLATES[skill_clean][diff]
                bank.append({
                    "question": q_text,
                    "topic": skill.title(),
                    "difficulty": diff,
                    "expected_keywords": kws,
                    "expected_answer": exp_ans,
                    "source": "core_skill_dynamic"
                })

    return bank


# ============================================================
# 5. UNIFIED QUESTION RETRIEVAL (BACKWARD COMPATIBLE & DYNAMIC)
# ============================================================

def generate_personalized_questions(
    candidate_skills,
    missing_skills,
    topic,
    difficulty="Medium",
    number_of_questions=3,
    projects_text=None
):
    """
    Unified function supporting both static CSV question fallback
    and dynamic AI question generation based on candidate profile.
    """
    results = []

    # 1. Generate project questions if projects text is provided
    if projects_text:
        projects = parse_projects_from_text(projects_text, candidate_skills)
        if projects:
            proj_qs = generate_project_questions(projects[0], difficulty=difficulty)
            for q in proj_qs:
                results.append(q["question"])

    # 2. Generate questions from skill gaps if applicable
    if missing_skills and len(results) < number_of_questions:
        for skill in missing_skills[:2]:
            q_obj = generate_skill_gap_question(skill, difficulty=difficulty)
            results.append(q_obj["question"])

    # 3. Retrieve standard topic questions from CSV as fallback
    csv_qs = generate_questions(topic, difficulty, number_of_questions)
    results.extend(csv_qs)

    # Remove duplicates preserving order
    deduped = list(dict.fromkeys(results))
    return deduped[:number_of_questions]


# ============================================================
# 6. STANDALONE VERIFICATION AND DEMO
# ============================================================

if __name__ == "__main__":
    print("============================================================")
    print("         AI DYNAMIC QUESTION GENERATION ENGINE              ")
    print("============================================================")

    # Sample Candidate Profile 1 (Rakshana Resume format)
    rakshana_skills = ["python", "java", "c++", "html"]
    rakshana_projects = """
    Smart Curriculum Activity & Attendance App (SIH Hackathon)
    Student Performance Analyzer (Internship)
    Institutional Data Analysis & Verification Role (Internship)
    """
    missing_skills_example = ["docker", "aws", "sql"]

    print("\n--- TEST: DYNAMIC PROJECT QUESTIONS GENERATION ---")
    parsed = parse_projects_from_text(rakshana_projects, rakshana_skills)
    print(f"Detected {len(parsed)} structured projects:")
    for p in parsed:
        print(f"  * {p['clean_name']} | Tech: {', '.join(p['technologies'])} | Context: {p['context']}")

    first_proj = parsed[1]  # Student Performance Analyzer
    print(f"\nGenerated questions for: '{first_proj['clean_name']}' [Medium]:")
    proj_questions = generate_project_questions(first_proj, difficulty="Medium")
    for i, q in enumerate(proj_questions, 1):
        print(f"  {i}. {q['question']}")
        print(f"     Expected Terms: {q['expected_keywords']}")

    print("\n--- TEST: DYNAMIC SKILL-GAP QUESTIONS ---")
    for skill in missing_skills_example:
        gap_q = generate_skill_gap_question(skill, difficulty="Hard")
        print(f"  Skill Gap [{skill.upper()}] (Hard): {gap_q['question']}")

    print("\n--- TEST: UNIFIED QUESTION GENERATOR ---")
    unified_qs = generate_personalized_questions(
        candidate_skills=rakshana_skills,
        missing_skills=missing_skills_example,
        topic="Algorithms",
        difficulty="Hard",
        number_of_questions=4,
        projects_text=rakshana_projects
    )
    for idx, q_text in enumerate(unified_qs, 1):
        print(f"  {idx}. {q_text}")

    print("\n============================================================")
    print("         DYNAMIC QUESTION ENGINE READY                      ")
    print("============================================================")