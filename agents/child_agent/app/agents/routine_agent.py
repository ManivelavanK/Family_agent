from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.screen_time import ScreenTimeLog
from app.models.activity import Activity
from app.models.profile import ChildProfile

def handle_query(db: Session, child_id: int, query: str) -> dict:
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    child_name = child.name if child else "Child"

    if "screen" in query.lower() or "time" in query.lower():
        # Query screen time average/logs for the past 7 days
        today = date.today()
        start_date = today - timedelta(days=7)
        logs = db.query(ScreenTimeLog).filter(
            ScreenTimeLog.child_id == child_id,
            ScreenTimeLog.date >= start_date
        ).all()

        total_minutes = sum(
            log.mobile + log.gaming + log.tv + log.social_media + log.study_screen_time + log.other
            for log in logs
        )
        avg_hours = (total_minutes / len(logs)) / 60.0 if logs else 0.0

        return {
            "agent": "Digital Wellness / Routine Agent",
            "reply": f"Hi {child_name}, you used an average of {avg_hours:.2f} hours of screen time per day over the last week.",
            "actions": {
                "average_daily_screen_time_hours": round(avg_hours, 2),
                "total_screen_time_entries": len(logs)
            }
        }

    # Query schedule/activities
    today = date.today()
    activities = db.query(Activity).filter(
        Activity.child_id == child_id,
        Activity.date == today
    ).all()

    act_list = [f"'{a.title}' at {a.start_time}" for a in activities]
    reply = f"Hello {child_name}! Here is your agenda for today: "
    if act_list:
        reply += ", ".join(act_list)
    else:
        reply += "No special activities scheduled for today."

    return {
        "agent": "Routine Agent",
        "reply": reply,
        "actions": {
            "today_activities_count": len(activities)
        }
    }
