from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from datetime import datetime
from app.database.database import Base


class EducationalDocumentChunk(Base):
    __tablename__ = "educational_document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True, nullable=False)
    document_id = Column(String, index=True, nullable=False)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    family_id = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=True)
    document_type = Column(String, nullable=False)  # STUDY_NOTES, TEXTBOOK, EXAM_PREP, WORKSHEET
    privacy_level = Column(String, nullable=False, default="FAMILY_ONLY")  # PUBLIC_EDUCATIONAL, FAMILY_ONLY, CHILD_PRIVATE
    title = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=False)  # Stores vector embedding array as JSON string for cross-db compatibility
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
