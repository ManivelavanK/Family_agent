import logging
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from app.database.database import SessionLocal
from app.ml.data_loader import load_consumption_data

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / "models" / "consumption_model.pkl"
ENCODER_PATH = Path(__file__).resolve().parent / "models" / "label_encoder.pkl"

FEATURE_COLS = ["day", "month", "weekday", "item_encoded", "lag_1d", "lag_7d", "rolling_mean_7d"]
MIN_RECORDS = 5


def train() -> dict:
    db = SessionLocal()
    try:
        df = load_consumption_data(db)
    finally:
        db.close()

    if len(df) < MIN_RECORDS:
        logger.warning(
            "Not enough data for training. Need %d records, got %d.", MIN_RECORDS, len(df)
        )
        return {"error": f"Not enough data. Need {MIN_RECORDS} records, have {len(df)}."}

    encoder = LabelEncoder()
    df["item_encoded"] = encoder.fit_transform(df["item_name"].str.lower())

    X = df[FEATURE_COLS]
    y = df["quantity_used"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    logger.info("Model trained. MAE on test set: %.4f", mae)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    logger.info("Model and encoder saved to %s", MODEL_PATH.parent)

    return {
        "status": "Model trained successfully",
        "training_records": len(X_train),
        "test_records": len(X_test),
        "mean_absolute_error": round(mae, 4),
        "items_in_model": list(encoder.classes_),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())
