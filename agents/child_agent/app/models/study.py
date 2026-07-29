from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database.database import Base

class StudyMaterial(Base):
    __tablename__ = "study_materials"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, nullable=False)
    title = Column(String, nullable=False)
    material_type = Column(String, nullable=False)  # Notes, PDF, Video, Website, Book, etc.
    file_link_reference = Column(String, nullable=False)  # file/link/reference
    chapter = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    exam = Column(String, nullable=True)
    status = Column(String, nullable=False, default="UNREAD")  # UNREAD, IN_PROGRESS, READ


class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)

    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    focus_score = Column(Integer, nullable=False)  # focus score out of 100 or similar
    notes = Column(Text, nullable=True)
