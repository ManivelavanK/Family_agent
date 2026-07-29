from sqlalchemy.orm import Session
from datetime import datetime, date, time
from typing import Optional

from app.services import baby_service, feeding_service, growth_service, health_service, vaccination_service
from app.models.sleep import SleepRecord
from app.schemas.baby_schema import BabyResponse
from app.schemas.growth_schema import GrowthResponse
from app.schemas.vaccination_schema import VaccinationResponse

def get_dashboard_summary(db: Session, baby_id: int) -> dict:
    # 1. Baby Profile
    baby = baby_service.get_baby_by_id(db=db, baby_id=baby_id)
    if not baby:
        raise ValueError(f"Baby with ID {baby_id} not found.")
    
    baby_profile = BabyResponse.model_validate(baby)

    # 2. Feeding Summary
    feeding_summary = feeding_service.get_today_summary(db=db, baby_id=baby_id)

    # 3. Sleep Summary today
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    today_sleep_records = db.query(SleepRecord).filter(
        SleepRecord.baby_id == baby_id,
        SleepRecord.start_time >= today_start,
        SleepRecord.end_time <= today_end
    ).all()
    today_sleep_duration = sum(s.duration_minutes for s in today_sleep_records)
    
    sleep_summary = {
        "total_sleep_duration_minutes": today_sleep_duration,
        "total_sleep_duration_hours": round(today_sleep_duration / 60, 1),
        "sleep_records_count": len(today_sleep_records)
    }

    # 4. Latest Growth Record
    growth_history = growth_service.get_growth_history(db=db, baby_id=baby_id)
    latest_growth = GrowthResponse.model_validate(growth_history[0]) if growth_history else None

    # 5. Latest Health Summary
    latest_health = health_service.get_health_summary(db=db, baby_id=baby_id)

    # 6. Next Vaccination (first pending cron due date >= today)
    upcoming_vaccines = vaccination_service.get_upcoming_vaccinations(db=db, baby_id=baby_id)
    next_vaccination = VaccinationResponse.model_validate(upcoming_vaccines[0]) if upcoming_vaccines else None

    return {
        "baby_profile": baby_profile,
        "feeding_summary": feeding_summary,
        "sleep_summary": sleep_summary,
        "latest_growth": latest_growth,
        "latest_health": latest_health,
        "next_vaccination": next_vaccination
    }
