import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.response import APIResponse
from app.ml.train import train_models
from app.ml.risk_service import evaluate_patient_health_risk

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ml", tags=["Machine Learning (AI/ML)"])


@router.post("/train", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def trigger_training_workflow():
    """
    Triggers model training for both Vitals forecasting (regression) and Health Risk (Random Forest Classification).
    """
    logger.info("Request received: Train ML models")
    result = train_models()
    return APIResponse(
        success=True,
        message="All models trained successfully.",
        data=result
    )


@router.get("/risk", response_model=APIResponse)
def get_health_risk_assessment(db: Session = Depends(get_db)):
    """
    Analyzes patient logs (Vitals, Activities, Nutrition) to output computed health risk and confidence score.
    """
    logger.info("Request received: Get patient health risk classification")
    result = evaluate_patient_health_risk(db)
    return APIResponse(
        success=True,
        message="Patient health risk classification compiled successfully",
        data=result
    )
