import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.vitals import Vitals
from app.models.activity import Activity
from app.models.nutrition import Nutrition
from app.ml.predictor import predict_health_risk

logger = logging.getLogger(__name__)


def evaluate_patient_health_risk(db: Session) -> dict:
    """
    Retrieves latest health metrics across database logs and triggers ML risk classifier.
    """
    logger.info("ML Service: Running health risk classification...")

    # 1. Fetch latest Vitals
    last_vital = db.query(Vitals).order_by(Vitals.timestamp.desc()).first()
    systolic = last_vital.blood_pressure_systolic if last_vital else 120
    sugar = last_vital.blood_sugar if last_vital else 95.0
    hr = last_vital.heart_rate if last_vital else 72

    # 2. Fetch latest Sleep duration
    last_activity = db.query(Activity).order_by(Activity.date.desc()).first()
    sleep = last_activity.sleep_hours if last_activity else 7.0

    # 3. Fetch latest daily nutrition calories and water
    last_nutrition = db.query(Nutrition).order_by(Nutrition.timestamp.desc()).first()
    if last_nutrition:
        target_date = last_nutrition.timestamp.date()
        calories = db.query(func.sum(Nutrition.calories)).filter(
            func.date(Nutrition.timestamp) == target_date
        ).scalar() or 2000.0
        water = db.query(func.sum(Nutrition.water_ml)).filter(
            func.date(Nutrition.timestamp) == target_date
        ).scalar() or 1800.0
    else:
        calories = 2000.0
        water = 1800.0

    # 4. Predict
    risk_level, confidence = predict_health_risk(
        systolic=int(systolic),
        sugar=float(sugar),
        hr=int(hr),
        sleep=float(sleep),
        calories=float(calories),
        water=float(water)
    )

    logger.info("ML Service: Evaluated risk: %s (Confidence: %.2f)", risk_level, confidence)
    return {
        "risk_level": risk_level,
        "confidence": confidence,
        "parameters_analyzed": {
            "systolic_bp": systolic,
            "blood_sugar": sugar,
            "heart_rate": hr,
            "sleep_hours": sleep,
            "calories": calories,
            "water_ml": water
        }
    }
