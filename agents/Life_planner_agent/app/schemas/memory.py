import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.models.memory import MemoryType

class PlannerMemoryBase(BaseModel):
    family_id: str = Field("default_family", max_length=100)
    memory_type: MemoryType = MemoryType.PREFERENCE
    title: str = Field(..., max_length=255)
    content: str
    source_type: Optional[str] = Field("USER", max_length=100)
    source_id: Optional[int] = None
    importance: int = Field(3, ge=1, le=5)

class PlannerMemoryCreate(PlannerMemoryBase):
    pass

class PlannerMemoryUpdate(BaseModel):
    family_id: Optional[str] = Field(None, max_length=100)
    memory_type: Optional[MemoryType] = None
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    source_type: Optional[str] = Field(None, max_length=100)
    source_id: Optional[int] = None
    importance: Optional[int] = Field(None, ge=1, le=5)

class PlannerMemoryResponse(PlannerMemoryBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class AIMemoryCandidate(BaseModel):
    memory_type: MemoryType
    title: str
    content: str
    importance: int = Field(3, ge=1, le=5)
    source_type: Optional[str] = "CONVERSATION"
    source_id: Optional[int] = None

class AIMemoryExtractionResponse(BaseModel):
    should_remember: bool
    memories: List[AIMemoryCandidate] = []
    reasoning: str

    model_config = ConfigDict(from_attributes=True)
