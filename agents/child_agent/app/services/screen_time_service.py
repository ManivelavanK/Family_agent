import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.screen_time import ScreenTimeLog
from app.models.profile import ChildProfile
from app.schemas.screen_time import ScreenTimeCreate, ScreenTimeAnalysisResponse
from app.services.age_adaptation_service import classify_age_group

def create_screen_time_log(db: Session, log_in: ScreenTimeCreate) -> ScreenTimeLog:
    db_log = ScreenTimeLog(
        child_id=log_in.child_id,
        date=log_in.date,
        mobile=log_in.mobile,
        gaming=log_in.gaming,
        tv=log_in.tv,
        social_media=log_in.social_media,
        study_screen_time=log_in.study_screen_time,
        other=log_in.other,
        late_night_minutes=log_in.late_night_minutes,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs_by_child_id(db: Session, child_id: int) -> List[ScreenTimeLog]:
    return db.query(ScreenTimeLog).filter(ScreenTimeLog.child_id == child_id).order_by(ScreenTimeLog.date.desc()).all()

def get_daily_total(db: Session, child_id: int) -> int:
    today = datetime.date.today()
    log = db.query(ScreenTimeLog).filter(
        ScreenTimeLog.child_id == child_id,
        ScreenTimeLog.date == today
    ).first()
    if not log:
        return 0
    return (log.mobile + log.gaming + log.tv + log.social_media + log.study_screen_time + log.other)

def get_weekly_total(db: Session, child_id: int) -> int:
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=6)
    logs = db.query(ScreenTimeLog).filter(
        ScreenTimeLog.child_id == child_id,
        ScreenTimeLog.date >= seven_days_ago
    ).all()
    return sum(l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other for l in logs)

def get_monthly_total(db: Session, child_id: int) -> int:
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    logs = db.query(ScreenTimeLog).filter(
        ScreenTimeLog.child_id == child_id,
        ScreenTimeLog.date >= start_of_month,
        ScreenTimeLog.date <= today
    ).all()
    return sum(l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other for l in logs)

def generate_screen_time_analysis(db: Session, child_id: int) -> ScreenTimeAnalysisResponse:
    # 1. Fetch child profile for age limits
    profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    age = profile.age if profile else 10
    age_group = classify_age_group(age)
    
    # Age group limit (in minutes) for daily entertainment screen time
    age_limits = {
        "EARLY_CHILDHOOD": 60,
        "PRIMARY_SCHOOL": 90,
        "MIDDLE_SCHOOL": 120,
        "HIGH_SCHOOL": 180,
        "COLLEGE": 300,
    }
    recommended_limit = age_limits.get(age_group, 120)

    # 2. Fetch past 7 days logs
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=6)
    past_logs = db.query(ScreenTimeLog).filter(
        ScreenTimeLog.child_id == child_id,
        ScreenTimeLog.date >= seven_days_ago,
        ScreenTimeLog.date <= today
    ).all()

    total_screen = 0
    total_ent = 0
    total_study = 0
    total_late_night = 0
    high_gaming_days = 0
    days_logged = len(past_logs) if len(past_logs) > 0 else 1

    for l in past_logs:
        ent = l.mobile + l.gaming + l.tv + l.social_media + l.other
        total_ent += ent
        total_study += l.study_screen_time
        total_screen += (ent + l.study_screen_time)
        total_late_night += l.late_night_minutes
        if l.gaming > 120:
            high_gaming_days += 1

    daily_avg_ent = round(total_ent / 7.0, 1)  # divide by 7 days of the week
    ratio = round(total_ent / total_study, 2) if total_study > 0 else 0.0

    # 3. Calculate weekly trend (compare to previous 7 days)
    prev_end = seven_days_ago - datetime.timedelta(days=1)
    prev_start = prev_end - datetime.timedelta(days=6)
    prev_logs = db.query(ScreenTimeLog).filter(
        ScreenTimeLog.child_id == child_id,
        ScreenTimeLog.date >= prev_start,
        ScreenTimeLog.date <= prev_end
    ).all()
    prev_total = sum(l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other for l in prev_logs)

    if prev_total > 0:
        pct_change = ((total_screen - prev_total) / prev_total) * 100
        if pct_change > 5.0:
            trend = f"UPWARD (+{round(pct_change, 1)}% change compared to previous week)"
        elif pct_change < -5.0:
            trend = f"DOWNWARD ({round(pct_change, 1)}% change compared to previous week)"
        else:
            trend = "STABLE"
    else:
        trend = "STABLE"

    # 4. Detect wellness concerns (without making medical claims)
    alerts = []
    if daily_avg_ent > recommended_limit:
        alerts.append(
            f"Excessive screen time detected: Your child's daily average entertainment screen time of {daily_avg_ent} minutes "
            f"exceeds the recommended age-adapted limit of {recommended_limit} minutes."
        )
    if total_late_night > 0:
        alerts.append(
            f"Late-night screen usage detected: Logged {total_late_night} minutes of screen activity after 10 PM. "
            "Consider establishing screen-free boundaries before bedtime to protect sleep routines."
        )
    if high_gaming_days > 0:
        alerts.append(
            f"High gaming usage detected: Logged gaming sessions exceeded 120 minutes on {high_gaming_days} day(s) "
            "in the past week. Consider encouraging offline hobbies and physical activities."
        )
    if ratio > 3.0 and total_ent > 60:
        alerts.append(
            f"Poor study/screen balance: Entertainment screen usage ({total_ent} mins) is {ratio} times greater than "
            f"educational study screen usage ({total_study} mins). Try setting balance guidelines."
        )

    if not alerts:
        alerts.append("Digital wellness is well-balanced. Keep up the healthy habits!")

    return ScreenTimeAnalysisResponse(
        total_screen_time=total_screen,
        entertainment_time=total_ent,
        study_time=total_study,
        entertainment_study_ratio=ratio,
        daily_average_entertainment=daily_avg_ent,
        weekly_trend=trend,
        alerts=alerts
    )
