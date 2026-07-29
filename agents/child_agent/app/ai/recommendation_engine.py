import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pydantic import ValidationError

from app.schemas.context import ChildContext
from app.schemas.ai_recommendation import (
    DetailedRecommendationItem,
    ChildRecommendationEngineOutput,
)
from app.ai.groq_service import _get_groq_client, generate_fallback_recommendations

logger = logging.getLogger(__name__)


def generate_fallback_detailed_recommendations(context: ChildContext) -> ChildRecommendationEngineOutput:
    """
    Deterministic fallback generator for structured detailed recommendations.
    Uses context indicators to produce exact, compliant recommendation items.
    """
    recs: List[DetailedRecommendationItem] = []
    now_iso = datetime.utcnow().isoformat()

    # 1. Homework check
    if context.homework.overdue_count > 0 or context.homework.pending_count > 0:
        recs.append(
            DetailedRecommendationItem(
                category="homework",
                title="Homework Prioritization Required",
                explanation=f"Child has {context.homework.pending_count} pending homework task(s), including {context.homework.overdue_count} overdue assignment(s).",
                priority="HIGH" if context.homework.overdue_count > 0 else "MEDIUM",
                suggested_action=f"Focus first on completing high priority/overdue tasks in {', '.join(context.homework.pending_subjects) if context.homework.pending_subjects else 'pending subjects'}.",
                reason="Overdue homework impacts academic performance and causes study backlog.",
                confidence="HIGH",
                requires_parent_attention=context.homework.overdue_count > 0,
                requires_immediate_action=context.homework.overdue_count > 0,
                source_data=["homework.pending_count", "homework.overdue_count", "homework.pending_subjects"],
                created_at=now_iso,
            )
        )
    else:
        recs.append(
            DetailedRecommendationItem(
                category="homework",
                title="Homework Up to Date",
                explanation="All homework assignments are currently completed.",
                priority="LOW",
                suggested_action="Maintain regular daily homework review habits.",
                reason="Child has no pending or overdue homework items.",
                confidence="HIGH",
                requires_parent_attention=False,
                requires_immediate_action=False,
                source_data=["homework.pending_count"],
                created_at=now_iso,
            )
        )

    # 2. Screen Time check
    if context.screen_time.avg_daily_minutes > 120.0 or context.screen_time.screen_time_exceeded:
        recs.append(
            DetailedRecommendationItem(
                category="screen_time",
                title="Screen Time Balance Needed",
                explanation=f"Daily average screen time is {context.screen_time.avg_daily_minutes} minutes, which exceeds recommended limits.",
                priority="HIGH",
                suggested_action="Implement screen-free breaks after 45 minutes of usage and avoid screens 1 hour before sleep.",
                reason="Excessive screen time affects sleep quality and focus duration.",
                confidence="HIGH",
                requires_parent_attention=True,
                requires_immediate_action=False,
                source_data=["screen_time.avg_daily_minutes", "screen_time.late_night_count"],
                created_at=now_iso,
            )
        )

    # 3. Upcoming Exam check
    if context.exams.upcoming_count > 0:
        recs.append(
            DetailedRecommendationItem(
                category="exams",
                title="Upcoming Exam Preparation Plan",
                explanation=f"Child has {context.exams.upcoming_count} upcoming exam(s).",
                priority="HIGH",
                suggested_action="Schedule 25-minute Pomodoro study blocks for exam revision across key subjects.",
                reason="Early structured exam revision improves retention and reduces stress.",
                confidence="HIGH",
                requires_parent_attention=False,
                requires_immediate_action=True,
                source_data=["exams.upcoming_count", "exams.upcoming_exams"],
                created_at=now_iso,
            )
        )

    # 4. Study Consistency & Focus check
    if context.study.total_sessions == 0 or (context.study.avg_focus_score and context.study.avg_focus_score < 70.0):
        recs.append(
            DetailedRecommendationItem(
                category="study_habits",
                title="Improve Study Routine & Focus",
                explanation=f"Study session count is {context.study.total_sessions} with average focus score of {context.study.avg_focus_score or 'N/A'}.",
                priority="MEDIUM",
                suggested_action="Establish a consistent 45-minute daily quiet study window in a distraction-free space.",
                reason="Regular focus study sessions improve subject mastery.",
                confidence="HIGH",
                requires_parent_attention=False,
                requires_immediate_action=False,
                source_data=["study.total_sessions", "study.avg_focus_score"],
                created_at=now_iso,
            )
        )

    # 5. Academic Performance check
    if context.exams.avg_exam_percentage is not None and context.exams.avg_exam_percentage >= 85.0:
        recs.append(
            DetailedRecommendationItem(
                category="academic",
                title="Strong Academic Performance",
                explanation=f"Average exam performance is strong at {context.exams.avg_exam_percentage}%.",
                priority="LOW",
                suggested_action="Encourage advanced enrichment materials and positive praise.",
                reason="High academic scores indicate good comprehension.",
                confidence="HIGH",
                requires_parent_attention=False,
                requires_immediate_action=False,
                source_data=["exams.avg_exam_percentage"],
                created_at=now_iso,
            )
        )

    # Safety-critical check (100% deterministic safety rule)
    if context.safety.check_in_status in ("OVERDUE", "EMERGENCY"):
        recs.append(
            DetailedRecommendationItem(
                category="safety",
                title="Safety Alert - Immediate Attention Required",
                explanation=f"Current safety check-in status is {context.safety.check_in_status}.",
                priority="HIGH",
                suggested_action="Verify child location and contact parent/emergency contacts immediately.",
                reason="Safety check-in status indicates overdue return or emergency state.",
                confidence="HIGH",
                requires_parent_attention=True,
                requires_immediate_action=True,
                source_data=["safety.check_in_status"],
                created_at=now_iso,
            )
        )

    return ChildRecommendationEngineOutput(
        child_id=context.profile.child_id,
        recommendations=recs,
        generated_by="Deterministic Rule Engine (Fallback)",
    )


