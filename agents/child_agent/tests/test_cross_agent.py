import os
import pytest
from datetime import date, timedelta, time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.attendance import Attendance
from app.models.screen_time import ScreenTimeLog
from app.models.pocket_money import ChildExpense, SavingGoal
from app.models.exam import Exam
from app.models.activity import Activity
from app.models.schedule import ScheduleItem, HolidayCalendar
from app.models.nutrition import MotherAgentBridgeEvent
from app.models.safety import CheckInLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cross_agent.db"
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
        if os.path.exists("test_cross_agent.db"):
            try:
                os.remove("test_cross_agent.db")
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

def test_cross_agent_flows(client, session):
    # 1. Create Child Profile
    child = ChildProfile(
        family_id="fam_cross",
        name="Leo",
        age=12,
        date_of_birth=date(2014, 4, 15),
        gender="Male",
        parent_contact="555-000-1111",
        education_stage="Middle School"
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    # 2. Add homework, attendance, screentime, and savings goals
    today = date.today()
    hw = Homework(
        family_id="fam_cross",
        child_id=child.id,
        subject="Math",
        title="Algebra Worksheet",
        assigned_date=today,
        due_date=today,
        completion_status=False
    )
    att = Attendance(
        child_id=child.id,
        date=today,
        subject="Math",
        status="PRESENT"
    )
    st = ScreenTimeLog(
        child_id=child.id,
        date=today,
        mobile=30,
        gaming=60,
        tv=30,
        social_media=0,
        study_screen_time=45,
        other=15
    )
    sg = SavingGoal(
        child_id=child.id,
        title="Laptop",
        target_amount=500.0,
        current_saved=150.0,
        target_date=today + timedelta(days=60)
    )
    session.add_all([hw, att, st, sg])
    session.commit()

    # 3. Test GET child-summary
    res = client.get(f"/api/v1/family/child-summary/fam_cross")
    assert res.status_code == 200
    data = res.json()
    assert data["family_id"] == "fam_cross"
    assert len(data["summaries"]) == 1
    summary = data["summaries"][0]
    assert summary["name"] == "Leo"
    assert summary["pending_homework_count"] == 1
    assert summary["attendance_rate"] == 100.0
    assert summary["average_screen_time_hours"] == 3.0  # (30+60+30+0+45+15)/60 = 180/60 = 3.0
    assert len(summary["saving_goals_progress"]) == 1
    assert summary["saving_goals_progress"][0]["title"] == "Laptop"

    # 4. Test POST child-expense
    expense_payload = {
        "family_id": "fam_cross",
        "child_id": child.id,
        "amount": 15.50,
        "category": "Food",
        "description": "Lunch at school cafe",
        "date": today.isoformat()
    }
    res = client.post("/api/v1/family/child-expense", json=expense_payload)
    print("CHILD EXPENSE RESPONSE ERROR DETAILS:", res.json())
    assert res.status_code == 201
    exp_data = res.json()
    assert exp_data["amount"] == 15.50
    assert exp_data["category"] == "Food"

    # 5. Test POST child-education-expense
    edu_payload = {
        "family_id": "fam_cross",
        "child_id": child.id,
        "amount": 120.00,
        "expense_type": "Books",
        "description": "Semester textbook purchases",
        "date": today.isoformat()
    }
    res = client.post("/api/v1/family/child-education-expense", json=edu_payload)
    assert res.status_code == 201
    edu_data = res.json()
    assert edu_data["amount"] == 120.00
    assert edu_data["expense_type"] == "Books"
    assert edu_data["description"] == "Semester textbook purchases"

    # 6. Test GET child-events
    # Seed events
    ex = Exam(child_id=child.id, subject="Math", exam_name="Algebra Finals", exam_date=today)
    act = Activity(child_id=child.id, title="Soccer Practice", activity_type="Sports", date=today, start_time=time(16, 0), end_time=time(17, 30))
    sched = ScheduleItem(child_id=child.id, day_of_week="Monday", subject="Science", start_time=time(9, 0), end_time=time(10, 0), schedule_type="PERIOD")
    holiday = HolidayCalendar(child_id=child.id, date=today, title="Independence Day")
    session.add_all([ex, act, sched, holiday])
    session.commit()

    res = client.get("/api/v1/family/child-events/fam_cross")
    assert res.status_code == 200
    events_data = res.json()
    assert events_data["family_id"] == "fam_cross"
    assert len(events_data["events"]) >= 4

    # 7. Test GET child-grocery-needs
    bridge_evt = MotherAgentBridgeEvent(
        child_id=child.id,
        date=today,
        event_name="School Picnic",
        child_recommendation="Need juices and snacks",
        mother_agent_grocery_items=["Apple Juice", "Granola Bars"],
        status="PENDING_MOTHER_AGENT_SYNC"
    )
    session.add(bridge_evt)
    session.commit()

    res = client.get("/api/v1/family/child-grocery-needs/fam_cross")
    assert res.status_code == 200
    grocery_data = res.json()
    assert grocery_data["family_id"] == "fam_cross"
    assert len(grocery_data["needs"]) == 1
    assert grocery_data["needs"][0]["event_name"] == "School Picnic"
    assert grocery_data["needs"][0]["items"] == ["Apple Juice", "Granola Bars"]

    # 8. Test POST child-check-in
    checkin_payload = {
        "child_id": child.id,
        "date": today.isoformat(),
        "expected_return_time": "15:30:00",
        "actual_check_in_time": "15:25:00",
        "location_note": "School Gate",
        "status": "SAFE"
    }
    res = client.post("/api/v1/family/child-check-in", json=checkin_payload)
    assert res.status_code == 200
    checkin_data = res.json()
    assert checkin_data["status"] == "SAFE"
    assert checkin_data["location_note"] == "School Gate"

    # 9. Test POST child-alert
    alert_payload = {
        "child_id": child.id,
        "alert_type": "EMERGENCY",
        "message": "Panic button pressed",
        "location_note": "Unknown coordinates"
    }
    res = client.post("/api/v1/family/child-alert", json=alert_payload)
    assert res.status_code == 200
    alert_data = res.json()
    assert alert_data["alert_type"] == "EMERGENCY"
    assert alert_data["status"] == "LOGGED"

def test_cross_family_rejections(client, session):
    # Create Child 1 in Family 1
    child1 = ChildProfile(
        family_id="fam_1",
        name="Timmy",
        age=8,
        date_of_birth=date(2018, 5, 20),
        gender="Male",
        parent_contact="555-555-5555",
        education_stage="Primary School"
    )
    # Create Child 2 in Family 2
    child2 = ChildProfile(
        family_id="fam_2",
        name="Sally",
        age=10,
        date_of_birth=date(2016, 5, 20),
        gender="Female",
        parent_contact="555-555-6666",
        education_stage="Primary School"
    )
    session.add_all([child1, child2])
    session.commit()
    session.refresh(child1)
    session.refresh(child2)

    # 1. Valid Expense: Family 1 + Child 1 -> Success
    res = client.post("/api/v1/family/child-expense", json={
        "family_id": "fam_1",
        "child_id": child1.id,
        "amount": 10.0,
        "category": "Food"
    })
    assert res.status_code == 201

    # 2. Invalid Expense: Family 1 + Child belonging to Family 2 -> 403
    res = client.post("/api/v1/family/child-expense", json={
        "family_id": "fam_1",
        "child_id": child2.id,
        "amount": 10.0,
        "category": "Food"
    })
    assert res.status_code == 403

    # 3. Nonexistent Child Expense -> 404
    res = client.post("/api/v1/family/child-expense", json={
        "family_id": "fam_1",
        "child_id": 9999,
        "amount": 10.0,
        "category": "Food"
    })
    assert res.status_code == 404

    # 4. Valid Education Expense: Family 1 + Child 1 -> Success
    res = client.post("/api/v1/family/child-education-expense", json={
        "family_id": "fam_1",
        "child_id": child1.id,
        "amount": 50.0,
        "expense_type": "Books"
    })
    assert res.status_code == 201

    # 5. Invalid Education Expense: Family 1 + Child belonging to Family 2 -> 403
    res = client.post("/api/v1/family/child-education-expense", json={
        "family_id": "fam_1",
        "child_id": child2.id,
        "amount": 50.0,
        "expense_type": "Books"
    })
    assert res.status_code == 403

    # 6. Nonexistent Child Education Expense -> 404
    res = client.post("/api/v1/family/child-education-expense", json={
        "family_id": "fam_1",
        "child_id": 9999,
        "amount": 50.0,
        "expense_type": "Books"
    })
    assert res.status_code == 404

def test_check_in_statuses(client, session):
    child = ChildProfile(
        family_id="fam_check",
        name="Billy",
        age=12,
        date_of_birth=date(2014, 4, 15),
        gender="Male",
        parent_contact="555-000-1111",
        education_stage="Middle School"
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    # Valid check-in statuses
    for status_val in ["SAFE", "EXPECTED", "LATE", "MISSED_CHECK_IN", "EMERGENCY"]:
        res = client.post("/api/v1/family/child-check-in", json={
            "child_id": child.id,
            "expected_return_time": "18:00:00",
            "status": status_val
        })
        assert res.status_code == 200
        assert res.json()["status"] == status_val

    # Invalid status -> 422 Validation Error
    res = client.post("/api/v1/family/child-check-in", json={
        "child_id": child.id,
        "expected_return_time": "18:00:00",
        "status": "INVALID_STATUS"
    })
    assert res.status_code == 422

