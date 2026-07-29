import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.homework import Homework
from app.models.profile import ChildProfile
from app.schemas.homework import HomeworkCreate, HomeworkUpdate, HomeworkPlanningRecommendations
from app.services.age_adaptation_service import classify_age_group

def create_homework(db: Session, homework_in: HomeworkCreate) -> Homework:
    db_homework = Homework(
        family_id=homework_in.family_id,
        child_id=homework_in.child_id,
        subject=homework_in.subject,
        title=homework_in.title,
        description=homework_in.description,
        assigned_date=homework_in.assigned_date,
        due_date=homework_in.due_date,
        priority=homework_in.priority.upper() if homework_in.priority else "MEDIUM",
        estimated_minutes=homework_in.estimated_minutes,
        actual_minutes=homework_in.actual_minutes,
        completion_status=False,
        completion_date=None,
    )
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)
    return db_homework

def get_homework_by_id(db: Session, homework_id: int) -> Optional[Homework]:
    return db.query(Homework).filter(Homework.id == homework_id).first()

def get_homework_by_child_id(db: Session, child_id: int) -> List[Homework]:
    return db.query(Homework).filter(Homework.child_id == child_id).all()

def update_homework(db: Session, homework_id: int, homework_in: HomeworkUpdate) -> Optional[Homework]:
    db_homework = get_homework_by_id(db, homework_id)
    if not db_homework:
        return None
    
    update_data = homework_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "priority" and value is not None:
            value = value.upper()
        setattr(db_homework, field, value)
        
    db.commit()
    db.refresh(db_homework)
    return db_homework

def delete_homework(db: Session, homework_id: int) -> bool:
    db_homework = get_homework_by_id(db, homework_id)
    if not db_homework:
        return False
    db.delete(db_homework)
    db.commit()
    return True

def mark_homework_completed(db: Session, homework_id: int) -> Optional[Homework]:
    db_homework = get_homework_by_id(db, homework_id)
    if not db_homework:
        return None
    db_homework.completion_status = True
    db_homework.completion_date = datetime.date.today()
    db.commit()
    db.refresh(db_homework)
    return db_homework

def get_overdue_homework(db: Session, child_id: int) -> List[Homework]:
    today = datetime.date.today()
    return db.query(Homework).filter(
        Homework.child_id == child_id,
        Homework.completion_status == False,
        Homework.due_date < today
    ).all()

def get_due_today_homework(db: Session, child_id: int) -> List[Homework]:
    today = datetime.date.today()
    return db.query(Homework).filter(
        Homework.child_id == child_id,
        Homework.completion_status == False,
        Homework.due_date == today
    ).all()

def get_upcoming_homework(db: Session, child_id: int) -> List[Homework]:
    today = datetime.date.today()
    return db.query(Homework).filter(
        Homework.child_id == child_id,
        Homework.completion_status == False,
        Homework.due_date > today
    ).all()

def get_high_priority_homework(db: Session, child_id: int) -> List[Homework]:
    return db.query(Homework).filter(
        Homework.child_id == child_id,
        Homework.completion_status == False,
        Homework.priority == "HIGH"
    ).all()

def get_homework_planning_recommendations(db: Session, child_id: int) -> Optional[HomeworkPlanningRecommendations]:
    child_profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child_profile:
        return None
    
    age_group = classify_age_group(child_profile.age)
    
    if age_group == "COLLEGE":
        planning_style = "Assignments, Projects, Labs & Deadlines"
        tips = [
            "Break down long-term course projects into weekly milestones.",
            "Schedule dedicated lab work write-up times immediately after practical classes.",
            "Prioritize task lists by grading weights and deadline proximity.",
            "Set aside time for internship and career preparation tasks.",
            "Leverage study groups for complex engineering or scikit-learn ML coursework."
        ]
    else:
        planning_style = "Subject-Based Homework Planning"
        tips = [
            "Structure your study plan by school subjects (e.g., Mathematics first, followed by Languages).",
            "Keep daily homework sessions focused on school timetable requirements.",
            "Maintain a clear separation between daily homework and extracurricular play.",
            "Review your notebook notes daily before tackling homework exercises.",
            "Seek parent or elder guidance for complex problem sets."
        ]
        
    return HomeworkPlanningRecommendations(
        child_id=child_id,
        education_stage=child_profile.education_stage,
        planning_style=planning_style,
        tips=tips
    )
