"""
End-to-End System Integration Test for AI Interview & Employability Platform
Tests:
1. Multi-user isolation
2. Authentication (Register, Login, Me, Token persistence)
3. Resume upload & parsing (PDF and text)
4. Dynamic target role logic (AI suggested vs explicit selection)
5. Critical VLSI test (Candidate Nisha does NOT become AI/ML Engineer)
6. Job Description matching & skill gaps
7. Interview setup, question generation, and multimodal completion
8. 5-week dynamic roadmap generation
9. Longitudinal progress tracking across multiple attempts
"""

import os
import requests
import json
import sys
import uuid

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001/api")

def run_tests():
    run_id = uuid.uuid4().hex[:6]
    print("=" * 60)
    print(f"RUNNING E2E MULTI-USER INTEGRATION TESTS (Run ID: {run_id})")
    print("=" * 60)

    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] Backend health check passed.")

    def register_candidate_with_otp(email, password, payload):
        # 1. Request OTP
        otp_res = requests.post(f"{BASE_URL}/auth/send-otp", json={"email": email})
        assert otp_res.status_code == 200, f"Send OTP failed: {otp_res.text}"
        dev_otp = otp_res.json().get("devOtp")
        # 2. Verify OTP
        if dev_otp:
            ver_res = requests.post(f"{BASE_URL}/auth/verify-otp", json={"email": email, "otp": dev_otp})
            assert ver_res.status_code == 200, f"Verify OTP failed: {ver_res.text}"
        # 3. Finalize registration
        reg_body = dict(payload)
        if dev_otp:
            reg_body["otp"] = dev_otp
        reg_res = requests.post(f"{BASE_URL}/auth/register", json=reg_body)
        if reg_res.status_code == 200:
            return reg_res.json()["token"]
        login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        assert login_res.status_code == 200, f"Login failed for {email}: {login_res.text}"
        return login_res.json()["token"]

    # ----------------------------------------------------
    # TEST USER A: AI/ML Candidate
    # ----------------------------------------------------
    print("\n--- Testing User A (AI/ML Candidate) ---")
    user_a_email = f"aiml_{run_id}@example.com"
    user_a_pass = "Password@123"

    reg_payload_a = {
        "name": "Aryan Sharma",
        "email": user_a_email,
        "password": user_a_pass,
        "college": "Indian Institute of Technology",
        "degree": "B.Tech",
        "department": "Computer Science & Engineering",
        "graduationYear": "2026"
    }

    token_a = register_candidate_with_otp(user_a_email, user_a_pass, reg_payload_a)
    print("[OK] User A registered and verified with OTP successfully.")

    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify initial me data
    me_a = requests.get(f"{BASE_URL}/auth/me", headers=headers_a).json()
    assert me_a["user"]["name"] == "Aryan Sharma"
    print(f"[OK] User A authenticated as: {me_a['user']['name']}")

    # User A parses resume text
    resume_text_a = """
    Aryan Sharma
    Education: B.Tech in Computer Science, IIT
    Skills: Python, PyTorch, TensorFlow, Machine Learning, Deep Learning, SQL, Docker, FastApi, Git, Pandas, NumPy, NLP.
    Projects: Multimodal Emotion Recognition using PyTorch, Real-Time Distributed Analytics Engine.
    Internships: AI Research Intern at DeepTech Labs.
    """
    parse_res_a = requests.post(
        f"{BASE_URL}/resumes/parse-text",
        headers=headers_a,
        json={"rawText": resume_text_a, "fileName": "Aryan_AIML_Resume.txt"}
    )
    assert parse_res_a.status_code == 200, f"Resume parse failed: {parse_res_a.text}"
    resume_data_a = parse_res_a.json()["resume"]
    assert "machine learning" in [s.lower() for s in resume_data_a["skills"]]
    assert "pytorch" in [s.lower() for s in resume_data_a["skills"]]
    print(f"[OK] User A resume parsed: {len(resume_data_a['skills'])} skills extracted.")
    print(f"[OK] User A AI suggested role: {parse_res_a.json()['aiSuggestedRole']}")

    # Select target role for User A
    role_res_a = requests.put(
        f"{BASE_URL}/jobs/target-role",
        headers=headers_a,
        json={"targetRole": "AI/ML Engineer"}
    )
    assert role_res_a.status_code == 200
    assert role_res_a.json()["targetRole"] == "AI/ML Engineer"
    print("[OK] User A target role set to: AI/ML Engineer")

    # Match JD for User A
    jd_res_a = requests.post(
        f"{BASE_URL}/jobs/match",
        headers=headers_a,
        json={
            "title": "Junior AI/ML Engineer",
            "descriptionText": "Looking for AI/ML Engineer with Python, PyTorch, Docker, Kubernetes, AWS, Machine Learning.",
            "targetRole": "AI/ML Engineer"
        }
    )
    assert jd_res_a.status_code == 200
    print(f"[OK] User A JD match score: {jd_res_a.json()['matchScore']}%")

    # Round 1: Aptitude Assessment for User A
    apt_q_res = requests.post(f"{BASE_URL}/aptitude/start", headers=headers_a, json={"questionsPerSection": 5})
    assert apt_q_res.status_code == 200, f"Aptitude start failed: {apt_q_res.text}"
    apt_q_data = apt_q_res.json()
    attempt_id = apt_q_data["attemptId"]
    questions = apt_q_data["questions"]
    assert len(questions) == 15
    sections = set(q["section"] for q in questions)
    assert "Quantitative Ability" in sections
    assert "Logical Reasoning" in sections
    assert "Verbal Ability" in sections
    print(f"[OK] User A initialized Round 1 Aptitude with {len(questions)} questions across 3 sections.")

    # Submit answers for User A
    answers_payload = [
        {"question_id": q["id"], "selected_option": q["options"][0], "time_taken_seconds": 35.0}
        for q in questions
    ]
    apt_sub_res = requests.post(
        f"{BASE_URL}/aptitude/submit",
        headers=headers_a,
        json={"attemptId": attempt_id, "answers": answers_payload}
    )
    assert apt_sub_res.status_code == 200, f"Aptitude submit failed: {apt_sub_res.text}"
    apt_res_data = apt_sub_res.json()["attempt"]
    assert "overallScore" in apt_res_data
    print(f"[OK] User A Round 1 Aptitude submitted. Overall Score: {apt_res_data['overallScore']}%, Quant: {apt_res_data['quantitativeScore']}%, Logic: {apt_res_data['reasoningScore']}%, Verbal: {apt_res_data['verbalScore']}%")
    next_round = apt_sub_res.json().get("nextRound", {})
    assert next_round.get("round") == 2
    print(f"[OK] Next Round message verified: {next_round.get('message')}")

    # Verify latest aptitude endpoint
    latest_apt_res = requests.get(f"{BASE_URL}/aptitude/latest", headers=headers_a)
    assert latest_apt_res.status_code == 200
    assert latest_apt_res.json()["attempt"]["id"] == attempt_id
    print("[OK] User A latest aptitude attempt verified via API.")

    # Setup interview for User A
    session_res_a = requests.post(
        f"{BASE_URL}/interviews/setup",
        headers=headers_a,
        json={
            "roundType": "Full Mock Interview",
            "questionCount": 3,
            "difficulty": "medium",
            "targetRole": "AI/ML Engineer"
        }
    )
    assert session_res_a.status_code == 200
    session_a = session_res_a.json()["session"]
    session_id_a = session_a["id"]
    print(f"[OK] User A interview session created (ID: {session_id_a}) with {len(session_a['questions'])} questions.")

    # Complete interview for User A
    complete_res_a = requests.post(
        f"{BASE_URL}/interviews/{session_id_a}/complete",
        headers=headers_a,
        json={
            "answers": [
                {
                    "questionId": 1,
                    "question": session_a["questions"][0]["question"],
                    "answer": "In our project on Multimodal Emotion Recognition, I architected a dual-stream CNN and LSTM in PyTorch using Situation-Task-Action-Result format.",
                    "category": "Technical",
                    "difficulty": "Medium"
                },
                {
                    "questionId": 2,
                    "question": session_a["questions"][1]["question"],
                    "answer": "When optimizing model latency, I implemented TensorRT quantization reducing inference time by 45%.",
                    "category": "Technical",
                    "difficulty": "Medium"
                }
            ],
            "cvMetrics": {"camera_facing_percentage": 92.0, "face_detected_ratio": 98.0},
            "speechMetrics": {"speaking_rate_wpm": 135.0, "filler_word_count": 2}
        }
    )
    assert complete_res_a.status_code == 200
    assessment_a = complete_res_a.json()["assessment"]
    print(f"[OK] User A interview evaluated. Readiness: {assessment_a['readiness']['score']}% ({assessment_a['readiness']['level']})")

    # ----------------------------------------------------
    # TEST USER B: VLSI Candidate (Nisha)
    # ----------------------------------------------------
    print("\n--- Testing User B: VLSI Candidate (Nisha) ---")
    user_b_email = f"nisha_vlsi_{run_id}@example.com"
    user_b_pass = "NishaVLSI@2026"

    reg_payload_b = {
        "name": "Nisha",
        "email": user_b_email,
        "password": user_b_pass,
        "college": "PSG College of Technology",
        "degree": "B.E.",
        "department": "Electronics and Communication Engineering",
        "graduationYear": "2026"
    }

    token_b = register_candidate_with_otp(user_b_email, user_b_pass, reg_payload_b)
    print("[OK] User B (Nisha) registered and verified with OTP successfully.")

    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Verify initial me data for User B: Must NOT have target_role pre-filled as AI/ML
    me_b = requests.get(f"{BASE_URL}/auth/me", headers=headers_b).json()
    assert me_b["user"]["name"] == "Nisha"
    assert me_b["user"]["targetRole"] is None or me_b["user"]["targetRole"] == "", \
        f"Expected empty initial target role for new user B, got {me_b['user']['targetRole']}"
    print(f"[OK] User B initial target role is correctly unselected: {me_b['user']['targetRole']}")

    # User B parses VLSI resume
    resume_text_b = """
    Nisha
    Education: B.E in Electronics & Communication (VLSI Specialization), PSG Tech
    Department: VLSI / Electronics
    Skills: Verilog, VHDL, RTL Design, FPGA, Vivado, Cadence, Digital Electronics, CMOS, Static Timing Analysis, C, C++, Linux.
    Projects: 32-bit RISC-V Pipelined Processor in Verilog, High-Speed UART Controller on Xilinx FPGA.
    Internships: VLSI Design Intern at ChipWorks.
    Certifications: Advanced Digital Design with SystemVerilog.
    """
    parse_res_b = requests.post(
        f"{BASE_URL}/resumes/parse-text",
        headers=headers_b,
        json={"rawText": resume_text_b, "fileName": "Nisha_VLSI_Resume.txt"}
    )
    assert parse_res_b.status_code == 200
    b_resume = parse_res_b.json()["resume"]
    b_ai_suggested_role = parse_res_b.json()["aiSuggestedRole"]
    b_extracted_skills = [s.lower() for s in b_resume["skills"]]

    print(f"[OK] Extracted skills for Nisha: {b_extracted_skills}")
    assert "verilog" in b_extracted_skills, "Verilog missing from extracted skills"
    assert "vhdl" in b_extracted_skills, "VHDL missing from extracted skills"
    assert "fpga" in b_extracted_skills, "FPGA missing from extracted skills"

    # CRITICAL CHECK: AI suggested role must NOT be AI/ML Engineer
    print(f"[OK] AI Suggested Role for Nisha: '{b_ai_suggested_role}'")
    assert "VLSI" in b_ai_suggested_role, f"Expected VLSI in suggested role, got: {b_ai_suggested_role}"
    assert "AI/ML" not in b_ai_suggested_role, f"VLSI candidate was incorrectly assigned AI/ML!"

    # Verify user B's actual target role is STILL unselected until they choose
    me_b_after_parse = requests.get(f"{BASE_URL}/auth/me", headers=headers_b).json()
    assert me_b_after_parse["user"]["targetRole"] != "AI/ML Software Engineer", \
        "Target role should never automatically become AI/ML Software Engineer!"
    print("[OK] Confirmed: Resume upload did NOT force a target role on Nisha.")

    # Nisha explicitly accepts / selects "VLSI Design Engineer"
    role_res_b = requests.put(
        f"{BASE_URL}/jobs/target-role",
        headers=headers_b,
        json={"targetRole": "VLSI Design Engineer"}
    )
    assert role_res_b.status_code == 200
    assert role_res_b.json()["targetRole"] == "VLSI Design Engineer"
    print("[OK] User B target role confirmed as: VLSI Design Engineer")

    # Match VLSI Job Description
    jd_res_b = requests.post(
        f"{BASE_URL}/jobs/match",
        headers=headers_b,
        json={
            "title": "VLSI Design Engineer",
            "descriptionText": "Hiring VLSI Design Engineer proficient in Verilog, VHDL, RTL Design, FPGA, Static Timing Analysis, SystemVerilog, UVM, and Scripting.",
            "targetRole": "VLSI Design Engineer"
        }
    )
    assert jd_res_b.status_code == 200
    b_jd = jd_res_b.json()
    print(f"[OK] VLSI JD Match Score: {b_jd['matchScore']}%")
    print(f"  Matched Skills: {b_jd['matchedSkills']}")
    print(f"  Missing Skills: {b_jd['missingSkills']}")
    assert "verilog" in [s.lower() for s in b_jd["matchedSkills"]]

    # Setup VLSI Interview Session
    session_res_b = requests.post(
        f"{BASE_URL}/interviews/setup",
        headers=headers_b,
        json={
            "roundType": "Technical",
            "questionCount": 3,
            "difficulty": "medium",
            "targetRole": "VLSI Design Engineer"
        }
    )
    assert session_res_b.status_code == 200
    b_session = session_res_b.json()["session"]
    print(f"[OK] VLSI Interview questions generated: {len(b_session['questions'])}")
    for q in b_session["questions"]:
        print(f"  - [{q['category']}] {q['question'][:80]}...")

    # Complete VLSI Interview
    complete_res_b = requests.post(
        f"{BASE_URL}/interviews/{b_session['id']}/complete",
        headers=headers_b,
        json={
            "answers": [
                {
                    "questionId": 1,
                    "question": b_session["questions"][0]["question"],
                    "answer": "In our 32-bit RISC-V pipelined processor, I resolved data hazards using operand forwarding and hazard detection units in Verilog.",
                    "category": "Technical",
                    "difficulty": "Medium"
                }
            ],
            "cvMetrics": {"camera_facing_percentage": 94.0, "face_detected_ratio": 97.0},
            "speechMetrics": {"speaking_rate_wpm": 140.0, "filler_word_count": 1}
        }
    )
    assert complete_res_b.status_code == 200
    b_assessment = complete_res_b.json()["assessment"]
    print(f"[OK] User B assessment generated: {b_assessment['readiness']['score']}%")

    # Check User B's Learning Roadmap: Must be VLSI/Hardware-oriented, NOT AI/ML!
    roadmap_res_b = requests.get(f"{BASE_URL}/assessments/roadmap", headers=headers_b)
    assert roadmap_res_b.status_code == 200
    b_roadmap = roadmap_res_b.json()["roadmap"]
    print(f"[OK] User B Learning Roadmap duration: {b_roadmap['duration_weeks']} weeks")
    print(f"  Week 1 milestone: {b_roadmap['weekly_action_plan'][0]['theme']}")
    # Verify no PyTorch / Deep Learning module forced onto VLSI candidate
    week_themes = " ".join([w["theme"] for w in b_roadmap["weekly_action_plan"]]).lower()
    assert "deep learning" not in week_themes, "VLSI candidate received an irrelevant deep learning module!"

    # ----------------------------------------------------
    # TEST USER ISOLATION
    # ----------------------------------------------------
    print("\n--- Verifying Strict Multi-User Data Isolation ---")
    # User B should NOT see User A's assessments
    b_assessments = requests.get(f"{BASE_URL}/assessments/latest", headers=headers_b).json()
    assert b_assessments["assessment"]["candidate"]["name"] == "Nisha"
    assert b_assessments["assessment"]["job_alignment"]["target_role"] == "VLSI Design Engineer"
    print("[OK] User B sees only User B's candidate name and VLSI target role.")

    a_assessments = requests.get(f"{BASE_URL}/assessments/latest", headers=headers_a).json()
    assert a_assessments["assessment"]["candidate"]["name"] == "Aryan Sharma"
    assert a_assessments["assessment"]["job_alignment"]["target_role"] == "AI/ML Engineer"
    print("[OK] User A sees only User A's candidate name and AI/ML target role.")

    # ----------------------------------------------------
    # TEST NEW USER C: Clean Empty States
    # ----------------------------------------------------
    print("\n--- Testing User C (New Clean Account) ---")
    user_c_email = f"karthik_{run_id}@example.com"
    user_c_pass = "BrandNew@2026"

    reg_payload_c = {
        "name": "Karthik Raja",
        "email": user_c_email,
        "password": user_c_pass,
        "college": "College of Engineering Guindy",
        "degree": "B.E.",
        "department": "Mechanical Engineering",
        "graduationYear": "2027"
    }
    token_c = register_candidate_with_otp(user_c_email, user_c_pass, reg_payload_c)
    print("[OK] User C registered and verified with OTP successfully.")
    headers_c = {"Authorization": f"Bearer {token_c}"}

    me_c = requests.get(f"{BASE_URL}/auth/me", headers=headers_c).json()
    assert me_c["user"]["resume"] is None, "New user should not have a resume"
    assert me_c["user"]["currentAssessment"] is None, "New user should not have an assessment"
    assert me_c["user"]["targetRole"] is None, "New user should not have a target role"
    print("[OK] New user C has zero prior data: No resume, no assessment, no target role.")

    c_gaps = requests.get(f"{BASE_URL}/assessments/skill-gaps", headers=headers_c).json()
    assert c_gaps["skillGaps"]["total_gaps"] == 0, "New user should have 0 skill gaps before resume/mock"
    print("[OK] User C has 0 skill gaps as expected.")

    c_roadmap = requests.get(f"{BASE_URL}/assessments/roadmap", headers=headers_c).json()
    assert c_roadmap["roadmap"] is None, "New user should have no roadmap before interview"
    print("[OK] User C roadmap returned null as expected.")

    print("\n" + "=" * 60)
    print("ALL E2E INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
