import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_nutrition_log.db"
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
        if os.path.exists("test_nutrition_log.db"):
            try:
                os.remove("test_nutrition_log.db")
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


def test_nutrition_logging_and_summary_analytics(client):
    # 1. Create child profile
    child_res = client.post("/children/profile", json={
        "family_id": "fam_nutrition",
        "name": "Sammy",
        "date_of_birth": "2016-09-15",
        "age": 9,
        "gender": "Male",
        "parent_contact": "555-123-9999"
    })
    assert child_res.status_code == 201
    child_id = child_res.json()["id"]

    # 2. Record daily nutrition log (with skipped breakfast on day 1)
    today = date.today()
    log_1 = {
        "child_id": child_id,
        "date": str(today - timedelta(days=1)),
        "breakfast_eaten": False,
        "breakfast_details": "Skipped due to rushing for school bus",
        "lunch_eaten": True,
        "lunch_details": "Turkey sandwich & apple",
        "snack_eaten": True,
        "snack_details": "Almonds",
        "dinner_eaten": True,
        "dinner_details": "Chicken and broccoli with rice",
        "water_ml": 1600,
        "water_glasses": 7,
        "meal_notes": "Felt tired in the morning after skipping breakfast."
    }
    res_log_1 = client.post("/children/nutrition/log", json=log_1)
    assert res_log_1.status_code == 201

    log_2 = {
        "child_id": child_id,
        "date": str(today),
        "breakfast_eaten": True,
        "breakfast_details": "Oatmeal with berries and honey",
        "lunch_eaten": True,
        "lunch_details": "Veggie pasta salad",
        "snack_eaten": True,
        "snack_details": "Orange slices",
        "dinner_eaten": True,
        "dinner_details": "Fish tacos",
        "water_ml": 1800,
        "water_glasses": 8,
        "meal_notes": "Felt energetic today!"
    }
    res_log_2 = client.post("/children/nutrition/log", json=log_2)
    assert res_log_2.status_code == 201

    # 3. Retrieve log by date
    res_get_log = client.get(f"/children/nutrition/{child_id}/log", params={"log_date": str(today)})
    assert res_get_log.status_code == 200
    assert res_get_log.json()["breakfast_details"] == "Oatmeal with berries and honey"

    # 4. GET summary analytics (meal consistency, water consistency, meal skipping detection, reminders)
    res_summary = client.get(f"/children/nutrition/{child_id}/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()

    assert summary["child_id"] == child_id
    assert summary["total_days_analyzed"] == 2
    assert "meal_consistency" in summary
    assert "water_consistency" in summary
    assert summary["has_skipped_meals"] is True
    assert len(summary["skipped_meals_detected"]) > 0
    assert any("Breakfast was skipped" in warning for warning in summary["skipped_meals_detected"])
    assert len(summary["basic_nutrition_reminders"]) > 0
    assert "does NOT make medical or dietary diagnoses" in summary["medical_disclaimer"]


def test_mother_agent_event_bridge(client):
    # 1. Create child profile
    child_res = client.post("/children/profile", json={
        "family_id": "fam_sports",
        "name": "Maya",
        "date_of_birth": "2014-03-10",
        "age": 12,
        "gender": "Female",
        "parent_contact": "555-777-6666"
    })
    child_id = child_res.json()["id"]

    # 2. Trigger Mother Agent bridge event (School sports event tomorrow)
    tomorrow = date.today() + timedelta(days=1)
    bridge_payload = {
        "child_id": child_id,
        "date": str(tomorrow),
        "event_name": "School Sports Event",
        "child_recommendation": "Need extra snack/water for tomorrow's sports event.",
        "mother_agent_grocery_items": ["Fruit snacks", "Energy bars", "Hydration electrolyte drinks"]
    }
    res_bridge = client.post("/children/nutrition/mother-agent-event", json=bridge_payload)
    assert res_bridge.status_code == 201
    event_data = res_bridge.json()
    assert event_data["event_name"] == "School Sports Event"
    assert event_data["status"] == "PENDING_MOTHER_AGENT_SYNC"

    # 3. Retrieve Mother Agent bridge events
    res_events = client.get(f"/children/nutrition/{child_id}/mother-agent-events")
    assert res_events.status_code == 200
    assert len(res_events.json()) == 1
    assert "Fruit snacks" in res_events.json()[0]["mother_agent_grocery_items"]

    # 4. Verify summary includes Mother Agent event recommendations
    res_summary = client.get(f"/children/nutrition/{child_id}/summary")
    assert res_summary.status_code == 200
    recs = res_summary.json()["mother_agent_event_recommendations"]
    assert any("School Sports Event" in rec for rec in recs)
    assert any("Need extra snack/water" in rec for rec in recs)
