import logging
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models.grocery_item import GroceryItem
from app.models.expiry import ExpiryItem
from app.models.settings import HouseholdSettings
from app.services.prediction_service import predict_consumption

logger = logging.getLogger(__name__)


def evaluate_stock_shortage(db: Session) -> List[Dict[str, str]]:
    """Evaluates if stock is below the auto order threshold."""
    settings = db.query(HouseholdSettings).first()
    threshold = settings.auto_order_threshold if settings else 2.0

    items = db.query(GroceryItem).all()
    alerts = []

    for item in items:
        if item.quantity < threshold:
            alerts.append({
                "item_name": item.name,
                "severity": "Medium" if item.quantity > 0.5 else "High",
                "title": f"Low Stock: {item.name}",
                "description": f"Current stock is {item.quantity} {item.unit}, which is below the threshold of {threshold} {item.unit}.",
                "recommended_action": f"Purchase additional {item.name} to restore sufficient stock."
            })
    return alerts


def evaluate_expiry_warnings(db: Session) -> List[Dict[str, str]]:
    """Evaluates if grocery items are nearing expiry or expired."""
    from datetime import date, datetime, timezone
    today = datetime.now(timezone.utc).date()
    expiry_items = db.query(ExpiryItem).all()
    alerts = []

    for item in expiry_items:
        if item.expiry_date:
            expiry_dt = item.expiry_date
            days_remaining = (expiry_dt - today).days
            if days_remaining < 0:
                alerts.append({
                    "item_name": item.item_name,
                    "severity": "High",
                    "title": f"Expired Item: {item.item_name}",
                    "description": f"Item expired {abs(days_remaining)} days ago.",
                    "recommended_action": "Safely discard the expired item and update inventory."
                })
            elif days_remaining <= 3:
                alerts.append({
                    "item_name": item.item_name,
                    "severity": "High",
                    "title": f"Near Expiry: {item.item_name}",
                    "description": f"Item will expire in {days_remaining} days.",
                    "recommended_action": f"Consume this item first or cook a recipe incorporating it."
                })
    return alerts


def evaluate_weekly_budget(db: Session) -> Optional[Dict[str, str]]:
    """Evaluates if recommended weekly purchase total exceeds the weekly budget limit."""
    settings = db.query(HouseholdSettings).first()
    if not settings:
        return None

    budget = settings.budget_limit_weekly
    estimated_total = 0.0

    inventory = db.query(GroceryItem).all()
    for item in inventory:
        prediction = predict_consumption(db, item.name)
        if "error" not in prediction:
            req = prediction.get("recommended_purchase", 0.0)
            if req > 0:
                # Multiply by a mock base price (e.g. $3.50 per unit)
                estimated_total += req * 3.50

    if estimated_total > budget:
        return {
            "severity": "Medium",
            "title": "Budget Limit Warning",
            "description": f"Forecasted purchase costs total ${estimated_total:.2f}, exceeding the weekly limit of ${budget:.2f}.",
            "recommended_action": "Review the shopping list and defer low-priority items."
        }
    return None
