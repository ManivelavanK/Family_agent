import logging
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.database.database import SessionLocal

from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.activity import Activity
from app.models.health import HealthLog
from app.models.attendance import Attendance
from app.models.safety import SafetyProfile, CheckInLog
from app.models.pocket_money import SavingGoal, PocketMoneyAllowance
from app.models.study import StudySession
from app.services.notification_service import NotificationService, NotificationType

logger = logging.getLogger(__name__)


def job_wrapper(job_func):
    """Decorator to manage database session lifecycle safely for background jobs."""
    def wrapper(*args, **kwargs):
        if "db" in kwargs:
            db = kwargs.pop("db")
            return job_func(db, *args, **kwargs)
        elif args and isinstance(args[0], Session):
            db = args[0]
            return job_func(db, *args[1:], **kwargs)

        db: Session = SessionLocal()
        try:
            return job_func(db, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing job '{job_func.__name__}': {e}", exc_info=True)
            raise e
        finally:
            db.close()
    return wrapper


@job_wrapper
def check_homework_reminders(db: Session):
    """Job 1: Homework reminder for pending or overdue assignments."""
    today = date.today()
    children = db.query(ChildProfile).all()
    for child in children:
        pending = (
            db.query(Homework)
            .filter(Homework.child_id == child.id, Homework.completion_status == False)
            .all()
        )
        if pending:
            high_priority = [h for h in pending if h.priority == "HIGH"]
            count = len(pending)
            title = f"Homework Reminder for {child.name}"
            msg = (
                f"You have {count} pending assignment(s)"
                + (f" ({len(high_priority)} high priority)" if high_priority else "")
                + ". Don't forget to submit on time!"
            )
            NotificationService.send_notification(
                db, child.id, title, msg, NotificationType.HOMEWORK_REMINDER.value
            )


@job_wrapper
def check_exam_reminders(db: Session):
    """Job 2: Exam preparation reminder for upcoming exams in next 3 days."""
    today = date.today()
    upcoming_limit = today + timedelta(days=3)
    children = db.query(ChildProfile).all()
    for child in children:
        exams = (
            db.query(Exam)
            .filter(Exam.child_id == child.id, Exam.exam_date >= today, Exam.exam_date <= upcoming_limit)
            .all()
        )
        for exam in exams:
            days_left = (exam.exam_date - today).days
            day_str = "today" if days_left == 0 else (f"tomorrow" if days_left == 1 else f"in {days_left} days")
            title = f"Exam Alert: {exam.subject}"
            msg = f"Upcoming exam '{exam.exam_name}' in {exam.subject} is scheduled {day_str}. Time to review revision notes!"
            NotificationService.send_notification(
                db, child.id, title, msg, NotificationType.EXAM_REMINDER.value
            )


@job_wrapper
def check_activity_reminders(db: Session):
    """Job 3: Activity reminder for activities scheduled for today."""
    today = date.today()
    children = db.query(ChildProfile).all()
    for child in children:
        activities = (
            db.query(Activity)
            .filter(Activity.child_id == child.id, Activity.date == today)
            .all()
        )
        for act in activities:
            title = f"Activity Reminder: {act.title}"
            msg = f"Scheduled {act.activity_type} ({act.title}) today at {act.start_time}. Location: {act.location or 'Default'}."
            NotificationService.send_notification(
                db, child.id, title, msg, NotificationType.ACTIVITY_REMINDER.value
            )


@job_wrapper
def check_water_reminders(db: Session):
    """Job 4: Water hydration reminder."""
    today = date.today()
    children = db.query(ChildProfile).all()
    for child in children:
        latest_health = (
            db.query(HealthLog)
            .filter(HealthLog.child_id == child.id, HealthLog.date == today)
            .first()
        )
        water = latest_health.water_intake_ml if latest_health and latest_health.water_intake_ml else 0
        if water < 1500:
            title = "Hydration Reminder 💧"
            msg = f"Water intake so far is {water}ml. Remember to drink at least 1500ml of water daily!"
            NotificationService.send_notification(
                db, child.id, title, msg, NotificationType.WATER_REMINDER.value
            )


@job_wrapper
def check_sleep_reminders(db: Session):
    """Job 5: Sleep routine reminder."""
    today = date.today()
    children = db.query(ChildProfile).all()
    for child in children:
        latest_health = (
            db.query(HealthLog)
            .filter(HealthLog.child_id == child.id)
            .order_by(HealthLog.date.desc())
            .first()
        )
        sleep_hours = latest_health.sleep_hours if latest_health and latest_health.sleep_hours else 8.0
        if sleep_hours < 8.0:
            title = "Restorative Sleep Advice 🌙"
            msg = f"Average sleep was {sleep_hours} hrs. Ensure 8-9 hours of consistent sleep tonight for peak focus."
            NotificationService.send_notification(
                db, child.id, title, msg, NotificationType.SLEEP_REMINDER.value
            )


@job_wrapper
def check_attendance_warnings(db: Session):
    """Job 6: Attendance warning when attendance falls below 80% or recent absence."""
    children = db.query(ChildProfile).all()
    for child in children:
        logs = db.query(Attendance).filter(Attendance.child_id == child.id).all()
        if logs:
            total = len(logs)
            present = sum(1 for a in logs if a.status in ("PRESENT", "EXCUSED", "Present"))
            pct = (present / total) * 100.0
            if pct < 80.0:
                title = "Attendance Alert ⚠️"
                msg = f"Current attendance rate is {pct:.1f}%, which is below the 80% threshold. Please check class schedules."
                NotificationService.send_notification(
                    db, child.id, title, msg, NotificationType.ATTENDANCE_WARNING.value
                )


@job_wrapper
def check_safety_checkin_warnings(db: Session):
    """Job 7: Safety check-in warning if check-in is pending or emergency status."""
    children = db.query(ChildProfile).all()
    for child in children:
        check_in = (
            db.query(CheckInLog)
            .filter(CheckInLog.child_id == child.id)
            .order_by(CheckInLog.date.desc())
            .first()
        )
        if check_in and check_in.status in ("MISSED", "EMERGENCY", "PENDING"):
            title = f"Safety Status Alert: {check_in.status}"
            msg = f"Latest safety check-in status for {child.name} is '{check_in.status}'. Please confirm location and safety."
            NotificationService.send_notification(
                db, child.id, title, msg, NotificationType.SAFETY_WARNING.value
            )


@job_wrapper
def check_pocket_money_reminders(db: Session):
    """Job 8: Pocket-money and savings milestone reminder."""
    children = db.query(ChildProfile).all()
    for child in children:
        goals = db.query(SavingGoal).filter(SavingGoal.child_id == child.id).all()
        for goal in goals:
            pct = (goal.current_saved / goal.target_amount) * 100.0 if goal.target_amount > 0 else 0
            if pct < 100.0:
                title = f"Savings Goal Progress: {goal.title}"
                msg = f"You have saved ${goal.current_saved:.2f} out of ${goal.target_amount:.2f} ({pct:.1f}%) for '{goal.title}'!"
                NotificationService.send_notification(
                    db, child.id, title, msg, NotificationType.POCKET_MONEY_REMINDER.value
                )


@job_wrapper
def check_study_reminders(db: Session):
    """Job 9: Study session & focus block encouragement reminder."""
    children = db.query(ChildProfile).all()
    for child in children:
        title = f"Study Session Encouragement 📚"
        msg = f"Ready for a focused 25-minute Pomodoro study block today, {child.name}?"
        NotificationService.send_notification(
            db, child.id, title, msg, NotificationType.STUDY_REMINDER.value
        )
