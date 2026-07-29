from sqlalchemy.orm import Session
from datetime import datetime, date, time
from app.services import feeding_service, sleep_service, health_service, vaccination_service
from app.models.sleep import SleepRecord
from app.rule_engine import baby_rules

def generate_alerts(db: Session, baby_id: int) -> dict:
    # 1. Fetch latest feeding time
    feedings = feeding_service.get_feeding_history(db=db, baby_id=baby_id)
    latest_feeding_time = feedings[0].feeding_time if feedings else None

    # 2. Fetch today's total sleep duration in minutes
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    today_sleep_records = db.query(SleepRecord).filter(
        SleepRecord.baby_id == baby_id,
        SleepRecord.start_time >= today_start,
        SleepRecord.end_time <= today_end
    ).all()
    today_sleep_duration = sum(s.duration_minutes for s in today_sleep_records)

    # 3. Fetch latest health record temperature
    health_history = health_service.get_health_history(db=db, baby_id=baby_id)
    latest_temp = health_history[0].temperature_c if health_history else None

    # 4. Fetch upcoming vaccinations
    upcoming_vaccines = vaccination_service.get_upcoming_vaccinations(db=db, baby_id=baby_id)

    # Run rules
    alerts = []
    
    feed_alert = baby_rules.check_feeding_overdue(latest_feeding_time)
    if feed_alert:
        alerts.append(feed_alert)
        
    sleep_alert = baby_rules.check_poor_sleep(today_sleep_duration)
    if sleep_alert:
        alerts.append(sleep_alert)
        
    fever_alert = baby_rules.check_fever(latest_temp)
    if fever_alert:
        alerts.append(fever_alert)
        
    vaccine_alert = baby_rules.check_vaccination_reminder(upcoming_vaccines)
    if vaccine_alert:
        alerts.append(vaccine_alert)

    return {"alerts": alerts}
