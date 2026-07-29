import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_schedule_log.db"
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
        if os.path.exists("test_schedule_log.db"):
            try:
                os.remove("test_schedule_log.db")
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


def test_school_and_college_schedule_workflows(client):
    # 1. Create School child (age 10)
    school_res = client.post("/children/profile", json={
        "family_id": "fam_sched_school",
        "name": "Benny",
        "date_of_birth": "2016-02-14",
        "age": 10,
        "gender": "Male",
        "parent_contact": "555-111-2222"
    })
    assert school_res.status_code == 201
    school_child_id = school_res.json()["id"]

    # 2. Create College student (age 19)
    college_res = client.post("/children/profile", json={
        "family_id": "fam_sched_college",
        "name": "Chloe",
        "date_of_birth": "2007-06-01",
        "age": 19,
        "gender": "Female",
        "parent_contact": "555-333-4444"
    })
    assert college_res.status_code == 201
    college_child_id = college_res.json()["id"]

    today = date.today()
    day_name = today.strftime("%A")

    # 3. Add School schedule items
    client.post("/children/schedule", json={
        "child_id": school_child_id,
        "day_of_week": day_name,
        "subject": "Morning School Bus #4",
        "start_time": "07:30:00",
        "end_time": "08:15:00",
        "transport_info": "Bus Route #4 - Stop A",
        "schedule_type": "BUS"
    })
    client.post("/children/schedule", json={
        "child_id": school_child_id,
        "day_of_week": day_name,
        "subject": "Morning Assembly",
        "start_time": "08:30:00",
        "end_time": "08:45:00",
        "room": "Courtyard",
        "schedule_type": "ASSEMBLY"
    })
    client.post("/children/schedule", json={
        "child_id": school_child_id,
        "day_of_week": day_name,
        "subject": "Mathematics (Period 1)",
        "start_time": "09:00:00",
        "end_time": "09:45:00",
        "room": "Room 101",
        "teacher": "Mrs. Davis",
        "schedule_type": "PERIOD"
    })

    # 4. Add College schedule items
    client.post("/children/schedule", json={
        "child_id": college_child_id,
        "day_of_week": day_name,
        "subject": "Metro Commute to Campus",
        "start_time": "08:15:00",
        "end_time": "08:50:00",
        "transport_info": "Red Line Express Metro",
        "schedule_type": "COMMUTE"
    })
    client.post("/children/schedule", json={
        "child_id": college_child_id,
        "day_of_week": day_name,
        "subject": "Computer Systems Architecture",
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "room": "Hall A",
        "teacher": "Dr. Alan Turing",
        "schedule_type": "LECTURE"
    })
    client.post("/children/schedule", json={
        "child_id": college_child_id,
        "day_of_week": day_name,
        "subject": "Robotics Lab",
        "start_time": "11:00:00",
        "end_time": "13:00:00",
        "room": "Tech Lab 3",
        "teacher": "Prof. Ada Lovelace",
        "schedule_type": "LAB"
    })

    # 5. GET /children/schedule/{child_id}/today for School child
    res_school_today = client.get(f"/children/schedule/{school_child_id}/today")
    assert res_school_today.status_code == 200
    st_school = res_school_today.json()
    assert st_school["education_stage"] == "SCHOOL"
    assert len(st_school["schedule_items"]) == 3
    assert len(st_school["bus_timings"]) == 1
    assert "School Timetable" in st_school["summary"]

    # 6. GET /children/schedule/{child_id}/today for College student
    res_college_today = client.get(f"/children/schedule/{college_child_id}/today")
    assert res_college_today.status_code == 200
    st_college = res_college_today.json()
    assert st_college["education_stage"] == "COLLEGE"
    assert len(st_college["schedule_items"]) == 3
    assert "College Timetable" in st_college["summary"]

    # 7. GET /children/schedule/{child_id}/week
    res_week = client.get(f"/children/schedule/{school_child_id}/week")
    assert res_week.status_code == 200
    week_data = res_week.json()
    day_key = day_name.lower()
    assert len(week_data[day_key]) == 3

    # 8. Holiday Calendar Test
    client.post("/children/schedule/holiday", json={
        "child_id": school_child_id,
        "date": str(today),
        "title": "National Holiday",
        "description": "School is closed today.",
        "is_no_school": True
    })

    res_today_holiday = client.get(f"/children/schedule/{school_child_id}/today")
    assert res_today_holiday.status_code == 200
    holiday_st = res_today_holiday.json()
    assert holiday_st["is_holiday"] is True
    assert holiday_st["holiday_info"]["title"] == "National Holiday"
    assert "is a Holiday" in holiday_st["summary"]
