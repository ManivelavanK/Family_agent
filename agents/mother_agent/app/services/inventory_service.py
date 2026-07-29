import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.grocery_item import GroceryItem
from app.schemas.grocery_item import GroceryItemCreate

logger = logging.getLogger(__name__)


def add_item(db: Session, item: GroceryItemCreate) -> GroceryItem:
    existing = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == item.name.lower())
        .with_for_update()
        .first()
    )

    if existing:
        existing.quantity += item.quantity
        existing.category = item.category
        existing.unit = item.unit.lower()
    else:
        existing = GroceryItem(
            name=item.name.strip(),
            category=item.category,
            quantity=item.quantity,
            unit=item.unit.lower(),
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    logger.info("Item '%s' added/updated. New quantity: %s", existing.name, existing.quantity)
    return existing


def get_items(db: Session) -> list[dict]:
    """Return merged inventory — one row per unique item name (case-insensitive)."""
    rows = (
        db.query(
            func.min(GroceryItem.id).label("id"),
            func.lower(GroceryItem.name).label("name_lower"),
            func.min(GroceryItem.name).label("name"),
            func.min(GroceryItem.category).label("category"),
            func.sum(GroceryItem.quantity).label("quantity"),
            func.min(GroceryItem.unit).label("unit"),
        )
        .group_by(func.lower(GroceryItem.name))
        .all()
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "quantity": row.quantity,
            "unit": row.unit,
        }
        for row in rows
    ]


def update_inventory(
    db: Session,
    item_name: str,
    category: str,
    quantity: float,
    unit: str,
) -> GroceryItem:
    """
    Upsert inventory for an item. Does NOT commit — caller is responsible
    for committing the transaction.
    """
    existing = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == item_name.lower())
        .with_for_update()
        .first()
    )

    if existing:
        existing.quantity += quantity
        existing.unit = unit.lower()
    else:
        existing = GroceryItem(
            name=item_name.strip(),
            category=category,
            quantity=quantity,
            unit=unit.lower(),
        )
        db.add(existing)

    return existing
