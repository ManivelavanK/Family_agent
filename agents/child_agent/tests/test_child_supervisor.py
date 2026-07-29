import os
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app.models.profile import ChildProfile
from app.agents import child_supervisor

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_supervisor.db"
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
        if os.path.exists("test_supervisor.db"):
            try:
                os.remove("test_supervisor.db")
            except Exception:
                pass

def test_supervisor_deterministic_routing(session):
    # 1. Create a child profile
    child = ChildProfile(
        family_id="fam_sup_1",
        name="Timmy",
        age=10,
        date_of_birth=date(2016, 5, 20),
        gender="Male",
        parent_contact="555-555-5555",
        education_stage="Primary School"
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    # 2. Test Education Agent Routing
    res = child_supervisor.route_and_execute(session, child.id, "What should I study today?")
    assert res["routed_category"] == "EDUCATION"
    assert "Education Agent" in res["agent"]

    res = child_supervisor.route_and_execute(session, child.id, "I have an exam in 5 days.")
    assert res["routed_category"] == "EDUCATION"
    assert "upcoming_exams_count" in res["actions"]

    # 3. Test Finance Agent Routing
    res = child_supervisor.route_and_execute(session, child.id, "I spent ₹300 today.")
    assert res["routed_category"] == "FINANCE"
    assert "Finance Agent" in res["agent"]

    res = child_supervisor.route_and_execute(session, child.id, "Can I afford this ₹2,000 course?")
    assert res["routed_category"] == "FINANCE"
    assert "can_afford" in res["actions"]

    # 4. Test Safety Agent Routing
    res = child_supervisor.route_and_execute(session, child.id, "I am going out and will return at 8.")
    assert res["routed_category"] == "SAFETY"
    assert "Safety Agent" in res["agent"]

    # 5. Test Wellness Agent Routing
    res = child_supervisor.route_and_execute(session, child.id, "I am stressed.")
    assert res["routed_category"] == "WELLNESS"
    assert "Wellness Agent" in res["agent"]

    # 6. Test Routine / Screen Time Routing
    res = child_supervisor.route_and_execute(session, child.id, "How much screen time did I use this week?")
    assert res["routed_category"] == "ROUTINE"
    assert "average_daily_screen_time_hours" in res["actions"]
