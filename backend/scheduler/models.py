import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ScheduledTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    priority: str = "NORMAL"  # CRITICAL, HIGH, NORMAL, LOW
    status: str = "PENDING"   # PENDING, QUEUED, RUNNING, WAITING, COMPLETED, FAILED, CANCELLED, RETRYING
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_time: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 5.0  # Seconds to wait before retrying
    logs: List[str] = Field(default_factory=list)
    execution_duration: float = 0.0
