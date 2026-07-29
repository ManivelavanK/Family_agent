from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class VaccinationRecord(Base):
    __tablename__ = "vaccination_records"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id", ondelete="CASCADE"), nullable=False, index=True)
    vaccine_name = Column(String(100), nullable=False)
    dose_number = Column(Integer, nullable=True)
    due_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False)
    hospital = Column(String(150), nullable=True)
    doctor_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    baby = relationship("Baby", back_populates="vaccination_records")
