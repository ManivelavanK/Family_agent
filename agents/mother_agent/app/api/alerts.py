import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.alert import KitchenAlertResponse
from app.rule_engine.alert_service import evaluate_and_log_alerts, get_active_alerts, resolve_alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/alerts", tags=["Kitchen Rules & Alerts"])


@router.post("/evaluate", response_model=list[KitchenAlertResponse])
def run_evaluation(db: Session = Depends(get_db)):
    """Runs all grocery rules evaluation check and logs any active alerts."""
    try:
        alerts = evaluate_and_log_alerts(db)
        return alerts
    except Exception as e:
        logger.exception("Manual rules evaluation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rules evaluation failed: {str(e)}"
        )


@router.get("/active", response_model=list[KitchenAlertResponse])
def get_active(db: Session = Depends(get_db)):
    """Retrieves all active alerts."""
    return get_active_alerts(db)


@router.post("/{alert_id}/resolve")
def resolve(alert_id: int, db: Session = Depends(get_db)):
    """Resolves an active alert."""
    success = resolve_alert(db, alert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found."
        )
    return {"status": "Success", "message": "Alert resolved."}
