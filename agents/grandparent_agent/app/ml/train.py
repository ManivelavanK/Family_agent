import logging
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from app.database.database import SessionLocal
from app.models.vitals import Vitals

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent / "models"
BP_MODEL_PATH = MODEL_DIR / "bp_systolic_model.pkl"
BS_MODEL_PATH = MODEL_DIR / "blood_sugar_model.pkl"
RISK_MODEL_PATH = MODEL_DIR / "risk_classifier.pkl"

MIN_RECORDS = 3


def train_models() -> dict:
    """Trains regression models for vitals forecasting and a classifier for health risk."""
    db = SessionLocal()
    try:
        logs = db.query(Vitals).order_by(Vitals.timestamp).all()
    finally:
        db.close()

    regression_status = "Not trained"
    bp_coefs = []
    bs_coefs = []

    # 1. Vitals Forecasting Regression Models
    if len(logs) >= MIN_RECORDS:
        data = []
        for idx, log in enumerate(logs):
            data.append({
                "idx": idx,
                "systolic": log.blood_pressure_systolic,
                "sugar": log.blood_sugar
            })
        df = pd.DataFrame(data)

        X = df[["idx"]]
        y_systolic = df["systolic"]
        y_sugar = df["sugar"]

        bp_model = LinearRegression()
        bp_model.fit(X, y_systolic)

        bs_model = LinearRegression()
        bs_model.fit(X, y_sugar)

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(bp_model, BP_MODEL_PATH)
        joblib.dump(bs_model, BS_MODEL_PATH)
        regression_status = "Models trained successfully"
        bp_coefs = bp_model.coef_.tolist()
        bs_coefs = bs_model.coef_.tolist()
        logger.info("Vitals forecasting models trained successfully.")
    else:
        logger.warning("Not enough vitals data to train regression models. Need %d, got %d.", MIN_RECORDS, len(logs))
        regression_status = f"Regression skipped: Need at least {MIN_RECORDS} vitals logs."

    # 2. Risk Classifier Training (Random Forest)
    # Generates a synthetic training set for reliable medical checks
    logger.info("Generating synthetic medical logs for risk classifier training...")
    np.random.seed(42)
    n_samples = 150

    # Fields: systolic, sugar, heart_rate, sleep, calories, water
    # Targets: 0: Low Risk, 1: Medium Risk, 2: High Risk
    X_synth = []
    y_synth = []

    for _ in range(n_samples):
        risk = np.random.choice([0, 1, 2])
        if risk == 0:  # Low Risk
            systolic = np.random.randint(110, 130)
            sugar = np.random.randint(70, 115)
            hr = np.random.randint(60, 80)
            sleep = np.random.uniform(6.5, 8.5)
            calories = np.random.randint(1600, 2200)
            water = np.random.randint(1500, 2500)
        elif risk == 1:  # Medium Risk
            systolic = np.random.choice([np.random.randint(130, 140), np.random.randint(110, 130)])
            sugar = np.random.choice([np.random.randint(115, 140), np.random.randint(70, 115)])
            hr = np.random.choice([np.random.randint(80, 100), np.random.randint(60, 80)])
            sleep = np.random.uniform(5.0, 6.5)
            calories = np.random.randint(1400, 2400)
            water = np.random.randint(1000, 1500)
        else:  # High Risk
            systolic = np.random.choice([np.random.randint(140, 180), np.random.randint(110, 130)])
            sugar = np.random.choice([np.random.randint(180, 250), np.random.randint(70, 115)])
            hr = np.random.choice([np.random.randint(100, 130), np.random.randint(60, 80)])
            # Make sure at least one severe metric is present to justify High Risk
            if systolic < 140 and sugar < 180 and hr < 100:
                systolic = np.random.randint(141, 180)
            sleep = np.random.uniform(3.0, 5.0)
            calories = np.random.randint(1000, 3000)
            water = np.random.randint(500, 1000)

        X_synth.append([systolic, sugar, hr, sleep, calories, water])
        y_synth.append(risk)

    X_train = pd.DataFrame(X_synth, columns=["systolic", "sugar", "heart_rate", "sleep", "calories", "water"])
    y_train = pd.Series(y_synth)

    # Train Random Forest Classifier
    risk_model = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
    risk_model.fit(X_train, y_train)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(risk_model, RISK_MODEL_PATH)
    logger.info("Health risk classifier model trained successfully.")

    return {
        "regression_status": regression_status,
        "classification_status": "Model trained successfully",
        "training_records": len(X_train),
        "bp_coefficients": bp_coefs,
        "bs_coefficients": bs_coefs
    }
