from sqlalchemy import Column, Integer, Date, ForeignKey, Float, JSON
from app.database.database import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    study_hours = Column(Float, nullable=False, default=0.0)
    completed_assignments = Column(Integer, nullable=False, default=0)
    goals_completed = Column(Integer, nullable=False, default=0)
    consistency_score = Column(Integer, nullable=False, default=0)  # out of 100
    performance_trend = Column(JSON, nullable=True)  # custom metrics or breakdown
