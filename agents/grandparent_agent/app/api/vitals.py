import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.vitals import Vitals
from app.schemas.vitals import VitalsCreate, VitalsResponse
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/vitals", tags=["Vitals"])


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_vitals_log(vitals_in: VitalsCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Add vital signs log")
    db_vitals = Vitals(
        blood_pressure_systolic=vitals_in.blood_pressure_systolic,
        blood_pressure_diastolic=vitals_in.blood_pressure_diastolic,
        blood_sugar=vitals_in.blood_sugar,
        heart_rate=vitals_in.heart_rate,
        temperature=vitals_in.temperature,
    )
    db.add(db_vitals)
    db.commit()
    db.refresh(db_vitals)
    logger.info("Database updated: Vital signs logged")
    return APIResponse(
        success=True,
        message="Vitals logged successfully",
        data=VitalsResponse.model_validate(db_vitals)
    )


@router.get("/", response_model=APIResponse)
def list_vitals_logs(limit: int = 50, db: Session = Depends(get_db)):
    logger.info("Request received: List vital logs")
    logs = db.query(Vitals).order_by(Vitals.timestamp.desc()).limit(limit).all()
    data = [VitalsResponse.model_validate(log) for log in logs]
    return APIResponse(
        success=True,
        message="Vitals logs retrieved successfully",
        data=data
    )
