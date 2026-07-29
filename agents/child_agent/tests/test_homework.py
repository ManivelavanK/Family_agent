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
from app.models.homework import Homework
from app.services.homework_service import (
    get_overdue_homework,
    get_due_today_homework,
    get_upcoming_homework,
    get_high_priority_homework,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hw.db"
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
        if os.path.exists("test_hw.db"):
            try:
                os.remove("test_hw.db")
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

def test_homework_crud_and_status(client, session):
    # 1. Create Child Profile
    child_payload = {
        "family_id": "fam_hw",
        "name": "David",
        "date_of_birth": "2015-01-01",
        "age": 11,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    # 2. Add Homework Tasks (Overdue, Due Today, Upcoming, High Priority)
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Overdue task
    hw_overdue = {
        "family_id": "fam_hw",
        "child_id": child_id,
        "subject": "Math",
        "title": "Algebra Sheet 1",
        "description": "Linear equations",
        "assigned_date": str(yesterday - timedelta(days=2)),
        "due_date": str(yesterday),
        "priority": "MEDIUM",
        "estimated_minutes": 30
    }
    
    # Due today & High priority task
    hw_today_high = {
        "family_id": "fam_hw",
        "child_id": child_id,
        "subject": "Science",
        "title": "Physics Experiment Report",
        "description": "Gravity measurements",
        "assigned_date": str(yesterday),
        "due_date": str(today),
        "priority": "HIGH",
        "estimated_minutes": 45
    }

    # Upcoming task
    hw_upcoming = {
        "family_id": "fam_hw",
        "child_id": child_id,
        "subject": "History",
        "title": "WWII Essay",
        "description": "Read chapter 5",
        "assigned_date": str(today),
        "due_date": str(tomorrow),
        "priority": "LOW",
        "estimated_minutes": 60
    }

    res_h1 = client.post("/children/homework", json=hw_overdue)
    assert res_h1.status_code == 201
    h1_id = res_h1.json()["id"]

    res_h2 = client.post("/children/homework", json=hw_today_high)
    assert res_h2.status_code == 201
    h2_id = res_h2.json()["id"]

    res_h3 = client.post("/children/homework", json=hw_upcoming)
    assert res_h3.status_code == 201
    h3_id = res_h3.json()["id"]

    # 3. Check Overdue List API
    res_overdue_list = client.get(f"/children/homework/{child_id}/overdue")
    assert res_overdue_list.status_code == 200
    assert len(res_overdue_list.json()) == 1
    assert res_overdue_list.json()[0]["id"] == h1_id

    # 4. Check status list functions directly in service
    due_today_list = get_due_today_homework(session, child_id)
    assert len(due_today_list) == 1
    assert due_today_list[0].id == h2_id

    upcoming_list = get_upcoming_homework(session, child_id)
    assert len(upcoming_list) == 1
    assert upcoming_list[0].id == h3_id

    high_priority_list = get_high_priority_homework(session, child_id)
    assert len(high_priority_list) == 1
    assert high_priority_list[0].id == h2_id

    # 5. Mark Completed
    res_complete = client.patch(f"/children/homework/{h1_id}/complete")
    assert res_complete.status_code == 200
    assert res_complete.json()["completion_status"] is True
    assert res_complete.json()["completion_date"] == str(today)

    # 6. Verify it is no longer overdue
    res_overdue_list2 = client.get(f"/children/homework/{child_id}/overdue")
    assert len(res_overdue_list2.json()) == 0

def test_homework_recommendations(client):
    # 1. School Child Profile (Age 10)
    child_school = {
        "family_id": "fam_hw",
        "name": "School kid",
        "date_of_birth": "2016-01-01",
        "age": 10,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_school = client.post("/children/profile", json=child_school)
    school_id = res_school.json()["id"]

    res_school_recs = client.get(f"/children/homework/{school_id}/recommendations")
    assert res_school_recs.status_code == 200
    school_data = res_school_recs.json()
    assert school_data["planning_style"] == "Subject-Based Homework Planning"
    assert len(school_data["tips"]) > 0
    assert "subjects" in school_data["tips"][0].lower()

    # 2. College Student Profile (Age 19)
    child_college = {
        "family_id": "fam_hw",
        "name": "College student",
        "date_of_birth": "2007-01-01",
        "age": 19,
        "gender": "Female",
        "parent_contact": "999-999-9999"
    }
    res_college = client.post("/children/profile", json=child_college)
    college_id = res_college.json()["id"]

    res_college_recs = client.get(f"/children/homework/{college_id}/recommendations")
    assert res_college_recs.status_code == 200
    college_data = res_college_recs.json()
    assert college_data["planning_style"] == "Assignments, Projects, Labs & Deadlines"
    assert len(college_data["tips"]) > 0
    assert "milestones" in college_data["tips"][0].lower()

def test_homework_actual_minutes_regression(client, session):
    child_payload = {
        "family_id": "fam_hw_regr",
        "name": "Alex",
        "date_of_birth": "2015-01-01",
        "age": 11,
        "gender": "Male",
        "parent_contact": "999-999-9999"
    }
    res_child = client.post("/children/profile", json=child_payload)
    assert res_child.status_code == 201
    child_id = res_child.json()["id"]

    today = date.today()
    hw_payload = {
        "family_id": "fam_hw_regr",
        "child_id": child_id,
        "subject": "Science",
        "title": "Lab Report",
        "assigned_date": today.isoformat(),
        "due_date": (today + timedelta(days=2)).isoformat(),
        "priority": "HIGH",
        "estimated_minutes": 60,
        "actual_minutes": 45
    }
    res_hw = client.post("/children/homework", json=hw_payload)
    assert res_hw.status_code == 201
    assert res_hw.json()["actual_minutes"] == 45

