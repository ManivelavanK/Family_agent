import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # e.g., LOW_STOCK, GRANDPARENT_EMERGENCY, BABY_VACCINE_DUE, etc.
    source_agent: str
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(default_factory=dict)

class RoutingRecord(BaseModel):
    event_id: str
    event_type: str
    source_agent: str
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    routed_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = "PENDING"  # PENDING, ROUTED, FAILED, RETRYING
    retries: int = 0
    logs: List[str] = Field(default_factory=list)
    execution_duration: float = 0.0
