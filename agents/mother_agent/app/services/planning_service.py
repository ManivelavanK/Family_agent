import logging
from sqlalchemy.orm import Session
from app.models.grocery_item import GroceryItem
from app.models.expiry import ExpiryItem
from app.services.prediction_service import predict_consumption
from app.services.ai_service import generate_planning_recommendation
from app.communication.service import send_to_father, send_to_grandparent
from app.communication.models import AgentEventPayload

logger = logging.getLogger(__name__)


def generate_weekly_plan(db: Session) -> dict:
    inventory = db.query(GroceryItem).all()
    expiry_items = db.query(ExpiryItem).all()

    expiry_risk_items = {e.item_name.lower() for e in expiry_items}
    plan = []
    total_cost_estimate = 0.0

    for item in inventory:
        prediction = predict_consumption(db, item.name)

        if "error" in prediction:
            logger.warning("Skipping '%s' in weekly plan: %s", item.name, prediction["error"])
            continue

        required_purchase = prediction.get("recommended_purchase", 0.0)
        predicted_requirement = prediction.get("next_7_days_requirement", 0.0)
        expiry_warning = item.name.lower() in expiry_risk_items

        if expiry_warning and required_purchase > 0:
            priority = "HIGH"
            action = "Purchase required and consume existing stock before expiry."
        elif required_purchase > 0:
            priority = "MEDIUM"
            action = "Purchase additional quantity based on predicted usage."
        elif expiry_warning:
            priority = "MEDIUM"
            action = "Use this item first — expiry is approaching."
        else:
            priority = "LOW"
            action = "No immediate action required."

        if required_purchase > 0:
            total_cost_estimate += required_purchase * 3.50  # Assuming mock cost of $3.50 per unit

        if required_purchase > 0 or expiry_warning:
            reasons = []
            if item.quantity < predicted_requirement:
                reasons.append("Current stock is lower than predicted weekly requirement.")
            if expiry_warning:
                reasons.append("Item expiry risk detected.")
            if required_purchase > 0:
                reasons.append("Future consumption requires additional purchase.")

            plan.append({
                "item": item.name,
                "priority": priority,
                "current_stock": item.quantity,
                "predicted_requirement": predicted_requirement,
                "recommended_purchase": round(required_purchase, 2),
                "expiry_risk": expiry_warning,
                "action": action,
                "reason": reasons,
            })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    plan.sort(key=lambda x: priority_order.get(x["priority"], 3))

    ai_summary = None
    if plan:
        high_priority = [p["item"] for p in plan if p["priority"] == "HIGH"]
        medium_priority = [p["item"] for p in plan if p["priority"] == "MEDIUM"]
        prompt = f"""You are a family grocery planning assistant.

Weekly plan summary:
- HIGH priority items (buy urgently): {high_priority}
- MEDIUM priority items (buy soon): {medium_priority}

Write a 2-3 sentence practical shopping advice for the family. Return only plain text."""
        try:
            ai_summary = generate_planning_recommendation(prompt)
        except Exception as e:
            logger.error("Planning AI summary failed: %s", e)

    # Autonomous Multi-step Orchestration & Cross-Agent Intelligence
    steps_executed = [
        "Step 1: Scanned kitchen inventory.",
        "Step 2: Predicted consumption requirements for the next 7 days.",
        "Step 3: Identified low stock items and item expiry warnings."
    ]

    # Coordinate with Father Agent if budget is high (over $100)
    father_coordination = "No extra financial coordination needed."
    if total_cost_estimate > 100.0:
        steps_executed.append("Step 4: Cost exceeds $100. Dispatched budget approval request to Father Agent.")
        payload = AgentEventPayload(
            event="Budget Approval Request",
            severity="Medium",
            message=f"Grocery shopping cost exceeds threshold. Estimate: ${total_cost_estimate:.2f}."
        )
        res = send_to_father(payload)
        father_coordination = f"Father Agent response: {res.get('status', 'Failed')}"
    else:
        steps_executed.append("Step 4: Checked budget limits. Cost is within acceptable threshold.")

    # Query Grandparent Agent for medical/dietary concerns
    steps_executed.append("Step 5: Queried Grandparent Agent for dietary restrictions/needs.")
    gp_payload = AgentEventPayload(
        event="Dietary Restrictions Check",
        severity="Low",
        message="Checking if grandparent has specific dietary requirements or food restrictions."
    )
    gp_res = send_to_grandparent(gp_payload)
    gp_coordination = f"Grandparent Agent response: {gp_res.get('status', 'Failed')}"

    return {
        "agent": "Planning Agent",
        "weekly_plan": plan,
        "ai_summary": ai_summary,
        "coordination_log": {
            "father": father_coordination,
            "grandparent": gp_coordination
        },
        "steps_executed": steps_executed
    }
