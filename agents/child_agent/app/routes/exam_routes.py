from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.exam import Exam
from app.ai.llm import query_llm
from app.ai.prompts import EXAM_READINESS_SYSTEM_PROMPT
from pydantic import BaseModel
from datetime import date
from typing import Optional
import json

router = APIRouter(prefix="/api/v1/exams", tags=["Exams"])

class ExamCreate(BaseModel):
    student_id: int
    subject_id: int
    exam_date: date
    topic: str
    target_score: Optional[int] = 85
    actual_score: Optional[int] = None
    readiness_score: Optional[int] = 50
    risk_level: Optional[str] = "Medium"
    study_plan: Optional[dict] = None

class ExamUpdate(BaseModel):
    exam_date: Optional[date] = None
    topic: Optional[str] = None
    target_score: Optional[int] = None
    actual_score: Optional[int] = None
    readiness_score: Optional[int] = None
    risk_level: Optional[str] = None
    study_plan: Optional[dict] = None

@router.get("")
def get_exams(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Exam)
    if student_id:
        query = query.filter(Exam.student_id == student_id)
    return query.all()

@router.post("")
def create_exam(payload: ExamCreate, db: Session = Depends(get_db)):
    new_exam = Exam(**payload.dict())
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam

@router.post("/{exam_id}/evaluate-readiness")
def evaluate_exam_readiness(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Analyze readiness using LLM based on subject and duration logged
    user_prompt = f"Exam Topic: {exam.topic}, Date: {exam.exam_date}, Target: {exam.target_score}."
    
    res = query_llm(
        system_prompt=EXAM_READINESS_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_json=True,
        temperature=0.3
    )
    
    try:
        data = json.loads(res)
        exam.readiness_score = int(data.get("readiness_score", 65))
        exam.risk_level = data.get("risk_level", "Medium")
        exam.study_plan = data.get("study_plan", ["Review formulas", "Do mock tests", "Ask AI Tutor"])
        db.commit()
    except Exception:
        # Fallback values
        exam.readiness_score = 70
        exam.risk_level = "Medium"
        exam.study_plan = ["Complete assignments", "Review flashcards"]
        db.commit()
        
    return exam

@router.put("/{exam_id}")
def update_exam(exam_id: int, payload: ExamUpdate, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    for key, val in payload.dict(exclude_unset=True).items():
        setattr(exam, key, val)
        
    db.commit()
    db.refresh(exam)
    return exam

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    db.delete(exam)
    db.commit()
    return {"status": "success", "message": "Exam deleted"}
