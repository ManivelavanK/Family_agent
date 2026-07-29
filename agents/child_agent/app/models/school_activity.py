from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from app.database.database import Base

class SchoolActivity(Base):
    __tablename__ = "school_activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String, nullable=False) # "attendance" | "reading" | "homework" | "unit_test"
    title = Column(String, nullable=False)
    status = Column(String, nullable=True) # "Present" | "Absent" | "Completed" | "Pending"
    value = Column(Float, nullable=True) # Score, reading pages, etc.
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
