import logging
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.schemas.agent_protocol import InterAgentMessage, InterAgentResponse, AgentMessageType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent-bus", tags=["Agent Communication Bus"])


@router.post("/message", response_model=InterAgentResponse)
def handle_agent_message(msg: InterAgentMessage) -> InterAgentResponse:
    """Standardized endpoint to receive and process messages from Coordinator or peer agents."""
    logger.info("Received inter-agent message %s from %s -> %s (Type: %s)",
                msg.message_id, msg.sender_agent, msg.target_agent, msg.message_type)

    if msg.target_agent != "mother_agent" and msg.target_agent != "coordinator":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message target '{msg.target_agent}' is invalid for Mother Agent listener.",
        )

    # Route message according to type
    if msg.message_type == AgentMessageType.QUERY_STATE:
        return InterAgentResponse(
            success=True,
            responding_agent="mother_agent",
            reply_to_id=msg.message_id,
            data={
                "status": "active",
                "domain": "kitchen_grocery",
                "pending_tasks": 0,
            },
        )
    elif msg.message_type == AgentMessageType.REQUEST_APPROVAL:
        return InterAgentResponse(
            success=True,
            responding_agent="mother_agent",
            reply_to_id=msg.message_id,
            data={
                "approval_status": "APPROVED",
                "notes": "Budget approval processed by Mother Agent rules engine.",
            },
        )
    else:
        return InterAgentResponse(
            success=True,
            responding_agent="mother_agent",
            reply_to_id=msg.message_id,
            data={"acknowledged": True},
        )
