import logging
import html
from sqlalchemy.orm import Session
from app.models.price import ProductPrice
from app.services.ai_service import generate_price_recommendation

logger = logging.getLogger(__name__)


def add_price(db: Session, item_name: str, store_name: str, price: float) -> ProductPrice:
    """Upsert a price record for an item at a store."""
    existing = (
        db.query(ProductPrice)
        .filter(
            ProductPrice.item_name == item_name.strip(),
            ProductPrice.store_name == store_name.strip(),
        )
        .first()
    )

    if existing:
        existing.price = price
    else:
        existing = ProductPrice(
            item_name=item_name.strip(),
            store_name=store_name.strip(),
            price=price,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing


def analyze_prices(db: Session, items: list[str]) -> dict:
    # Strip and sanitize item names
    clean_items = [i.strip() for i in items if i.strip()]

    if not clean_items:
        return {"message": "No items provided for price comparison."}

    prices = (
        db.query(ProductPrice)
        .filter(ProductPrice.item_name.in_(clean_items))
        .order_by(ProductPrice.item_name, ProductPrice.price)
        .all()
    )

    if not prices:
        return {"message": "No price data available for the requested items."}

    price_data = [
        {
            "item": html.escape(p.item_name),
            "store": html.escape(p.store_name),
            "price": p.price,
        }
        for p in prices
    ]

    prompt = f"""You are a smart grocery price assistant.

Analyze these product prices:
{price_data}

Provide:
1. Cheapest store for each item
2. Total savings possible
3. Buying recommendation

Return only plain text."""

    try:
        recommendation = generate_price_recommendation(prompt)
    except Exception as e:
        logger.error("Price recommendation AI call failed: %s", e)
        recommendation = "Unable to generate AI recommendation at this time."

    return {
        "price_comparison": price_data,
        "recommendation": recommendation,
    }
