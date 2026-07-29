import os
import pytest
from datetime import date, timedelta, time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
# Import models to ensure tables are created
from app.models.profile import ChildProfile
from app.models.activity import Activity

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_activities.db"
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
        if os.path.exists("test_activities.db"):
            try:
                os.remove("test_activities.db")
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

def test_activities_crud_and_agenda_conflicts(client):
    # 1. Create Child Profile (School Student: age 10)
    child_payload = {
        "family_id": "fam_act",
        "name": "Milo",
        "date_of_birth": "2016-01-01",
        "age": 10,
        "gender": "Male",
        "parent_contact": "999-999-9999",
        "daily_wake_time": "06:30:00",
        "daily_sleep_time": "21:30:00"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Add Homework due today to insert Homework block in agenda
    today = date.today()
    hw_payload = {
        "family_id": "fam_act",
        "child_id": child_id,
        "subject": "Mathematics",
        "title": "Algebra page 10",
        "assigned_date": str(today),
        "due_date": str(today),
        "priority": "High",
        "estimated_minutes": 45
    }
    client.post("/children/homework", json=hw_payload)

    # 3. Create overlapping activity to trigger conflict
    # Homework block runs from 16:30 to 17:30.
    # Let's add Tuition from 17:00 to 18:00 (this overlaps with Homework!)
    act_payload = {
        "child_id": child_id,
        "title": "Math Tuition",
        "activity_type": "Tuition",
        "date": str(today),
        "start_time": "17:00:00",
        "end_time": "18:00:00",
        "priority": "High"
    }
    res_act = client.post("/children/activities", json=act_payload)
    assert res_act.status_code == 201
    act_id = res_act.json()["id"]

    # Verify List API
    res_list = client.get(f"/children/activities/{child_id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 4. Fetch Agenda Today
    res_agenda = client.get(f"/children/agenda/{child_id}/today")
    assert res_agenda.status_code == 200
    agenda_days = res_agenda.json()
    assert len(agenda_days) == 1
    
    day = agenda_days[0]
    assert day["total_conflicting_items"] >= 2
    
    items = day["items"]
    # Check that Tuition and Homework are flagged conflicting
    homework_item = [i for i in items if "homework" in i["title"].lower()][0]
    tuition_item = [i for i in items if "tuition" in i["title"].lower()][0]
    assert homework_item["is_conflict"] is True
    assert tuition_item["is_conflict"] is True
    assert "Tuition" in homework_item["conflict_description"]

    # Verify School Hours exist (age 10 is School Child)
    # Note: School Hours only exist on weekdays. Let's check weekday vs weekend.
    is_weekday = today.weekday() < 5
    school_hours_exist = any("School Hours" in i["title"] for i in items)
    assert school_hours_exist == is_weekday

def test_activities_college_agenda(client):
    # 1. Create College Child Profile (age 19)
    child_payload = {
        "family_id": "fam_act",
        "name": "Nadia",
        "date_of_birth": "2007-01-01",
        "age": 19,
        "gender": "Female",
        "parent_contact": "999-999-9999",
        "daily_wake_time": "07:00:00",
        "daily_sleep_time": "23:00:00"
    }
    res_child = client.post("/children/profile", json=child_payload)
    child_id = res_child.json()["id"]

    # 2. Fetch Weekly Agenda
    res_agenda = client.get(f"/children/agenda/{child_id}/week")
    assert res_agenda.status_code == 200
    agenda_days = res_agenda.json()
    assert len(agenda_days) == 7

    # Verify College Lectures exists on at least one day (on a weekday)
    has_lectures = False
    for day in agenda_days:
        for item in day["items"]:
            if "College Lectures" in item["title"]:
                has_lectures = True
                break
    # Since a week of 7 days must contain at least one weekday, this must be True
    assert has_lectures is True
