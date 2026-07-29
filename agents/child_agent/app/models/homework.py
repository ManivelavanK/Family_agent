from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey
from app.database.database import Base

class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String, nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assigned_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    priority = Column(String, nullable=False, default="MEDIUM")  # HIGH, MEDIUM, LOW
    estimated_minutes = Column(Integer, nullable=True)
    actual_minutes = Column(Integer, nullable=True)
    completion_status = Column(Boolean, nullable=False, default=False)
    completion_date = Column(Date, nullable=True)

