from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from app.database.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    priority = Column(String, nullable=False, default="Medium")  # High, Medium, Low
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Pending")  # Pending, Completed, Overdue
    actual_minutes_spent = Column(Integer, nullable=True, default=0)
