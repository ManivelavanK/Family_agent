import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rec_log.db"
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
        if os.path.exists("test_rec_log.db"):
            try:
                os.remove("test_rec_log.db")
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


def test_groq_recommendation_pipeline(client):
    # 1. Create Child Profile
    child_res = client.post("/children/profile", json={
        "family_id": "fam_rec_100",
        "name": "Maya",
        "date_of_birth": "2014-03-15",
        "age": 12,
        "gender": "Female",
        "parent_contact": "555-999-8888"
    })
    assert child_res.status_code == 201
    child_id = child_res.json()["id"]
    today = date.today()

    # 2. Populate Homework
    client.post("/children/homework", json={
        "family_id": "fam_rec_100",
        "child_id": child_id,
        "subject": "Mathematics",
        "title": "Algebra Worksheet",
        "assigned_date": str(today),
        "due_date": str(today + timedelta(days=2)),
        "priority": "HIGH",
        "estimated_minutes": 45,
        "actual_minutes": 50,
        "completed": False
    })

    # 3. Populate Attendance
    client.post("/children/attendance", json={
        "child_id": child_id,
        "date": str(today),
        "subject": "Mathematics",
        "status": "PRESENT"
    })

    # 4. Populate Screen Time
    client.post("/children/screen-time", json={
        "child_id": child_id,
        "date": str(today),
        "mobile": 40,
        "gaming": 30,
        "tv": 20,
        "social_media": 10,
        "study_screen_time": 45,
        "other": 5,
        "late_night_minutes": 0
    })

    # 5. Populate Health
    client.post("/children/health", json={
        "child_id": child_id,
        "date": str(today),
        "sleep_hours": 8.5,
        "water_intake_ml": 2000,
        "physical_activity_minutes": 60,
        "mood": "Energetic"
    })

    # 6. Populate Pocket Money Allowance & Saving Goal
    pm_res = client.post("/children/pocket-money", json={
        "child_id": child_id,
        "family_id": "fam_rec_100",
        "amount": 25.0,
        "frequency": "WEEKLY",
        "date": str(today)
    })
    assert pm_res.status_code == 201, f"Expected 201, got {pm_res.status_code}: {pm_res.text}"

    sg_res = client.post("/children/expenses/saving-goal", json={
        "child_id": child_id,
        "title": "New Telescope",
        "target_amount": 100.0,
        "current_saved": 35.0,
        "target_date": "2026-12-31"
    })
    assert sg_res.status_code == 201, f"Expected 201, got {sg_res.status_code}: {sg_res.text}"

    # 7. Request Recommendation via POST /children/recommendation
    rec_res = client.post("/children/recommendation", json={
        "child_id": child_id,
        "include_ml_predictions": True,
        "focus_areas": ["study", "saving", "health"]
    })

    assert rec_res.status_code == 200, f"Expected 200, got {rec_res.status_code}: {rec_res.text}"
    data = rec_res.json()

    # Validate output structure
    assert data["child_id"] == child_id
    assert data["child_name"] == "Maya"
    assert data["age"] == 12
    assert isinstance(data["age_group"], str) and len(data["age_group"]) > 0

    # Validate deterministic summary
    det_sum = data["deterministic_summary"]
    assert det_sum["homework_summary"]["pending_count"] >= 1
    assert det_sum["attendance_summary"]["present_days"] >= 1
    assert det_sum["pocket_money_summary"]["total_allowance"] == 25.0
    assert det_sum["pocket_money_summary"]["total_saved"] == 35.0

    # Validate ML predictions object
    assert "ml_predictions" in data

    # Validate 10 AI recommendation categories
    ai_recs = data["ai_recommendations"]
    assert isinstance(ai_recs["study_suggestions"], list)
    assert isinstance(ai_recs["homework_prioritization"], list)
    assert isinstance(ai_recs["time_management"], list)
    assert isinstance(ai_recs["daily_motivation"], str) and len(ai_recs["daily_motivation"]) > 0
    assert isinstance(ai_recs["healthy_routine_advice"], list)
    assert isinstance(ai_recs["screen_time_advice"], list)
    assert isinstance(ai_recs["saving_suggestions"], list)
    assert isinstance(ai_recs["parent_recommendations"], list)
    assert isinstance(ai_recs["exam_preparation_suggestions"], list)
    assert isinstance(ai_recs["relaxation_suggestions"], list)

    assert "generated_by" in data
    assert "disclaimer" in data
