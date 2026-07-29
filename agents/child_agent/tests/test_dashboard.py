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
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense
from app.models.safety import CheckInLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dashboard.db"
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
        if os.path.exists("test_dashboard.db"):
            try:
                os.remove("test_dashboard.db")
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

def test_get_daily_dashboard(client, session):
    # 1. Create Child Profile
    child = ChildProfile(
        family_id="fam_dash_1",
        name="Elena",
        age=15,
        date_of_birth=date(2011, 8, 12),
        gender="Female",
        parent_contact="555-444-3333",
        education_stage="High School"
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    # 2. Add some logs to satisfy MIN_SAMPLES for ML and ensure no exceptions
    today = date.today()
    for i in range(5):
        day = today - timedelta(days=i)
        # Homework logs
        hw = Homework(
            family_id="fam_dash_1",
            child_id=child.id,
            subject="Math",
            title=f"Homework {i}",
            assigned_date=day,
            due_date=day,
            completion_status=True,
            estimated_minutes=30,
            actual_minutes=25
        )
        # Attendance logs
        att = Attendance(
            child_id=child.id,
            date=day,
            subject="Math",
            status="PRESENT"
        )
        # Screen time logs
        st = ScreenTimeLog(
            child_id=child.id,
            date=day,
            mobile=15,
            gaming=20,
            tv=10,
            social_media=15,
            study_screen_time=30,
            other=10
        )
        session.add_all([hw, att, st])
    
    # Add pending check-in
    check_in = CheckInLog(
        child_id=child.id,
        date=today,
        expected_return_time=time(20, 0),
        status="EXPECTED"
    )
    # Add pocket money & expenses
    allowance = PocketMoneyAllowance(
        family_id="fam_dash_1",
        child_id=child.id,
        amount=1500.0,
        frequency="Monthly",
        date=today
    )
    expense = ChildExpense(
        family_id="fam_dash_1",
        child_id=child.id,
        amount=300.0,
        category="Food",
        date=today
    )
    session.add_all([check_in, allowance, expense])
    session.commit()

    # 3. Call GET /children/dashboard/{child_id}
    res = client.get(f"/children/dashboard/{child.id}")
    assert res.status_code == 200
    data = res.json()
    assert "greeting" in data
    assert "timetable" in data
    assert "important_alerts" in data
    assert "recommendations" in data
    assert "aggregated_data" in data

    # Phase 6 AI Dashboard assertions
    assert "overall_status" in data
    assert "todays_priorities" in data
    assert "what_should_i_do_today" in data
    assert "what_should_parent_know" in data
    assert "recommended_study_plan" in data

    agg = data["aggregated_data"]
    assert agg["profile"]["name"] == "Elena"
    assert agg["pocket_money"]["remaining_balance"] == 1200.0

