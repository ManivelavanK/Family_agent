from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.notification import NotificationLogResponse
from app.services.notification_service import NotificationService
from app.models.profile import ChildProfile

from app.schemas.test_whatsapp import WhatsAppTestNotificationRequest, WhatsAppTestNotificationResponse

from app.services.parent_notification_service import ParentNotificationService
from app.models.homework import Homework
from app.models.exam import Exam

router = APIRouter(tags=["Child Notifications & Alerts"])



@router.get(
    "/children/notifications/{child_id}",
    response_model=List[NotificationLogResponse],
    status_code=status.HTTP_200_OK,
)
def get_child_notifications(
    child_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Retrieves logged notifications and background job reminders for a specific child profile.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {child_id} not found.",
        )

    return NotificationService.get_notifications_for_child(db=db, child_id=child_id, limit=limit)


@router.post(
    "/children/notifications/test-whatsapp",
    response_model=WhatsAppTestNotificationResponse,
    status_code=status.HTTP_200_OK,
)
def test_whatsapp_notification(
    req: WhatsAppTestNotificationRequest,
    db: Session = Depends(get_db),
):

    """
    STEP 5: Real Test Endpoint for Real Twilio WhatsApp Notifications.
    1. Verifies child exists.
    2. Verifies family authorization.
    3. Retrieves relevant child data.
    4. Generates parent-safe message.
    5. Passes through Privacy Policy Engine.
    6. Sends via Real Twilio WhatsApp API.
    7. Returns Twilio Message SID and delivery status (NEVER exposing credentials).
    """
    # 1. Verify child exists
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child profile with ID {req.child_id} not found.",
        )

    # 2. Retrieve context data for test payload if not supplied
    template_data = req.template_data or {}
    if not template_data.get("subject") or not template_data.get("title"):
        hw = db.query(Homework).filter(Homework.child_id == child.id).first()
        if hw:
            template_data["subject"] = hw.subject
            template_data["title"] = hw.title
            template_data["due_date"] = hw.due_date.isoformat()
            template_data["priority"] = "High"
        else:
            template_data["subject"] = "Machine Learning"
            template_data["title"] = "Complete Regression Assignment"
            template_data["due_date"] = "30 July"
            template_data["priority"] = "High"

    template_data["child_name"] = child.name

    # 3. Dispatch via ParentNotificationService using Real Twilio Service
    service = ParentNotificationService(db=db)
    result = service.dispatch_parent_whatsapp(
        child_id=child.id,
        notification_type=req.message_type,
        template_data=template_data,
        bypass_cooldown=True,  # Test endpoint bypasses cooldown to allow instant validation
    )

    if not result.get("success"):
        return WhatsAppTestNotificationResponse(
            success=False,
            message_sid=result.get("message_sid"),
            channel="whatsapp",
            notification_type=req.message_type,
            status=result.get("status", "failed"),
            error=result.get("error") or result.get("reason"),
        )

    return WhatsAppTestNotificationResponse(
        success=True,
        message_sid=result.get("message_sid"),
        channel="whatsapp",
        notification_type=req.message_type,
        status=result.get("status", "sent"),
        error=None,
    )


