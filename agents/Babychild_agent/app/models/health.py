from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id", ondelete="CASCADE"), nullable=False, index=True)
    temperature_c = Column(Float, nullable=False)
    heart_rate = Column(Integer, nullable=True)
    symptoms = Column(Text, nullable=True)
    medicine = Column(String(200), nullable=True)
    doctor_name = Column(String(100), nullable=True)
    visit_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    baby = relationship("Baby", back_populates="health_records")
