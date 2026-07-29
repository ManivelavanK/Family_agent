import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.response import APIResponse
from app.rule_engine.alert_service import evaluate_rules_and_generate_alerts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/rules", tags=["Rule Engine"])


@router.get("/check", response_model=APIResponse)
def check_health_rules(db: Session = Depends(get_db)):
    """
    Evaluates all rules based on latest stored logs and returns a list of active alerts.
    """
    logger.info("Request received: Check health rules")
    alerts = evaluate_rules_and_generate_alerts(db)
    return APIResponse(
        success=True,
        message="Rules checked successfully",
        data=alerts
    )
