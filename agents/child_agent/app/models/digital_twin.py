from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class DigitalTwin(Base):
    __tablename__ = "digital_twins"
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), unique=True, nullable=False, index=True)
    learning_score = Column(Float, nullable=False, default=0.0)
    subject_mastery = Column(JSON, nullable=False, default={})  # e.g., {"Math": 0.85}
    exam_readiness = Column(Float, nullable=False, default=0.0)
    focus_score = Column(Float, nullable=False, default=0.0)
    knowledge_gaps = Column(JSON, nullable=False, default={})
    productivity_trend = Column(JSON, nullable=False, default={})
    learning_style = Column(String, nullable=True)
    weekly_capacity = Column(Float, nullable=False, default=0.0)
    confidence = Column(Float, nullable=False, default=0.0)
    last_computed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="digital_twin")
