import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.profile import Profile
from app.models.emergency import EmergencyIncident
from app.schemas.emergency import SOSRequest, EmergencyIncidentResponse
from app.schemas.response import APIResponse
from app.services.notification_service import send_notification
from app.communication.service import send_to_mother, send_to_father, send_to_children
from app.communication.models import AgentEventPayload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/emergency", tags=["Emergency"])


@router.post("/sos", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(sos_in: SOSRequest, db: Session = Depends(get_db)):
    logger.info("Request received: Stateful Emergency SOS Triggered")
    
    profile = db.query(Profile).first()
    if not profile or not profile.emergency_contact_name or not profile.emergency_contact_phone:
        logger.warning("SOS Failed: No emergency contact profile configured in the database")
        return APIResponse(
            success=False,
            message="No emergency contact configured."
        )

    phone = profile.emergency_contact_phone.strip()
    if not phone or len(phone) < 5:
        logger.warning("SOS Failed: Emergency phone number configuration is invalid")
        return APIResponse(
            success=False,
            message="No emergency contact configured."
        )

    current_time = datetime.now(timezone.utc)

    # 1. Create and store incident
    incident = EmergencyIncident(
        time=current_time,
        reason=sos_in.reason or "Manual emergency button pressed",
        severity=sos_in.severity or "Critical",
        status="Active",
        family_notified=True,
        notes=sos_in.notes
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    logger.info("Database updated: Emergency Incident ID %d created", incident.id)

    # 2. Local console notification
    alert_title = "CRITICAL EMERGENCY ALERT"
    alert_body = f"SOS Triggered by {profile.name}. Reason: {incident.reason}. Contact: {profile.emergency_contact_phone}"
    send_notification(alert_title, alert_body, "Emergency")
    
    # 3. Notify external family agents
    logger.info("Scheduler/Communication: Notifying external peer family agents...")
    event_payload = AgentEventPayload(
        event="CRITICAL EMERGENCY ALERT",
        severity=incident.severity,
        message=alert_body
    )
    try:
        send_to_mother(event_payload)
        send_to_father(event_payload)
        send_to_children(event_payload)
    except Exception as e:
        logger.error("Failed to notify peer agents: %s", str(e))

    # Format return payload
    data = EmergencyIncidentResponse.model_validate(incident)

    return APIResponse(
        success=True,
        message="Alert Sent",
        data=data.model_dump()
    )


@router.get("/history", response_model=APIResponse)
def read_emergency_history(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieves history of all logged emergency incidents.
    """
    logger.info("Request received: Get emergency history logs")
    incidents = db.query(EmergencyIncident).order_by(EmergencyIncident.time.desc()).limit(limit).all()
    data = [EmergencyIncidentResponse.model_validate(inc).model_dump() for inc in incidents]
    return APIResponse(
        success=True,
        message="Emergency history retrieved successfully",
        data=data
    )


@router.get("/{incident_id}", response_model=APIResponse)
def read_emergency_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the details of a specific emergency incident by integer ID.
    """
    logger.info("Request received: Get emergency incident ID %d", incident_id)
    incident = db.query(EmergencyIncident).filter(EmergencyIncident.id == incident_id).first()
    if not incident:
        logger.warning("Emergency Incident read failed: ID %d not found", incident_id)
        return APIResponse(
            success=False,
            message="Incident not found"
        )
    data = EmergencyIncidentResponse.model_validate(incident)
    return APIResponse(
        success=True,
        message="Incident retrieved successfully",
        data=data.model_dump()
    )
