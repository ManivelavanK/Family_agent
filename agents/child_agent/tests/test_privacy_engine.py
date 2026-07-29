import pytest
from datetime import date, time

from app.schemas.privacy import PrivacyCategory, ViewerRole
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
from app.services.privacy_engine import (
    PrivacyPolicyEngine,
    ChildPrivateDataFilter,
    ParentSummaryGenerator,
)


def create_sample_context(check_in_status="SAFE"):
    return ChildContext(
        profile=PrivacyFilteredProfile(
            child_id=1,
            name="Maya",
            age=13,
            age_group="ADOLESCENCE",
            education_stage="SECONDARY_SCHOOL",
        ),
        homework=HomeworkSummaryContext(pending_count=2, overdue_count=1, completed_count=3),
        study=StudySummaryContext(total_study_minutes=120, total_sessions=4, avg_focus_score=80.0),
        exams=ExamSummaryContext(total_exams=1, upcoming_count=1),
        attendance=AttendanceSummaryContext(attendance_percentage=95.0),
        screen_time=ScreenTimeSummaryContext(avg_daily_minutes=150.0, screen_time_exceeded=True),
        health=HealthRoutineSummaryContext(avg_sleep_hours=8.0, avg_water_intake_ml=1600),
        activities=ActivitiesSummaryContext(),
        pocket_money=PocketMoneySummaryContext(allowance_total=1000.0, total_spent=400.0, total_saved=600.0),
        safety=SafetySummaryContext(check_in_status=check_in_status),
        nutrition=NutritionSummaryContext(),
        schedule=ScheduleSummaryContext(),
    )


def test_private_diary_content_not_exposed_to_parent():
    engine = PrivacyPolicyEngine()
    filter_tool = ChildPrivateDataFilter(engine=engine)

    raw_data = {
        "child_id": 1,
        "diary_entries": ["Today I felt very sad about my math exam score."],
        "diary_text": "Private personal thoughts...",
        "homework_count": 2,
    }

    # Verify PARENT role filtering removes raw diary text
    sanitized_parent = filter_tool.sanitize_for_viewer(raw_data, viewer_role=ViewerRole.PARENT)
    assert "diary_entries" not in sanitized_parent
    assert "diary_text" not in sanitized_parent
    assert "diary_privacy_note" in sanitized_parent
    assert sanitized_parent["homework_count"] == 2

    # Verify CHILD role retains access to own diary text
    sanitized_child = filter_tool.sanitize_for_viewer(raw_data, viewer_role=ViewerRole.CHILD)
    assert "diary_entries" in sanitized_child
    assert sanitized_child["diary_entries"] == ["Today I felt very sad about my math exam score."]


def test_academic_summaries_work_for_parent():
    context = create_sample_context()
    generator = ParentSummaryGenerator()

    summary = generator.generate_parent_summary(context)

    assert summary.academic_summary["pending_count"] == 2
    assert summary.academic_summary["overdue_count"] == 1
    assert summary.study_summary["total_study_minutes"] == 120
    assert summary.study_summary["consistency_status"] == "Consistent"


def test_safety_alert_escalation_bypass():
    engine = PrivacyPolicyEngine()

    # Normal non-emergency scenario: PARENT cannot view CHILD_PRIVATE raw text
    can_access_normal = engine.can_access(
        role=ViewerRole.PARENT,
        category=PrivacyCategory.CHILD_PRIVATE,
        is_raw_text=True,
        is_safety_emergency=False,
    )
    assert can_access_normal is False

    # Emergency scenario: Safety bypass activates
    can_access_emergency = engine.can_access(
        role=ViewerRole.PARENT,
        category=PrivacyCategory.CHILD_PRIVATE,
        is_raw_text=True,
        is_safety_emergency=True,
    )
    assert can_access_emergency is True


def test_sensitive_data_filtering():
    engine = PrivacyPolicyEngine()
    filter_tool = ChildPrivateDataFilter(engine=engine)

    data = {
        "name": "Alex",
        "allergies": "Penicillin",
        "blood_group": "A+",
        "parent_contact": "555-1234",
    }

    # External FAMILY_AGENT viewing data -> sensitive medical & phone stripped
    filtered = filter_tool.sanitize_for_viewer(data, viewer_role=ViewerRole.FAMILY_AGENT)
    assert "allergies" not in filtered
    assert "blood_group" not in filtered
    assert "parent_contact" not in filtered
    assert filtered["name"] == "Alex"


def test_parent_summary_generator_wellness_concern_flag():
    context = create_sample_context()
    generator = ParentSummaryGenerator()

    raw_diary = [
        {"content": "I feel hopeless and sad today."}
    ]

    summary = generator.generate_parent_summary(context, raw_diary_entries=raw_diary)

    # Asserts that wellness flag is raised for parent without embedding raw text
    assert summary.wellness_summary["has_serious_wellness_concern"] is True
    assert "diary_entries" not in summary.wellness_summary
    assert any("Wellness concern" in a for a in summary.alerts_requiring_parent)
