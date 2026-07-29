from sqlalchemy import Column, Integer, String, Text, Date
from app.database.database import Base


class Insurance(Base):
    __tablename__ = "insurance"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(100), nullable=False, unique=True)
    provider = Column(String(100), nullable=False)
    coverage_details = Column(Text, nullable=True)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(50), default="Active", nullable=False)  # Active, Expired, Pending
