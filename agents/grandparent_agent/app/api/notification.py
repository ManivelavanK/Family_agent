import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.response import APIResponse
from app.schemas.notification import WhatsAppSendRequest, WhatsAppTestRequest, AgentNotificationRequest
from app.notification.whatsapp_service import send_message
from app.notification.templates import render_template
from app import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/notification", tags=["WhatsApp Notifications"])


@router.post("/send", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def send_notification_endpoint(req: WhatsAppSendRequest):
    """
    Manually triggers template-based WhatsApp notifications.
    """
    logger.info("Request received: Send template WhatsApp notification to: %s", req.phone)
    text = render_template(req.type, req.variables)
    result = send_message(req.phone, text)
    
    success = result.get("status") in ["Delivered", "Mock Delivered"]
    status_label = result.get("status", "Failed")
    msg_summary = "WhatsApp message sent successfully" if status_label == "Delivered" else "WhatsApp mock message simulated"
    if not success:
        msg_summary = f"WhatsApp dispatch failed: {result.get('reason', 'Unknown reason')}"

    return APIResponse(
        success=success,
        message=msg_summary,
        data=result
    )


@router.post("/test", response_model=APIResponse)
def test_notification_endpoint(req: WhatsAppTestRequest):
    """
    Verification testing route. Sends a simple configuration checkup test message.
    """
    logger.info("Request received: Send test WhatsApp to: %s", req.phone)
    test_message = "Hello! This is a verification message from your KinNest Grandparent Agent."
    result = send_message(req.phone, test_message)
    
    success = result.get("status") in ["Delivered", "Mock Delivered"]
    status_label = result.get("status", "Failed")
    msg_summary = "WhatsApp message sent successfully" if status_label == "Delivered" else "WhatsApp mock message simulated"
    if not success:
        msg_summary = f"WhatsApp test dispatch failed: {result.get('reason', 'Unknown reason')}"

    return APIResponse(
        success=success,
        message=msg_summary,
        data=result
    )


@router.post("/agent", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def receive_agent_notification(req: AgentNotificationRequest):
    """
    Multi-Agent Bus Endpoint. Receives alert events from other Family Agents
    and automatically forwards them to configured family members.
    """
    logger.info("Request received: Agent notification from %s: %s", req.source_agent, req.event)
    
    forward_text = f"[{req.source_agent} Agent Notification]\nEvent: {req.event}\nMessage: {req.message}"
    result = send_message(config.DEFAULT_FAMILY_PHONE, forward_text)
    
    return APIResponse(
        success=result.get("status") in ["Delivered", "Mock Delivered"],
        message="WhatsApp notification forwarded from external agent.",
        data=result
    )
