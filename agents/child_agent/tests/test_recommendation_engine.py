import pytest
from datetime import date, time, datetime
from unittest.mock import patch, MagicMock

from app.schemas.context import (
    ChildContext,
    PrivacyFilteredProfile,
    HomeworkSummaryContext,
    StudySummaryContext,
    ExamSummaryContext,
    AttendanceSummaryContext,
    ScreenTimeSummaryContext,
    HealthRoutineSummaryContext,
    ActivitiesSummaryContext,
    PocketMoneySummaryContext,
    SafetySummaryContext,
    NutritionSummaryContext,
    ScheduleSummaryContext,
)
from app.schemas.ai_recommendation import (
    DetailedRecommendationItem,
    ChildRecommendationEngineOutput,
)
from app.ai.recommendation_engine import (
    generate_ai_child_recommendations,
    generate_fallback_detailed_recommendations,
)


def create_base_context(child_id=1, name="Test Child", age=10):
    return ChildContext(
        profile=PrivacyFilteredProfile(
            child_id=child_id,
            name=name,
            age=age,
            age_group="MIDDLE_CHILDHOOD",
            education_stage="PRIMARY_SCHOOL",
        ),
        homework=HomeworkSummaryContext(),
        study=StudySummaryContext(),
        exams=ExamSummaryContext(),
        attendance=AttendanceSummaryContext(),
        screen_time=ScreenTimeSummaryContext(),
        health=HealthRoutineSummaryContext(),
        activities=ActivitiesSummaryContext(),
        pocket_money=PocketMoneySummaryContext(),
        safety=SafetySummaryContext(),
        nutrition=NutritionSummaryContext(),
        schedule=ScheduleSummaryContext(),
    )


def test_good_academic_performance():
    ctx = create_base_context()
    ctx.exams.avg_exam_percentage = 94.5
    ctx.exams.total_exams = 4

    out = generate_fallback_detailed_recommendations(ctx)
    acad_recs = [r for r in out.recommendations if r.category == "academic"]
    assert len(acad_recs) > 0
    assert acad_recs[0].priority == "LOW"
    assert "94.5" in acad_recs[0].explanation


def test_poor_homework_completion():
    ctx = create_base_context()
    ctx.homework.total_count = 5
    ctx.homework.pending_count = 3
    ctx.homework.overdue_count = 2
    ctx.homework.pending_subjects = ["Mathematics", "History"]

    out = generate_fallback_detailed_recommendations(ctx)
    hw_recs = [r for r in out.recommendations if r.category == "homework"]
    assert len(hw_recs) > 0
    assert hw_recs[0].priority == "HIGH"
    assert hw_recs[0].requires_immediate_action is True
    assert hw_recs[0].requires_parent_attention is True


def test_excessive_screen_time():
    ctx = create_base_context()
    ctx.screen_time.avg_daily_minutes = 180.0
    ctx.screen_time.screen_time_exceeded = True

    out = generate_fallback_detailed_recommendations(ctx)
    screen_recs = [r for r in out.recommendations if r.category == "screen_time"]
    assert len(screen_recs) > 0
    assert screen_recs[0].priority == "HIGH"
    assert screen_recs[0].requires_parent_attention is True


def test_upcoming_exam():
    ctx = create_base_context()
    ctx.exams.upcoming_count = 2
    ctx.exams.upcoming_exams = [
        {"id": 1, "exam_name": "Science Quiz", "subject": "Science", "exam_date": "2026-08-01"}
    ]

    out = generate_fallback_detailed_recommendations(ctx)
    exam_recs = [r for r in out.recommendations if r.category == "exams"]
    assert len(exam_recs) > 0
    assert exam_recs[0].requires_immediate_action is True


def test_poor_study_consistency():
    ctx = create_base_context()
    ctx.study.total_sessions = 0
    ctx.study.avg_focus_score = 55.0

    out = generate_fallback_detailed_recommendations(ctx)
    study_recs = [r for r in out.recommendations if r.category == "study_habits"]
    assert len(study_recs) > 0
    assert study_recs[0].priority == "MEDIUM"


def test_multiple_simultaneous_issues():
    ctx = create_base_context()
    ctx.homework.overdue_count = 3
    ctx.homework.pending_count = 4
    ctx.screen_time.avg_daily_minutes = 210.0
    ctx.screen_time.screen_time_exceeded = True
    ctx.exams.upcoming_count = 1
    ctx.safety.check_in_status = "OVERDUE"

    out = generate_fallback_detailed_recommendations(ctx)
    assert len(out.recommendations) >= 4

    categories = [r.category for r in out.recommendations]
    assert "homework" in categories
    assert "screen_time" in categories
    assert "exams" in categories
    assert "safety" in categories

    safety_rec = [r for r in out.recommendations if r.category == "safety"][0]
    assert safety_rec.requires_parent_attention is True
    assert safety_rec.requires_immediate_action is True


def test_missing_data_handling():
    ctx = create_base_context()
    # All summaries at zero/default values
    out = generate_fallback_detailed_recommendations(ctx)

    for r in out.recommendations:
        assert r.category in [
            "academic", "homework", "study_habits", "focus", "exams",
            "attendance", "screen_time", "routine", "activities", "financial", "wellness", "safety"
        ]
        assert r.explanation is not None
        assert r.suggested_action is not None


@patch("app.ai.recommendation_engine._get_groq_client")
def test_invalid_llm_response_falls_back(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    # Return invalid JSON string from LLM
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="INVALID_NON_JSON_STRING"))]
    mock_client.chat.completions.create.return_value = mock_response

    ctx = create_base_context()
    ctx.homework.overdue_count = 1
    ctx.homework.pending_count = 2

    out = generate_ai_child_recommendations(ctx)

    # Should fall back cleanly to fallback generator without crashing
    assert isinstance(out, ChildRecommendationEngineOutput)
    assert "Fallback" in out.generated_by
    assert len(out.recommendations) > 0
    assert any(r.category == "homework" for r in out.recommendations)
