/**
 * Sample Demo Candidates (Clearly Isolated Demo Mode)
 * ----------------------------------------------------
 * These personas provide pre-configured benchmark data for college project reviews,
 * viva examinations, and demonstrations.
 * 
 * IMPORTANT:
 * Real users who register create completely empty, private candidate profiles.
 * Demo data is strictly isolated and never overwrites real user accounts.
 */

export const DEMO_CANDIDATES = [
  {
    id: "demo_abidharani",
    name: "Abidharani A",
    email: "abidharani@student.edu",
    college: "Bachelor of Engineering B.E in COMPUTER SCIENCE AND ENGINEERING",
    targetRole: "AI/ML Software Engineer",
    phone: "+91 98765 43210",
    location: "Chennai, India",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250",
    isDemo: true,
    resume: {
      fileName: "Abidharani_A_Resume.pdf",
      uploadedAt: "2026-09-18",
      skills: [
        "python", "java", "c++", "javascript", "html", "css", "mongodb",
        "git", "github", "machine learning", "deep learning", "pandas",
        "numpy", "power bi", "data structures", "dbms", "computer vision", "cloud computing"
      ],
      projects: [
        "Sign Language to Voice Converter using Computer Vision & Deep Learning",
        "Automatic Medicine Vending Machine using Python and Machine Learning",
        "AI-Based Online Interview Observable Behavior Analysis System",
        "Student Management Portal Web Application"
      ],
      internships: [
        "Infosys Springboard Virtual Internship 7.0",
        "Azusys Technologies - Software Developer Intern"
      ],
      certifications: [
        "NPTEL Deep Learning & Algorithms",
        "HackerRank Python & Problem Solving Gold Badge"
      ]
    },
    jobDescription: {
      title: "AI/ML Software Engineer",
      text: "Seeking AI/ML Software Engineer proficient in Python, Machine Learning, Deep Learning, Data Structures, Algorithms, SQL, and Docker. Experience with Flask, AWS, and Git required.",
      matchScore: 66.7,
      matchedSkills: [
        "c++", "data structures", "dbms", "deep learning", "git",
        "github", "java", "javascript", "machine learning", "mongodb",
        "numpy", "pandas", "power bi", "python"
      ],
      missingSkills: ["algorithms", "aws", "docker", "flask", "node.js", "react", "sql"]
    },
    currentAssessment: {
      candidate: {
        name: "Abidharani A",
        education: "Bachelor of Engineering B.E in COMPUTER SCIENCE AND ENGINEERING",
        target_role: "AI/ML Software Engineer"
      },
      job_alignment: {
        target_role: "AI/ML Software Engineer",
        match_score: 66.7,
        matched_skills: [
          "c++", "data structures", "dbms", "deep learning", "git",
          "github", "java", "javascript", "machine learning", "mongodb",
          "numpy", "pandas", "power bi", "python"
        ],
        missing_skills: ["algorithms", "aws", "docker", "flask", "node.js", "react", "sql"]
      },
      skill_gaps: {
        total_gaps: 7,
        high_priority_count: 5,
        medium_priority_count: 2,
        low_priority_count: 0,
        prioritized_gaps: [
          { skill: "algorithms", priority: "HIGH", reason: "Foundational technical problem-solving required for AI systems.", is_core: true, target: "Advanced" },
          { skill: "sql", priority: "HIGH", reason: "Core relational database querying required for backend pipelines.", is_core: true, target: "Intermediate" },
          { skill: "docker", priority: "HIGH", reason: "Mandatory containerization technology for ML deployment.", is_core: true, target: "Proficient" },
          { skill: "aws", priority: "HIGH", reason: "Cloud infrastructure requirement for cloud-native AI.", is_core: true, target: "Proficient" },
          { skill: "flask", priority: "HIGH", reason: "Backend microservice API layer.", is_core: true, target: "Intermediate" },
          { skill: "node.js", priority: "MEDIUM", reason: "Secondary full-stack integration capability.", is_core: false, target: "Familiar" },
          { skill: "react", priority: "MEDIUM", reason: "Frontend interface component mastery.", is_core: false, target: "Familiar" }
        ],
        high_priority: ["algorithms", "sql", "docker", "aws", "flask"],
        medium_priority: ["node.js", "react"],
        low_priority: []
      },
      technical_assessment: {
        overall_technical_score: 76.5,
        average_score: 0.765,
        strong_topics: ["Python", "Machine Learning", "Git"],
        weak_topics: ["Data Structures", "Docker"]
      },
      hr_assessment: {
        overall_hr_score: 81.0,
        average_relevance: 84.0,
        average_semantic_similarity: 0.94,
        average_completeness: 78.0,
        average_clarity: 88.0,
        average_star_score: 82.0
      },
      visual_assessment: {
        face_visibility_percentage: 96.0,
        camera_facing_percentage: 88.0,
        posture_consistency_percentage: 90.0,
        movement_stability_percentage: 92.0,
        gesture_frequency_percentage: 25.0
      },
      speech_assessment: {
        speaking_rate_wpm: 138.0,
        pause_count: 4,
        average_pause_seconds: 0.8,
        longest_pause_seconds: 1.6,
        fillers_per_100_words: 1.4,
        filler_count: 5,
        energy_consistency_percentage: 90.0,
        speech_continuity_percentage: 85.0
      },
      multimodal_assessment: {
        employability_score: 80.9,
        readiness_level: "Ready",
        readiness_description: "Demonstrates solid core competence with minor refinement opportunities.",
        confidence: 1.0,
        component_scores: {
          technical: 76.5,
          hr_nlp: 81.0,
          speech: 92.8,
          computer_vision: 92.1,
          resume_jd: 66.7
        },
        active_weights: {
          technical: 0.30,
          hr_nlp: 0.25,
          speech: 0.15,
          computer_vision: 0.15,
          resume_jd: 0.15
        }
      },
      readiness: {
        score: 80.9,
        level: "Ready",
        description: "Demonstrates solid core competence with minor refinement opportunities."
      },
      strengths: [
        "Strong overall technical problem solving (76.5%).",
        "Solid mastery in Python, Machine Learning, and version control (Git).",
        "Structured, relevant behavioral communication with solid STAR delivery (82.0%).",
        "Natural conversational speaking rate maintained (138.0 WPM).",
        "Minimal filler word density observed (1.4 per 100 words).",
        "Consistent camera-facing visual orientation and upright shoulder posture."
      ],
      improvement_areas: [
        "Resume-to-JD alignment indicates gaps in Docker, SQL, and AWS.",
        "Data Structures responses exhibited conceptual hesitation during tree traversals.",
        "Initial answers occasionally lacked concise thesis statements."
      ],
      recommendations: [
        "Acquire hands-on project experience containerizing models with Docker and AWS.",
        "Practice structured STAR narrative delivery to keep initial framing under 20 seconds.",
        "Practice timed algorithmic problem solving focusing on binary search and tree recursion."
      ],
      learning_roadmap: {
        duration_weeks: 5,
        total_estimated_hours: 86,
        weekly_action_plan: [
          {
            week: 1,
            theme: "High-Priority Technical Foundations",
            target_topics: ["Algorithms", "Data Structures"],
            milestone: "Demonstrate mastery of core implementation in Algorithms and Data Structures.",
            objectives: [
              "Review tree traversals, graph algorithms (BFS/DFS), and time complexity.",
              "Solve 12 medium LeetCode/HackerRank coding challenges.",
              "Practice dry-running algorithms on a whiteboard."
            ],
            completed: true
          },
          {
            week: 2,
            theme: "Database & Backend Microservices",
            target_topics: ["SQL", "Flask"],
            milestone: "Build a complete relational backend service with optimized queries.",
            objectives: [
              "Master SQL CTEs, window functions, and indexing strategies.",
              "Construct a REST API using Flask and SQLAlchemy.",
              "Write comprehensive unit test cases."
            ],
            completed: false
          },
          {
            week: 3,
            theme: "Cloud & Containerization Mastery",
            target_topics: ["Docker", "AWS"],
            milestone: "Containerize and deploy an AI model service to cloud infrastructure.",
            objectives: [
              "Write multi-stage Dockerfiles with minimal image size.",
              "Deploy containerized microservice to AWS ECS / Lambda.",
              "Configure environment variables and persistent volume storage."
            ],
            completed: false
          },
          {
            week: 4,
            theme: "Behavioral Communication & STAR Polish",
            target_topics: ["STAR Framework", "Speech Pacing"],
            milestone: "Rehearse 5 core project and conflict resolution stories.",
            objectives: [
              "Map academic projects into Situation, Task, Action, and Result format.",
              "Practice maintaining 130–150 WPM conversational pacing.",
              "Reduce verbal filler words by substituting silent pauses."
            ],
            completed: false
          },
          {
            week: 5,
            theme: "Full Multimodal Mock Interview Reassessment",
            target_topics: ["Full Mock Interview", "Placement Readiness"],
            milestone: "Achieve >= 85% placement readiness score across all modalities.",
            objectives: [
              "Complete full-length technical round covering previously weak topics.",
              "Complete timed behavioral interview with webcam and microphone recording.",
              "Review updated readiness report and celebrate progression."
            ],
            completed: false
          }
        ]
      },
      progress_tracking: {
        current_attempt: 2,
        total_attempts: 2,
        is_baseline: false,
        score_delta_previous: 8.5,
        score_delta_baseline: 8.5,
        progress_narrative: "Readiness improved by 8.5 points across 2 attempts (72.4% -> 80.9%).",
        improved_areas: [
          "Overall Placement Readiness (+8.5 pts)",
          "Technical Problem Solving (+12.0%)",
          "Filler Word Density (-1.8 per 100 words)",
          "Camera-Facing Orientation (+6.0%)"
        ],
        declining_areas: [],
        stable_areas: ["Upper-body Posture Consistency", "Speech Cadence"],
        resolved_skill_gaps: ["Machine Learning", "Git"],
        persistent_gaps: ["Docker", "AWS", "SQL"],
        timeline: [
          {
            attempt: 1,
            date: "2026-09-18",
            score: 72.4,
            readiness_level: "Ready",
            component_scores: { technical: 64.5, hr_nlp: 75.0, speech: 85.0, computer_vision: 86.0, resume_jd: 62.0 }
          },
          {
            attempt: 2,
            date: "2026-10-04",
            score: 80.9,
            readiness_level: "Ready",
            component_scores: { technical: 76.5, hr_nlp: 81.0, speech: 92.8, computer_vision: 92.1, resume_jd: 66.7 }
          }
        ]
      },
      visualization_data: {
        radar_chart: [
          { dimension: "Technical", score: 76.5, fullMark: 100 },
          { dimension: "HR / STAR", score: 81.0, fullMark: 100 },
          { dimension: "Speech", score: 92.8, fullMark: 100 },
          { dimension: "Visual / CV", score: 92.1, fullMark: 100 },
          { dimension: "Resume / JD", score: 66.7, fullMark: 100 }
        ],
        progress_timeline: [
          { attempt: "Attempt 1", score: 72.4, technical: 64.5, hr: 75.0, speech: 85.0 },
          { attempt: "Attempt 2", score: 80.9, technical: 76.5, hr: 81.0, speech: 92.8 }
        ]
      }
    }
  },
  {
    id: "demo_rohan",
    name: "Rohan Sharma",
    email: "rohan.sharma@campus.edu",
    college: "Delhi Technological University (DTU) - IT",
    targetRole: "Cloud & DevOps Engineer",
    phone: "+91 91234 56789",
    location: "New Delhi, India",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=250",
    isDemo: true,
    resume: {
      fileName: "Rohan_DevOps_Resume.pdf",
      uploadedAt: "2026-10-02",
      skills: ["linux", "bash", "python", "docker", "kubernetes", "aws", "terraform", "ci/cd", "git", "prometheus", "grafana"],
      projects: [
        "Kubernetes Multi-Cluster Deployment with Helm and ArgoCD",
        "Automated CI/CD Pipeline for Microservices using GitHub Actions & Docker",
        "Cloud Infrastructure as Code using Terraform on AWS"
      ],
      internships: ["DevOps Trainee at CloudOps Technologies (3 months)"],
      certifications: ["AWS Certified Solutions Architect Associate", "CKA Certified Kubernetes Administrator"]
    },
    jobDescription: {
      title: "Cloud & DevOps Engineer",
      text: "Looking for a Cloud/DevOps Engineer experienced in AWS, Docker, Kubernetes, Terraform, Linux, CI/CD, Python, and Prometheus monitoring.",
      matchScore: 82.5,
      matchedSkills: ["aws", "ci/cd", "docker", "git", "kubernetes", "linux", "python", "terraform"],
      missingSkills: ["golang", "ansible", "jenkins"]
    },
    // Rohan has uploaded a resume & JD, but has NOT taken an interview yet
    currentAssessment: null
  },
  {
    id: "demo_priya",
    name: "Priya Nair",
    email: "priya.nair@techuniv.edu",
    college: "Vellore Institute of Technology (VIT) - ECE",
    targetRole: "Frontend React Developer",
    phone: "+91 99887 76655",
    location: "Bengaluru, India",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=250",
    isDemo: true,
    // Brand new user: No resume, no JD, no assessment
    resume: null,
    jobDescription: null,
    currentAssessment: null
  }
];
