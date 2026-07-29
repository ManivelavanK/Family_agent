import logging
from fastapi import APIRouter, status
from app.schemas.response import APIResponse
from app.communication.models import AgentEventPayload
from app.communication.service import send_to_mother, send_to_father, send_to_children

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/communication", tags=["Agent Communication"])


@router.post("/mother", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def alert_mother_agent(payload: AgentEventPayload):
    logger.info("Request received: Send event alert to Mother Agent")
    status_report = send_to_mother(payload)
    return APIResponse(
        success=True,
        message="Event dispatched to Mother Agent",
        data=status_report
    )


@router.post("/father", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def alert_father_agent(payload: AgentEventPayload):
    logger.info("Request received: Send event alert to Father Agent")
    status_report = send_to_father(payload)
    return APIResponse(
        success=True,
        message="Event dispatched to Father Agent",
        data=status_report
    )


@router.post("/children", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def alert_children_agent(payload: AgentEventPayload):
    logger.info("Request received: Send event alert to Children Agent")
    status_report = send_to_children(payload)
    return APIResponse(
        success=True,
        message="Event dispatched to Children Agent",
        data=status_report
    )
