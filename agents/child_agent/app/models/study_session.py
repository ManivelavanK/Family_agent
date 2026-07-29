from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database.database import Base

class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    focus_score = Column(Integer, nullable=False, default=100)  # Focus rating out of 100
    notes = Column(Text, nullable=True)
