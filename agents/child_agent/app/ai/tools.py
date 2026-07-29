from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.subject import Subject
from app.models.assignment import Assignment
from app.models.study_session import StudySession
from app.models.goal import Goal
from app.models.exam import Exam
from app.models.progress import Progress
from app.models.notification import Notification
from app.models.memory import StudentMemory

# Tool implementations for database reading/writing

def get_student_profile(db: Session, student_id: int = 1):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {}
    return {
        "id": student.id,
        "name": student.name,
        "grade": student.grade,
        "learning_style": student.learning_style,
        "interests": student.interests,
        "career_interest": student.career_interest,
        "weekly_target_hours": student.weekly_target_hours,
        "age": student.age,
        "education_level": student.education_level,
        "institution": student.institution,
        "year_of_study": student.year_of_study,
        "profile_metadata": student.profile_metadata or {}
    }

def get_subjects(db: Session, student_id: int = 1):
    subjects = db.query(Subject).filter(Subject.student_id == student_id).all()
    return [{
        "id": s.id,
        "name": s.name,
        "target_hours_per_week": s.target_hours_per_week,
        "current_grade": s.current_grade,
        "color": s.color
    } for s in subjects]

def get_assignments(db: Session, student_id: int = 1):
    assignments = db.query(Assignment).filter(Assignment.student_id == student_id).all()
    return [{
        "id": a.id,
        "subject_id": a.subject_id,
        "title": a.title,
        "due_date": a.due_date.isoformat() if isinstance(a.due_date, (date, datetime)) else a.due_date,
        "priority": a.priority,
        "description": a.description,
        "status": a.status,
        "actual_minutes_spent": a.actual_minutes_spent
    } for a in assignments]

def get_goals(db: Session, student_id: int = 1):
    goals = db.query(Goal).filter(Goal.student_id == student_id).all()
    return [{
        "id": g.id,
        "title": g.title,
        "target_date": g.target_date.isoformat() if isinstance(g.target_date, (date, datetime)) else g.target_date,
        "description": g.description,
        "status": g.status,
        "strategy": g.strategy,
        "progress_percentage": g.progress_percentage
    } for g in goals]

def get_exams(db: Session, student_id: int = 1):
    exams = db.query(Exam).filter(Exam.student_id == student_id).all()
    return [{
        "id": e.id,
        "subject_id": e.subject_id,
        "exam_date": e.exam_date.isoformat() if isinstance(e.exam_date, (date, datetime)) else e.exam_date,
        "topic": e.topic,
        "target_score": e.target_score,
        "actual_score": e.actual_score,
        "readiness_score": e.readiness_score,
        "risk_level": e.risk_level,
        "study_plan": e.study_plan
    } for e in exams]

def get_study_sessions(db: Session, student_id: int = 1):
    sessions = db.query(StudySession).filter(StudySession.student_id == student_id).all()
    return [{
        "id": s.id,
        "subject_id": s.subject_id,
        "topic": s.topic,
        "start_time": s.start_time.isoformat(),
        "end_time": s.end_time.isoformat(),
        "duration_minutes": s.duration_minutes,
        "focus_score": s.focus_score,
        "notes": s.notes
    } for s in sessions]

def get_progress(db: Session, student_id: int = 1):
    progress_entries = db.query(Progress).filter(Progress.student_id == student_id).order_by(Progress.date.desc()).all()
    return [{
        "id": p.id,
        "date": p.date.isoformat() if isinstance(p.date, (date, datetime)) else p.date,
        "study_hours": p.study_hours,
        "completed_assignments": p.completed_assignments,
        "goals_completed": p.goals_completed,
        "consistency_score": p.consistency_score,
        "performance_trend": p.performance_trend
    } for p in progress_entries]

def get_notifications(db: Session, student_id: int = 1):
    notifs = db.query(Notification).filter(Notification.student_id == student_id).order_by(Notification.created_at.desc()).all()
    return [{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "read_status": n.read_status,
        "created_at": n.created_at.isoformat()
    } for n in notifs]

def get_memory(db: Session, student_id: int = 1):
    memories = db.query(StudentMemory).filter(StudentMemory.student_id == student_id).all()
    return [{
        "id": m.id,
        "memory_type": m.memory_type,
        "content": m.content,
        "created_at": m.created_at.isoformat()
    } for m in memories]

def create_assignment(db: Session, student_id: int, subject_id: int, title: str, due_date: date, priority: str = "Medium", description: str = "") -> dict:
    new_assign = Assignment(
        student_id=student_id,
        subject_id=subject_id,
        title=title,
        due_date=due_date,
        priority=priority,
        description=description,
        status="Pending",
        actual_minutes_spent=0
    )
    db.add(new_assign)
    db.commit()
    db.refresh(new_assign)
    return {"status": "success", "id": new_assign.id, "title": new_assign.title}

def record_study_session(db: Session, student_id: int, subject_id: int, topic: str, start_time: datetime, end_time: datetime, focus_score: int = 100, notes: str = "") -> dict:
    duration = int((end_time - start_time).total_seconds() / 60)
    session = StudySession(
        student_id=student_id,
        subject_id=subject_id,
        topic=topic,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration,
        focus_score=focus_score,
        notes=notes
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Auto-update progress log
    today = start_time.date()
    prog = db.query(Progress).filter(Progress.student_id == student_id, Progress.date == today).first()
    if not prog:
        prog = Progress(student_id=student_id, date=today, study_hours=0.0, completed_assignments=0, goals_completed=0, consistency_score=80)
        db.add(prog)
    prog.study_hours += (duration / 60.0)
    db.commit()
    
    return {"status": "success", "id": session.id, "duration_minutes": duration}

def create_goal(db: Session, student_id: int, title: str, target_date: date, description: str = "", strategy: str = "") -> dict:
    goal = Goal(
        student_id=student_id,
        title=title,
        target_date=target_date,
        description=description,
        status="In Progress",
        strategy=strategy,
        progress_percentage=0
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"status": "success", "id": goal.id, "title": goal.title}
