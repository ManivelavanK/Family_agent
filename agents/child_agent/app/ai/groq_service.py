import os
import json
import logging
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def _get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY") or GROQ_API_KEY
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment. Using deterministic fallback.")
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None


def generate_fallback_recommendations(context: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback deterministic recommendation generator if Groq API is unavailable."""
    profile = context.get("profile", {})
    age_group = profile.get("age_group", "MIDDLE_CHILDHOOD")
    name = profile.get("name", "Child")

    hw = context.get("homework_summary", {})
    health = context.get("health_summary", {})
    screen = context.get("screen_time_summary", {})
    pocket = context.get("pocket_money_summary", {})
    safety = context.get("safety_summary", {})
    activities = context.get("activities_summary", {})

    return {
        "study_suggestions": [
            f"Set aside a quiet 45-minute study window for {name}.",
            "Use the Pomodoro technique (25 min study, 5 min break) for focused learning."
        ],
        "homework_prioritization": [
            f"Prioritize the {hw.get('pending_count', 0)} pending homework assignments starting with high priority items.",
            "Complete complex subjects early in the session while energy is highest."
        ],
        "time_management": [
            "Maintain a consistent weekday routine balancing study, play, and family time.",
            "Use daily schedule timetables to track class and activity transitions."
        ],
        "daily_motivation": f"Keep doing your best, {name}! Consistency builds confidence and success every single day.",
        "healthy_routine_advice": [
            f"Maintain average target sleep of 8-9 hours per night (current avg: {health.get('avg_sleep_hours', 8.0)} hrs).",
            f"Ensure daily hydration target of at least 1500 ml (current avg: {health.get('avg_water_intake_ml', 1500)} ml)."
        ],
        "screen_time_advice": [
            f"Keep entertainment screen time under control (current avg: {screen.get('avg_daily_screen_time_minutes', 0)} mins).",
            "Avoid screen usage 1 hour before bedtime to support restorative sleep."
        ],
        "saving_suggestions": [
            f"Allocate 20% of pocket allowance toward active savings goals (total saved: ${pocket.get('total_saved', 0.0)}).",
            "Track daily spending to build smart financial awareness."
        ],
        "parent_recommendations": [
            f"Conduct regular weekly check-ins with {name} regarding schoolwork and wellbeing.",
            f"Ensure safety contact rules are reviewed (current safety alert status: {safety.get('check_in_status', 'SAFE')})."
        ],
        "exam_preparation_suggestions": [
            "Review key chapter formulas and summary notes 1 week prior to exams.",
            "Take mock revision quizzes to reinforce long-term memory."
        ],
        "relaxation_suggestions": [
            "Engage in 15 minutes of outdoor walking or guided breathing activities after study sessions.",
            "Listen to calming music or pursue creative hobbies during downtime."
        ]
    }


def generate_ai_recommendations(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends structured child context to Groq AI for reasoning, explanation, and recommendation generation.
    Returns validated structured dict.
    """
    client = _get_groq_client()
    if not client:
        fallback = generate_fallback_recommendations(context)
        fallback["_generated_by"] = "Deterministic Rule Engine (Fallback - Missing API Key)"
        return fallback

    prompt_content = f"""
You are the KinNest Child Intelligence Assistant.
Analyze the following structured child profile, health, study, safety, financial data, and ML predictions.

CONTEXT DATA:
{json.dumps(context, indent=2, default=str)}

Task:
Generate structured, empathetic, age-appropriate, encouraging recommendations across all 10 required domains.

RULES:
1. Do NOT recalculate or modify financial values, attendance percentages, health metrics, or safety alert statuses. Treat provided context as absolute ground truth.
2. Return ONLY a valid JSON object matching this schema EXACTLY:
{{
  "study_suggestions": ["string"],
  "homework_prioritization": ["string"],
  "time_management": ["string"],
  "daily_motivation": "string",
  "healthy_routine_advice": ["string"],
  "screen_time_advice": ["string"],
  "saving_suggestions": ["string"],
  "parent_recommendations": ["string"],
  "exam_preparation_suggestions": ["string"],
  "relaxation_suggestions": ["string"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional child safety, wellbeing, and education reasoning AI. Respond ONLY in valid raw JSON with no markdown backticks."
                },
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            temperature=0.6,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content.strip()
        # Clean any potential markdown wrapping
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:]
        if raw_json.startswith("```"):
            raw_json = raw_json[3:]
        if raw_json.endswith("```"):
            raw_json = raw_json[:-3]

        parsed = json.loads(raw_json.strip())
        parsed["_generated_by"] = "Groq AI (llama-3.3-70b-versatile)"
        return parsed

    except Exception as e:
        logger.error(f"Groq API call failed: {e}. Falling back to rule-based engine.")
        fallback = generate_fallback_recommendations(context)
        fallback["_generated_by"] = f"Deterministic Rule Engine (Fallback - {type(e).__name__})"
        return fallback
