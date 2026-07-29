from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.health import (
    HealthLogCreate,
    HealthLogResponse,
    HealthReportResponse,
)
from app.services import health_service

router = APIRouter(prefix="/children/health", tags=["Child Health & Routine"])


@router.post("", response_model=HealthLogResponse, status_code=status.HTTP_201_CREATED)
def record_health_log(log: HealthLogCreate, db: Session = Depends(get_db)):
    return health_service.create_health_log(db=db, log_in=log)


@router.get("/{child_id}/report", response_model=HealthReportResponse)
def get_report(child_id: int, db: Session = Depends(get_db)):
    report = health_service.generate_health_report(db=db, child_id=child_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found to generate health report",
        )
    return report


@router.get("/{child_id}", response_model=List[HealthLogResponse])
def get_logs(child_id: int, db: Session = Depends(get_db)):
    return health_service.get_logs_by_child_id(db=db, child_id=child_id)
