from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.exam import (
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ExamCountdownResponse,
    ExamStudyPlanResponse,
)
from app.services import exam_service

router = APIRouter(prefix="/children/exams", tags=["Exam Planner"])


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    return exam_service.create_exam(db=db, exam_in=exam)


@router.get("/{child_id}/upcoming", response_model=List[ExamResponse])
def get_upcoming(child_id: int, db: Session = Depends(get_db)):
    return exam_service.get_upcoming_exams(db=db, child_id=child_id)


@router.get("/{child_id}/countdown", response_model=List[ExamCountdownResponse])
def get_countdown(child_id: int, db: Session = Depends(get_db)):
    return exam_service.get_exams_countdown(db=db, child_id=child_id)


@router.get("/{child_id}/study-plan", response_model=List[ExamStudyPlanResponse])
def get_study_plan(child_id: int, db: Session = Depends(get_db)):
    return exam_service.generate_exam_study_plans(db=db, child_id=child_id)


@router.get("/{child_id}", response_model=List[ExamResponse])
def get_exams(child_id: int, db: Session = Depends(get_db)):
    return exam_service.get_exams_by_child_id(db=db, child_id=child_id)


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(exam_id: int, exam: ExamUpdate, db: Session = Depends(get_db)):
    db_exam = exam_service.update_exam(db=db, exam_id=exam_id, exam_in=exam)
    if not db_exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with ID {exam_id} not found",
        )
    return db_exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    success = exam_service.delete_exam(db=db, exam_id=exam_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with ID {exam_id} not found",
        )
    return None
