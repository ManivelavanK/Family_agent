import logging
import html
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.consumption import Consumption
from app.services.memory_service import save_memory

logger = logging.getLogger(__name__)


def generate_consumption_memory(db: Session, item_name: str) -> str | None:
    records = (
        db.query(Consumption)
        .filter(func.lower(Consumption.item_name) == item_name.lower())
        .order_by(Consumption.consumption_date.asc())
        .all()
    )

    if not records:
        return None

    total_quantity = sum(r.quantity_used for r in records)
    unit = records[0].unit

    if len(records) == 1:
        daily_usage = total_quantity
    else:
        total_days = (records[-1].consumption_date - records[0].consumption_date).days
        total_days = max(total_days, 1)
        daily_usage = total_quantity / total_days

    weekly_usage = daily_usage * 7
    monthly_usage = daily_usage * 30

    safe_name = html.escape(item_name)
    memory = (
        f"Daily consumption: {round(daily_usage, 2)} {unit}/day | "
        f"Weekly: {round(weekly_usage, 2)} {unit}/week | "
        f"Monthly: {round(monthly_usage, 2)} {unit}/month"
    )

    save_memory(db, "consumption_pattern", safe_name, memory)
    logger.info("Consumption memory updated for '%s'.", item_name)
    return memory
