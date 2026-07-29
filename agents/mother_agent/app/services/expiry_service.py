import logging
from datetime import date
from sqlalchemy.orm import Session
from app.models.expiry import ExpiryItem
from app.schemas.expiry import ExpiryCreate

logger = logging.getLogger(__name__)


def add_expiry(db: Session, expiry: ExpiryCreate) -> ExpiryItem:
    item = ExpiryItem(
        item_name=expiry.item_name.strip(),
        expiry_date=expiry.expiry_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info("Expiry record added for '%s' on %s.", item.item_name, item.expiry_date)
    return item


def check_expiry(db: Session) -> list[dict]:
    today = date.today()
    items = db.query(ExpiryItem).order_by(ExpiryItem.expiry_date.asc()).all()

    report = []
    for item in items:
        if item.expiry_date is None:
            continue
        days = (item.expiry_date - today).days

        if days < 0:
            status = "Expired"
        elif days == 0:
            status = "Expires Today"
        elif days <= 3:
            status = f"Expires in {days} day{'s' if days != 1 else ''}"
        else:
            status = "Safe"

        report.append({
            "item": item.item_name,
            "expiry_date": str(item.expiry_date),
            "days_remaining": days,
            "status": status,
        })

    return report
