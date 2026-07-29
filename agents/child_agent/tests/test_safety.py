import os
import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
# Import models to ensure tables are created
from app.models.profile import ChildProfile
from app.models.safety import SafetyProfile, CheckInLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_safety_log.db"
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
        if os.path.exists("test_safety_log.db"):
            try:
                os.remove("test_safety_log.db")
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

def test_safety_escalations_and_alerts(client):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_safety",
        "name": "Penny",
        "date_of_birth": "2018-05-05",
        "age": 8,
        "gender": "Female",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Configure Safety Profile
    profile_payload = {
        "child_id": child_id,
        "trusted_contacts": [
            {"name": "Uncle Bob", "phone": "111-222-3333", "relation": "Uncle"}
        ],
        "parent_contacts": [
            {"name": "Mom", "phone": "444-555-6666", "relation": "Mother"}
        ],
        "emergency_contacts": [
            {"name": "Dr. Smith", "phone": "777-888-9999", "service_type": "Pediatrician"}
        ],
        "pickup_person": "Aunt Sally",
        "transport_info": "School Bus #4",
        "usual_locations": ["Greenwood Park", "Community Library"],
        "emergency_notes": "Allergic to bees.",
        "escalation_threshold_minutes": 15
    }
    res_profile = client.post("/children/safety/profile", json=profile_payload)
    assert res_profile.status_code == 201

    # Fetch profile verification
    res_get_prof = client.get(f"/children/safety/{child_id}/profile")
    assert res_get_prof.status_code == 200
    assert res_get_prof.json()["pickup_person"] == "Aunt Sally"
    assert res_get_prof.json()["escalation_threshold_minutes"] == 15

    # 3. Schedule Expected Return: 19:00:00 (7:00 PM)
    today = date.today()
    schedule_payload = {
        "child_id": child_id,
        "date": str(today),
        "expected_return_time": "19:00:00",
        "location_note": "Playing in Greenwood Park"
    }
    res_return = client.post(f"/children/safety/{child_id}/expected-return", json=schedule_payload)
    assert res_return.status_code == 200

    # 4. Check Status: EXPECTED at 18:30 (before return time)
    res_status = client.get(f"/children/safety/{child_id}/status", params={"current_time": "18:30:00"})
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "EXPECTED"

    # 5. Check Status: LATE at 19:10 (10 mins after return time)
    res_status_late = client.get(f"/children/safety/{child_id}/status", params={"current_time": "19:10:00"})
    assert res_status_late.json()["status"] == "LATE"

    # 6. Check Status: MISSED_CHECK_IN at 19:25 (25 mins after return time > 15 min threshold)
    res_status_missed = client.get(f"/children/safety/{child_id}/status", params={"current_time": "19:25:00"})
    assert res_status_missed.json()["status"] == "MISSED_CHECK_IN"
    assert res_status_missed.json()["parent_notified"] is True

    # 7. Check Alerts & Guidance at 19:25
    res_alerts = client.get(f"/children/safety/{child_id}/alerts", params={"current_time": "19:25:00"})
    assert res_alerts.status_code == 200
    alerts = res_alerts.json()
    assert alerts["status"] == "MISSED_CHECK_IN"
    assert alerts["minutes_late"] == 25
    assert "privacy_disclaimer" in alerts
    assert "does NOT invoke automated emergency/police" in alerts["privacy_disclaimer"]
    
    guidance = alerts["action_guidance"]
    # Ensure alerts list steps: remind child, notify parent, list trusted, check locations
    assert any("remind child" in step.lower() for step in guidance)
    assert any("mom" in step.lower() for step in guidance)
    assert any("uncle bob" in step.lower() for step in guidance)
    assert any("greenwood park" in step.lower() for step in guidance)

    # 8. Record Call Log status abstraction
    call_payload = {
        "child_id": child_id,
        "date": str(today),
        "call_time": "19:26:00",
        "call_state": "CALL_ATTEMPTED",
        "contact_name": "Mom",
        "contact_phone": "444-555-6666",
        "notes": "Attempting contact after missed check-in"
    }
    res_call = client.post("/children/safety/call-log", json=call_payload)
    assert res_call.status_code == 201

    res_call_logs = client.get(f"/children/safety/{child_id}/call-logs")
    assert res_call_logs.status_code == 200
    assert len(res_call_logs.json()) >= 1
    assert res_call_logs.json()[0]["call_state"] == "CALL_ATTEMPTED"

    # 9. Child Checks in Safely
    checkin_payload = {
        "child_id": child_id,
        "date": str(today),
        "actual_check_in_time": "19:30:00",
        "location_note": "Returned home safely"
    }
    res_checkin = client.post("/children/safety/check-in", json=checkin_payload)
    assert res_checkin.status_code == 200
    assert res_checkin.json()["status"] == "SAFE"

    # Verify status is now SAFE
    res_status_safe = client.get(f"/children/safety/{child_id}/status")
    assert res_status_safe.json()["status"] == "SAFE"


def test_emergency_status_and_custom_escalation(client):
    # 1. Create Child
    child_res = client.post("/children/profile", json={
        "family_id": "fam_emerg",
        "name": "Tommy",
        "date_of_birth": "2016-01-01",
        "age": 10,
        "gender": "Male",
        "parent_contact": "555-123-4567"
    })
    child_id = child_res.json()["id"]

    # 2. Safety Profile with custom threshold = 5 mins
    client.post("/children/safety/profile", json={
        "child_id": child_id,
        "escalation_threshold_minutes": 5
    })

    # 3. Schedule return at 17:00
    today = date.today()
    client.post(f"/children/safety/{child_id}/expected-return", json={
        "child_id": child_id,
        "date": str(today),
        "expected_return_time": "17:00:00"
    })

    # At 17:07 (7 mins late > 5 min custom threshold) -> MISSED_CHECK_IN
    st = client.get(f"/children/safety/{child_id}/status", params={"current_time": "17:07:00"}).json()
    assert st["status"] == "MISSED_CHECK_IN"

    # 4. Trigger manual EMERGENCY check-in / alert
    client.post("/children/safety/check-in", json={
        "child_id": child_id,
        "date": str(today),
        "actual_check_in_time": "17:10:00",
        "location_note": "SOS triggered by child or parent",
        "status": "EMERGENCY"
    })

    alert = client.get(f"/children/safety/{child_id}/alerts").json()
    assert alert["status"] == "EMERGENCY"
    assert alert["parent_notified"] is True

