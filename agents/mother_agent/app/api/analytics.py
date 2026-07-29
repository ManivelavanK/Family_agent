from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.consumption import Consumption
from app.models.expiry import ExpiryItem

router = APIRouter(prefix="/api/v1/analytics", tags=["Grocery Analytics"])


@router.get("/consumption")
def get_consumption_analytics(db: Session = Depends(get_db)):
    """Computes total consumption metrics grouped by item name."""
    rows = (
        db.query(
            Consumption.item_name,
            func.sum(Consumption.quantity_used).label("total_quantity"),
            func.count(Consumption.id).label("usages_count")
        )
        .group_by(Consumption.item_name)
        .all()
    )

    return [
        {
            "item_name": r.item_name,
            "total_quantity": float(r.total_quantity or 0.0),
            "usages_count": int(r.usages_count or 0)
        }
        for r in rows
    ]


@router.get("/waste")
def get_waste_analytics(db: Session = Depends(get_db)):
    """Summarizes waste metrics based on expired items count."""
    expired_count = db.query(ExpiryItem).count()
    return {
        "waste_rate_percentage": 12.5,  # Mock calculation
        "total_expired_items_count": expired_count,
        "prevented_waste_actions_logged": 5
    }
