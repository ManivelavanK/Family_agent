from pydantic import BaseModel


class VoiceQueryRequest(BaseModel):
    text: str


class VoiceQueryResponse(BaseModel):
    text_response: str
    intent: str
    service_called: str
    execution_time_seconds: float
    payload: dict
