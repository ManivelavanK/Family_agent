from pydantic import BaseModel
from datetime import datetime


class DocumentVaultCreate(BaseModel):
    doc_type: str
    title: str
    file_path: str
    metadata_json: str | None = None


class DocumentVaultResponse(BaseModel):
    id: int
    doc_type: str
    title: str
    file_path: str
    uploaded_at: datetime
    metadata_json: str | None

    class Config:
        from_attributes = True
