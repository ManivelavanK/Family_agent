import datetime
import math
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from app.models.health import HealthLog
from app.models.profile import ChildProfile
from app.schemas.health import HealthLogCreate, HealthReportResponse
from app.services.age_adaptation_service import classify_age_group

def create_health_log(db: Session, log_in: HealthLogCreate) -> HealthLog:
    db_log = HealthLog(
        child_id=log_in.child_id,
        date=log_in.date,
        height=log_in.height,
        weight=log_in.weight,
        water_intake_ml=log_in.water_intake_ml,
        sleep_hours=log_in.sleep_hours,
        sleep_time=log_in.sleep_time,
        wake_time=log_in.wake_time,
        physical_activity_minutes=log_in.physical_activity_minutes,
        exercise_type=log_in.exercise_type,
        vaccinations=log_in.vaccinations,
        health_notes=log_in.health_notes,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs_by_child_id(db: Session, child_id: int) -> List[HealthLog]:
    return db.query(HealthLog).filter(HealthLog.child_id == child_id).order_by(HealthLog.date.desc()).all()

def generate_health_report(db: Session, child_id: int) -> Optional[HealthReportResponse]:
    # 1. Fetch Child Profile
    profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not profile:
        return None
        
    age_group = classify_age_group(profile.age)
    
    # Age-adapted recommended sleep ranges
    sleep_guidelines = {
        "EARLY_CHILDHOOD": (10.0, 13.0),
        "PRIMARY_SCHOOL": (9.0, 11.0),
        "MIDDLE_SCHOOL": (9.0, 10.0),
        "HIGH_SCHOOL": (8.0, 10.0),
        "COLLEGE": (7.0, 9.0),
    }
    sleep_min, sleep_max = sleep_guidelines.get(age_group, (8.0, 10.0))

    # 2. Fetch past 7 days logs
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=6)
    logs = db.query(HealthLog).filter(
        HealthLog.child_id == child_id,
        HealthLog.date >= seven_days_ago,
        HealthLog.date <= today
    ).all()

    # 3. Compile daily summary (for today's date)
    daily_summary_data = {
        "logged": False,
        "date": today,
        "water_intake_ml": 0,
        "sleep_hours": 0.0,
        "physical_activity_minutes": 0,
        "height": None,
        "weight": None
    }
    for l in logs:
        if l.date == today:
            daily_summary_data.update({
                "logged": True,
                "water_intake_ml": l.water_intake_ml,
                "sleep_hours": l.sleep_hours,
                "physical_activity_minutes": l.physical_activity_minutes,
                "height": l.height,
                "weight": l.weight
            })
            break

    # 4. Compile weekly report / averages
    num_logs = len(logs)
    total_water = 0
    total_sleep = 0.0
    total_activity = 0
    latest_height = None
    latest_weight = None
    
    sleep_consistent_days = 0
    water_consistent_days = 0
    activity_consistent_days = 0
    
    sleep_durations = []
    
    # Sort logs chronologically to get latest metrics correctly
    sorted_logs = sorted(logs, key=lambda x: x.date)
    for l in sorted_logs:
        total_water += l.water_intake_ml
        total_sleep += l.sleep_hours
        total_activity += l.physical_activity_minutes
        
        sleep_durations.append(l.sleep_hours)
        
        if l.height is not None:
            latest_height = l.height
        if l.weight is not None:
            latest_weight = l.weight
            
        # Consistency checks per day
        if sleep_min <= l.sleep_hours <= sleep_max:
            sleep_consistent_days += 1
        if l.water_intake_ml >= 1500:
            water_consistent_days += 1
        if l.physical_activity_minutes >= 45:
            activity_consistent_days += 1

    avg_water = round(total_water / num_logs, 1) if num_logs > 0 else 0.0
    avg_sleep = round(total_sleep / num_logs, 1) if num_logs > 0 else 0.0
    avg_activity = round(total_activity / num_logs, 1) if num_logs > 0 else 0.0

    # Calculate sleep standard deviation for irregularity detection
    sleep_std_dev = 0.0
    if len(sleep_durations) > 1:
        mean_sleep = sum(sleep_durations) / len(sleep_durations)
        variance = sum((x - mean_sleep) ** 2 for x in sleep_durations) / (len(sleep_durations) - 1)
        sleep_std_dev = math.sqrt(variance)

    # Consistency Percentages (based on the past 7 calendar days)
    sleep_consistency = round((sleep_consistent_days / 7.0) * 100.0, 1)
    water_consistency = round((water_consistent_days / 7.0) * 100.0, 1)
    activity_consistency = round((activity_consistent_days / 7.0) * 100.0, 1)

    # 5. Routine Analysis Alerts
    alerts = []
    
    if num_logs > 0:
        if avg_sleep < sleep_min:
            alerts.append(
                f"Insufficient sleep: Your child's daily average sleep of {avg_sleep} hours "
                f"is below the recommended {sleep_min}-{sleep_max} hours for their age group."
            )
        if sleep_std_dev > 1.5:
            alerts.append(
                f"Irregular sleep schedule: Sleep duration fluctuates significantly (variance std dev = {round(sleep_std_dev, 1)} hours). "
                "Establishing a consistent bedtime and waking routine is recommended."
            )
        if avg_water < 1500:
            alerts.append(
                f"Low water intake: Hydration of {avg_water} mL is below the recommended daily benchmark of 1,500 mL."
            )
        if avg_activity < 45:
            alerts.append(
                f"Low activity: Daily physical activity of {avg_activity} minutes is below the recommended active guideline of 45 minutes."
            )
            
    # Routine logging check
    if num_logs < 4:
        alerts.append(
            f"Poor routine consistency: Frequent gaps in wellness logging ({num_logs} logs in past 7 days). "
            "Tracking metrics daily helps establish regular routines and provides better insights."
        )

    # Non-diagnostic medical guidance disclaimer
    if alerts:
        alerts.append(
            "Note: This routine analysis is for educational purposes only and does not substitute for medical diagnoses. "
            "If these patterns persist and cause concern, please contact a parent/guardian or healthcare professional for guidance."
        )
    else:
        alerts.append("Routine and health habits are well-balanced. Keep up the excellent routine consistency!")

    return HealthReportResponse(
        child_id=child_id,
        daily_summary=daily_summary_data,
        weekly_averages={
            "average_water_intake_ml": avg_water,
            "average_sleep_hours": avg_sleep,
            "average_physical_activity_minutes": avg_activity,
            "latest_height_cm": latest_height,
            "latest_weight_kg": latest_weight,
            "logs_count": num_logs
        },
        sleep_consistency_percentage=sleep_consistency,
        water_consistency_percentage=water_consistency,
        activity_consistency_percentage=activity_consistency,
        routine_analysis_alerts=alerts
    )
