import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
# Import models to ensure tables are created
from app.models.profile import ChildProfile
from app.models.exam import Exam

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_exams.db"
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
        if os.path.exists("test_exams.db"):
            try:
                os.remove("test_exams.db")
            except Exception:
                pass

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

def test_exams_crud_and_countdown(client):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_exams",
        "name": "Grace",
        "date_of_birth": "2014-01-01",
        "age": 12,
        "gender": "Female",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Add Exam (due in 5 days, difficulty Hard, preparation 30%)
    today = date.today()
    exam_date = today + timedelta(days=5)
    
    exam_payload = {
        "child_id": child_id,
        "subject": "Chemistry",
        "exam_name": "Midterm Exam",
        "exam_date": str(exam_date),
        "syllabus": "Organic Compounds, Periodic Table, Acids and Bases",
        "preparation_percentage": 30,
        "difficulty": "Hard",
        "notes": "Need to pass this."
    }
    res_exam = client.post("/children/exams", json=exam_payload)
    assert res_exam.status_code == 201
    exam_id = res_exam.json()["id"]

    # 3. Get Countdown API
    res_countdown = client.get(f"/children/exams/{child_id}/countdown")
    assert res_countdown.status_code == 200
    data = res_countdown.json()
    assert len(data) == 1
    assert data[0]["days_remaining"] == 5
    assert data[0]["priority"] == "HIGH"  # days_remaining <= 7

    # 4. Get Study Plan API
    res_plan = client.get(f"/children/exams/{child_id}/study-plan")
    assert res_plan.status_code == 200
    plan_data = res_plan.json()
    assert len(plan_data) == 1
    assert plan_data[0]["exam_name"] == "Midterm Exam"
    assert plan_data[0]["recommended_daily_study_hours"] > 0
    # Differentiate check: 12-year-old child should get School Recommendations
    assert any("School" in step for step in plan_data[0]["preparation_plan"])

def test_exams_college_study_plan(client):
    # 1. Create College Student Profile
    child_payload = {
        "family_id": "fam_exams",
        "name": "Harry",
        "date_of_birth": "2006-01-01",
        "age": 20,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    child_id = res_child.json()["id"]

    # 2. Add Exam
    today = date.today()
    exam_date = today + timedelta(days=15)
    exam_payload = {
        "child_id": child_id,
        "subject": "Machine Learning",
        "exam_name": "Final Project & Theory Exam",
        "exam_date": str(exam_date),
        "syllabus": "Regression, Neural Networks, PCA",
        "preparation_percentage": 50,
        "difficulty": "Hard",
        "notes": "Calculus heavy."
    }
    res_exam = client.post("/children/exams", json=exam_payload)
    assert res_exam.status_code == 201

    # 3. Get Study Plan API and check College tips
    res_plan = client.get(f"/children/exams/{child_id}/study-plan")
    assert res_plan.status_code == 200
    plan_data = res_plan.json()
    assert len(plan_data) == 1
    # 20-year-old should get College Recommendations
    assert any("College" in step for step in plan_data[0]["preparation_plan"])
