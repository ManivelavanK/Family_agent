import os
import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.notification import NotificationLog
from app.models.homework import Homework
from app.services.parent_notification_service import ParentNotificationService, OPTED_OUT_NUMBERS
from app.integrations.twilio.service import TwilioWhatsAppService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_real_tw_100",
        name="Elena",
        date_of_birth=date(2011, 8, 12),
        age=15,
        gender="FEMALE",
        education_stage="HIGH_SCHOOL",
        parent_contact="+1-555-0199",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


from unittest.mock import MagicMock


def test_twilio_configuration_and_valid_invalid_numbers(db_session):
    service = TwilioWhatsAppService()
    service.account_sid = "your_placeholder"

    res = service.send_whatsapp_message(to_phone="invalid_num", body="Test")

    assert res["status"] == "failed"
    assert "REAL TWILIO INTEGRATION REQUIRED" in res["error"]



def test_parent_notification_service_privacy_filtering(db_session):
    mock_twilio = MagicMock()
    mock_twilio.send_whatsapp_message.return_value = {"sid": "SMmock_999", "status": "sent", "error": None}

    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)
    template_data = {
        "subject": "Chemistry",
        "title": "Lab Report",
        "due_date": "2026-08-05",
        "diary_entries": ["SENSITIVE PRIVATE DIARY ENTRY"],
        "allergies": "Peanuts",
    }

    res = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="HOMEWORK_REMINDER",
        template_data=template_data,
    )

    # Database log verification
    logs = db_session.query(NotificationLog).filter(NotificationLog.child_id == 1).all()
    assert len(logs) > 0
    logged_msg = logs[-1].message
    assert "SENSITIVE PRIVATE DIARY ENTRY" not in logged_msg
    assert "Peanuts" not in logged_msg


def test_duplicate_prevention_and_cooldown(db_session):
    mock_twilio = MagicMock()
    mock_twilio.send_whatsapp_message.return_value = {"sid": "SMmock_998", "status": "sent", "error": None}

    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)

    # First dispatch - creates log entry
    service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="EXCESSIVE_SCREEN_TIME_ALERT",
        template_data={"avg_daily_minutes": 190},
    )

    # Immediate second dispatch - blocked by 12h cooldown
    res2 = service.dispatch_parent_whatsapp(
        child_id=1,
        notification_type="EXCESSIVE_SCREEN_TIME_ALERT",
        template_data={"avg_daily_minutes": 195},
    )
    assert res2["status"] == "skipped"
    assert res2["reason"] == "12-hour cooldown active."


def test_child_family_authorization(db_session):
    mock_twilio = MagicMock()
    service = ParentNotificationService(db=db_session, twilio_service=mock_twilio)

    # Non-existent child ID
    res = service.dispatch_parent_whatsapp(
        child_id=999,
        notification_type="HOMEWORK_REMINDER",
        template_data={},
    )
    assert res["status"] == "failed"
    assert "not found" in res["reason"]

