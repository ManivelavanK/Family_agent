import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.baby import Baby
from app.models.feeding import Feeding
from app.models.health import HealthRecord
from app.models.vaccination import VaccinationRecord
from app.scheduler import jobs

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def setup_scheduler_baby(db_session: Session):
    # Setup baby with contact
    baby = Baby(
        family_id=101,
        name="Sched Baby",
        date_of_birth=date.today() - timedelta(days=30),
        parent_contact="whatsapp:+1234567890"
    )
    db_session.add(baby)
    db_session.commit()
    db_session.refresh(baby)
    
    yield baby
    
    # Cleanup
    db_session.delete(baby)
    db_session.commit()

def test_check_baby_alerts_job_overdue_feeding(db_session, setup_scheduler_baby):
    # Add feeding 5 hours ago (feeding overdue)
    feed = Feeding(
        baby_id=setup_scheduler_baby.id,
        feeding_type="formula",
        feeding_time=datetime.now() - timedelta(hours=5)
    )
    db_session.add(feed)
    db_session.commit()

    with patch("app.services.notification_service.send_feeding_alert") as mock_send_feeding:
        jobs.check_baby_alerts_job()

    mock_send_feeding.assert_any_call(
        to_phone=setup_scheduler_baby.parent_contact,
        baby_name=setup_scheduler_baby.name,
        hours=4.0
    )
    
    db_session.delete(feed)
    db_session.commit()

def test_check_baby_alerts_job_fever(db_session, setup_scheduler_baby):
    # Add health record with temperature 39.0
    health = HealthRecord(
        baby_id=setup_scheduler_baby.id,
        temperature_c=39.0,
        visit_date=date.today()
    )
    db_session.add(health)
    db_session.commit()

    with patch("app.services.notification_service.send_fever_alert") as mock_send_fever:
        jobs.check_baby_alerts_job()

    mock_send_fever.assert_any_call(
        to_phone=setup_scheduler_baby.parent_contact,
        baby_name=setup_scheduler_baby.name,
        temp=39.0
    )
    
    db_session.delete(health)
    db_session.commit()

def test_vaccination_reminders_job(db_session, setup_scheduler_baby):
    # Add vaccine due tomorrow
    v = VaccinationRecord(
        baby_id=setup_scheduler_baby.id,
        vaccine_name="Hepatitis B",
        due_date=date.today() + timedelta(days=1),
        status="pending"
    )
    db_session.add(v)
    db_session.commit()

    with patch("app.services.notification_service.send_vaccination_reminder") as mock_send_vaccine:
        jobs.vaccination_reminders_job()

    mock_send_vaccine.assert_any_call(
        to_phone=setup_scheduler_baby.parent_contact,
        baby_name=setup_scheduler_baby.name,
        vaccine_name="Hepatitis B",
        due_date=str(date.today() + timedelta(days=1))
    )
    
    db_session.delete(v)
    db_session.commit()

def test_daily_summaries_job(db_session, setup_scheduler_baby):
    # Add feeding today
    feed = Feeding(
        baby_id=setup_scheduler_baby.id,
        feeding_type="formula",
        quantity_ml=120,
        feeding_time=datetime.now()
    )
    db_session.add(feed)
    db_session.commit()

    with patch("app.services.notification_service.send_daily_summary") as mock_send_summary:
        jobs.daily_summaries_job()

    target_call = None
    for call in mock_send_summary.call_args_list:
        args, kwargs = call
        to_phone = kwargs.get("to_phone") or (args[0] if len(args) > 0 else None)
        if to_phone == setup_scheduler_baby.parent_contact:
            target_call = call
            break
            
    assert target_call is not None
    args, kwargs = target_call
    baby_name = kwargs.get("baby_name") or (args[1] if len(args) > 1 else None)
    summary_text = kwargs.get("summary_text") or (args[2] if len(args) > 2 else None)
    assert baby_name == setup_scheduler_baby.name
    assert "Total Feedings: 1 times" in summary_text
    assert "120" in summary_text

    db_session.delete(feed)
    db_session.commit()
