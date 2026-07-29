from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime, timezone
from app.database.database import Base


class Vitals(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    blood_pressure_systolic = Column(Integer, nullable=False)
    blood_pressure_diastolic = Column(Integer, nullable=False)
    blood_sugar = Column(Float, nullable=False)  # in mg/dL
    heart_rate = Column(Integer, nullable=False)   # in bpm
    temperature = Column(Float, nullable=True)    # in Fahrenheit
