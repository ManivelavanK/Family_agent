from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AgentMessageType(str, Enum):
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    RESPONSE_APPROVAL = "RESPONSE_APPROVAL"
    NOTIFY_EVENT = "NOTIFY_EVENT"
    QUERY_STATE = "QUERY_STATE"
    STATE_RESPONSE = "STATE_RESPONSE"


class AgentUrgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InterAgentMessage(BaseModel):
    protocol: str = Field(default="KinNest-Agent-v1", description="Protocol version identifier")
    message_id: str = Field(..., description="Unique message UUID")
    sender_agent: str = Field(..., description="Identifier of the sending agent (e.g., mother_agent)")
    target_agent: str = Field(..., description="Identifier of the recipient agent or coordinator")
    message_type: AgentMessageType = Field(..., description="Type of inter-agent action/query")
    urgency: AgentUrgency = Field(default=AgentUrgency.MEDIUM, description="Urgency level for action queuing")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured message payload")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Relevant contextual state metadata")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of message creation")


class InterAgentResponse(BaseModel):
    success: bool
    responding_agent: str
    reply_to_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
