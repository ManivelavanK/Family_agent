from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
