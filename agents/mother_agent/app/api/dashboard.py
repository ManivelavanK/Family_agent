from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.grocery_item import GroceryItem
from app.models.alert import KitchenAlert
from app.models.reflection import Reflection

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard Summary"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Consolidated state summary of the grocery management system."""
    stock_count = db.query(GroceryItem).count()
    active_alerts_count = db.query(KitchenAlert).filter(KitchenAlert.status == "Active").count()
    latest_reflections = (
        db.query(Reflection)
        .order_by(Reflection.created_at.desc())
        .limit(3)
        .all()
    )

    ref_list = [
        {"item": r.item_name, "insight": r.insight, "rec": r.recommendation}
        for r in latest_reflections
    ]

    return {
        "status": "Healthy",
        "total_tracked_items_count": stock_count,
        "active_alerts_count": active_alerts_count,
        "latest_reflections": ref_list
    }
