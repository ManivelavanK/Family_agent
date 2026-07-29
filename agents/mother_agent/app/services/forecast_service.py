import logging
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "models" / "consumption_model.pkl"


def forecast() -> dict:
    if not MODEL_PATH.exists():
        return {"error": "Model not trained yet. POST /api/v1/ml/train to train the model."}

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        logger.error("Failed to load model: %s", e)
        return {"error": f"Failed to load model: {e}"}

    today = datetime.now(timezone.utc)

    feature_row = {
        "day": [today.day],
        "month": [today.month],
        "weekday": [today.weekday()],
        "item_encoded": [0],
        "lag_1d": [0.0],
        "lag_7d": [0.0],
        "rolling_mean_7d": [0.0],
    }

    features = pd.DataFrame(feature_row)

    if hasattr(model, "feature_names_in_"):
        try:
            features = features[list(model.feature_names_in_)]
        except KeyError as e:
            logger.error("Forecast feature mismatch: %s", e)
            return {"error": f"Feature mismatch: {e}. Retrain the model."}

    try:
        prediction = float(model.predict(features)[0])
    except Exception as e:
        logger.error("Forecast prediction failed: %s", e)
        return {"error": f"Forecast failed: {e}"}

    daily = round(max(prediction, 0.0), 2)

    return {
        "predicted_daily_usage": daily,
        "next_7_days_prediction": round(daily * 7, 2),
    }
