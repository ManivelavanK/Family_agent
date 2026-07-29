from sqlalchemy import Column, Integer, String, Date, Float, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Baby(Base):
    __tablename__ = "babies"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=True)
    birth_weight = Column(Float, nullable=True)
    blood_group = Column(String(20), nullable=True)
    allergies = Column(Text, nullable=True)
    parent_contact = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    feedings = relationship("Feeding", back_populates="baby", cascade="all, delete-orphan")
    sleep_records = relationship("SleepRecord", back_populates="baby", cascade="all, delete-orphan")
    growth_records = relationship("GrowthRecord", back_populates="baby", cascade="all, delete-orphan")
    health_records = relationship("HealthRecord", back_populates="baby", cascade="all, delete-orphan")
    vaccination_records = relationship("VaccinationRecord", back_populates="baby", cascade="all, delete-orphan")
