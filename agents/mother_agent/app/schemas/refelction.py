from pydantic import BaseModel
from datetime import datetime


class ReflectionResponse(BaseModel):

    id: int

    item_name: str

    insight: str

    recommendation: str

    created_at: datetime


    class Config:
        from_attributes = True