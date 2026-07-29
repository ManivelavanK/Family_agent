from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class SupervisorRequest(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    message: str = Field(..., min_length=3, description="User's natural language request")
    execute: Optional[bool] = Field(False, description="Whether to execute approved changes")
    approved: Optional[bool] = Field(False, description="User approval flag")

class SupervisorAgentSelection(BaseModel):
    agent: str = Field(..., description="Agent name: father, mother, child, grandparent, baby")
    reason: str
    required_capabilities: List[str] = []

class SupervisorAgentResponse(BaseModel):
    agent: str
    available: bool
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    response_time_ms: Optional[float] = None

class SupervisorResponse(BaseModel):
    success: bool
    message: str
    request: SupervisorRequest
    selected_agents: List[str] = []
    agent_responses: List[SupervisorAgentResponse] = []
    available_agents: List[str] = []
    unavailable_agents: List[str] = []
    family_context: Dict[str, Any] = {}
    recommendation: Dict[str, Any] = {}
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_approval: bool = True
    next_action: str = Field("REVIEW_RECOMMENDATION", description="REVIEW_RECOMMENDATION, CONFIRM, EXECUTE")

    model_config = ConfigDict(from_attributes=True)

class AgentHealthStatus(BaseModel):
    agent: str
    url: Optional[str] = None
    available: bool
    capabilities: List[str] = []
    response_time_ms: Optional[float] = None
