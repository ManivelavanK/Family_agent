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
from app.models.health import HealthLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_health.db"
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
        if os.path.exists("test_health.db"):
            try:
                os.remove("test_health.db")
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

def test_health_crud_and_routine_analysis(client):
    # 1. Create Child Profile (Middle School: 11-year-old, sleep guideline = 9.0 to 10.0 hours)
    child_payload = {
        "family_id": "fam_health",
        "name": "Leo",
        "date_of_birth": "2015-01-01",
        "age": 11,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Record 3 daily logs to trigger sleep, water, and activity flags + low consistency check
    today = date.today()
    
    # Day 1: Good sleep (9.5h), low water (800ml), good activity (60m)
    log_1 = {
        "child_id": child_id,
        "date": str(today - timedelta(days=2)),
        "height": 145.0,
        "weight": 40.0,
        "water_intake_ml": 800,
        "sleep_hours": 9.5,
        "sleep_time": "21:30:00",
        "wake_time": "07:00:00",
        "physical_activity_minutes": 60,
        "exercise_type": "Soccer",
        "vaccinations": ["MMR", "BCG"],
        "health_notes": "Healthy day."
    }

    # Day 2: Poor sleep (6.0h), good water (1800ml), low activity (15m)
    log_2 = {
        "child_id": child_id,
        "date": str(today - timedelta(days=1)),
        "height": 145.2,
        "weight": 40.1,
        "water_intake_ml": 1800,
        "sleep_hours": 6.0,
        "sleep_time": "23:00:00",
        "wake_time": "05:00:00",
        "physical_activity_minutes": 15,
        "exercise_type": "None",
        "health_notes": "Felt tired."
    }

    # Day 3: Good sleep (9.0h), low water (1000ml), low activity (20m)
    log_3 = {
        "child_id": child_id,
        "date": str(today),
        "height": 145.2,
        "weight": 40.2,
        "water_intake_ml": 1000,
        "sleep_hours": 9.0,
        "sleep_time": "22:00:00",
        "wake_time": "07:00:00",
        "physical_activity_minutes": 20,
        "exercise_type": "Walking"
    }

    client.post("/children/health", json=log_1)
    client.post("/children/health", json=log_2)
    client.post("/children/health", json=log_3)

    # 3. List logs
    res_list = client.get(f"/children/health/{child_id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 3

    # 4. Generate Health & Routine Report
    res_report = client.get(f"/children/health/{child_id}/report")
    assert res_report.status_code == 200
    report = res_report.json()

    # Daily Summary checks (Day 3 / today)
    assert report["daily_summary"]["water_intake_ml"] == 1000
    assert report["daily_summary"]["sleep_hours"] == 9.0
    assert report["daily_summary"]["weight"] == 40.2

    # Weekly Averages checks
    # Water average: (800+1800+1000)/3 = 1200.0
    # Sleep average: (9.5+6.0+9.0)/3 = 8.17 => 8.2
    # Activity average: (60+15+20)/3 = 31.7 => 31.7
    assert report["weekly_averages"]["average_water_intake_ml"] == 1200.0
    assert report["weekly_averages"]["average_sleep_hours"] == 8.2
    assert report["weekly_averages"]["average_physical_activity_minutes"] == 31.7
    assert report["weekly_averages"]["latest_height_cm"] == 145.2
    assert report["weekly_averages"]["latest_weight_kg"] == 40.2

    # Consistencies (3 logged days out of 7 calendar days)
    # Sleep consistent days: Day 1 (9.5), Day 3 (9.0) => 2 days => (2/7)*100 = 28.6%
    # Water consistent days: Day 2 (1800) => 1 day => (1/7)*100 = 14.3%
    # Activity consistent days: Day 1 (60) => 1 day => (1/7)*100 = 14.3%
    assert report["sleep_consistency_percentage"] == 28.6
    assert report["water_consistency_percentage"] == 14.3
    assert report["activity_consistency_percentage"] == 14.3

    # Alerts checks
    alerts = report["routine_analysis_alerts"]
    assert len(alerts) > 0
    # Average sleep is 8.2, which is under recommended range limit (9.0)
    # Average water is 1200.0, which is under 1500 limit
    # Average activity is 31.7, which is under 45 mins limit
    # Log count is 3 (< 4 logs) => poor consistency alert
    assert any("sleep" in a.lower() for a in alerts)
    assert any("water" in a.lower() for a in alerts)
    assert any("activity" in a.lower() for a in alerts)
    assert any("consistency" in a.lower() for a in alerts)
    
    # Check non-diagnostic medical guidance disclaimer exists
    assert any("healthcare professional" in a.lower() for a in alerts)
