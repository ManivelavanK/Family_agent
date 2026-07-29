import logging
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.grocery_item import GroceryItem

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "models" / "consumption_model.pkl"
ENCODER_PATH = Path(__file__).resolve().parent.parent / "ml" / "models" / "label_encoder.pkl"


def _load_model():
    """Load model and encoder from disk. Returns (None, None) if not trained yet."""
    if not MODEL_PATH.exists():
        return None, None
    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH) if ENCODER_PATH.exists() else None
        return model, encoder
    except Exception as e:
        logger.error("Failed to load model/encoder: %s", e)
        return None, None


def predict_consumption(db: Session, item_name: str) -> dict:
    model, encoder = _load_model()

    if model is None:
        return {"error": "Model not trained yet. POST /api/v1/ml/train to train the model."}

    today = datetime.now(timezone.utc)

    feature_row: dict = {
        "day": [today.day],
        "month": [today.month],
        "weekday": [today.weekday()],
        "lag_1d": [0.0],
        "lag_7d": [0.0],
        "rolling_mean_7d": [0.0],
    }

    if encoder is not None:
        try:
            encoded = int(encoder.transform([item_name.lower()])[0])
        except Exception:
            logger.warning(
                "Item '%s' not in encoder vocabulary, using -1 as unknown.", item_name
            )
            encoded = -1
        feature_row["item_encoded"] = [encoded]
    else:
        # Model was trained without item encoding — add placeholder to match feature count
        expected = len(model.feature_names_in_) if hasattr(model, "feature_names_in_") else 0
        if expected == 4:
            feature_row["item_encoded"] = [0]

    features = pd.DataFrame(feature_row)

    # Ensure column order matches training
    if hasattr(model, "feature_names_in_"):
        try:
            features = features[list(model.feature_names_in_)]
        except KeyError as e:
            logger.error("Feature mismatch for '%s': %s", item_name, e)
            return {"error": f"Feature mismatch: {e}. Retrain the model via POST /api/v1/ml/train."}

    try:
        prediction = float(model.predict(features)[0])
    except Exception as e:
        logger.error("Model prediction failed for item '%s': %s", item_name, e)
        return {"error": f"Prediction failed: {e}"}

    daily_usage = round(max(prediction, 0.0), 2)
    weekly_requirement = round(daily_usage * 7, 2)

    item = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == item_name.lower())
        .first()
    )

    current_stock = float(item.quantity) if item else 0.0
    purchase_required = round(max(weekly_requirement - current_stock, 0.0), 2)

    return {
        "item": item_name,
        "unit": item.unit if item else "",
        "predicted_daily_usage": daily_usage,
        "next_7_days_requirement": weekly_requirement,
        "current_stock": current_stock,
        "recommended_purchase": purchase_required,
    }
