from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.study import StudySession
from app.models.profile import ChildProfile

def handle_query(db: Session, child_id: int, query: str) -> dict:
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    child_name = child.name if child else "Child"
    
    # 1. Look for pending homework
    pending_hw = db.query(Homework).filter(
        Homework.child_id == child_id,
        Homework.completion_status == False
    ).all()
    
    # 2. Look for upcoming exams
    today = date.today()
    upcoming_limit = today + timedelta(days=7)
    exams = db.query(Exam).filter(
        Exam.child_id == child_id,
        Exam.exam_date >= today,
        Exam.exam_date <= upcoming_limit
    ).all()

    # Determine response logic
    if "exam" in query.lower() or "test" in query.lower() or "study" in query.lower():
        # User wants study plan/advice
        exam_details = [f"{e.exam_name} in {e.subject} on {e.exam_date.isoformat()}" for e in exams]
        hw_details = [f"'{h.title}' in {h.subject}" for h in pending_hw]
        
        reply = f"Hello {child_name}! Let's build a study plan."
        if exam_details:
            reply += f" You have upcoming exams: {', '.join(exam_details)}."
        if hw_details:
            reply += f" Remember to complete your pending homework: {', '.join(hw_details)}."
        
        reply += " Try starting with a 25-minute Pomodoro focus block today."
        
        return {
            "agent": "Education Agent",
            "reply": reply,
            "actions": {
                "recommendation": "Start Pomodoro Study Session",
                "pending_homework_count": len(pending_hw),
                "upcoming_exams_count": len(exams)
            }
        }
    
    # Default education summary
    return {
        "agent": "Education Agent",
        "reply": f"Hi {child_name}, you have {len(pending_hw)} pending homework tasks and {len(exams)} exams in the next 7 days.",
        "actions": {
            "pending_homework_count": len(pending_hw),
            "upcoming_exams_count": len(exams)
        }
    }
