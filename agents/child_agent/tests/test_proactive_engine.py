import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.screen_time import ScreenTimeLog
from app.models.pocket_money import SavingGoal, ChildExpense
from app.models.safety import CheckInLog
from app.models.nutrition import NutritionLog

from app.services.proactive_engine import ProactiveChildIntelligenceEngine


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_pro_100",
        name="Elena",
        date_of_birth=date(2013, 9, 15),
        age=12,
        gender="FEMALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-8888",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


def test_academic_proactive_detections(db_session):
    # Homework overdue & approaching exam
    db_session.add(Homework(family_id="fam_pro_100", child_id=1, subject="Physics", title="Gravity Lab", assigned_date=date.today(), due_date=date(2025, 1, 1), completion_status=False))
    db_session.add(Exam(child_id=1, exam_name="Midterm Physics", subject="Physics", exam_date=date.today(), preparation_percentage=40, difficulty="Hard"))
    db_session.commit()

    engine = ProactiveChildIntelligenceEngine(db=db_session)
    report = engine.analyze_child(child_id=1)

    event_types = [i.event_type for i in report.insights]
    assert "HOMEWORK_OVERDUE" in event_types
    assert "EXAM_INSUFFICIENT_PREPARATION" in event_types
    assert report.new_insights_logged > 0


def test_wellness_and_safety_proactive_detections(db_session):
    db_session.add(ScreenTimeLog(child_id=1, date=date.today(), mobile=120, gaming=60, tv=30, social_media=0, study_screen_time=0, other=0, late_night_minutes=15))
    db_session.add(CheckInLog(child_id=1, date=date.today(), expected_return_time=time(18, 0), status="OVERDUE", location_note="Park"))
    db_session.add(NutritionLog(child_id=1, date=date.today(), breakfast_eaten=False, water_ml=600))
    db_session.commit()

    engine = ProactiveChildIntelligenceEngine(db=db_session)
    report = engine.analyze_child(child_id=1)

    event_types = [i.event_type for i in report.insights]
    assert "EXCESSIVE_SCREEN_TIME" in event_types
    assert "SAFETY_STATUS_ATTENTION" in event_types
    assert "NUTRITION_HYDRATION_CONCERN" in event_types


def test_deduplication_cooldown(db_session):
    db_session.add(Homework(family_id="fam_pro_100", child_id=1, subject="History", title="Essay", assigned_date=date.today(), due_date=date(2025, 1, 1), completion_status=False))
    db_session.commit()

    engine = ProactiveChildIntelligenceEngine(db=db_session, cooldown_hours=12)

    # First analysis run - detects and logs notification
    report1 = engine.analyze_child(child_id=1)
    assert report1.new_insights_logged >= 1
    assert report1.cooldown_skipped_insights == 0

    # Second immediate analysis run - should trigger cooldown de-duplication
    report2 = engine.analyze_child(child_id=1)
    assert report2.new_insights_logged == 0
    assert report2.cooldown_skipped_insights >= 1
