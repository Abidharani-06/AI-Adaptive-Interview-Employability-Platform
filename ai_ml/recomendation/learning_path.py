"""
Personalized Learning Roadmap & Action Plan Generator
------------------------------------------------------
Generates a structured, candidate-specific learning path and multi-week improvement plan
derived dynamically from:
1. Prioritized technical skill gaps (High, Medium, Low priority)
2. Demonstrated weak interview topics
3. HR / STAR behavioral performance
4. Speech pacing and acoustic delivery observations
5. Visual behavior observations

Configurable schedule duration, milestone tracking, and practical project tasks.
"""

from typing import Dict, List, Any, Optional

# Knowledge curriculum database for common tech skills
CURRICULUM_DATABASE = {
    "data structures": {
        "title": "Data Structures & Memory Models",
        "subtopics": ["Arrays & Strings", "Linked Lists", "Stacks & Queues", "Binary Trees & BST", "Graphs & Adjacency", "Hash Maps & Collision"],
        "practice_tasks": ["Implement an LRU Cache from scratch", "Traverse binary trees iteratively and recursively", "Detect cycles in directed and undirected graphs"],
        "estimated_hours": 18
    },
    "algorithms": {
        "title": "Algorithms & Computational Complexity",
        "subtopics": ["Time/Space Big-O Analysis", "Divide & Conquer", "Dynamic Programming & Memoization", "Greedy Strategies", "Graph Traversals (BFS/DFS)", "Dijkstra & Shortest Path"],
        "practice_tasks": ["Solve classic DP problems (Knapsack, Longest Common Subsequence)", "Implement QuickSort and MergeSort with in-place partitioning"],
        "estimated_hours": 20
    },
    "sql": {
        "title": "Relational Databases & SQL Mastery",
        "subtopics": ["SELECT, Filter & WHERE clauses", "INNER/LEFT/RIGHT JOINs", "GROUP BY, HAVING & Aggregations", "Subqueries & Common Table Expressions (CTEs)", "Window Functions (ROW_NUMBER, RANK)", "Indexing & Query Optimization"],
        "practice_tasks": ["Write complex multi-table queries with CTEs and Window Functions", "Analyze query execution plans with EXPLAIN and design composite indexes"],
        "estimated_hours": 12
    },
    "dbms": {
        "title": "Database Management Systems Architecture",
        "subtopics": ["ACID Properties", "Normalization (1NF to BCNF)", "Transaction Concurrency & Locking", "Write-Ahead Logging", "NoSQL vs Relational Trade-offs"],
        "practice_tasks": ["Design a normalized schema for an e-commerce platform", "Compare locking vs MVCC in PostgreSQL"],
        "estimated_hours": 10
    },
    "docker": {
        "title": "Containerization with Docker",
        "subtopics": ["Container vs VM Architecture", "Dockerfile Instructions & Multi-Stage Builds", "Docker Image Optimization", "Volumes & Persistent Storage", "Docker Networking", "Docker Compose Orchestration"],
        "practice_tasks": ["Containerize a multi-tier web application with Redis and PostgreSQL using Docker Compose", "Minimize image footprint using Alpine Linux and multi-stage builds"],
        "estimated_hours": 10
    },
    "kubernetes": {
        "title": "Container Orchestration with Kubernetes",
        "subtopics": ["Pods, Deployments & ReplicaSets", "Services & Ingress Controllers", "ConfigMaps & Secrets", "Persistent Volumes (PV/PVC)", "Health Probes (Liveness/Readiness)", "Helm Charts"],
        "practice_tasks": ["Deploy a microservice cluster with horizontal pod autoscaling", "Configure rolling updates and zero-downtime rollbacks"],
        "estimated_hours": 16
    },
    "machine learning": {
        "title": "Applied Machine Learning Systems",
        "subtopics": ["Feature Engineering & Preprocessing", "Supervised Learning (Regression & Classification)", "Decision Trees & Random Forests", "Gradient Boosting (XGBoost/LightGBM)", "Cross-Validation & Hyperparameter Tuning", "Model Evaluation (ROC-AUC, F1, Precision/Recall)"],
        "practice_tasks": ["Build an end-to-end classification pipeline with Scikit-Learn", "Implement cross-validation with grid search on tabular datasets"],
        "estimated_hours": 20
    },
    "deep learning": {
        "title": "Deep Learning & Neural Architectures",
        "subtopics": ["Backpropagation & Gradient Descent", "CNNs for Computer Vision", "RNNs & LSTMs for Sequences", "Attention Mechanisms & Transformers", "Regularization (Dropout, Batch Normalization)", "PyTorch Training Loops"],
        "practice_tasks": ["Train a CNN in PyTorch for image classification", "Implement self-attention layer from scratch"],
        "estimated_hours": 22
    },
    "natural language processing": {
        "title": "Natural Language Processing (NLP)",
        "subtopics": ["Tokenization & Lemmatization", "TF-IDF & Word Embeddings (Word2Vec)", "Transformer Models (BERT, RoBERTa)", "Hugging Face Pipelines", "Text Classification & Named Entity Recognition", "Semantic Similarity Models"],
        "practice_tasks": ["Fine-tune a Hugging Face Transformer for sentence classification", "Build a semantic search engine using sentence-transformers"],
        "estimated_hours": 18
    },
    "computer vision": {
        "title": "Computer Vision Engineering",
        "subtopics": ["OpenCV Image Processing", "Edge & Contour Detection", "MediaPipe Landmark Tracking", "Face & Pose Detection", "Object Detection (YOLO)", "Video Stream Optimization"],
        "practice_tasks": ["Implement a real-time facial feature tracking application using OpenCV & MediaPipe", "Build a movement displacement tracking pipeline"],
        "estimated_hours": 16
    },
    "system design": {
        "title": "Scalable System Architecture & Design",
        "subtopics": ["Client-Server & REST Architecture", "Load Balancers & Reverse Proxies", "Caching Strategies (Redis/Memcached)", "Database Sharding & Replication", "Message Queues (Kafka/RabbitMQ)", "Rate Limiting & Microservice Resiliency"],
        "practice_tasks": ["Design a distributed URL shortener (TinyURL)", "Architect a real-time notification service with WebSockets and Redis"],
        "estimated_hours": 18
    },
    "flask": {
        "title": "Backend Development with Flask",
        "subtopics": ["Routing, Blueprints & App Factories", "Request Lifecycle & Middleware", "SQLAlchemy ORM & Migrations", "JWT Authentication", "RESTful API Best Practices", "Unit Testing with Pytest"],
        "practice_tasks": ["Build a CRUD REST API with JWT authentication and SQLite/PostgreSQL", "Write unit test suite for all endpoints with coverage > 85%"],
        "estimated_hours": 12
    },
    "python": {
        "title": "Advanced Python Programming",
        "subtopics": ["Generators, Iterators & Decorators", "Object-Oriented Design & Metaclasses", "Type Annotations & Mypy", "Concurrency (Threading, Multiprocessing, Asyncio)", "Context Managers & Memory Profiling"],
        "practice_tasks": ["Implement a custom thread-safe caching decorator", "Write an asynchronous data scraper with asyncio and aiohttp"],
        "estimated_hours": 14
    },
    "verilog": {
        "title": "Verilog HDL & Hardware Modeling",
        "subtopics": ["Gate-Level & Dataflow Modeling", "Behavioral Modeling & Always Blocks", "Blocking vs Non-Blocking Assignments", "Finite State Machines (Moore & Mealy)", "Testbench Architecture & Clock Generation", "Synthesis Guidelines & RTL Constraints"],
        "practice_tasks": ["Design and simulate a parameterizable FIFO buffer in Verilog", "Implement a Mealy FSM sequence detector with testbench verification"],
        "estimated_hours": 18
    },
    "vhdl": {
        "title": "VHDL Design & Verification",
        "subtopics": ["Entity & Architecture Declarations", "Signals vs Variables", "Concurrent Statements & Processes", "Structural Modeling & Component Instantiation", "VHDL Packages & Testbenches", "Timing Analysis & Clock Constraints"],
        "practice_tasks": ["Design an 8-bit Arithmetic Logic Unit (ALU) in VHDL", "Simulate clock-synchronized register transfer operations"],
        "estimated_hours": 16
    },
    "rtl": {
        "title": "RTL Architecture & Digital Design",
        "subtopics": ["Register Transfer Level Principles", "Clock Domain Crossing (CDC)", "Static Timing Analysis (STA)", "Setup & Hold Time Budgets", "Pipelining & Critical Path Optimization", "Linting & CDC Verification Rules"],
        "practice_tasks": ["Pipeline a multi-stage multiplier to optimize maximum operating frequency", "Analyze STA timing violations and fix setup/hold slack"],
        "estimated_hours": 20
    },
    "digital electronics": {
        "title": "Digital Electronics & Logic Design",
        "subtopics": ["Boolean Algebra & De Morgan's Laws", "Combinational Logic & Karnaugh Maps", "Multiplexers, Encoders & Decoders", "Flip-Flops, Latches & Registers", "Synchronous & Asynchronous Counters", "Propagation Delay & Metastability"],
        "practice_tasks": ["Design a 4-bit synchronous up/down counter with reset", "Minimize 5-variable logic equations using K-maps"],
        "estimated_hours": 14
    },
    "fpga": {
        "title": "FPGA Prototyping & Vivado Flow",
        "subtopics": ["FPGA Internal Architecture (CLBs, LUTs, BRAM, DSP)", "Xilinx Vivado Synthesis & Implementation", "Pin Constraints & XDC Timing Constraints", "Hardware Debugging with Integrated Logic Analyzer (ILA)", "Bitstream Generation & Board Flashing", "IP Integrator & AXI Bus Protocol"],
        "practice_tasks": ["Implement and flash a UART communication controller on FPGA hardware", "Use Vivado ILA to capture real-time hardware bus transactions"],
        "estimated_hours": 18
    },
    "embedded systems": {
        "title": "Embedded Systems Architecture & Firmware",
        "subtopics": ["Microcontroller Architecture (ARM Cortex-M)", "GPIO, Timers, PWM & ADC/DAC Peripherals", "Serial Communication (UART, SPI, I2C)", "Interrupt Handling & Nested Vector Interrupt Controllers", "Real-Time Operating Systems (FreeRTOS Tasks & Queues)", "Memory Mapping & Linker Scripts"],
        "practice_tasks": ["Write bare-metal drivers for I2C sensor interfacing", "Create a multi-task FreeRTOS application with semaphores and message queues"],
        "estimated_hours": 18
    },
    "linux": {
        "title": "Linux Systems & Shell Engineering",
        "subtopics": ["Bash Scripting & Automation", "Process Management (fork, exec, signals)", "File System Permissions & Inodes", "System Monitoring (top, htop, vmstat, strace)", "Networking Utilities & Socket Programming", "Kernel Space vs User Space"],
        "practice_tasks": ["Write an automated server health monitoring daemon in Bash", "Trace system calls and performance bottlenecks using strace"],
        "estimated_hours": 12
    },
    "aws": {
        "title": "AWS Cloud Engineering & Infrastructure",
        "subtopics": ["IAM Policies, Roles & Security Groups", "EC2 Compute & Auto Scaling", "S3 Scalable Storage & CloudFront", "VPC Networking, Subnets & Routing Tables", "RDS & DynamoDB Database Services", "ECS, ECR & Containerized Cloud Deployment"],
        "practice_tasks": ["Architect a fault-tolerant multi-AZ web tier behind an Application Load Balancer", "Automate infrastructure provisioning using AWS CLI / CloudFormation"],
        "estimated_hours": 16
    }
}


