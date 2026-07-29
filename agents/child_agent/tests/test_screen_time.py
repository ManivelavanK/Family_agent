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
from app.models.screen_time import ScreenTimeLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_screentime.db"
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
        if os.path.exists("test_screentime.db"):
            try:
                os.remove("test_screentime.db")
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

def test_screen_time_crud_and_analysis(client):
    # 1. Create Child Profile (Middle School: 12-year-old, limit = 120 mins)
    child_payload = {
        "family_id": "fam_st",
        "name": "Kelly",
        "date_of_birth": "2014-01-01",
        "age": 12,
        "gender": "Female",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Add Screen Time Logs
    today = date.today()
    
    # Log 1: normal day, some entertainment & study
    log_1 = {
        "child_id": child_id,
        "date": str(today - timedelta(days=1)),
        "mobile": 30,
        "gaming": 40,
        "tv": 30,
        "social_media": 20,
        "study_screen_time": 60,
        "other": 10,
        "late_night_minutes": 0
    }
    # Entertainment = 30+40+30+20+10 = 130 mins
    # Study = 60 mins
    # Total = 190 mins

    # Log 2: High gaming & Late night day
    log_2 = {
        "child_id": child_id,
        "date": str(today),
        "mobile": 20,
        "gaming": 130, # Exceeds 120 min limit
        "tv": 40,
        "social_media": 30,
        "study_screen_time": 20,
        "other": 0,
        "late_night_minutes": 25 # triggers late-night
    }
    # Entertainment = 20+130+40+30+0 = 220 mins
    # Study = 20 mins
    # Total = 240 mins

    client.post("/children/screen-time", json=log_1)
    client.post("/children/screen-time", json=log_2)

    # 3. Check Aggregations
    # Daily total today
    res_daily = client.get(f"/children/screen-time/{child_id}/daily")
    assert res_daily.status_code == 200
    assert res_daily.json()["total_minutes"] == 240

    # Weekly total (both days)
    res_weekly = client.get(f"/children/screen-time/{child_id}/weekly")
    assert res_weekly.status_code == 200
    assert res_weekly.json()["total_minutes"] == 430

    # 4. Get Analysis & Digital Wellness Alerts
    res_analysis = client.get(f"/children/screen-time/{child_id}/analysis")
    assert res_analysis.status_code == 200
    analysis = res_analysis.json()

    assert analysis["total_screen_time"] == 430
    assert analysis["entertainment_time"] == 350
    assert analysis["study_time"] == 80
    
    # Ratio: 350 / 80 = 4.375 => 4.38
    assert analysis["entertainment_study_ratio"] == 4.38
    
    # Daily average entertainment: 350 / 7 = 50.0 mins
    assert analysis["daily_average_entertainment"] == 50.0

    alerts = analysis["alerts"]
    # Daily average is 50.0, which is below recommended limit (120 mins).
    # Gaming exceeded 120 on one day (130 mins). Late-night was 25 mins.
    # Ratio is 4.38 (>3.0) and entertainment is 350 (>60 mins).
    assert any("gaming" in a.lower() for a in alerts)
    assert any("late-night" in a.lower() for a in alerts)
    assert any("balance" in a.lower() for a in alerts)
