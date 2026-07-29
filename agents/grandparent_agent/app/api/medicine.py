import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.medicine import MedicineCreate, MedicineResponse, MedicineUpdate
from app.schemas.response import APIResponse
from app.services.medicine_service import (
    add_medicine,
    get_medicines,
    update_medicine,
    take_dose,
    delete_medicine,
    get_medication_intelligence,
    get_low_stock_refills
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/medicine", tags=["Medicine"])


@router.get("/intelligence", response_model=APIResponse)
def check_medicine_intelligence(db: Session = Depends(get_db)):
    """
    Computes upcoming doses, remaining levels, refill status, missed doses, and warnings.
    """
    logger.info("Request received: Check medication intelligence parameters")
    reports = get_medication_intelligence(db)
    return APIResponse(
        success=True,
        message="Medication intelligence reports compiled successfully",
        data=reports
    )


@router.get("/refill", response_model=APIResponse)
def list_medicine_refills(db: Session = Depends(get_db)):
    """
    Retrieves a list of active medicines requiring a refill (remaining tablets <= 5).
    """
    logger.info("Request received: List low-stock medicines requiring refill")
    refills = get_low_stock_refills(db)
    return APIResponse(
        success=True,
        message="Medicines requiring refill retrieved successfully",
        data=refills
    )


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(med_in: MedicineCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Add medicine")
    med = add_medicine(db, med_in)
    logger.info("Database updated: Medicine entry added")
    return APIResponse(
        success=True,
        message="Medicine added successfully",
        data=MedicineResponse.model_validate(med)
    )


@router.get("/", response_model=APIResponse)
def list_medicines(active_only: bool = True, db: Session = Depends(get_db)):
    logger.info("Request received: List medicines")
    meds = get_medicines(db, active_only)
    data = [MedicineResponse.model_validate(m) for m in meds]
    return APIResponse(
        success=True,
        message="Medicines retrieved successfully",
        data=data
    )


@router.put("/{med_id}/update", response_model=APIResponse)
def modify_medicine(med_id: int, update_data: MedicineUpdate, db: Session = Depends(get_db)):
    logger.info("Request received: Update medicine ID %d", med_id)
    try:
        med = update_medicine(db, med_id, update_data)
        logger.info("Database updated: Medicine ID %d modified", med_id)
        return APIResponse(
            success=True,
            message="Medicine updated successfully",
            data=MedicineResponse.model_validate(med)
        )
    except ValueError as e:
        logger.warning("Medicine update failed: %s", str(e))
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.post("/{med_name}/take", response_model=APIResponse)
def record_dose(med_name: str, db: Session = Depends(get_db)):
    logger.info("Request received: Take medicine '%s'", med_name)
    try:
        med = take_dose(db, med_name)
        logger.info("Database updated: Medicine '%s' dose recorded", med_name)
        return APIResponse(
            success=True,
            message="Dose recorded successfully",
            data=MedicineResponse.model_validate(med)
        )
    except ValueError as e:
        logger.warning("Dose record failed: %s", str(e))
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.delete("/{med_id}", response_model=APIResponse)
def remove_medicine(med_id: int, db: Session = Depends(get_db)):
    logger.info("Request received: Delete medicine ID %d", med_id)
    success = delete_medicine(db, med_id)
    if not success:
        logger.warning("Medicine deletion failed: Medicine not found")
        return APIResponse(
            success=False,
            message="Medicine not found."
        )
    logger.info("Database updated: Medicine ID %d deleted", med_id)
    return APIResponse(
        success=True,
        message="Medicine deleted successfully"
    )
