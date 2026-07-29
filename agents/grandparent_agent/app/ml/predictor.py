import logging
import joblib
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent / "models"
BP_MODEL_PATH = MODEL_DIR / "bp_systolic_model.pkl"
BS_MODEL_PATH = MODEL_DIR / "blood_sugar_model.pkl"
RISK_MODEL_PATH = MODEL_DIR / "risk_classifier.pkl"

RISK_LABELS = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}


def predict_next_vitals(next_index: int) -> tuple[float, float, bool]:
    """
    Returns predicted blood_pressure_systolic, blood_sugar, and whether the ML model was used.
    """
    if BP_MODEL_PATH.exists() and BS_MODEL_PATH.exists():
        try:
            bp_model = joblib.load(BP_MODEL_PATH)
            bs_model = joblib.load(BS_MODEL_PATH)
            pred_bp = bp_model.predict([[next_index]])[0]
            pred_bs = bs_model.predict([[next_index]])[0]
            return float(pred_bp), float(pred_bs), True
        except Exception as e:
            logger.error(f"Error reading ML models: {e}")

    # Baseline fallback (if not trained)
    pred_bp = 120.0 + (next_index % 5) * 0.5
    pred_bs = 95.0 + (next_index % 3) * 1.2
    return pred_bp, pred_bs, False


def predict_health_risk(
    systolic: int,
    sugar: float,
    hr: int,
    sleep: float,
    calories: float,
    water: float
) -> tuple[str, float]:
    """
    Predicts patient health risk level (Low, Medium, High Risk) and return confidence score.
    """
    if RISK_MODEL_PATH.exists():
        try:
            model = joblib.load(RISK_MODEL_PATH)
            features = [[systolic, sugar, hr, sleep, calories, water]]
            pred_class = int(model.predict(features)[0])
            confidence = float(np.max(model.predict_proba(features)[0]))
            return RISK_LABELS.get(pred_class, "Low Risk"), round(confidence, 4)
        except Exception as e:
            logger.error("Error reading ML risk model: %s. Using fallback.", e)

    # Heuristic Fallback
    logger.info("Using baseline heuristic rules for risk assessment (model not found).")
    if systolic > 140 or sugar > 180 or hr > 100:
        return "High Risk", 0.90
    if systolic > 130 or sugar > 140 or hr > 85 or sleep < 6 or water < 1500:
        return "Medium Risk", 0.75
    return "Low Risk", 0.95
