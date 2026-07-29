from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.homework import (
    HomeworkCreate,
    HomeworkUpdate,
    HomeworkResponse,
    HomeworkPlanningRecommendations,
)
from app.services import homework_service

router = APIRouter(prefix="/children/homework", tags=["Education & Homework"])


@router.post("", response_model=HomeworkResponse, status_code=status.HTTP_201_CREATED)
def create_homework(homework: HomeworkCreate, db: Session = Depends(get_db)):
    return homework_service.create_homework(db=db, homework_in=homework)


@router.get("/{child_id}/overdue", response_model=List[HomeworkResponse])
def get_overdue(child_id: int, db: Session = Depends(get_db)):
    return homework_service.get_overdue_homework(db=db, child_id=child_id)


@router.get("/{child_id}/recommendations", response_model=HomeworkPlanningRecommendations)
def get_recommendations(child_id: int, db: Session = Depends(get_db)):
    recs = homework_service.get_homework_planning_recommendations(db=db, child_id=child_id)
    if not recs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found to generate recommendations",
        )
    return recs


@router.get("/{child_id}", response_model=List[HomeworkResponse])
def get_homework_by_child(child_id: int, db: Session = Depends(get_db)):
    return homework_service.get_homework_by_child_id(db=db, child_id=child_id)


@router.put("/{homework_id}", response_model=HomeworkResponse)
def update_homework(homework_id: int, homework: HomeworkUpdate, db: Session = Depends(get_db)):
    db_homework = homework_service.update_homework(db=db, homework_id=homework_id, homework_in=homework)
    if not db_homework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Homework with ID {homework_id} not found",
        )
    return db_homework


@router.delete("/{homework_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_homework(homework_id: int, db: Session = Depends(get_db)):
    success = homework_service.delete_homework(db=db, homework_id=homework_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Homework with ID {homework_id} not found",
        )
    return None


@router.patch("/{homework_id}/complete", response_model=HomeworkResponse)
def mark_completed(homework_id: int, db: Session = Depends(get_db)):
    db_homework = homework_service.mark_homework_completed(db=db, homework_id=homework_id)
    if not db_homework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Homework with ID {homework_id} not found",
        )
    return db_homework
