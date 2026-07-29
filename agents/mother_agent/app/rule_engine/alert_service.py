import logging
from sqlalchemy.orm import Session
from app.models.alert import KitchenAlert
from app.rule_engine.grocery_rules import (
    evaluate_stock_shortage,
    evaluate_expiry_warnings,
    evaluate_weekly_budget
)
from app.notification.notification_service import send_kitchen_alert_notification

logger = logging.getLogger(__name__)


def evaluate_and_log_alerts(db: Session) -> list[KitchenAlert]:
    """Runs all checks, logs them as active alerts in the database, and triggers alerts notifications."""
    logger.info("Evaluating grocery rules...")
    
    # Gather potential alerts
    shortage_alerts = evaluate_stock_shortage(db)
    expiry_alerts = evaluate_expiry_warnings(db)
    budget_alert = evaluate_weekly_budget(db)

    all_potential = []
    all_potential.extend(shortage_alerts)
    all_potential.extend(expiry_alerts)
    if budget_alert:
        all_potential.append(budget_alert)

    logged_alerts = []

    for alert_data in all_potential:
        # Avoid creating duplicate active alerts for the same item name and title
        existing = db.query(KitchenAlert).filter(
            KitchenAlert.item_name == alert_data.get("item_name"),
            KitchenAlert.title == alert_data["title"],
            KitchenAlert.status == "Active"
        ).first()

        if existing:
            # Just update existing record
            existing.description = alert_data["description"]
            existing.severity = alert_data["severity"]
            existing.recommended_action = alert_data["recommended_action"]
            db.commit()
            logged_alerts.append(existing)
        else:
            new_alert = KitchenAlert(
                item_name=alert_data.get("item_name"),
                severity=alert_data["severity"],
                title=alert_data["title"],
                description=alert_data["description"],
                recommended_action=alert_data["recommended_action"],
                status="Active"
            )
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            logged_alerts.append(new_alert)

            # Send WhatsApp notification immediately for High severity alerts
            if new_alert.severity == "High":
                try:
                    send_kitchen_alert_notification(
                        db,
                        title=new_alert.title,
                        severity=new_alert.severity,
                        description=new_alert.description,
                        action=new_alert.recommended_action
                    )
                except Exception as e:
                    logger.error("Failed to send WhatsApp alert notification: %s", e)

    return logged_alerts


def get_active_alerts(db: Session) -> list[KitchenAlert]:
    return db.query(KitchenAlert).filter(KitchenAlert.status == "Active").all()


def resolve_alert(db: Session, alert_id: int) -> bool:
    alert = db.query(KitchenAlert).filter(KitchenAlert.id == alert_id).first()
    if alert:
        alert.status = "Resolved"
        db.commit()
        return True
    return False
