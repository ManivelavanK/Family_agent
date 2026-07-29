import pytest
from datetime import date, time, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.study import StudySession, StudyMaterial
from app.models.exam import Exam
from app.models.attendance import Attendance
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog
from app.models.activity import Activity
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense, SavingGoal
from app.models.safety import SafetyProfile, CheckInLog
from app.models.nutrition import NutritionLog, MotherAgentBridgeEvent
from app.models.schedule import ScheduleItem, HolidayCalendar
from app.models.notification import NotificationLog

from app.ai.context_builder import ChildContextBuilder
from app.schemas.context import ChildContext


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_complete_child_context(db_session):
    # Setup complete child profile
    child = ChildProfile(
        family_id="fam_test_100",
        name="Alex River",
        date_of_birth=date(2014, 5, 10),
        age=10,
        gender="MALE",
        education_stage="PRIMARY_SCHOOL",
        class_or_year="5th Grade",
        school_or_college="Springfield Elementary",
        blood_group="O+",
        allergies="Peanuts",
        emergency_contact="+1-555-0199",
        parent_contact="+1-555-0100",
        interests=["Robotics", "Chess", "Swimming", "Gaming", "Coding"],
        career_interest="Software Engineer",
        daily_wake_time=time(7, 0),
        daily_sleep_time=time(21, 30),
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(child)

    # Populate domain data
    db_session.add(Homework(family_id="fam_test_100", child_id=child.id, subject="Math", title="Fractions", assigned_date=date.today(), due_date=date.today(), completion_status=False, priority="HIGH"))
    db_session.add(Homework(family_id="fam_test_100", child_id=child.id, subject="Science", title="Plants", assigned_date=date.today(), due_date=date(2025, 1, 1), completion_status=False, priority="MEDIUM")) # overdue
    db_session.add(StudySession(child_id=child.id, subject="Math", topic="Algebra", start_time=datetime.now(), end_time=datetime.now(), duration_minutes=45, focus_score=85.0))
    db_session.add(Exam(child_id=child.id, exam_name="Midterm Math", subject="Math", exam_date=date.today(), preparation_percentage=85, difficulty="Medium"))
    db_session.add(Attendance(child_id=child.id, date=date.today(), subject="Math", status="PRESENT"))
    db_session.add(ScreenTimeLog(child_id=child.id, date=date.today(), mobile=30, gaming=45, tv=30, social_media=0, study_screen_time=30, other=0, late_night_minutes=0))
    db_session.add(HealthLog(child_id=child.id, date=date.today(), sleep_hours=9.0, water_intake_ml=1600, physical_activity_minutes=45))
    db_session.add(Activity(child_id=child.id, title="Soccer Practice", activity_type="Sports", date=date.today(), start_time=time(16, 0), end_time=time(17, 0)))
    db_session.add(PocketMoneyAllowance(family_id="fam_test_100", child_id=child.id, amount=500.0, frequency="WEEKLY", date=date.today()))
    db_session.add(ChildExpense(family_id="fam_test_100", child_id=child.id, amount=150.0, category="Food", date=date.today()))
    db_session.add(SavingGoal(child_id=child.id, title="Bicycle", target_amount=2000.0, current_saved=600.0, target_date=date(2026, 12, 31)))
    db_session.add(CheckInLog(child_id=child.id, date=date.today(), expected_return_time=time(18, 0), status="SAFE", location_note="At school playground"))
    db_session.add(NutritionLog(child_id=child.id, date=date.today(), breakfast_eaten=True, water_ml=1600))
    db_session.add(ScheduleItem(child_id=child.id, day_of_week="Tuesday", subject="Math Class", start_time=time(9, 0), end_time=time(10, 0), schedule_type="PERIOD"))
    db_session.add(NotificationLog(child_id=child.id, title="Homework Alert", message="Math pending", notification_type="HOMEWORK_REMINDER"))
    db_session.commit()

    builder = ChildContextBuilder(db=db_session, child_id=child.id)
    context = builder.build(include_ml_predictions=True)

    assert isinstance(context, ChildContext)
    assert context.profile.name == "Alex River"
    assert context.profile.age == 10
    assert context.homework.total_count == 2
    assert context.homework.pending_count == 2
    assert context.homework.overdue_count == 1
    assert context.study.total_sessions == 1
    assert context.study.avg_focus_score == 85.0
    assert context.exams.total_exams == 1
    assert context.attendance.attendance_percentage == 100.0
    assert context.screen_time.avg_daily_minutes == 135.0
    assert context.health.avg_sleep_hours == 9.0
    assert context.pocket_money.allowance_total == 500.0
    assert context.pocket_money.total_spent == 150.0
    assert context.pocket_money.total_saved == 600.0
    assert context.safety.check_in_status == "SAFE"
    assert context.nutrition.breakfast_consistency_pct == 100.0
    assert len(context.recent_notifications) == 1


def test_missing_data_handling(db_session):
    # Child profile exists, but no activity/exam/homework records present
    child = ChildProfile(
        family_id="fam_test_200",
        name="Jamie Lee",
        date_of_birth=date(2018, 2, 1),
        age=8,
        gender="FEMALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-0200",
    )
    db_session.add(child)
    db_session.commit()

    builder = ChildContextBuilder(db=db_session, child_id=child.id)
    context = builder.build(include_ml_predictions=False)

    assert context.profile.name == "Jamie Lee"
    assert context.homework.total_count == 0
    assert context.homework.pending_count == 0
    assert context.study.total_sessions == 0
    assert context.study.avg_focus_score is None
    assert context.exams.avg_exam_percentage is None
    assert context.attendance.attendance_percentage == 100.0
    assert context.screen_time.avg_daily_minutes == 0.0
    assert context.health.avg_sleep_hours == 8.0
    assert context.pocket_money.allowance_total == 0.0
    assert context.safety.check_in_status == "SAFE"
    assert context.recent_notifications == []
    assert context.ml_predictions is None


def test_empty_data_raises_not_found(db_session):
    builder = ChildContextBuilder(db=db_session, child_id=9999)
    with pytest.raises(ValueError, match="Child profile with ID 9999 not found."):
        builder.build()


def test_large_context_size_limiting(db_session):
    child = ChildProfile(
        family_id="fam_test_300",
        name="Sam Taylor",
        date_of_birth=date(2012, 1, 1),
        age=14,
        gender="MALE",
        education_stage="ADOLESCENCE",
        parent_contact="+1-555-0300",
        interests=["Music", "Art", "Basketball", "Robotics", "Physics", "Chemistry", "Astronomy"],
    )
    db_session.add(child)
    db_session.commit()

    # Add 20 notifications
    for i in range(20):
        db_session.add(NotificationLog(
            child_id=child.id,
            title=f"Notification {i}",
            message=f"Message body {i}",
            notification_type="SYSTEM"
        ))
    
    # Add 10 homework items
    for i in range(10):
        db_session.add(Homework(
            family_id="fam_test_300",
            child_id=child.id,
            subject=f"Subject_{i}",
            title=f"Assignment {i}",
            assigned_date=date.today(),
            due_date=date(2020, 1, 1),
            completion_status=False
        ))

    db_session.commit()

    builder = ChildContextBuilder(db=db_session, child_id=child.id)
    context = builder.build(max_notifications=5, max_items_per_list=5)

    # Test size limits
    assert len(context.profile.interests) <= 5
    assert len(context.recent_notifications) == 5
    assert len(context.homework.overdue_items) <= 5
    assert context.homework.total_count == 10
    assert context.homework.overdue_count == 10


def test_privacy_filtering(db_session):
    child = ChildProfile(
        family_id="fam_secret_400",
        name="Jordan Private",
        date_of_birth=date(2015, 8, 20),
        age=11,
        gender="FEMALE",
        education_stage="PRIMARY_SCHOOL",
        blood_group="AB-",
        allergies="Penicillin and Severe Nut Allergy",
        emergency_contact="SECRET_EMERGENCY_CONTACT_911",
        parent_contact="PARENT_PRIVATE_PHONE_999",
    )
    db_session.add(child)
    db_session.commit()

    builder = ChildContextBuilder(db=db_session, child_id=child.id)
    context = builder.build()

    context_dict = context.model_dump()
    profile_dict = context_dict["profile"]

    # Verify sensitive attributes are absent from PrivacyFilteredProfile
    assert "allergies" not in profile_dict
    assert "blood_group" not in profile_dict
    assert "emergency_contact" not in profile_dict
    assert "parent_contact" not in profile_dict
    assert profile_dict["name"] == "Jordan Private"
    assert profile_dict["age"] == 11
