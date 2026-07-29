import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List
from app.models.growth import GrowthRecord

def predict_next_weight(growth_records: List[GrowthRecord]) -> dict:
    if len(growth_records) < 2:
        raise ValueError("Insufficient historical data. At least 2 growth records are required for ML prediction.")

    # Sort records chronologically
    records_sorted = sorted(growth_records, key=lambda r: r.record_date)
    first_date = records_sorted[0].record_date

    # Prepare features: X = days elapsed since the first record, y = weight in kg
    X = []
    y = []
    for r in records_sorted:
        days = (r.record_date - first_date).days
        X.append([days])
        y.append(r.weight_kg)

    X_arr = np.array(X)
    y_arr = np.array(y)

    # Train linear regression model
    model = LinearRegression()
    model.fit(X_arr, y_arr)

    # Predict 30 days after the most recent record date
    latest_days = X_arr[-1][0]
    target_day = latest_days + 30
    predicted_val = model.predict(np.array([[target_day]]))[0]

    # Enforce non-negative weight prediction
    predicted_weight = max(0.0, float(predicted_val))

    # Determine trend based on regression slope
    slope = float(model.coef_[0])
    if slope > 0.005:
        trend = "upward"
    elif slope < -0.005:
        trend = "downward"
    else:
        trend = "stable"

    return {
        "current_weight": float(records_sorted[-1].weight_kg),
        "predicted_weight": round(predicted_weight, 2),
        "growth_trend": trend
    }
