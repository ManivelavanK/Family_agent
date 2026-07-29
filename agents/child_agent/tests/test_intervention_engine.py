import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.screen_time import ScreenTimeLog
from app.models.study import StudySession

from app.schemas.context import ChildContext
from app.ai.context_builder import ChildContextBuilder
from app.services.intervention_engine import AIFamilyInterventionEngine, INTERVENTION_HISTORY_STORE


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_intv_100",
        name="Leo",
        date_of_birth=date(2013, 3, 10),
        age=12,
        gender="MALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-7777",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


def test_multi_domain_intervention_plan_generation(db_session):
    INTERVENTION_HISTORY_STORE.clear()

    # Setup scenario: Exam approaching + High screen time + Low study focus
    db_session.add(Exam(child_id=1, exam_name="Final Math", subject="Math", exam_date=date.today(), preparation_percentage=45, difficulty="Hard"))
    db_session.add(ScreenTimeLog(child_id=1, date=date.today(), mobile=120, gaming=60, tv=30, social_media=0, study_screen_time=0, other=0, late_night_minutes=0))
    db_session.add(StudySession(child_id=1, subject="Math", topic="Geometry", start_time=date.today(), end_time=date.today(), duration_minutes=15, focus_score=50))
    db_session.commit()

    builder = ChildContextBuilder(db=db_session, child_id=1)
    context = builder.build(include_ml_predictions=False)

    engine = AIFamilyInterventionEngine(db=db_session)
    problems = engine.detect_multi_domain_problems(context)
    assert len(problems) > 0

    plan = engine.generate_intervention_plan(child_id=1, problem_data=problems[0])

    assert plan.child_id == 1
    assert "StudyCoachAgent" in plan.selected_agents
    assert "ScreenTimeAgent" in plan.selected_agents
    assert "ActivityAgent" in plan.selected_agents
    assert "ParentCommunicationAgent" in plan.selected_agents
    assert "WellnessAgent" in plan.selected_agents
    assert "ScheduleAgent" in plan.selected_agents

    assert len(plan.actions) == 6
    assert plan.child_message is not None
    assert plan.parent_message is not None
    assert "KinNest does not secretly lock devices" in plan.parent_message


def test_consent_boundary_enforcement(db_session):
    engine = AIFamilyInterventionEngine(db=db_session)
    problem_data = {
        "problem": "High screen time detected.",
        "evidence": ["180 mins screen time"],
        "priority": "HIGH",
    }
    plan = engine.generate_intervention_plan(child_id=1, problem_data=problem_data)

    # Verify all proposed actions use recommendation/consent mode rather than secretive punishments
    for action in plan.actions:
        assert "secret device lock" not in action.description.lower()
        assert "secret punishment" not in action.description.lower()




def test_intervention_history_and_outcome_tracking(db_session):
    INTERVENTION_HISTORY_STORE.clear()

    engine = AIFamilyInterventionEngine(db=db_session)
    problem_data = {
        "problem": "Overdue homework assignments.",
        "evidence": ["2 overdue tasks"],
        "priority": "HIGH",
    }

    plan = engine.generate_intervention_plan(child_id=1, problem_data=problem_data)
    intv_id = plan.intervention_id

    # Verify history recorded
    history = AIFamilyInterventionEngine.get_intervention_history(child_id=1)
    assert len(history) == 1
    assert history[0]["intervention_id"] == intv_id
    assert history[0]["status"] == "ACTIVE"

    # Update outcome
    updated = AIFamilyInterventionEngine.update_intervention_outcome(
        intervention_id=intv_id,
        outcome_rating="IMPROVED",
        status="RESOLVED"
    )
    assert updated is not None
    assert updated["status"] == "RESOLVED"
    assert updated["outcome_rating"] == "IMPROVED"
