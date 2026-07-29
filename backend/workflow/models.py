from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class StepDefinition(BaseModel):
    name: str
    handler_name: str
    retryable: bool = False
    timeout_seconds: int = 30
    max_retries: int = 3

class WorkflowDefinition(BaseModel):
    name: str
    description: str = ""
    trigger_agent: str
    participants: List[str] = Field(default_factory=list)
    steps: List[StepDefinition] = Field(default_factory=list)

class WorkflowInstance(BaseModel):
    workflow_id: str
    workflow_name: str
    trigger_agent: str
    participants: List[str] = Field(default_factory=list)
    created_time: datetime = Field(default_factory=datetime.utcnow)
    updated_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = "PENDING"  # PENDING, RUNNING, WAITING, FAILED, COMPLETED, CANCELLED
    current_step_index: int = 0
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    context_payload: Dict[str, Any] = Field(default_factory=dict) # Carried throughout step transitions
    retries: Dict[str, int] = Field(default_factory=dict)         # step_name -> current retry count
    step_states: Dict[str, str] = Field(default_factory=dict)     # step_name -> SUCCESS, FAILED, WAITING
    shared_context_reference: Optional[str] = None                # References a specific category context if applicable
