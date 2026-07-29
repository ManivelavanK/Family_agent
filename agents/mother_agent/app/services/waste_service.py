import logging
import html
from sqlalchemy.orm import Session
from app.models.expiry import ExpiryItem
from app.services.ai_service import generate_waste_recommendation

logger = logging.getLogger(__name__)


def analyze_waste(db: Session) -> dict:
    expiry_items = db.query(ExpiryItem).order_by(ExpiryItem.expiry_date.asc()).all()

    if not expiry_items:
        return {"message": "No items are close to expiry.", "waste_risk": "Low"}

    expiring_products = [
        {
            "item": html.escape(item.item_name),
            "expiry_date": str(item.expiry_date),
        }
        for item in expiry_items
    ]

    prompt = f"""You are a food waste prevention assistant.

Analyze these expiring grocery items:
{expiring_products}

Provide:
1. Waste risk level
2. Items that should be used first
3. Recipe or usage suggestions
4. Future buying advice

Keep the answer practical for a family. Return only plain text."""

    try:
        recommendation = generate_waste_recommendation(prompt)
    except Exception as e:
        logger.error("Waste analysis AI call failed: %s", e)
        recommendation = "Unable to generate AI recommendation at this time."

    return {
        "expiring_items": expiring_products,
        "waste_analysis": recommendation,
    }
