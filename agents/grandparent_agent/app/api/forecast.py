import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.ml.train import train_models
from app.ml.forecast_service import generate_forecast
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/forecast", tags=["Forecast (ML)"])


@router.get("/", response_model=APIResponse)
def get_vitals_forecast(days: int = 5, db: Session = Depends(get_db)):
    logger.info("Request received: Generate vitals forecast")
    try:
        forecast = generate_forecast(db, days)
        logger.info("Prediction completed: Vitals forecast generated")
        return APIResponse(
            success=True,
            message="Forecast generated successfully",
            data=forecast
        )
    except ValueError as e:
        logger.warning("Forecast generation failed: %s", str(e))
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.post("/train", response_model=APIResponse)
def run_model_training():
    logger.info("Request received: Train ML forecasting models")
    result = train_models()
    if "error" in result:
        logger.warning("ML training failed: %s", result["error"])
        return APIResponse(
            success=False,
            message=result["error"]
        )
    logger.info("Model loaded/saved: Forecast models trained successfully")
    return APIResponse(
        success=True,
        message="Model trained successfully",
        data=result
    )
