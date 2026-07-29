import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.student import Student
from app.models.digital_twin import DigitalTwin

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_academic_digital_twin.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_school_student_digital_twin(client, session):
    # 1. Create a School Student
    student = Student(
        name="School Kid",
        grade="8th Grade",
        learning_style="Visual",
        interests=["Science", "Chess"],
        career_interest="Teacher",
        weekly_target_hours=8,
        education_level="SCHOOL",
        age=13,
        profile_metadata={
            "study_habits": "Prefers evening study",
            "reading_progress": "Completed Harry Potter Vol 1"
        }
    )
    session.add(student)
    session.commit()
    session.refresh(student)

    # 2. Get Digital Twin
    res = client.get(f"/api/v1/students/{student.id}/digital-twin")
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == student.id
    assert data["learning_style"] == "Visual"
    
    # Assert school metrics are present
    metrics = data["twin_metrics"]
    assert "homework_completion_rate" in metrics
    assert "attendance_rate" in metrics
    assert metrics["reading_progress"] == "Completed Harry Potter Vol 1"
    assert metrics["study_habits"] == "Prefers evening study"
    assert "coding_platforms_score" not in metrics

def test_college_student_digital_twin(client, session):
    # 1. Create a College Student
    student = Student(
        name="College Guy",
        grade="Undergraduate",
        learning_style="Practical",
        interests=["Coding", "Hackathons"],
        career_interest="Software Engineer",
        weekly_target_hours=15,
        education_level="COLLEGE",
        age=20,
        profile_metadata={
            "coding_platforms": {"leetcode": "solved_100", "github": "contrib_50"},
            "projects": ["Build Antigravity AI"],
            "hackathons": ["MLH Hack 2026"],
            "certifications": ["AWS Cloud Practitioner"],
            "resume_score": 0.85,
            "internship_tracking": "Interviewing with Google"
        }
    )
    session.add(student)
    session.commit()
    session.refresh(student)

    # 2. Get Digital Twin
    res = client.get(f"/api/v1/students/{student.id}/digital-twin")
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == student.id
    
    # Assert college metrics are present
    metrics = data["twin_metrics"]
    assert "coding_platforms_score" in metrics
    assert metrics["projects_completed_count"] == 1
    assert metrics["hackathons_count"] == 1
    assert metrics["certifications_count"] == 1
    assert metrics["resume_score"] == 0.85
    assert metrics["internship_status"] == "Interviewing with Google"
    assert "homework_completion_rate" not in metrics
