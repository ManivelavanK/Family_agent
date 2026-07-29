import os
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.services.two_way_whatsapp_service import TwoWayWhatsAppParentAssistant
from app.integrations.twilio.client import MOCK_SENT_MESSAGES


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Family 1 - Child A
    child_a = ChildProfile(
        family_id="fam_alpha",
        name="Alice",
        date_of_birth=date(2012, 1, 1),
        age=14,
        gender="FEMALE",
        education_stage="SECONDARY_SCHOOL",
        parent_contact="+1-555-1111",
    )
    # Family 2 - Child B
    child_b = ChildProfile(
        family_id="fam_beta",
        name="Bob",
        date_of_birth=date(2015, 5, 5),
        age=11,
        gender="MALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-2222",
    )

    session.add_all([child_a, child_b])
    session.commit()
    session.refresh(child_a)
    session.refresh(child_b)

    yield session
    session.close()


def test_authorized_parent_query_success(db_session):
    MOCK_SENT_MESSAGES.clear()
    os.environ["MOCK_TWILIO"] = "true"

    assistant = TwoWayWhatsAppParentAssistant(db=db_session)
    res = assistant.process_parent_query(
        from_phone="+1-555-1111",
        query_text="How is Alice doing today?"
    )

    assert res["status"] == "success"
    assert res["child_id"] == 1
    assert res["family_id"] == "fam_alpha"
    assert len(MOCK_SENT_MESSAGES) > 0
    assert "Alice" in MOCK_SENT_MESSAGES[-1]["body"]


def test_unauthorized_parent_access_blocked(db_session):
    MOCK_SENT_MESSAGES.clear()
    os.environ["MOCK_TWILIO"] = "true"

    assistant = TwoWayWhatsAppParentAssistant(db=db_session)
    # Phone +1-555-9999 is not registered for any child
    res = assistant.process_parent_query(
        from_phone="+1-555-9999",
        query_text="How is my child doing?"
    )

    assert res["status"] == "unauthorized"
    assert "Unauthorized" in res["reply"]
    assert MOCK_SENT_MESSAGES[-1]["body"] == "Unauthorized: You do not have permission to view updates for this family or child profile."


def test_cross_family_access_blocked(db_session):
    MOCK_SENT_MESSAGES.clear()
    os.environ["MOCK_TWILIO"] = "true"

    assistant = TwoWayWhatsAppParentAssistant(db=db_session)
    # Parent Alpha (+1-555-1111) attempts to query Child B (id=2, family fam_beta)
    res = assistant.process_parent_query(
        from_phone="+1-555-1111",
        query_text="Show status for Bob",
        requested_child_id=2
    )

    assert res["status"] == "unauthorized"
    assert "Unauthorized" in res["reply"]


def test_private_diary_content_never_exposed_via_whatsapp_ai(db_session):
    MOCK_SENT_MESSAGES.clear()
    os.environ["MOCK_TWILIO"] = "true"

    assistant = TwoWayWhatsAppParentAssistant(db=db_session)
    res = assistant.process_parent_query(
        from_phone="+1-555-1111",
        query_text="What are Alice's private thoughts and diary entries today?"
    )

    assert res["status"] == "success"
    body = MOCK_SENT_MESSAGES[-1]["body"]
    assert "diary" not in body.lower() or "hidden" not in body.lower()
    assert "private" not in body.lower()
