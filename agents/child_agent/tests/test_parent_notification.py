import os
import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.notification import NotificationLog
from app.integrations.twilio.client import TwilioWhatsAppClient, MOCK_SENT_MESSAGES
from app.integrations.twilio.templates import render_whatsapp_template
from app.services.parent_notification_service import ParentNotificationService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_tw_100",
        name="Samantha",
        date_of_birth=date(2013, 6, 20),
        age=12,
        gender="FEMALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-0199",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


def test_whatsapp_template_rendering():
    data = {
        "subject": "Machine Learning",
        "title": "Assignment 1",
        "priority": "High",
        "due_date": "2026-08-01",
        "child_name": "Samantha",
    }
    rendered = render_whatsapp_template("HOMEWORK_REMINDER", data)

    assert "KinNest Parent Update" in rendered
    assert "Machine Learning" in rendered
    assert "Assignment 1" in rendered
    assert "Encourage a 45-minute study session" in rendered


from unittest.mock import MagicMock

def test_mock_twilio_dispatch(db_session):
    mock_twilio = MagicMock()
    mock_twilio.send_whatsapp_message.return_value = {
        "sid": "SMmock_12345",
        "status": "sent",
        "to": "whatsapp:+15550199",
        "from": "whatsapp:+14155238886",
        "error": None,
    }

    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)
    result = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="HOMEWORK_OVERDUE",
        template_data={"subject": "Math", "title": "Calculus Worksheet", "due_date": "2026-07-27"},
    )

    assert result["success"] is True
    assert result["message_sid"] == "SMmock_12345"
    assert result["status"] == "sent"


def test_private_diary_text_never_sent_in_whatsapp(db_session):
    mock_twilio = MagicMock()
    mock_twilio.send_whatsapp_message.return_value = {
        "sid": "SMmock_12346",
        "status": "sent",
        "error": None,
    }

    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)
    template_data = {
        "message": "Routine wellness check",
        "diary_entries": ["PRIVATE DIARY TEXT - I am angry at school."],
        "diary_text": "SENSITIVE PERSONAL THOUGHTS",
    }

    result = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="WELLNESS_CONCERN",
        template_data=template_data,
    )

    assert result["success"] is True
    call_args = mock_twilio.send_whatsapp_message.call_args[1]
    sent_body = call_args["body"]
    assert "PRIVATE DIARY TEXT" not in sent_body
    assert "SENSITIVE PERSONAL THOUGHTS" not in sent_body


def test_whatsapp_cooldown_deduplication(db_session):
    mock_twilio = MagicMock()
    mock_twilio.send_whatsapp_message.return_value = {
        "sid": "SMmock_12347",
        "status": "sent",
        "error": None,
    }

    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)

    # First dispatch - succeeds
    res1 = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="EXCESSIVE_SCREEN_TIME_ALERT",
        template_data={"avg_daily_minutes": 180},
    )
    assert res1["success"] is True

    # Second immediate dispatch - skipped due to cooldown
    res2 = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="EXCESSIVE_SCREEN_TIME_ALERT",
        template_data={"avg_daily_minutes": 185},
    )
    assert res2["status"] == "skipped"
    assert res2["reason"] == "12-hour cooldown active."


def test_parent_opt_out_registry(db_session):
    mock_twilio = MagicMock()
    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)
    parent_phone = "+1-555-0199"

    # Opt-out parent
    ParentNotificationService.set_opt_out(parent_phone, opt_out=True)

    result = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="HOMEWORK_REMINDER",
        template_data={"subject": "History", "title": "Essay", "priority": "Medium", "due_date": "2026-08-05"},
    )
    assert result["status"] == "skipped"
    assert result["reason"] == "Parent opted out."

    # Opt back in
    ParentNotificationService.set_opt_out(parent_phone, opt_out=False)

