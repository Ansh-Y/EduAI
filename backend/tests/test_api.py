import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_and_info():
    response = client.get("/")
    assert response.status_code == 200
    assert "platform" in response.json()
    assert response.json()["status"] == "online"

    info_resp = client.get("/api/info")
    assert info_resp.status_code == 200
    data = info_resp.json()
    assert "demo_accounts" in data
    assert len(data["demo_accounts"]) >= 3


def test_auth_workflow():
    # 1. Invalid login
    bad_login = client.post("/api/auth/login", json={"email": "wrong@demo.com", "password": "wrong"})
    assert bad_login.status_code == 401

    # 2. Valid Teacher Login
    teacher_login = client.post("/api/auth/login", json={"email": "teacher@eduai.demo", "password": "password123"})
    assert teacher_login.status_code == 200
    token = teacher_login.json()["access_token"]
    assert token is not None

    # 3. Check /me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "teacher@eduai.demo"
    assert me_resp.json()["role"] == "teacher"


def test_role_enforcement():
    # Student login
    student_login = client.post("/api/auth/login", json={"email": "student@eduai.demo", "password": "password123"})
    student_token = student_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {student_token}"}

    # Student trying to call teacher analytics should be 403 Forbidden
    teacher_analytics = client.get("/api/analytics/teacher", headers=headers)
    assert teacher_analytics.status_code == 403

    # Student trying to call admin overview should be 403 Forbidden
    admin_overview = client.get("/api/admin/overview", headers=headers)
    assert admin_overview.status_code == 403


def test_course_listing_and_discovery():
    # Student listing courses should only receive published courses
    student_login = client.post("/api/auth/login", json={"email": "student@eduai.demo", "password": "password123"})
    headers = {"Authorization": f"Bearer {student_login.json()['access_token']}"}

    resp = client.get("/api/courses", headers=headers)
    assert resp.status_code == 200
    courses = resp.json()
    assert len(courses) >= 2
    for c in courses:
        assert c["is_published"] is True


def test_course_generation_demo_mode():
    teacher_login = client.post("/api/auth/login", json={"email": "teacher@eduai.demo", "password": "password123"})
    headers = {"Authorization": f"Bearer {teacher_login.json()['access_token']}"}

    gen_payload = {
        "title": "Autonomous Robotics & Control",
        "subject": "Robotics Engineering",
        "description": "Kinematics, PID control, state-space estimation, and path planning.",
        "prompt": "Focus on mobile robots and sensor fusion.",
        "difficulty": "Intermediate",
        "section_count": 3
    }
    resp = client.post("/api/courses/generate", json=gen_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Autonomous Robotics & Control"
    assert len(data["sections"]) == 3
    for sec in data["sections"]:
        assert len(sec["artifacts"]) == 6
        assert len(sec["objectives"]) >= 2


def test_smart_notes_download():
    # Test downloading section 1 PDF & DOCX
    pdf_resp = client.get("/api/sections/1/notes/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000

    docx_resp = client.get("/api/sections/1/notes/docx")
    assert docx_resp.status_code == 200
    assert "document" in docx_resp.headers["content-type"]
    assert len(docx_resp.content) > 1000


def test_quiz_submission_and_attempt_limits():
    student_login = client.post("/api/auth/login", json={"email": "student3@eduai.demo", "password": "password123"})
    headers = {"Authorization": f"Bearer {student_login.json()['access_token']}"}

    # First attempt on Section 1
    submit_payload = {
        "answers": {
            "1": "Data and Answers (Ground Truth)",
            "2": "False",
            "3": "Regression",
            "4": "Leakage",
            "5": "Parametric models have fixed parameters"
        }
    }
    resp = client.post("/api/quizzes/1/submit", json=submit_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert "passed" in data
    assert "feedback_plan" in data


def test_admin_user_management():
    admin_login = client.post("/api/auth/login", json={"email": "admin@eduai.demo", "password": "password123"})
    headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    overview_resp = client.get("/api/admin/overview", headers=headers)
    assert overview_resp.status_code == 200
    assert overview_resp.json()["total_users"] >= 5

    users_resp = client.get("/api/admin/users", headers=headers)
    assert users_resp.status_code == 200
    assert len(users_resp.json()) >= 5


def test_analytics_and_csv_export():
    teacher_login = client.post("/api/auth/login", json={"email": "teacher@eduai.demo", "password": "password123"})
    headers = {"Authorization": f"Bearer {teacher_login.json()['access_token']}"}

    t_analytics = client.get("/api/analytics/teacher", headers=headers)
    assert t_analytics.status_code == 200
    assert "enrollment_by_course" in t_analytics.json()

    csv_resp = client.get("/api/analytics/export/csv", headers=headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "EDUAI ACADEMIC REPORT" in csv_resp.text
