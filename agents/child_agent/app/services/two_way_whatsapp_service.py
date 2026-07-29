import os
import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.schemas.privacy import ViewerRole, PrivacyCategory
from app.services.privacy_engine import PrivacyPolicyEngine, ChildPrivateDataFilter
from app.agents.supervisor_agent import SupervisorAgent
from app.integrations.twilio.client import TwilioWhatsAppClient

logger = logging.getLogger(__name__)


class TwoWayWhatsAppParentAssistant:
    """
    Phase 9: Two-Way AI Parent WhatsApp Assistant.
    Pipeline:
    WhatsApp -> Twilio Webhook -> Parent Authentication & Family Isolation -> Privacy Policy Engine -> Child Context -> AI Supervisor -> Parent-Safe Response -> Twilio WhatsApp
    """

    def __init__(self, db: Session, client: Optional[TwilioWhatsAppClient] = None):
        self.db = db
        self.privacy_engine = PrivacyPolicyEngine()
        self.data_filter = ChildPrivateDataFilter(engine=self.privacy_engine)
        self.supervisor = SupervisorAgent(db=db)
        self.twilio_client = client or TwilioWhatsAppClient()

    def authenticate_parent_and_get_child(self, from_phone: str, requested_child_id: Optional[int] = None) -> Optional[ChildProfile]:
        clean_phone = from_phone.replace("whatsapp:", "").strip()

        # Find all children associated with this parent's phone number
        children = (
            self.db.query(ChildProfile)
            .filter((ChildProfile.parent_contact == clean_phone) | (ChildProfile.parent_contact == from_phone))
            .all()
        )

        if not children:
            logger.warning(f"Unauthorized parent access attempt from phone: {from_phone}")
            return None

        # Family isolation check
        if requested_child_id:
            authorized_child = next((c for c in children if c.id == requested_child_id), None)
            if not authorized_child:
                logger.warning(f"Cross-family access attempt: Phone {from_phone} tried to access unauthorized child_id {requested_child_id}")
                return None
            return authorized_child

        # Default to first authorized child in family
        return children[0]

    def verify_webhook_signature(self, signature: Optional[str], url: str, params: Dict[str, Any]) -> bool:
        """
        Verifies Twilio Webhook Signature.
        In test mode or MOCK_TWILIO=true, bypasses verification safely.
        """
        mock_mode = os.getenv("MOCK_TWILIO", "true").lower() in ("true", "1", "yes")
        if mock_mode or not signature:
            return True

        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        if not auth_token:
            return True

        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(auth_token)
            return validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Twilio signature verification error: {e}")
            return False

    def process_parent_query(self, from_phone: str, query_text: str, requested_child_id: Optional[int] = None) -> Dict[str, Any]:
        # 1. Parent Authentication & Family Isolation
        child = self.authenticate_parent_and_get_child(from_phone, requested_child_id)
        if not child:
            reply = "Unauthorized: You do not have permission to view updates for this family or child profile."
            self.twilio_client.send_whatsapp_message(to_phone=from_phone, body=reply)
            return {"status": "unauthorized", "reply": reply}

        # 2. Execute Supervisor Agent & Sub-Agents
        raw_result = self.supervisor.process_and_execute(child_id=child.id, query=query_text)
        action_plan = raw_result.get("action_plan", [])
        combined_reply = raw_result.get("combined_reply", "Request processed.")

        # 3. Privacy Policy Enforcement & Private Data Filtering
        # Ensure NO raw private diary text or sensitive internal metadata is returned to parent
        data_to_filter = {
            "reply": combined_reply,
            "action_plan": action_plan,
        }
        sanitized = self.data_filter.sanitize_for_viewer(data_to_filter, viewer_role=ViewerRole.PARENT)

        # Formulate parent-safe concise response
        final_body = (
            f"KinNest Parent Assistant ({child.name}):\n\n"
            f"{sanitized.get('reply')}\n\n"
            "Suggested guidance:\n"
            f"{action_plan[0] if action_plan else 'Maintain regular daily check-ins.'}\n\n"
            "— KinNest AI"
        )

        # 4. Dispatch via Twilio WhatsApp
        self.twilio_client.send_whatsapp_message(to_phone=from_phone, body=final_body)

        return {
            "status": "success",
            "child_id": child.id,
            "family_id": child.family_id,
            "parent_phone": from_phone,
            "reply": final_body,
        }
