import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.notification import NotificationLog
from app.schemas.privacy import ViewerRole, PrivacyCategory
from app.services.privacy_engine import PrivacyPolicyEngine, ParentSummaryGenerator, ChildPrivateDataFilter
from app.integrations.twilio.service import TwilioWhatsAppService
from app.integrations.twilio.templates import render_whatsapp_template

logger = logging.getLogger(__name__)

# Cooldown window for WhatsApp parent notifications (in hours)
WHATSAPP_COOLDOWN_HOURS = 12

# In-memory opt-in/opt-out registry for parent phone numbers
OPTED_OUT_NUMBERS = set()


class ParentNotificationService:
    """
    STEP 3, 4, 7 & 9: Real Twilio Parent Notification Service.
    Pipeline:
    Child Event -> Privacy Policy Engine -> Parent-Safe Summary -> Twilio WhatsApp Service -> Database Delivery Tracking
    Supports:
    1. Homework reminder
    2. Homework overdue
    3. Exam approaching
    4. Attendance concern
    5. Excessive screen time
    6. Safety alert
    7. Study progress
    8. Positive achievement
    9. Weekly child summary
    """

    def __init__(self, db: Session, twilio_service: Optional[TwilioWhatsAppService] = None):
        self.db = db
        self.privacy_engine = PrivacyPolicyEngine()
        self.summary_generator = ParentSummaryGenerator(engine=self.privacy_engine)
        self.data_filter = ChildPrivateDataFilter(engine=self.privacy_engine)
        self.twilio_service = twilio_service or TwilioWhatsAppService()

    @staticmethod
    def set_opt_out(phone_number: str, opt_out: bool = True):
        formatted = phone_number.replace("whatsapp:", "").strip()
        if opt_out:
            OPTED_OUT_NUMBERS.add(formatted)
        else:
            OPTED_OUT_NUMBERS.discard(formatted)

    @staticmethod
    def is_opted_out(phone_number: str) -> bool:
        formatted = phone_number.replace("whatsapp:", "").strip()
        return formatted in OPTED_OUT_NUMBERS

    def is_in_whatsapp_cooldown(self, child_id: int, notification_type: str) -> bool:
        cutoff = datetime.utcnow() - timedelta(hours=WHATSAPP_COOLDOWN_HOURS)
        recent = (
            self.db.query(NotificationLog)
            .filter(
                NotificationLog.child_id == child_id,
                NotificationLog.notification_type == notification_type,
                NotificationLog.channel == "WHATSAPP",
                NotificationLog.created_at >= cutoff,
            )
            .first()
        )
        return recent is not None

    def dispatch_parent_whatsapp(
        self,
        child_id: int,
        notification_type: str,
        template_data: Dict[str, Any],
        is_safety_emergency: bool = False,
        bypass_cooldown: bool = False,
    ) -> Dict[str, Any]:
        # 1. Fetch child profile & parent contact
        child = self.db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            return {"status": "failed", "reason": f"Child profile with ID {child_id} not found."}

        parent_phone = child.parent_contact
        if not parent_phone:
            return {"status": "failed", "reason": "No parent contact phone registered for child."}

        # 2. Check Opt-In / Opt-Out Status
        if self.is_opted_out(parent_phone):
            logger.info(f"Parent phone {parent_phone} is opted-out. Skipping WhatsApp dispatch.")
            return {"status": "skipped", "reason": "Parent opted out."}

        # 3. Child Privacy Layer & Policy Engine (STEP 4)
        category_map = {
            "SAFETY_ALERT": PrivacyCategory.SAFETY_CRITICAL,
            "HOMEWORK_OVERDUE": PrivacyCategory.ACADEMIC,
            "HOMEWORK_REMINDER": PrivacyCategory.ACADEMIC,
            "EXAM_APPROACHING": PrivacyCategory.ACADEMIC,
            "STUDY_PROGRESS": PrivacyCategory.ACADEMIC,
            "ATTENDANCE_CONCERN": PrivacyCategory.ACADEMIC,
            "EXCESSIVE_SCREEN_TIME_ALERT": PrivacyCategory.SUMMARY_ONLY,
            "WELLNESS_CONCERN": PrivacyCategory.SUMMARY_ONLY,
            "WEEKLY_CHILD_SUMMARY": PrivacyCategory.SUMMARY_ONLY,
            "POSITIVE_ACHIEVEMENT": PrivacyCategory.SUMMARY_ONLY,
        }
        target_category = category_map.get(notification_type, PrivacyCategory.SUMMARY_ONLY)

        if not self.privacy_engine.can_access(ViewerRole.PARENT, target_category, is_raw_text=False, is_safety_emergency=is_safety_emergency):
            return {"status": "blocked", "reason": "Blocked by PrivacyPolicyEngine."}

        # Ensure NO raw private diary text, medical notes, or raw contacts are passed to WhatsApp
        sanitized_data = self.data_filter.sanitize_for_viewer(template_data, viewer_role=ViewerRole.PARENT, is_safety_emergency=is_safety_emergency)
        sanitized_data["child_name"] = child.name

        # 4. Duplicate & Cooldown Prevention (STEP 9 - Emergency bypasses cooldown)
        if not is_safety_emergency and not bypass_cooldown and self.is_in_whatsapp_cooldown(child_id, notification_type):
            logger.info(f"Notification '{notification_type}' for child {child_id} skipped due to 12h WhatsApp cooldown.")
            return {"status": "skipped", "reason": "12-hour cooldown active."}

        # 5. Render WhatsApp Message Template
        message_body = render_whatsapp_template(notification_type, sanitized_data)

        # 6. Execute Real Twilio WhatsApp Dispatch
        res = self.twilio_service.send_whatsapp_message(to_phone=parent_phone, body=message_body)

        message_sid = res.get("sid")
        status_val = res.get("status", "failed")
        error_msg = res.get("error")

        # Retry once if initial API network call failed
        if status_val == "failed" and not error_msg:
            logger.warning("Retrying real Twilio WhatsApp API call...")
            res = self.twilio_service.send_whatsapp_message(to_phone=parent_phone, body=message_body)
            message_sid = res.get("sid")
            status_val = res.get("status", "failed")
            error_msg = res.get("error")

        # 7. Database Delivery Tracking (STEP 7)
        now = datetime.utcnow()
        log_entry = NotificationLog(
            child_id=child_id,
            family_id=child.family_id,
            title=f"WhatsApp Alert: {notification_type.replace('_', ' ').title()}",
            message=message_body,
            notification_type=notification_type,
            channel="WHATSAPP",
            recipient=parent_phone,
            message_sid=message_sid,
            status=status_val.upper(),
            error_message=error_msg,
            created_at=now,
            delivered_at=now if status_val in ("sent", "queued", "delivered") else None,
        )
        self.db.add(log_entry)
        self.db.commit()

        return {
            "success": status_val in ("sent", "queued", "delivered"),
            "message_sid": message_sid,
            "channel": "whatsapp",
            "notification_type": notification_type,
            "status": status_val,
            "error": error_msg,
        }
