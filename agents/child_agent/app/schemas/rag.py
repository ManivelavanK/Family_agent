from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentIngestionRequest(BaseModel):
    child_id: int
    family_id: str
    subject: str
    topic: Optional[str] = None
    document_type: str = Field("STUDY_NOTES", description="STUDY_NOTES, TEXTBOOK, EXAM_PREP, WORKSHEET")
    privacy_level: str = Field("FAMILY_ONLY", description="PUBLIC_EDUCATIONAL, FAMILY_ONLY, CHILD_PRIVATE")
    title: str
    raw_content: str


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    child_id: int
    family_id: str
    subject: str
    topic: Optional[str] = None
    document_type: str
    privacy_level: str
    chunk_index: int
    content: str
    embedding: List[float] = Field(default_factory=list)


class RAGQueryRequest(BaseModel):
    child_id: int
    family_id: str
    query: str
    subject: Optional[str] = None
    top_k: int = 3


class GroundedAnswerResponse(BaseModel):
    query: str
    answer: str
    retrieved_chunks_count: int
    source_documents: List[Dict[str, Any]]
