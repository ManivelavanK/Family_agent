from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.safety import (
    SafetyProfileCreate,
    SafetyProfileResponse,
    ExpectedReturnCreate,
    CheckInCreate,
    CheckInResponse,
    CallResponseLogCreate,
    CallResponseLogResponse,
    SafetyAlertResponse,
)
from app.services import safety_service

router = APIRouter(tags=["Child Safety & Parent Check-in"])


@router.post("/children/safety/profile", response_model=SafetyProfileResponse, status_code=status.HTTP_201_CREATED)
def configure_safety_profile(profile: SafetyProfileCreate, db: Session = Depends(get_db)):
    return safety_service.create_or_update_profile(db=db, profile_in=profile)


@router.get("/children/safety/{child_id}/profile", response_model=SafetyProfileResponse)
def get_safety_profile(child_id: int, db: Session = Depends(get_db)):
    db_prof = safety_service.get_profile_by_child_id(db=db, child_id=child_id)
    if not db_prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Safety profile for child ID {child_id} not found",
        )
    return db_prof


@router.post("/children/safety/{child_id}/expected-return", response_model=CheckInResponse)
def schedule_expected_return(child_id: int, schedule: ExpectedReturnCreate, db: Session = Depends(get_db)):
    if schedule.child_id != child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path parameter child_id does not match payload child_id",
        )
    return safety_service.set_expected_return(db=db, expected_in=schedule)


@router.post("/children/safety/check-in", response_model=CheckInResponse)
def log_check_in(check_in: CheckInCreate, db: Session = Depends(get_db)):
    db_log = safety_service.record_check_in(db=db, check_in_in=check_in)
    if not db_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to record check-in for child ID {check_in.child_id}",
        )
    return db_log


@router.get("/children/safety/{child_id}/status", response_model=CheckInResponse)
def get_safety_status(child_id: int, current_time: Optional[str] = None, db: Session = Depends(get_db)):
    eval_t = None
    if current_time:
        try:
            eval_t = datetime.time.fromisoformat(current_time)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="current_time must be in HH:MM:SS format",
            )
    log = safety_service.evaluate_child_safety_status(db=db, child_id=child_id, current_time=eval_t)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No safety check-in log scheduled today for child ID {child_id}",
        )
    return log


@router.get("/children/safety/{child_id}/alerts", response_model=SafetyAlertResponse)
def get_safety_alerts(child_id: int, current_time: Optional[str] = None, db: Session = Depends(get_db)):
    eval_t = None
    if current_time:
        try:
            eval_t = datetime.time.fromisoformat(current_time)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="current_time must be in HH:MM:SS format",
            )
    return safety_service.generate_safety_alerts(db=db, child_id=child_id, current_time=eval_t)


@router.post("/children/safety/call-log", response_model=CallResponseLogResponse, status_code=status.HTTP_201_CREATED)
def record_call_log(log: CallResponseLogCreate, db: Session = Depends(get_db)):
    return safety_service.create_call_log(db=db, log_in=log)


@router.get("/children/safety/{child_id}/call-logs", response_model=List[CallResponseLogResponse])
def get_call_logs(child_id: int, db: Session = Depends(get_db)):
    return safety_service.get_call_logs(db=db, child_id=child_id)