class LearningPathGenerator:
    """
    Generates dynamic, candidate-specific learning roadmaps and structured multi-week practice plans.
    """

    def __init__(self, curriculum_db: Optional[Dict[str, Any]] = None):
        self.curriculum = curriculum_db or CURRICULUM_DATABASE

    def get_skill_module(self, skill_name: str, priority: str = "MEDIUM") -> Dict[str, Any]:
        """
        Retrieves or dynamically constructs a structured learning module for a specific skill.
        """
        s_clean = skill_name.lower().strip()
        if s_clean in self.curriculum:
            data = dict(self.curriculum[s_clean])
            data["skill"] = skill_name
            data["priority"] = priority
            return data

        # Fallback curriculum generator for any unindexed skill
        capitalized = skill_name.title()
        return {
            "skill": skill_name,
            "title": f"{capitalized} Foundations & Application",
            "priority": priority,
            "subtopics": [
                f"{capitalized} Core Concepts & Syntax",
                f"{capitalized} Architecture & Best Practices",
                f"Hands-on Implementation with {capitalized}",
                f"Testing, Debugging & Performance Optimization",
                f"Common {capitalized} Technical Interview Questions"
            ],
            "practice_tasks": [
                f"Build a standalone prototype utilizing {capitalized}",
                f"Complete 5 coding challenges or practical drills involving {capitalized}"
            ],
            "estimated_hours": 12
        }

    def generate_roadmap(
        self,
        skill_gap_analysis: Dict[str, Any],
        component_scores: Optional[Dict[str, float]] = None,
        duration_weeks: int = 5
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive learning roadmap and personalized week-by-week action schedule.
        """
        comp = component_scores or {}
        prioritized_gaps = skill_gap_analysis.get("prioritized_gaps", [])

        # 1. Generate topic-level modules
        learning_modules = []
        total_estimated_hours = 0
        for gap in prioritized_gaps:
            mod = self.get_skill_module(gap["skill"], priority=gap.get("priority", "MEDIUM"))
            mod["reason"] = gap.get("reason", "Target skill gap identified.")
            learning_modules.append(mod)
            total_estimated_hours += mod.get("estimated_hours", 12)

        # 2. Dynamically determine candidate focus areas based on actual component scores
        tech_score = comp.get("technical", 70.0)
        hr_score = comp.get("hr_nlp", 70.0)
        speech_score = comp.get("speech", 70.0)
        cv_score = comp.get("computer_vision", 70.0)
        match_score = comp.get("resume_jd", 70.0)

        # 3. Construct Dynamic Multi-Week Action Plan
        weekly_plan = []
        high_skills = skill_gap_analysis.get("high_priority", [])
        med_skills = skill_gap_analysis.get("medium_priority", [])

        # Week 1: Core Foundation & Highest Priority Technical Gap
        w1_focus = high_skills[:2] if high_skills else (med_skills[:2] if med_skills else ["Core Algorithms & Data Structures"])
        weekly_plan.append({
            "week": 1,
            "theme": "High-Priority Technical Foundations",
            "target_topics": w1_focus,
            "objectives": [
                f"Review foundational theory and implementation patterns for {', '.join(w1_focus)}.",
                "Solve 8-10 targeted problem drills focusing on edge cases and optimal complexity.",
                "Conduct self-timed coding exercises without IDE auto-complete."
            ],
            "milestone": f"Demonstrate mastery of core implementation in {', '.join(w1_focus)}."
        })

        # Week 2: Secondary Technical Skills & Hands-On Implementation
        w2_focus = high_skills[2:4] if len(high_skills) > 2 else (med_skills[:2] if med_skills else ["System Architecture & Backend Flow"])
        weekly_plan.append({
            "week": 2,
            "theme": "Practical Application & Secondary Skill Gaps",
            "target_topics": w2_focus,
            "objectives": [
                f"Develop a mini-project or integration testing pipeline with {', '.join(w2_focus)}.",
                "Integrate database/caching layer with clean separation of concerns.",
                "Document technical decisions and trade-offs for technical discussion."
            ],
            "milestone": f"Completed working code repository showcasing {', '.join(w2_focus)}."
        })

        # Week 3: Behavioral & STAR Narrative Construction (Conditioned on HR score)
        if hr_score < 75.0 or "hr_nlp" not in comp:
            w3_theme = "Behavioral Interview Mastery & STAR Structuring"
            w3_objectives = [
                "Map 4 major academic/project experiences into the STAR framework (Situation, Task, Action, Result).",
                "Emphasize personal contributions ('I built', 'I optimized') rather than generic team descriptions.",
                "Practice direct answer delivery in under 90 seconds to maintain conciseness."
            ]
        else:
            w3_theme = "Advanced Behavioral Alignment & Leadership Scenarios"
            w3_objectives = [
                "Refine behavioral narratives for conflict resolution and technical trade-off scenarios.",
                "Align project achievements with target company values and engineering culture.",
                "Practice answers addressing technical debt, refactoring decisions, and deadlines."
            ]
        weekly_plan.append({
            "week": 3,
            "theme": w3_theme,
            "target_topics": ["STAR Technique", "Project Impact Communication", "Behavioral Relevance"],
            "objectives": w3_objectives,
            "milestone": "4 polished STAR behavioral stories rehearsed and validated."
        })

        # Week 4: Speech Pacing, Fillers & Delivery Control (Conditioned on Speech/CV)
        if speech_score < 75.0 or cv_score < 75.0:
            w4_theme = "Verbal Delivery & Observable Interview Presence"
            w4_objectives = [
                "Record 3 spoken responses; analyze speaking rate to maintain 130–150 WPM.",
                "Practice structured pauses (1–2 seconds) to eliminate verbal fillers ('um', 'like', 'actually').",
                "Ensure webcam is at eye level; practice maintaining camera-facing gaze during responses."
            ]
        else:
            w4_theme = "Executive Delivery & Communication Polish"
            w4_objectives = [
                "Practice vocal inflection, steady volume, and concise framing for complex technical concepts.",
                "Maintain upright, centered upper-body posture and stable physical presence throughout responses.",
                "Conduct timed 2-minute project walkthroughs with smooth transitions."
            ]
        weekly_plan.append({
            "week": 4,
            "theme": w4_theme,
            "target_topics": ["Speech Cadence", "Filler Word Elimination", "Observable Camera Presence"],
            "objectives": w4_objectives,
            "milestone": "Consistent 130-150 WPM delivery with < 1.5 fillers per 100 words and stable visual presence."
        })

        # Week 5: Comprehensive Multimodal Mock Reassessment
        weekly_plan.append({
            "week": 5,
            "theme": "Full-Length Multimodal Mock Interview Reassessment",
            "target_topics": ["Full Mock Technical Round", "HR Round", "Multimodal Evaluation"],
            "objectives": [
                "Complete a full adaptive technical round covering previous weak topics.",
                "Complete a timed behavioral interview with live audio and video recording.",
                "Review automated placement readiness report and compare progress against initial baseline."
            ],
            "milestone": "Full-length mock interview completed with target readiness score improvement."
        })

        # Adjust plan length if user specified custom duration
        if duration_weeks > 5:
            for extra_w in range(6, duration_weeks + 1):
                weekly_plan.append({
                    "week": extra_w,
                    "theme": f"Advanced Specialization & Portfolio Polish (Week {extra_w})",
                    "target_topics": ["Production Deployment", "System Scaling Drills"],
                    "objectives": [
                        "Deploy end-to-end application to cloud infrastructure.",
                        "Conduct peer code reviews and architectural mock discussions."
                    ],
                    "milestone": "Deployed portfolio artifact ready for technical review."
                })
        elif duration_weeks < 5:
            weekly_plan = weekly_plan[:duration_weeks]

        return {
            "total_modules": len(learning_modules),
            "total_estimated_hours": total_estimated_hours,
            "learning_modules": learning_modules,
            "duration_weeks": len(weekly_plan),
            "weekly_action_plan": weekly_plan,
            "recommended_focus": high_skills if high_skills else med_skills
        }
