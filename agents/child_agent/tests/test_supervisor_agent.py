import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.screen_time import ScreenTimeLog

from app.agents.supervisor_agent import SupervisorAgent


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_sup_1",
        name="Lucas",
        date_of_birth=date(2013, 4, 1),
        age=12,
        gender="MALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-9000",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


def test_routing_exam_query(db_session):
    supervisor = SupervisorAgent(db=db_session)
    res = supervisor.process_and_execute(child_id=1, query="My exam is next week and I haven't studied enough.")

    selected = res["selected_agents"]
    assert "ExamPlannerAgent" in selected
    assert "StudyCoachAgent" in selected
    assert "EducationAgent" in selected

    assert len(res["execution_logs"]) >= 3
    assert res["combined_reply"] is not None


def test_routing_screentime_and_homework_query(db_session):
    # Setup pending homework and high screen time
    db_session.add(Homework(family_id="fam_sup_1", child_id=1, subject="Math", title="Algebra", assigned_date=date.today(), due_date=date.today(), completion_status=False))
    db_session.add(ScreenTimeLog(child_id=1, date=date.today(), mobile=120, gaming=60, tv=30, social_media=0, study_screen_time=0, other=0, late_night_minutes=0))
    db_session.commit()

    supervisor = SupervisorAgent(db=db_session)
    res = supervisor.process_and_execute(child_id=1, query="My child is spending too much time on the phone and has assignments pending.")

    selected = res["selected_agents"]
    assert "ScreenTimeAgent" in selected
    assert "EducationAgent" in selected
    assert "ParentCommunicationAgent" in selected

    # Verify conflict detection
    assert len(res["detected_conflicts"]) > 0
    assert any("Conflict" in c for c in res["detected_conflicts"])


def test_routing_finance_query(db_session):
    supervisor = SupervisorAgent(db=db_session)
    res = supervisor.process_and_execute(child_id=1, query="Can I afford to buy a course for ₹1500?")

    selected = res["selected_agents"]
    assert "FinanceAgent" in selected
    assert res["execution_logs"][0]["status"] == "SUCCESS"


def test_routing_wellness_query(db_session):
    supervisor = SupervisorAgent(db=db_session)
    res = supervisor.process_and_execute(child_id=1, query="I feel stressed and anxious about school.")

    selected = res["selected_agents"]
    assert "WellnessAgent" in selected
    assert "StudyCoachAgent" in selected
