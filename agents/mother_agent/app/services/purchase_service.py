import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.purchase import Purchase
from app.models.grocery_item import GroceryItem
from app.schemas.purchase import PurchaseCreate

logger = logging.getLogger(__name__)


def add_purchase(db: Session, purchase: PurchaseCreate) -> Purchase:
    new_purchase = Purchase(
        item_name=purchase.item_name.strip(),
        category=purchase.category,
        quantity=purchase.quantity,
        unit=purchase.unit,
        price=purchase.price,
        purchase_date=purchase.purchase_date,
    )
    db.add(new_purchase)

    # Update inventory in the same transaction
    item = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == purchase.item_name.lower())
        .first()
    )
    if item:
        item.quantity += purchase.quantity
        item.unit = purchase.unit.lower()
    else:
        db.add(GroceryItem(
            name=purchase.item_name.strip(),
            category=purchase.category,
            quantity=purchase.quantity,
            unit=purchase.unit.lower(),
        ))

    db.commit()
    db.refresh(new_purchase)
    logger.info("Purchase recorded for '%s': qty=%s.", purchase.item_name, purchase.quantity)
    return new_purchase


def get_purchase_history(db: Session) -> list[Purchase]:
    return db.query(Purchase).order_by(Purchase.purchase_date.desc()).all()
