from datetime import datetime, date, timedelta
from typing import Optional, List
from app.models.vaccination import VaccinationRecord

def check_feeding_overdue(latest_feeding_time: Optional[datetime]) -> Optional[str]:
    if not latest_feeding_time:
        return None
    # Compare with current time
    if datetime.now() - latest_feeding_time > timedelta(hours=4):
        return "Baby may need feeding."
    return None

def check_poor_sleep(today_sleep_duration_minutes: float) -> Optional[str]:
    # 8 hours is 480 minutes
    if today_sleep_duration_minutes < 480:
        return "Baby slept less than recommended today."
    return None

def check_fever(latest_temperature_c: Optional[float]) -> Optional[str]:
    if latest_temperature_c is not None and latest_temperature_c > 38.0:
        return "High temperature detected."
    return None

def check_vaccination_reminder(upcoming_vaccinations: List[VaccinationRecord]) -> Optional[str]:
    today = date.today()
    three_days_later = today + timedelta(days=3)
    for v in upcoming_vaccinations:
        if v.status == "pending" and today <= v.due_date <= three_days_later:
            return "Vaccination due soon."
    return None