def generate_ai_child_recommendations(context: ChildContext) -> ChildRecommendationEngineOutput:
    """
    Phase 3 AI-powered Child Recommendation Pipeline using Groq LLM with Pydantic validation.
    Analyzes all domain indicators from ChildContext and generates structured, compliant recommendations.
    Strictly avoids inventing ungrounded facts. Fallbacks to deterministic engine if API key missing or invalid response.
    """
    client = _get_groq_client()
    if not client:
        return generate_fallback_detailed_recommendations(context)

    context_dict = context.model_dump()

    prompt_content = f"""
You are the KinNest Child Intelligence Recommendation Engine.
Analyze the following normalized, privacy-filtered child context:

CHILD CONTEXT DATA:
{json.dumps(context_dict, indent=2, default=str)}

TASK:
Generate a list of structured recommendations covering relevant domains (academic, homework, study_habits, focus, exams, attendance, screen_time, routine, activities, financial, wellness, safety).

STRICT RULES:
1. Do NOT invent facts or hallucinate metrics not present in CHILD CONTEXT DATA.
2. If required data is unavailable or missing (e.g. 0 exams, None focus score), explicitly state that data is unavailable in the explanation or mark confidence appropriately.
3. For each recommendation item, provide exact fields matching this JSON structure:
{{
  "category": "academic|homework|study_habits|focus|exams|attendance|screen_time|routine|activities|financial|wellness|safety",
  "title": "string",
  "explanation": "string",
  "priority": "HIGH|MEDIUM|LOW",
  "suggested_action": "string",
  "reason": "string",
  "confidence": "HIGH|MEDIUM|LOW",
  "requires_parent_attention": boolean,
  "requires_immediate_action": boolean,
  "source_data": ["string"]
}}
4. Keep safety alert decisions deterministic and grounded strictly in context.safety.
5. Return ONLY a JSON object containing a "recommendations" array. No markdown backticks.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional child education, safety, and wellbeing AI reasoning assistant. Respond strictly in valid raw JSON."
                },
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:]
        if raw_json.startswith("```"):
            raw_json = raw_json[3:]
        if raw_json.endswith("```"):
            raw_json = raw_json[:-3]

        parsed = json.loads(raw_json.strip())
        raw_items = parsed.get("recommendations", [])

        validated_items: List[DetailedRecommendationItem] = []
        for item in raw_items:
            try:
                # Ensure created_at field is present
                if "created_at" not in item or not item["created_at"]:
                    item["created_at"] = datetime.utcnow().isoformat()
                val_item = DetailedRecommendationItem(**item)
                validated_items.append(val_item)
            except ValidationError as ve:
                logger.warning(f"Skipping invalid recommendation item from LLM: {ve}")

        if not validated_items:
            logger.warning("No valid recommendation items returned from LLM. Using fallback engine.")
            return generate_fallback_detailed_recommendations(context)

        return ChildRecommendationEngineOutput(
            child_id=context.profile.child_id,
            recommendations=validated_items,
            generated_by="Groq AI (llama-3.3-70b-versatile)",
        )

    except Exception as e:
        logger.error(f"Groq recommendation pipeline failed: {e}. Falling back to deterministic engine.")
        return generate_fallback_detailed_recommendations(context)
