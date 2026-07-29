import os
import pytest
from datetime import date
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.safety import CheckInLog
from app.schemas.privacy import ViewerRole
from app.services.ai.child_intelligence_service import ChildIntelligenceService
from app.schemas.ai_intelligence import ChildAIIntelligenceReport, ChildAIInsight, ParentNotificationDecision
from app.ai.context_builder import ChildContextBuilder



@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_ai_100",
        name="Sophia",
        date_of_birth=date(2012, 9, 15),
        age=13,
        gender="FEMALE",
        education_stage="SECONDARY_SCHOOL",
        parent_contact="+1-555-9090",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


def test_context_aggregation_and_fallback(db_session):
    # Add overdue homework
    db_session.add(
        Homework(
            family_id="fam_ai_100",
            child_id=1,
            subject="Science",
            title="Biology Lab Report",
            assigned_date=date.today(),
            due_date=date(2026, 1, 1),
            completion_status=False,
        )
    )
    db_session.commit()

    service = ChildIntelligenceService(db=db_session)
    builder = ChildContextBuilder(db=db_session, child_id=1)
    context = builder.build(include_ml_predictions=False)
    report = service.generate_fallback_report(child_id=1, context=context)


    assert report.child_id == 1
    assert report.overall_status == "NEEDS_ATTENTION"
    assert len(report.key_insights) > 0
    assert report.key_insights[0].insight_type == "HOMEWORK_RISK"
    assert report.parent_notification_decision.should_notify is True


def test_privacy_filtering_and_diary_protection(db_session):
    service = ChildIntelligenceService(db=db_session)
    sensitive_data = {
        "safe_message": "Child is progressing well.",
        "diary_entries": ["PRIVATE DIARY TEXT - Feeling nervous about exams."],
        "diary_text": "Sensitive journal entry",
    }

    filtered = service.data_filter.sanitize_for_viewer(sensitive_data, viewer_role=ViewerRole.PARENT)
    assert "diary_entries" not in filtered
    assert "diary_text" not in filtered
    assert filtered["safe_message"] == "Child is progressing well."


def test_ai_unavailable_fallback_preserves_api_contract(db_session):
    service = ChildIntelligenceService(db=db_session)

    # Force Groq LLM failure to verify graceful fallback without throwing exceptions
    report = service.analyze_child_intelligence(child_id=1, trigger_parent_whatsapp=False)

    assert isinstance(report, ChildAIIntelligenceReport)
    assert report.child_id == 1
    assert report.overall_status in ("GOOD", "MODERATE", "EXCELLENT", "NEEDS_ATTENTION")
    assert isinstance(report.parent_notification_decision, ParentNotificationDecision)
