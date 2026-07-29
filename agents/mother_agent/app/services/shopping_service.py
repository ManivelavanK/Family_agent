import logging
from sqlalchemy.orm import Session
from app.models.grocery_item import GroceryItem
from app.services.prediction_service import predict_consumption

logger = logging.getLogger(__name__)


def generate_shopping_list(db: Session) -> list[dict]:
    inventory = db.query(GroceryItem).all()
    shopping_list = []

    for item in inventory:
        prediction = predict_consumption(db, item.name)

        if "error" in prediction:
            logger.warning("Skipping '%s' in shopping list: %s", item.name, prediction["error"])
            continue

        required_quantity = prediction.get("recommended_purchase", 0.0)

        if required_quantity > 0:
            shopping_list.append({
                "item": item.name,
                "unit": item.unit,
                "current_stock": item.quantity,
                "predicted_daily_usage": prediction["predicted_daily_usage"],
                "next_7_days_requirement": prediction["next_7_days_requirement"],
                "recommended_purchase": round(required_quantity, 2),
                "reason": "Based on predicted consumption for next 7 days.",
            })

    # Sort by recommended_purchase descending (most urgent first)
    shopping_list.sort(key=lambda x: x["recommended_purchase"], reverse=True)
    return shopping_list
