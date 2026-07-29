import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/appointment", tags=["Appointment"])


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(app_in: AppointmentCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Add medical appointment")
    db_app = Appointment(
        doctor_name=app_in.doctor_name,
        specialty=app_in.specialty,
        appointment_time=app_in.appointment_time,
        location=app_in.location,
        notes=app_in.notes
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    logger.info("Database updated: Appointment logged")
    return APIResponse(
        success=True,
        message="Appointment created successfully",
        data=AppointmentResponse.model_validate(db_app)
    )


@router.get("/", response_model=APIResponse)
def list_appointments(db: Session = Depends(get_db)):
    logger.info("Request received: List appointments")
    apps = db.query(Appointment).order_by(Appointment.appointment_time.asc()).all()
    data = [AppointmentResponse.model_validate(a) for a in apps]
    return APIResponse(
        success=True,
        message="Appointments retrieved successfully",
        data=data
    )


@router.put("/{app_id}", response_model=APIResponse)
def modify_appointment(app_id: int, app_in: AppointmentCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Update appointment ID %d", app_id)
    existing = db.query(Appointment).filter(Appointment.id == app_id).first()
    if not existing:
        logger.warning("Appointment update failed: Appointment not found")
        return APIResponse(
            success=False,
            message="Appointment not found"
        )
    existing.doctor_name = app_in.doctor_name
    existing.specialty = app_in.specialty
    existing.appointment_time = app_in.appointment_time
    existing.location = app_in.location
    existing.notes = app_in.notes
    db.commit()
    db.refresh(existing)
    logger.info("Database updated: Appointment ID %d updated", app_id)
    return APIResponse(
        success=True,
        message="Appointment updated successfully",
        data=AppointmentResponse.model_validate(existing)
    )


@router.delete("/{app_id}", response_model=APIResponse)
def remove_appointment(app_id: int, db: Session = Depends(get_db)):
    logger.info("Request received: Delete appointment ID %d", app_id)
    existing = db.query(Appointment).filter(Appointment.id == app_id).first()
    if not existing:
        logger.warning("Appointment deletion failed: Appointment not found")
        return APIResponse(
            success=False,
            message="Appointment not found"
        )
    db.delete(existing)
    db.commit()
    logger.info("Database updated: Appointment ID %d deleted", app_id)
    return APIResponse(
        success=True,
        message="Appointment deleted successfully"
    )
