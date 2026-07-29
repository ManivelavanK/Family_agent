import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.exam import Exam
from app.models.profile import ChildProfile
from app.schemas.exam import ExamCreate, ExamUpdate, ExamCountdownResponse, ExamStudyPlanResponse
from app.services.age_adaptation_service import classify_age_group

# --- Exam CRUD ---

def create_exam(db: Session, exam_in: ExamCreate) -> Exam:
    db_exam = Exam(
        child_id=exam_in.child_id,
        subject=exam_in.subject,
        exam_name=exam_in.exam_name,
        exam_date=exam_in.exam_date,
        syllabus=exam_in.syllabus,
        preparation_percentage=exam_in.preparation_percentage,
        difficulty=exam_in.difficulty,
        notes=exam_in.notes,
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def get_exam_by_id(db: Session, exam_id: int) -> Optional[Exam]:
    return db.query(Exam).filter(Exam.id == exam_id).first()

def get_exams_by_child_id(db: Session, child_id: int) -> List[Exam]:
    return db.query(Exam).filter(Exam.child_id == child_id).order_by(Exam.exam_date.asc()).all()

def update_exam(db: Session, exam_id: int, exam_in: ExamUpdate) -> Optional[Exam]:
    db_exam = get_exam_by_id(db, exam_id)
    if not db_exam:
        return None
    
    update_data = exam_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exam, field, value)
        
    db.commit()
    db.refresh(db_exam)
    return db_exam

def delete_exam(db: Session, exam_id: int) -> bool:
    db_exam = get_exam_by_id(db, exam_id)
    if not db_exam:
        return False
    db.delete(db_exam)
    db.commit()
    return True


# --- Specialized Exam Operations ---

def get_upcoming_exams(db: Session, child_id: int) -> List[Exam]:
    today = datetime.date.today()
    return db.query(Exam).filter(
        Exam.child_id == child_id,
        Exam.exam_date >= today
    ).order_by(Exam.exam_date.asc()).all()

def calculate_priority(days_remaining: int, difficulty: str, prep_percentage: int) -> str:
    if days_remaining <= 7 or (difficulty.lower() == "hard" and prep_percentage < 50):
        return "HIGH"
    elif days_remaining <= 21:
        return "MEDIUM"
    else:
        return "LOW"

def get_exams_countdown(db: Session, child_id: int) -> List[ExamCountdownResponse]:
    exams = get_exams_by_child_id(db, child_id)
    today = datetime.date.today()
    
    countdown_list = []
    for e in exams:
        days_remaining = (e.exam_date - today).days
        priority = calculate_priority(days_remaining, e.difficulty, e.preparation_percentage)
        
        countdown_list.append(
            ExamCountdownResponse(
                id=e.id,
                subject=e.subject,
                exam_name=e.exam_name,
                exam_date=e.exam_date,
                days_remaining=days_remaining,
                preparation_percentage=e.preparation_percentage,
                syllabus_completion=e.preparation_percentage,  # equivalent to prep %
                priority=priority
            )
        )
    return countdown_list

def generate_exam_study_plans(db: Session, child_id: int) -> List[ExamStudyPlanResponse]:
    child_profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child_profile:
        return []
    
    age_group = classify_age_group(child_profile.age)
    is_college = (age_group == "COLLEGE")
    
    upcoming_exams = get_upcoming_exams(db, child_id)
    today = datetime.date.today()
    
    plans = []
    for e in upcoming_exams:
        days_remaining = (e.exam_date - today).days
        if days_remaining < 0:
            days_remaining = 0
            
        # Parse syllabus topics
        topics = [t.strip() for t in e.syllabus.split(",") if t.strip()] if e.syllabus else ["General Syllabus Concepts"]
        
        # Calculate daily study hours based on difficulty & current preparation
        multiplier = 1.5 if e.difficulty.lower() == "hard" else (1.2 if e.difficulty.lower() == "medium" else 0.8)
        prep_factor = (100 - e.preparation_percentage) / 100.0
        
        daily_hours = round(prep_factor * 3.0 * multiplier, 1)
        daily_hours = max(0.5, min(daily_hours, 6.0))  # keep within realistic boundaries (0.5h to 6h)
        
        plan_steps = []
        plan_steps.append(f"Target Exam Date: {e.exam_date} ({days_remaining} days remaining).")
        plan_steps.append(f"Difficulty Level: {e.difficulty} | Current Preparation: {e.preparation_percentage}%.")
        
        if days_remaining > 0:
            plan_steps.append(f"Action: Study approximately {daily_hours} hours per day focusing on the following topics: {', '.join(topics)}.")
            
            if is_college:
                plan_steps.extend([
                    "Recommendation (College): Schedule 2-hour self-directed study blocks without social media distractions.",
                    "Recommendation (College): Practice with Previous Year Papers (PYPs) to understand exam structure.",
                    "Recommendation (College): Summarize lecture slides, academic readings, and write down formulas or lab concepts.",
                    "Recommendation (College): Form or participate in course study groups to test concept understanding."
                ])
            else:
                plan_steps.extend([
                    "Recommendation (School): Follow a daily revision timetable corresponding to school subjects.",
                    "Recommendation (School): Work through textbook chapter reviews and complete homework questions.",
                    "Recommendation (School): Request a parent check-in or practice quiz session to build confidence.",
                    "Recommendation (School): Create colorful flashcards to memorize definitions and core facts."
                ])
        else:
            plan_steps.append("Action: The exam is today or has passed! Conduct a final review of core summaries.")
            
        plans.append(
            ExamStudyPlanResponse(
                exam_name=e.exam_name,
                subject=e.subject,
                days_remaining=days_remaining,
                difficulty=e.difficulty,
                current_preparation=e.preparation_percentage,
                recommended_daily_study_hours=daily_hours,
                preparation_plan=plan_steps
            )
        )
        
    return plans
