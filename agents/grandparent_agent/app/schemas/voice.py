from pydantic import BaseModel, Field


class VoiceProcessRequest(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "Did I take my medicine today?"})


class VoiceSpeakRequest(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "Take your blood pressure medicine at 8 PM."})


class VoiceTranscribeResponse(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "Did I take my medicine today?"})
