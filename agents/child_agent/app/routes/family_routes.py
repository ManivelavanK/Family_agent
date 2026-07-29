from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.goal import Goal
from app.models.study_session import StudySession
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/family", tags=["Cross-Agent Family Integration Bridge"])

@router.get("/child-summary/{student_id}", response_model=Dict[str, Any])
def get_child_academic_summary(student_id: int, db: Session = Depends(get_db)):
    """
    GET /api/v1/family/child-summary/{student_id}
    Returns a child-safe summary for family integration (Father Agent / Mother Agent).
    Decoupled and safe. Contains no private chat logs.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    # Gather academic statistics
    assignments = db.query(Assignment).filter(Assignment.student_id == student_id).all()
    pending_count = len([a for a in assignments if a.status == "Pending"])
    completed_count = len([a for a in assignments if a.status == "Completed"])
    
    goals = db.query(Goal).filter(Goal.student_id == student_id).all()
    completed_goals = len([g for g in goals if g.status == "Completed"])
    total_goals = len(goals)
    
    sessions = db.query(StudySession).filter(StudySession.student_id == student_id).all()
    total_hours = sum(s.duration_minutes for s in sessions) / 60.0
    
    # Simple summary calculations
    academic_progress = f"{completed_count}/{len(assignments)} assignments completed" if assignments else "No assignments registered yet"
    goal_progress = f"{completed_goals}/{total_goals} goals completed" if total_goals else "No active goals registered"
    study_consistency = f"{total_hours:.1f} hours studied overall with average focus"
    
    deadlines = []
    for a in assignments:
        if a.status == "Pending":
            deadlines.append({
                "title": a.title,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "priority": a.priority
            })
            
    return {
        "student_name": student.name,
        "academic_progress": academic_progress,
        "goal_progress": goal_progress,
        "study_consistency": study_consistency,
        "upcoming_important_deadlines": deadlines[:3]  # Return top 3 deadlines
    }
