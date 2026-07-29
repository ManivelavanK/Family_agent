from sqlalchemy.orm import Session
from datetime import datetime, date, time
from app.services import baby_service, feeding_service, sleep_service, growth_service, health_service, vaccination_service, rule_service
from app.models.sleep import SleepRecord
from app.ai import groq_service

def get_ai_insights(db: Session, baby_id: int, question: str) -> str:
    # 1. Gather baby profile
    baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
    if not baby:
        raise ValueError(f"Baby with ID {baby_id} not found.")

    # 2. Gather today's feeding logs
    feed_summary = feeding_service.get_today_summary(db=db, baby_id=baby_id)

    # 3. Gather today's sleep logs
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    today_sleep_records = db.query(SleepRecord).filter(
        SleepRecord.baby_id == baby_id,
        SleepRecord.start_time >= today_start,
        SleepRecord.end_time <= today_end
    ).all()
    today_sleep_duration = sum(s.duration_minutes for s in today_sleep_records)

    # 4. Gather growth stats
    growth_sum = growth_service.get_growth_summary(db=db, baby_id=baby_id)

    # 5. Gather latest health stats
    health_sum = health_service.get_health_summary(db=db, baby_id=baby_id)

    # 6. Gather vaccination summary
    vaccines = vaccination_service.get_vaccination_history(db=db, baby_id=baby_id)
    vaccine_summary = f"Total vaccine records: {len(vaccines)}. "
    pending_vaccines = [v for v in vaccines if v.status == "pending"]
    vaccine_summary += f"Pending vaccinations: {len(pending_vaccines)}."

    # 7. Gather active rule alerts
    alerts_data = rule_service.generate_alerts(db=db, baby_id=baby_id)
    alerts = alerts_data.get("alerts", [])

    # Build prompt
    prompt = f"""
Here is the current status and daily logs for baby {baby.name}:
- Date of Birth: {baby.date_of_birth}
- Gender: {baby.gender}
- Birth Weight: {baby.birth_weight} kg
- Parent Contact: {baby.parent_contact}

Today's Feeding Summary:
- Total Feedings: {feed_summary.get('total_feedings', 0)}
- Total Quantity (ml): {feed_summary.get('total_quantity_ml', 0)} ml

Today's Sleep Summary:
- Total Sleep: {today_sleep_duration} minutes ({round(today_sleep_duration / 60, 1)} hours)

Growth Summary:
- Current Weight: {growth_sum.get('current_weight_kg')} kg (net change: {growth_sum.get('weight_change_kg')} kg)
- Current Height: {growth_sum.get('current_height_cm')} cm (net change: {growth_sum.get('height_change_cm')} cm)

Latest Health Status:
- Latest Temperature: {health_sum.get('latest_temperature_c')} C
- Latest Heart Rate: {health_sum.get('latest_heart_rate')} bpm
- Symptoms: {health_sum.get('latest_symptoms')}
- Medicine: {health_sum.get('latest_medicine')}
- Visit Date: {health_sum.get('latest_visit_date')}

Vaccination Status:
- {vaccine_summary}

Active Alerts:
- {', '.join(alerts) if alerts else 'No active alerts.'}

Parent's Question:
"{question}"
"""

    system_prompt = "You are babychild_agent, the smart baby care management AI assistant for the KinNest platform. Provide intelligent, helpful, and empathetic insights based on the provided logs."

    return groq_service.call_groq(prompt, system_prompt)
