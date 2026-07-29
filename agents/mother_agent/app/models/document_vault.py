from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from app.database.database import Base


class DocumentVault(Base):
    __tablename__ = "document_vault"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(String(50), nullable=False)  # Receipt, Recipe
    title = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(Text, nullable=True)  # JSON serialized parameters
