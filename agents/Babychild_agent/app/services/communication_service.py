from app.communication import agent_client
from app.config import MOTHER_AGENT_URL, FATHER_AGENT_URL, GRANDPARENT_AGENT_URL, PLANNING_AGENT_URL
import logging

logger = logging.getLogger(__name__)

async def notify_mother_low_formula(family_id: int, baby_id: int) -> bool:
    payload = {
        "family_id": family_id,
        "baby_id": baby_id,
        "item_name": "Baby Formula",
        "priority": "HIGH",
        "message": "Baby formula stock is running low."
    }
    return await agent_client.send_agent_notification(MOTHER_AGENT_URL, payload)

async def notify_father_medical_expense(family_id: int, baby_id: int, expense_type: str, amount: float, description: str) -> bool:
    payload = {
        "family_id": family_id,
        "baby_id": baby_id,
        "expense_type": expense_type,
        "amount": amount,
        "description": description
    }
    return await agent_client.send_agent_notification(FATHER_AGENT_URL, payload)

async def notify_grandparent_health_update(family_id: int, baby_id: int, baby_name: str, health_status: str, message: str) -> bool:
    payload = {
        "family_id": family_id,
        "baby_id": baby_id,
        "baby_name": baby_name,
        "health_status": health_status,
        "message": message
    }
    return await agent_client.send_agent_notification(GRANDPARENT_AGENT_URL, payload)

async def notify_planning_agent(family_id: int, baby_id: int, event_type: str, title: str, event_date: str, priority: str, notes: str) -> bool:
    payload = {
        "family_id": family_id,
        "baby_id": baby_id,
        "event_type": event_type,
        "title": title,
        "date": event_date,
        "priority": priority,
        "notes": notes
    }
    return await agent_client.send_agent_notification(PLANNING_AGENT_URL, payload)
