import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.grocery_item import GroceryItem
from app.models.consumption import Consumption
from app.services.ai_service import generate_recommendation

logger = logging.getLogger(__name__)


def analyze_item(db: Session, item_name: str) -> dict | None:
    inventory = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == item_name.lower())
        .first()
    )

    if inventory is None:
        return None

    average_usage = (
        db.query(func.avg(Consumption.quantity_used))
        .filter(func.lower(Consumption.item_name) == item_name.lower())
        .scalar()
    ) or 0.0

    remaining_days = round(inventory.quantity / average_usage, 2) if average_usage > 0 else 999.0

    if remaining_days <= 2:
        recommendation = "Buy immediately — stock will run out within 2 days."
    elif remaining_days <= 5:
        try:
            recommendation = generate_recommendation({
                "item_name": inventory.name,
                "current_stock": inventory.quantity,
                "average_daily_usage": round(average_usage, 2),
                "estimated_days_remaining": remaining_days,
            })
        except Exception as e:
            logger.error("AI recommendation failed for '%s': %s", item_name, e)
            recommendation = f"Stock running low. Consider purchasing soon (approx {remaining_days} days remaining)."
    else:
        recommendation = "Stock is sufficient for the next week."

    return {
        "item_name": inventory.name,
        "current_stock": inventory.quantity,
        "average_daily_usage": round(average_usage, 2),
        "estimated_days_remaining": remaining_days,
        "recommendation": recommendation,
    }
