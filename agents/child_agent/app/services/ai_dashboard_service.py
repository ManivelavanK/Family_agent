import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.profile import ChildProfile
from app.ai.context_builder import ChildContextBuilder
from app.schemas.context import ChildContext
from app.schemas.ai_dashboard import AIDailyDashboardResponse
from app.services import dashboard_service
from app.ai.groq_service import _get_groq_client

logger = logging.getLogger(__name__)


def generate_fallback_ai_dashboard(child_id: int, context: ChildContext, orig_dash: Any) -> AIDailyDashboardResponse:
    """
    Fallback generator for AI Daily Dashboard when LLM is unavailable.
    Synthesizes compliant briefing based on context indicators without exposing private diary logs.
    """
    child_name = context.profile.name

    # Determine overall status
    if context.safety.check_in_status in ("OVERDUE", "EMERGENCY") or context.homework.overdue_count > 0:
        status_summary = "NEEDS_ATTENTION"
    elif context.screen_time.avg_daily_minutes > 120.0 or context.homework.pending_count > 0:
        status_summary = "MODERATE"
    else:
        status_summary = "EXCELLENT"

    # Child priorities & guide
    child_actions = []
    if context.homework.pending_count > 0:
        child_actions.append(f"1. Complete {context.homework.pending_count} pending homework assignment(s).")
    else:
        child_actions.append("1. All homework up to date! Review upcoming class topics.")

    if context.exams.upcoming_count > 0:
        child_actions.append(f"2. Study for upcoming exam ({context.exams.upcoming_exams[0].get('exam_name', 'Exam')}) for 45 minutes.")
    else:
        child_actions.append("2. Practice focused 25-minute Pomodoro study block.")

    child_actions.append("3. Review class material and notes.")
    child_actions.append("4. Keep recreational screen time below your daily limit.")

    # Parent briefing summary (privacy-filtered, NO private diary text)
    parent_summary = []
    if context.homework.overdue_count == 0 and context.homework.completed_count > 0:
        parent_summary.append("• Homework assignments progressing steadily.")
    elif context.homework.overdue_count > 0:
        parent_summary.append(f"• Attention required: {context.homework.overdue_count} overdue assignment(s).")

    if context.study.avg_focus_score and context.study.avg_focus_score >= 75:
        parent_summary.append("• Study consistency and focus scores improving.")
    
    if context.screen_time.avg_daily_minutes > 120:
        parent_summary.append(f"• Recreational screen time elevated ({context.screen_time.avg_daily_minutes} mins/day).")
    else:
        parent_summary.append("• Screen time within healthy boundaries.")

    if context.safety.check_in_status == "SAFE":
        parent_summary.append("• Check-in status safe, no urgent safety concerns.")

    return AIDailyDashboardResponse(
        child_id=child_id,
        greeting=orig_dash.greeting,
        overall_status=status_summary,
        todays_priorities=child_actions[:3],
        homework_status={
            "pending_count": context.homework.pending_count,
            "completed_count": context.homework.completed_count,
            "overdue_count": context.homework.overdue_count,
        },
        upcoming_deadlines=context.exams.upcoming_exams + context.homework.overdue_items,
        exam_preparation_status={
            "upcoming_exams_count": context.exams.upcoming_count,
            "avg_exam_percentage": context.exams.avg_exam_percentage,
        },
        recommended_study_plan=[
            "Morning (45 min): Core Subject Study (Math/Science)",
            "Afternoon (30 min): Homework & Assignment Review",
            "Evening (20 min): Exam Revision & Quiet Reading",
        ],
        study_performance={
            "total_sessions": context.study.total_sessions,
            "avg_focus_score": context.study.avg_focus_score,
            "total_study_minutes": context.study.total_study_minutes,
        },
        screen_time_summary={
            "avg_daily_minutes": context.screen_time.avg_daily_minutes,
            "educational_minutes": context.screen_time.avg_educational_minutes,
            "screen_time_exceeded": context.screen_time.screen_time_exceeded,
        },
        wellness_routine_status={
            "avg_sleep_hours": context.health.avg_sleep_hours,
            "avg_water_ml": context.health.avg_water_intake_ml,
            "breakfast_consistency_pct": context.nutrition.breakfast_consistency_pct,
        },
        pocket_money_status={
            "allowance_total": context.pocket_money.allowance_total,
            "total_spent": context.pocket_money.total_spent,
            "total_saved": context.pocket_money.total_saved,
        },
        safety_status={
            "check_in_status": context.safety.check_in_status,
            "last_check_in_note": context.safety.last_check_in_note,
        },
        important_alerts=orig_dash.important_alerts,
        what_should_i_do_today=child_actions,
        what_should_parent_know=parent_summary,
        timetable=orig_dash.timetable,
        recommendations=orig_dash.recommendations,
        aggregated_data=orig_dash.aggregated_data,
    )


def generate_ai_daily_dashboard(db: Session, child_id: int) -> AIDailyDashboardResponse:
    """
    Phase 6: Generates AI-Assisted Daily Intelligence Dashboard Briefing.
    Bases statements strictly on available context data. Preserves private diary separation.
    """
    # 1. Fetch original dashboard for backward compatibility
    orig_dash = dashboard_service.generate_daily_dashboard(db=db, child_id=child_id)

    # 2. Build structured ChildContext
    builder = ChildContextBuilder(db=db, child_id=child_id)
    context = builder.build(include_ml_predictions=True)

    client = _get_groq_client()
    if not client:
        return generate_fallback_ai_dashboard(child_id, context, orig_dash)

    context_dict = context.model_dump()

    prompt_content = f"""
You are the KinNest AI Daily Intelligence Dashboard Assistant.
Analyze this structured child context:

CHILD CONTEXT DATA:
{json.dumps(context_dict, indent=2, default=str)}

TASK:
Generate a structured daily briefing for the child and parent covering all 14 dashboard domains.

STRICT RULES:
1. Base statements ONLY on provided available context data. Do NOT invent or assume ungrounded facts.
2. PRIVACY & SENSITIVE DATA SEPARATION: Do NOT expose private diary content, sensitive medical notes, or emergency phone numbers to parent summaries.
3. Return ONLY a JSON object adhering to this schema:
{{
  "overall_status": "EXCELLENT|GOOD|MODERATE|NEEDS_ATTENTION",
  "todays_priorities": ["string"],
  "recommended_study_plan": ["string"],
  "what_should_i_do_today": ["string"],
  "what_should_parent_know": ["string"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional child education intelligence assistant. Respond ONLY in valid raw JSON."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        parsed = json.loads(response.choices[0].message.content.strip())
        status_val = parsed.get("overall_status", "GOOD")
        priorities = parsed.get("todays_priorities", [])
        study_plan = parsed.get("recommended_study_plan", [])
        child_do = parsed.get("what_should_i_do_today", [])
        parent_know = parsed.get("what_should_parent_know", [])

        fallback_dash = generate_fallback_ai_dashboard(child_id, context, orig_dash)
        fallback_dash.overall_status = status_val
        if priorities:
            fallback_dash.todays_priorities = priorities
        if study_plan:
            fallback_dash.recommended_study_plan = study_plan
        if child_do:
            fallback_dash.what_should_i_do_today = child_do
        if parent_know:
            fallback_dash.what_should_parent_know = parent_know

        return fallback_dash

    except Exception as e:
        logger.error(f"AI Daily Dashboard generation failed: {e}. Using fallback generator.")
        return generate_fallback_ai_dashboard(child_id, context, orig_dash)
