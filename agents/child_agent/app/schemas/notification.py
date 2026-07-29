from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationLogBase(BaseModel):
    child_id: int
    title: str
    message: str
    notification_type: str
    channel: str = "IN_APP"
    status: str = "LOGGED"

class NotificationLogCreate(NotificationLogBase):
    pass

class NotificationLogResponse(NotificationLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
