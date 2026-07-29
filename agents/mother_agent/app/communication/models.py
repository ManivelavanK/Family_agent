from pydantic import BaseModel, Field


class AgentEventPayload(BaseModel):
    event: str = Field(...)
    severity: str = Field(...)
    message: str = Field(...)
