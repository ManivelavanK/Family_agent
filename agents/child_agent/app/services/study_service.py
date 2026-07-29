import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from app.models.study import StudyMaterial, StudySession
from app.schemas.study import StudyMaterialCreate, StudyMaterialUpdate, StudySessionCreate, StudyReportResponse

# --- Study Material CRUD ---

def create_study_material(db: Session, material_in: StudyMaterialCreate) -> StudyMaterial:
    db_material = StudyMaterial(
        child_id=material_in.child_id,
        subject=material_in.subject,
        title=material_in.title,
        material_type=material_in.material_type,
        file_link_reference=material_in.file_link_reference,
        chapter=material_in.chapter,
        topic=material_in.topic,
        difficulty=material_in.difficulty,
        exam=material_in.exam,
        status=material_in.status,
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def get_material_by_id(db: Session, material_id: int) -> Optional[StudyMaterial]:
    return db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()

def get_materials_by_child_id(db: Session, child_id: int) -> List[StudyMaterial]:
    return db.query(StudyMaterial).filter(StudyMaterial.child_id == child_id).all()

def update_study_material(db: Session, material_id: int, material_in: StudyMaterialUpdate) -> Optional[StudyMaterial]:
    db_material = get_material_by_id(db, material_id)
    if not db_material:
        return None
    
    update_data = material_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_material, field, value)
        
    db.commit()
    db.refresh(db_material)
    return db_material

def delete_study_material(db: Session, material_id: int) -> bool:
    db_material = get_material_by_id(db, material_id)
    if not db_material:
        return False
    db.delete(db_material)
    db.commit()
    return True


# --- Study Session Tracking & Reporting ---

def create_study_session(db: Session, session_in: StudySessionCreate) -> StudySession:
    # Auto-calculate duration in minutes
    duration = int((session_in.end_time - session_in.start_time).total_seconds() / 60)
    if duration < 0:
        duration = 0
        
    db_session = StudySession(
        child_id=session_in.child_id,
        subject=session_in.subject,
        topic=session_in.topic,
        start_time=session_in.start_time,
        end_time=session_in.end_time,
        duration_minutes=duration,
        focus_score=session_in.focus_score,
        notes=session_in.notes,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_sessions_by_child_id(db: Session, child_id: int) -> List[StudySession]:
    return db.query(StudySession).filter(StudySession.child_id == child_id).order_by(StudySession.start_time.desc()).all()

def generate_study_report(db: Session, child_id: int) -> StudyReportResponse:
    sessions = db.query(StudySession).filter(StudySession.child_id == child_id).all()
    
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    seven_days_ago = today_start - datetime.timedelta(days=6)
    
    daily_study = 0
    weekly_study = 0
    subject_times: Dict[str, int] = {}
    focus_scores = []
    unique_session_days = set()
    
    for s in sessions:
        # Subject-wise study time (all sessions)
        subject_times[s.subject] = subject_times.get(s.subject, 0) + s.duration_minutes
        
        # Focus score (all sessions)
        focus_scores.append(s.focus_score)
        
        # Daily study time (started today)
        if today_start <= s.start_time <= today_end:
            daily_study += s.duration_minutes
            
        # Weekly study time & unique session days (within past 7 days)
        if s.start_time >= seven_days_ago:
            weekly_study += s.duration_minutes
            unique_session_days.add(s.start_time.date())
            
    # Calculate Consistency Percentage
    consistency = (len(unique_session_days) / 7.0) * 100.0
    
    # Calculate Average Focus Score
    avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 0.0
    
    # Determine most and least studied subjects
    most_studied = None
    least_studied = None
    if subject_times:
        most_studied = max(subject_times, key=subject_times.get)
        least_studied = min(subject_times, key=subject_times.get)
        
    # Study Balance Analyzer
    recommendations = []
    if subject_times and len(subject_times) > 1:
        max_subject = max(subject_times, key=subject_times.get)
        max_time = subject_times[max_subject]
        
        if max_time > 0:
            for sub, time_mins in subject_times.items():
                # If subject is studied less than 30% of the most-studied subject, recommend attention
                if time_mins < (0.3 * max_time):
                    recommendations.append(
                        f"Study imbalance detected: You spent {max_time} minutes on '{max_subject}' "
                        f"but only {time_mins} minutes on '{sub}'. Consider dedicating more focus to '{sub}'."
                    )
                    
    # Fallback recommendations if only 1 subject studied
    elif len(subject_times) == 1:
        single_sub = list(subject_times.keys())[0]
        recommendations.append(
            f"You have only studied one subject ('{single_sub}') so far. "
            "Try adding other subjects to your daily or weekly routine to maintain a balanced curriculum."
        )
    else:
        recommendations.append("No study sessions logged yet. Start tracking study sessions to receive balance recommendations.")
        
    return StudyReportResponse(
        child_id=child_id,
        daily_study_time_minutes=daily_study,
        weekly_study_time_minutes=weekly_study,
        subject_wise_study_time_minutes=subject_times,
        most_studied_subject=most_studied,
        least_studied_subject=least_studied,
        study_consistency_percentage=round(consistency, 1),
        average_focus_score=round(avg_focus, 1),
        balance_recommendations=recommendations
    )
