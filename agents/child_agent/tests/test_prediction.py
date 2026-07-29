import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_prediction_log.db"
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
        if os.path.exists("test_prediction_log.db"):
            try:
                os.remove("test_prediction_log.db")
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


def test_prediction_insufficient_data_behavior(client):
    # 1. Create Child Profile
    child_res = client.post("/children/profile", json={
        "family_id": "fam_ml_nodata",
        "name": "Alex",
        "date_of_birth": "2016-05-10",
        "age": 10,
        "gender": "Male",
        "parent_contact": "555-000-1111"
    })
    assert child_res.status_code == 201
    child_id = child_res.json()["id"]

    # 2. Test Homework prediction with NO historical data
    res_hw = client.get(f"/children/predict/homework/{child_id}")
    assert res_hw.status_code == 200
    data_hw = res_hw.json()
    assert data_hw["has_sufficient_data"] is False
    assert data_hw["prediction"] is None
    assert "Insufficient historical data for prediction." in data_hw["explanation"]

    # 3. Test Attendance prediction with NO historical data
    res_att = client.get(f"/children/predict/attendance/{child_id}")
    assert res_att.status_code == 200
    assert res_att.json()["has_sufficient_data"] is False
    assert "Insufficient historical data for prediction." in res_att.json()["explanation"]

    # 4. Test Study prediction with NO historical data
    res_study = client.get(f"/children/predict/study/{child_id}")
    assert res_study.status_code == 200
    assert res_study.json()["has_sufficient_data"] is False

    # 5. Test Screen Time prediction with NO historical data
    res_st = client.get(f"/children/predict/screen-time/{child_id}")
    assert res_st.status_code == 200
    assert res_st.json()["has_sufficient_data"] is False

    # 6. Test Routine prediction with NO historical data
    res_routine = client.get(f"/children/predict/routine/{child_id}")
    assert res_routine.status_code == 200
    assert res_routine.json()["has_sufficient_data"] is False


def test_prediction_with_sufficient_real_data(client):
    # 1. Create Child Profile
    child_res = client.post("/children/profile", json={
        "family_id": "fam_ml_data",
        "name": "Zoe",
        "date_of_birth": "2015-11-20",
        "age": 11,
        "gender": "Female",
        "parent_contact": "555-222-3333"
    })
    child_id = child_res.json()["id"]
    today = date.today()

    # 2. Populate 4 Homework records
    for i in range(4):
        client.post("/children/homework", json={
            "family_id": "fam_ml_data",
            "child_id": child_id,
            "subject": "Mathematics",
            "title": f"Math Assignment #{i+1}",
            "assigned_date": str(today),
            "due_date": str(today + timedelta(days=i+1)),
            "estimated_minutes": 30 + i * 5,
            "actual_minutes": 35 + i * 5,
            "completed": True
        })

    # 3. Populate 4 Attendance records
    for i in range(4):
        client.post("/children/attendance", json={
            "child_id": child_id,
            "date": str(today - timedelta(days=i)),
            "subject": "Mathematics",
            "status": "PRESENT" if i != 2 else "ABSENT"
        })

    # 4. Populate 3 Study Session records
    now_str = "2026-07-28T10:00:00"
    end_str = "2026-07-28T11:00:00"
    for i in range(3):
        client.post("/children/study/session", json={
            "child_id": child_id,
            "subject": "Science",
            "topic": f"Physics Module #{i+1}",
            "start_time": now_str,
            "end_time": end_str,
            "focus_score": 85
        })

    # 5. Populate 4 Screen Time records
    for i in range(4):
        client.post("/children/screen-time", json={
            "child_id": child_id,
            "date": str(today - timedelta(days=i)),
            "mobile": 30 + i * 5,
            "gaming": 20,
            "tv": 10,
            "social_media": 10,
            "study_screen_time": 40,
            "other": 10,
            "late_night_minutes": 0
        })

    # 6. Populate 4 Health records
    for i in range(4):
        client.post("/children/health", json={
            "child_id": child_id,
            "date": str(today - timedelta(days=i)),
            "sleep_hours": 8.5,
            "water_intake_ml": 1800,
            "physical_activity_minutes": 45,
            "mood": "Happy"
        })

    # 7. Run ML Training endpoint
    train_res = client.post("/children/ml/train")
    assert train_res.status_code == 200
    assert "models_trained" in train_res.json()

    # 8. Test Homework prediction with real data
    pred_hw = client.get(f"/children/predict/homework/{child_id}", params={"subject": "Mathematics", "estimated_minutes": 40}).json()
    assert pred_hw["has_sufficient_data"] is True
    assert pred_hw["sample_count"] == 4
    assert pred_hw["prediction"] is not None
    assert pred_hw["confidence"] in ("HIGH", "MEDIUM")
    assert "Based on 4 actual historical homework logs" in pred_hw["explanation"]

    # 9. Test Attendance prediction with real data
    pred_att = client.get(f"/children/predict/attendance/{child_id}").json()
    assert pred_att["has_sufficient_data"] is True
    assert pred_att["sample_count"] == 4
    assert "historical_attendance_rate" in pred_att["details"]

    # 10. Test Study prediction with real data
    pred_study = client.get(f"/children/predict/study/{child_id}").json()
    assert pred_study["has_sufficient_data"] is True
    assert pred_study["prediction"] is not None
    assert "% Performance Index" in pred_study["prediction"]

    # 11. Test Screen Time prediction with real data
    pred_st = client.get(f"/children/predict/screen-time/{child_id}").json()
    assert pred_st["has_sufficient_data"] is True
    assert pred_st["prediction"] > 0

    # 12. Test Routine prediction with real data
    pred_routine = client.get(f"/children/predict/routine/{child_id}").json()
    assert pred_routine["has_sufficient_data"] is True
    assert "Routine Balance Score" in pred_routine["prediction"]
