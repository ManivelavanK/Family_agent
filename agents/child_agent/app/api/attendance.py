from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceRiskResponse,
)
from app.services import attendance_service

router = APIRouter(prefix="/children/attendance", tags=["Attendance Tracker"])


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def log_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    return attendance_service.create_attendance(db=db, attendance_in=attendance)


@router.get("/{child_id}/summary", response_model=AttendanceSummaryResponse)
def get_summary(child_id: int, db: Session = Depends(get_db)):
    return attendance_service.generate_attendance_summary(db=db, child_id=child_id)


@router.get("/{child_id}/risk", response_model=AttendanceRiskResponse)
def get_risk(child_id: int, db: Session = Depends(get_db)):
    return attendance_service.evaluate_attendance_risk(db=db, child_id=child_id)


@router.get("/{child_id}", response_model=List[AttendanceResponse])
def get_attendance(child_id: int, db: Session = Depends(get_db)):
    return attendance_service.get_attendance_by_child_id(db=db, child_id=child_id)
