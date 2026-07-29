from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    target_hours_per_week = Column(Integer, nullable=False, default=2)
    current_grade = Column(String, nullable=True)
    color = Column(String, nullable=True, default="#6366F1")  # Hex code for frontend rendering
