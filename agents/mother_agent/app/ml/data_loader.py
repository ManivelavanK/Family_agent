import logging
import pandas as pd
from sqlalchemy.orm import Session
from app.models.consumption import Consumption

logger = logging.getLogger(__name__)


def load_consumption_data(db: Session) -> pd.DataFrame:
    records = db.query(Consumption).all()

    if not records:
        logger.warning("No consumption records found in database.")
        return pd.DataFrame()

    raw_df = pd.DataFrame([
        {
            "item_name": r.item_name.lower().strip(),
            "consumption_date": pd.to_datetime(r.consumption_date),
            "quantity_used": float(r.quantity_used),
        }
        for r in records
    ])

    # Group by item and date to form a daily grid
    grouped = raw_df.groupby(["item_name", "consumption_date"])["quantity_used"].sum().reset_index()

    feature_dfs = []
    for item, group in grouped.groupby("item_name"):
        group = group.sort_values("consumption_date").set_index("consumption_date")
        # Reindex to full daily frequency to capture zero-consumption days correctly
        date_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq="D")
        full_group = group.reindex(date_range).fillna({"quantity_used": 0.0, "item_name": item})
        full_group["item_name"] = item
        full_group = full_group.reset_index().rename(columns={"index": "consumption_date"})

        # Feature Engineering: Date features + Lag/Rolling stats
        full_group["day"] = full_group["consumption_date"].dt.day
        full_group["month"] = full_group["consumption_date"].dt.month
        full_group["weekday"] = full_group["consumption_date"].dt.weekday
        full_group["lag_1d"] = full_group["quantity_used"].shift(1).fillna(0.0)
        full_group["lag_7d"] = full_group["quantity_used"].shift(7).fillna(0.0)
        full_group["rolling_mean_7d"] = full_group["quantity_used"].shift(1).rolling(window=7, min_periods=1).mean().fillna(0.0)

        feature_dfs.append(full_group)

    if not feature_dfs:
        return pd.DataFrame()

    df = pd.concat(feature_dfs, ignore_index=True)
    return df
