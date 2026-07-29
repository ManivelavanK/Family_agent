import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
# Import models to ensure tables are created
from app.models.profile import ChildProfile
from app.models.attendance import Attendance

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_attendance.db"
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
        if os.path.exists("test_attendance.db"):
            try:
                os.remove("test_attendance.db")
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

def test_attendance_crud_and_metrics(client):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_att",
        "name": "Ian",
        "date_of_birth": "2013-05-05",
        "age": 13,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Log Attendance Records
    # Present: 8 times, Absent: 2 times, Leave: 1 time.
    # Total Active: 10 sessions. Attendance Percentage: 8/10 = 80.0% (MEDIUM Risk)
    records = [
        {"child_id": child_id, "date": "2026-07-01", "subject": "Math", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-02", "subject": "Math", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-03", "subject": "Math", "status": "Absent"},
        {"child_id": child_id, "date": "2026-07-04", "subject": "Math", "status": "Leave"},
        {"child_id": child_id, "date": "2026-07-05", "subject": "Science", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-06", "subject": "Science", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-07", "subject": "Science", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-08", "subject": "Science", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-09", "subject": "Science", "status": "Absent"},
        {"child_id": child_id, "date": "2026-07-10", "subject": "English", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-11", "subject": "English", "status": "Present"},
    ]

    for rec in records:
        res = client.post("/children/attendance", json=rec)
        assert res.status_code == 201

    # 3. Check List API
    res_list = client.get(f"/children/attendance/{child_id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 11

    # 4. Check Summary API
    res_summary = client.get(f"/children/attendance/{child_id}/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["days_present"] == 8
    assert summary["days_absent"] == 2
    assert summary["days_on_leave"] == 1
    assert summary["attendance_percentage"] == 80.0
    
    # Subject breakdown check
    # Math: 2 present, 1 absent => 66.7%
    # Science: 4 present, 1 absent => 80.0%
    # English: 2 present, 0 absent => 100.0%
    assert summary["subject_wise_attendance"]["Math"] == 66.7
    assert summary["subject_wise_attendance"]["Science"] == 80.0
    assert summary["subject_wise_attendance"]["English"] == 100.0
    
    # Monthly breakdown check
    assert summary["monthly_attendance"]["2026-07"] == 80.0

    # 5. Check Risk API (threshold = 75%)
    # Current: 8/10 = 80%. Target 75%.
    # Safe consecutive misses: M <= 8/0.75 - 10 = 10.67 - 10 = 0.67 => floor is 0 classes.
    # Wait, let's verify math: if we miss 1 class, total active becomes 11, present remains 8.
    # 8/11 = 72.7% which is below 75%. So safe misses = 0. That's correct!
    res_risk = client.get(f"/children/attendance/{child_id}/risk")
    assert res_risk.status_code == 200
    risk = res_risk.json()
    assert risk["attendance_percentage"] == 80.0
    assert risk["risk_level"] == "MEDIUM"  # 80% to 89.9%
    assert risk["classes_can_miss"] == 0
    assert risk["classes_needed_to_recover"] == 0

def test_attendance_critical_risk(client):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_att",
        "name": "Jack",
        "date_of_birth": "2013-05-05",
        "age": 13,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    child_id = res_child.json()["id"]

    # 2. Log Attendance: 1 present, 3 absent. Total active = 4. Percentage = 25.0%
    records = [
        {"child_id": child_id, "date": "2026-07-01", "subject": "Math", "status": "Present"},
        {"child_id": child_id, "date": "2026-07-02", "subject": "Math", "status": "Absent"},
        {"child_id": child_id, "date": "2026-07-03", "subject": "Math", "status": "Absent"},
        {"child_id": child_id, "date": "2026-07-04", "subject": "Math", "status": "Absent"},
    ]
    for rec in records:
        client.post("/children/attendance", json=rec)

    # 3. Check Risk API
    # Recover threshold = 75%.
    # (1 + R) / (4 + R) >= 0.75 ==> 1 + R >= 3 + 0.75R ==> 0.25R >= 2 ==> R >= 8 classes.
    # Let's verify: if we attend 8 classes, present becomes 9, total active becomes 12.
    # 9/12 = 75.0% (target reached!). So recovery classes R = 8.
    res_risk = client.get(f"/children/attendance/{child_id}/risk")
    assert res_risk.status_code == 200
    risk = res_risk.json()
    assert risk["attendance_percentage"] == 25.0
    assert risk["risk_level"] == "CRITICAL"
    assert risk["classes_can_miss"] == 0
    assert risk["classes_needed_to_recover"] == 8
