import logging
from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.attendance import Attendance
from app.models.study import StudySession
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog
from app.models.activity import Activity
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense
from app.models.safety import CheckInLog
from app.models.schedule import ScheduleItem

from app.services.age_adaptation_service import classify_age_group
from app.services.notification_service import NotificationService
from app.ml import predictor
from app.ai.groq_service import generate_ai_recommendations
from app.schemas.dashboard import DailyDashboardResponse

logger = logging.getLogger(__name__)

def generate_daily_dashboard(db: Session, child_id: int) -> DailyDashboardResponse:
    # 1. Fetch profile
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ValueError(f"Child profile with ID {child_id} not found.")
    
    age_group = classify_age_group(child.age)
    today = date.today()
    day_name = today.strftime("%A")

    # 2. Today's timetable
    schedule_items = db.query(ScheduleItem).filter(
        ScheduleItem.child_id == child_id,
        ScheduleItem.day_of_week.ilike(f"%{day_name}%")
    ).all()

    activities = db.query(Activity).filter(
        Activity.child_id == child_id,
        Activity.date == today
    ).all()

    # Format and sort timetable
    timetable_list = []
    for item in schedule_items:
        timetable_list.append({
            "start": item.start_time,
            "end": item.end_time,
            "text": f"{item.start_time.strftime('%H:%M')} - {item.subject} ({item.schedule_type})"
        })
    for act in activities:
        timetable_list.append({
            "start": act.start_time,
            "end": act.end_time,
            "text": f"{act.start_time.strftime('%H:%M')} - {act.title} ({act.activity_type})"
        })
    timetable_list.sort(key=lambda x: x["start"])
    formatted_timetable = [item["text"] for item in timetable_list]

    # 3. Homework summary
    homework_logs = db.query(Homework).filter(Homework.child_id == child_id).all()
    pending_hw = [h for h in homework_logs if not h.completion_status]
    overdue_hw = [h for h in pending_hw if h.due_date < today]

    # 4. Upcoming exams (next 7 days)
    upcoming_limit = today + timedelta(days=7)
    upcoming_exams = db.query(Exam).filter(
        Exam.child_id == child_id,
        Exam.exam_date >= today,
        Exam.exam_date <= upcoming_limit
    ).all()

    # 5. Study Plan & Session logs
    study_logs = db.query(StudySession).filter(StudySession.child_id == child_id).all()
    total_study_minutes = sum(s.duration_minutes for s in study_logs if s.duration_minutes)

    # 6. Attendance summary
    attendance_records = db.query(Attendance).filter(Attendance.child_id == child_id).all()
    if attendance_records:
        present_count = sum(1 for r in attendance_records if r.status.upper() in ("PRESENT", "EXCUSED"))
        attendance_rate = (present_count / len(attendance_records)) * 100.0
    else:
        attendance_rate = 100.0

    # 7. Screen time summary
    screen_logs = db.query(ScreenTimeLog).filter(ScreenTimeLog.child_id == child_id).all()
    avg_screen_time_mins = 0.0
    last_screen_time_mins = 0
    if screen_logs:
        total_screen_mins = sum(
            l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other
            for l in screen_logs
        )
        avg_screen_time_mins = total_screen_mins / len(screen_logs)
        latest_screen = sorted(screen_logs, key=lambda x: x.date, reverse=True)[0]
        last_screen_time_mins = (
            latest_screen.mobile + latest_screen.gaming + latest_screen.tv +
            latest_screen.social_media + latest_screen.study_screen_time + latest_screen.other
        )

    # 8. Health routine
    health_logs = db.query(HealthLog).filter(HealthLog.child_id == child_id).all()
    avg_sleep = 8.0
    avg_water = 1500
    if health_logs:
        avg_sleep = sum(l.sleep_hours for l in health_logs if l.sleep_hours) / len(health_logs)
        avg_water = sum(l.water_intake_ml for l in health_logs if l.water_intake_ml) / len(health_logs)

    # 9. Pocket money & expenses
    allowances = db.query(PocketMoneyAllowance).filter(PocketMoneyAllowance.child_id == child_id).all()
    expenses = db.query(ChildExpense).filter(ChildExpense.child_id == child_id).all()
    total_allowance = sum(a.amount for a in allowances)
    total_expenses = sum(e.amount for e in expenses)
    remaining_balance = total_allowance - total_expenses

    # 10. Safety check-in
    latest_check_in = db.query(CheckInLog).filter(CheckInLog.child_id == child_id).order_by(CheckInLog.date.desc()).first()

    # 11. Notifications
    notifications = NotificationService.get_notifications_for_child(db=db, child_id=child_id, limit=5)

    # 12. ML Predictions
    ml_predictions = {
        "homework_completion_minutes": predictor.predict_homework_completion(db, child_id).prediction,
        "attendance_trend": predictor.predict_attendance_trend(db, child_id).prediction,
        "study_performance": predictor.predict_study_performance(db, child_id).prediction,
        "screen_time_trend": predictor.predict_screen_time_trend(db, child_id).prediction,
        "routine_balance": predictor.predict_routine_balance(db, child_id).prediction,
    }

    # 13. Dynamic Greeting
    curr_hour = datetime.now().hour
    if curr_hour < 12:
        greeting = f"Good morning, {child.name}!"
    elif curr_hour < 17:
        greeting = f"Good afternoon, {child.name}!"
    else:
        greeting = f"Good evening, {child.name}!"

    # 14. Important Alerts
    alerts = []
    if overdue_hw:
        alerts.append(f"You have {len(overdue_hw)} overdue assignment(s)!")
    elif pending_hw:
        due_soon = [h for h in pending_hw if h.due_date <= today + timedelta(days=1)]
        if due_soon:
            alerts.append(f"Assignment '{due_soon[0].title}' is due soon")
            
    if attendance_rate < 80.0:
        alerts.append(f"Attendance is low ({attendance_rate:.1f}%)")
        
    alerts.append(f"₹{remaining_balance:.2f} pocket money remains")
    
    if latest_check_in and latest_check_in.status in ("EXPECTED", "PENDING"):
        alerts.append(f"Return-home check-in required by {latest_check_in.expected_return_time.strftime('%I:%M %p')}")

    if upcoming_exams:
        alerts.append(f"Upcoming exam: {upcoming_exams[0].exam_name} in {upcoming_exams[0].subject}")

    # 15. Recommendations (AI + fallback)
    context = {
        "profile": {
            "name": child.name,
            "age": child.age,
            "age_group": age_group
        },
        "homework_summary": {
            "pending_count": len(pending_hw),
            "overdue_count": len(overdue_hw)
        },
        "health_summary": {
            "avg_sleep_hours": avg_sleep,
            "avg_water_intake_ml": avg_water
        },
        "screen_time_summary": {
            "avg_daily_screen_time_minutes": avg_screen_time_mins,
            "last_screen_time_minutes": last_screen_time_mins
        },
        "pocket_money_summary": {
            "remaining_balance": remaining_balance,
            "total_saved": total_allowance - total_expenses
        },
        "safety_summary": {
            "check_in_status": latest_check_in.status if latest_check_in else "SAFE"
        },
        "activities_summary": {
            "today_activities_count": len(activities)
        }
    }
    
    ai_recs = generate_ai_recommendations(context)
    
    recommendations = []
    if ai_recs.get("homework_prioritization"):
        recommendations.append(f"1. {ai_recs['homework_prioritization'][0]}")
    else:
        recommendations.append("1. Complete your highest-priority pending assignments first.")
        
    if ai_recs.get("study_suggestions"):
        recommendations.append(f"2. {ai_recs['study_suggestions'][0]}")
    else:
        recommendations.append("2. Study Mathematics or key subjects for 45 minutes.")
        
    if ai_recs.get("relaxation_suggestions"):
        recommendations.append(f"3. {ai_recs['relaxation_suggestions'][0]}")
    else:
        recommendations.append("3. Take a 20-minute restorative screen break between study sessions.")
        
    if ai_recs.get("screen_time_advice"):
        recommendations.append(f"4. {ai_recs['screen_time_advice'][0]}")
    else:
        recommendations.append("4. Keep entertainment screen time below your age-adjusted limit.")

    # 16. Compile full payload
    aggregated_data = {
        "profile": {
            "name": child.name,
            "age": child.age,
            "dob": child.date_of_birth.isoformat() if child.date_of_birth else None,
            "parent_contact": child.parent_contact,
            "education_stage": child.education_stage
        },
        "age_adaptation": {
            "age_group": age_group,
            "education_stage": child.education_stage
        },
        "homework": {
            "total": len(homework_logs),
            "pending": len(pending_hw),
            "overdue": len(overdue_hw)
        },
        "exams": [
            {"subject": e.subject, "name": e.exam_name, "date": e.exam_date.isoformat()}
            for e in upcoming_exams
        ],
        "study_plan": {
            "total_study_minutes": total_study_minutes,
            "sessions_count": len(study_logs)
        },
        "attendance": {
            "attendance_rate": attendance_rate,
            "records_count": len(attendance_records)
        },
        "screen_time": {
            "average_daily_minutes": avg_screen_time_mins,
            "last_recorded_minutes": last_screen_time_mins
        },
        "health_routine": {
            "average_sleep_hours": avg_sleep,
            "average_water_ml": avg_water
        },
        "activities": [
            {"title": a.title, "type": a.activity_type, "start": a.start_time.isoformat()}
            for a in activities
        ],
        "pocket_money": {
            "total_allowance": total_allowance,
            "total_expenses": total_expenses,
            "remaining_balance": remaining_balance
        },
        "safety_status": {
            "latest_status": latest_check_in.status if latest_check_in else "UNKNOWN",
            "expected_return": latest_check_in.expected_return_time.isoformat() if latest_check_in else None
        },
        "notifications": [
            {"title": n.title, "type": n.notification_type, "created_at": n.created_at.isoformat()}
            for n in notifications
        ],
        "ml_predictions": ml_predictions
    }

    return DailyDashboardResponse(
        greeting=greeting,
        timetable=formatted_timetable,
        important_alerts=alerts,
        recommendations=recommendations,
        aggregated_data=aggregated_data
    )
