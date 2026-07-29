from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Present, Absent, Leave
