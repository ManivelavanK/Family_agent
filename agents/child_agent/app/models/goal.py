from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from app.database.database import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    target_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="In Progress")  # In Progress, Completed, Failed
    strategy = Column(Text, nullable=True)  # AI-generated strategies
    progress_percentage = Column(Integer, nullable=False, default=0)
