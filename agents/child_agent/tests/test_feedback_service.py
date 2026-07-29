import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.study import StudySession
from app.models.homework import Homework
from app.services.feedback_service import (
    RecommendationFeedbackService,
    AdaptiveRecommendationEngine,
    RECOMMENDATION_OUTCOMES_STORE,
    PERSONALIZATION_PROFILES_STORE,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    child = ChildProfile(
        family_id="fam_fb_100",
        name="Lucas",
        date_of_birth=date(2014, 4, 15),
        age=11,
        gender="MALE",
        education_stage="PRIMARY_SCHOOL",
        parent_contact="+1-555-8888",
    )
    session.add(child)
    session.commit()
    session.refresh(child)

    yield session
    session.close()


def test_recommendation_outcome_tracking_successful(db_session):
    RECOMMENDATION_OUTCOMES_STORE.clear()
    PERSONALIZATION_PROFILES_STORE.clear()

    service = RecommendationFeedbackService(db=db_session)
    rec = service.record_recommendation(
        recommendation_id="rec_001",
        child_id=1,
        category="STUDY",
        suggested_action="Study Mathematics for 45 minutes",
    )
    assert rec.outcome_status == "PENDING"

    # Add observed study session matching recommendation
    db_session.add(StudySession(child_id=1, subject="Math", topic="Algebra", start_time=date.today(), end_time=date.today(), duration_minutes=50, focus_score=87))
    db_session.commit()

    evals = service.evaluate_recommendations(child_id=1)
    assert len(evals) == 1
    assert evals[0].outcome_status == "SUCCESSFUL"
    assert evals[0].effectiveness_score >= 80.0


def test_adaptive_recommendation_learning_loop(db_session):
    RECOMMENDATION_OUTCOMES_STORE.clear()
    PERSONALIZATION_PROFILES_STORE.clear()

    service = RecommendationFeedbackService(db=db_session)
    adaptive_engine = AdaptiveRecommendationEngine(db=db_session)

    # Record 2 ignored recommendations to trigger pattern adaptation
    service.record_recommendation("rec_002", 1, "STUDY", "Study Math for 60 minutes")
    service.record_recommendation("rec_003", 1, "STUDY", "Study Science for 60 minutes")

    base_recs = ["Study Mathematics or key subjects for 60 minutes."]

    # Adapt recommendations based on history
    adapted_recs = adaptive_engine.adapt_recommendations(child_id=1, base_recommendations=base_recs)

    assert len(adapted_recs) > 0
    assert "25-minute study block" in adapted_recs[0]

    profile = adaptive_engine.get_personalization_profile(child_id=1)
    assert profile.optimal_study_duration_mins == 25
    assert profile.planning_style == "FLEXIBLE"
