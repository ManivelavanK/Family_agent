import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.insurance import Insurance
from app.schemas.insurance import InsuranceCreate, InsuranceResponse
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/insurance", tags=["Insurance"])


@router.post("/add", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_insurance(ins_in: InsuranceCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Add insurance policy")
    db_ins = Insurance(
        policy_number=ins_in.policy_number,
        provider=ins_in.provider,
        coverage_details=ins_in.coverage_details,
        expiry_date=ins_in.expiry_date,
        status=ins_in.status
    )
    db.add(db_ins)
    db.commit()
    db.refresh(db_ins)
    logger.info("Database updated: Insurance details logged")
    return APIResponse(
        success=True,
        message="Insurance policy added successfully",
        data=InsuranceResponse.model_validate(db_ins)
    )


@router.get("/", response_model=APIResponse)
def list_insurance_policies(db: Session = Depends(get_db)):
    logger.info("Request received: List insurance policies")
    policies = db.query(Insurance).all()
    data = [InsuranceResponse.model_validate(p) for p in policies]
    return APIResponse(
        success=True,
        message="Insurance policies retrieved successfully",
        data=data
    )


@router.put("/{ins_id}", response_model=APIResponse)
def modify_insurance(ins_id: int, ins_in: InsuranceCreate, db: Session = Depends(get_db)):
    logger.info("Request received: Update insurance ID %d", ins_id)
    existing = db.query(Insurance).filter(Insurance.id == ins_id).first()
    if not existing:
        logger.warning("Insurance update failed: Insurance ID not found")
        return APIResponse(
            success=False,
            message="Insurance policy not found"
        )
    existing.policy_number = ins_in.policy_number
    existing.provider = ins_in.provider
    existing.coverage_details = ins_in.coverage_details
    existing.expiry_date = ins_in.expiry_date
    existing.status = ins_in.status
    db.commit()
    db.refresh(existing)
    logger.info("Database updated: Insurance ID %d updated", ins_id)
    return APIResponse(
        success=True,
        message="Insurance policy updated successfully",
        data=InsuranceResponse.model_validate(existing)
    )


@router.delete("/{ins_id}", response_model=APIResponse)
def remove_insurance(ins_id: int, db: Session = Depends(get_db)):
    logger.info("Request received: Delete insurance ID %d", ins_id)
    existing = db.query(Insurance).filter(Insurance.id == ins_id).first()
    if not existing:
        logger.warning("Insurance deletion failed: Insurance ID not found")
        return APIResponse(
            success=False,
            message="Insurance policy not found"
        )
    db.delete(existing)
    db.commit()
    logger.info("Database updated: Insurance ID %d deleted", ins_id)
    return APIResponse(
        success=True,
        message="Insurance policy deleted successfully"
    )
