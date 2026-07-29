from sqlalchemy import Column, Integer, String, Date, Time, JSON, Text
from app.database.database import Base

class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    education_stage = Column(String, nullable=False)  # Classify: EARLY_CHILDHOOD, PRIMARY_SCHOOL, etc.
    class_or_year = Column(String, nullable=True)
    school_or_college = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    parent_contact = Column(String, nullable=False)
    interests = Column(JSON, nullable=True)  # Store hobbies/interests list
    career_interest = Column(String, nullable=True)
    daily_wake_time = Column(Time, nullable=True)
    daily_sleep_time = Column(Time, nullable=True)
