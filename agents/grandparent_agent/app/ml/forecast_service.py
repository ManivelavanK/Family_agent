import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.vitals import Vitals
from app.ml.predictor import predict_next_vitals, BP_MODEL_PATH, BS_MODEL_PATH
from app.schemas.forecast import VitalsForecastResponse, ForecastPoint

logger = logging.getLogger(__name__)


def generate_forecast(db: Session, days_ahead: int = 5) -> VitalsForecastResponse:
    if not (BP_MODEL_PATH.exists() and BS_MODEL_PATH.exists()):
        raise ValueError("Model not trained")

    current_count = db.query(Vitals).count()
    predictions = []
    start_date = date.today()
    
    for i in range(days_ahead):
        pred_date = start_date + timedelta(days=i+1)
        next_idx = current_count + i
        sys, sugar, is_trained = predict_next_vitals(next_idx)
            
        predictions.append(ForecastPoint(
            date=pred_date,
            predicted_blood_pressure_systolic=round(sys, 2),
            predicted_blood_sugar=round(sugar, 2)
        ))
        
    return VitalsForecastResponse(
        metric="Systolic Blood Pressure & Blood Sugar",
        predictions=predictions,
        model_trained=True
    )
