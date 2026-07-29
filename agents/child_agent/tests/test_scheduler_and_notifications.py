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
from app.models.exam import Exam
from app.models.activity import Activity
from app.models.health import HealthLog
from app.models.pocket_money import SavingGoal
from app.scheduler.scheduler import start_scheduler, shutdown_scheduler, scheduler
from app.scheduler import jobs
from app.services.notification_service import NotificationService, NotificationType, NotificationChannel

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_scheduler_log.db"
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
        if os.path.exists("test_scheduler_log.db"):
            try:
                os.remove("test_scheduler_log.db")
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


def test_notification_service_send_and_get(session):
    # 1. Create a child profile via ORM
    child = ChildProfile(
        family_id="fam_test",
        name="Leo",
        age=10,
        date_of_birth=date(2016, 1, 1),
        gender="Male",
        parent_contact="555-111-2222",
        education_stage="Primary School"
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    # 2. Send notification via NotificationService across channels
    log1 = NotificationService.send_notification(
        session,
        child_id=child.id,
        title="Homework Alert",
        message="Complete math sheet",
        notification_type=NotificationType.HOMEWORK_REMINDER.value,
        channel=NotificationChannel.IN_APP.value,
    )
    assert log1.id is not None
    assert log1.status == "LOGGED"

    log2 = NotificationService.send_notification(
        session,
        child_id=child.id,
        title="WhatsApp Water Alert",
        message="Drink 250ml water",
        notification_type=NotificationType.WATER_REMINDER.value,
        channel=NotificationChannel.WHATSAPP.value,
    )
    assert log2.channel == "WHATSAPP"

    # 3. Retrieve notifications for child
    logs = NotificationService.get_notifications_for_child(session, child.id)
    assert len(logs) == 2


def test_scheduler_jobs_execution(session):
    # Setup child record and triggering conditions via ORM
    child = ChildProfile(
        family_id="fam_test_2",
        name="Aria",
        age=8,
        date_of_birth=date(2018, 5, 10),
        gender="Female",
        parent_contact="555-333-4444",
        education_stage="Primary School"
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    today = date.today()

    # Add test domain entities
    hw = Homework(
        family_id="fam_test_2",
        child_id=child.id,
        subject="Science",
        title="Project",
        assigned_date=today,
        due_date=today,
        priority="HIGH",
        completion_status=False
    )
    ex = Exam(
        child_id=child.id,
        subject="Science",
        exam_name="Midterm",
        exam_date=today
    )
    act = Activity(
        child_id=child.id,
        title="Piano",
        activity_type="Music",
        date=today,
        start_time=time(15, 0),
        end_time=time(16, 0),
        priority="High"
    )
    health = HealthLog(
        child_id=child.id,
        date=today,
        sleep_hours=6.0,
        water_intake_ml=500,
        physical_activity_minutes=20
    )
    sg = SavingGoal(
        child_id=child.id,
        title="Bicycle",
        target_amount=100.0,
        current_saved=40.0,
        target_date=today + timedelta(days=30)
    )
    session.add_all([hw, ex, act, health, sg])
    session.commit()

    # Manually execute all 9 background jobs using session
    jobs.check_homework_reminders(db=session)
    jobs.check_exam_reminders(db=session)
    jobs.check_activity_reminders(db=session)
    jobs.check_water_reminders(db=session)
    jobs.check_sleep_reminders(db=session)
    jobs.check_attendance_warnings(db=session)
    jobs.check_safety_checkin_warnings(db=session)
    jobs.check_pocket_money_reminders(db=session)
    jobs.check_study_reminders(db=session)

    # Verify notifications were created
    notifications = NotificationService.get_notifications_for_child(session, child.id)
    assert len(notifications) >= 5
    types_logged = {n.notification_type for n in notifications}
    assert NotificationType.HOMEWORK_REMINDER.value in types_logged
    assert NotificationType.EXAM_REMINDER.value in types_logged
    assert NotificationType.WATER_REMINDER.value in types_logged
    assert NotificationType.POCKET_MONEY_REMINDER.value in types_logged
    assert NotificationType.STUDY_REMINDER.value in types_logged


def test_scheduler_lifecycle():
    # Test safe start and shutdown
    start_scheduler()
    assert scheduler.running is True
    # Idempotent second call
    start_scheduler()
    assert scheduler.running is True
    # Shutdown safely
    shutdown_scheduler()
    assert scheduler.running is False
    # Idempotent second shutdown
    shutdown_scheduler()
    assert scheduler.running is False


def test_get_child_notifications_api(client, session):
    # 1. Create Child Profile via API
    res = client.post("/children/profile", json={
        "family_id": "fam_notif_1",
        "name": "Noah",
        "date_of_birth": "2015-08-20",
        "age": 10,
        "gender": "Male",
        "parent_contact": "555-777-8888"
    })
    assert res.status_code == 201
    child_id = res.json()["id"]

    # 2. Generate notification
    NotificationService.send_notification(
        session,
        child_id=child_id,
        title="Test Notification",
        message="This is a test notification",
        notification_type=NotificationType.STUDY_REMINDER.value,
        channel="IN_APP"
    )

    # 3. Call GET /children/notifications/{child_id}
    api_res = client.get(f"/children/notifications/{child_id}")
    assert api_res.status_code == 200
    data = api_res.json()
    assert len(data) == 1
    assert data[0]["child_id"] == child_id
    assert data[0]["title"] == "Test Notification"
    assert data[0]["channel"] == "IN_APP"
