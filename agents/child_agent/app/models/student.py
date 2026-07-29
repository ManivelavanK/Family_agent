from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade = Column(String, nullable=True)
    learning_style = Column(String, nullable=True, default="Visual")
    interests = Column(JSON, nullable=True)  # List of interests/hobbies
    career_interest = Column(String, nullable=True)
    weekly_target_hours = Column(Integer, nullable=False, default=10)
    education_level = Column(String, nullable=False, default="SCHOOL")  # SCHOOL | COLLEGE | POSTGRAD
    age = Column(Integer, nullable=True)
    institution = Column(String, nullable=True)
    year_of_study = Column(String, nullable=True)
    profile_metadata = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    digital_twin = relationship("DigitalTwin", back_populates="student", uselist=False, cascade="all, delete-orphan")

