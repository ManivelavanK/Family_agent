from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, JSON, Text, Boolean
from app.database.database import Base

class SafetyProfile(Base):
    __tablename__ = "safety_profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    trusted_contacts = Column(JSON, nullable=True)  # List of dicts (name, phone, relation)
    parent_contacts = Column(JSON, nullable=True)   # List of dicts (name, phone, relation)
    emergency_contacts = Column(JSON, nullable=True) # List of dicts (name, phone, service_type)
    pickup_person = Column(String, nullable=True)
    transport_info = Column(String, nullable=True)   # School/college transport details
    usual_locations = Column(JSON, nullable=True)   # List of strings/locations
    emergency_notes = Column(Text, nullable=True)
    escalation_threshold_minutes = Column(Integer, nullable=False, default=15)


class CheckInLog(Base):
    __tablename__ = "check_in_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    expected_return_time = Column(Time, nullable=False)
    actual_check_in_time = Column(Time, nullable=True)
    location_note = Column(String, nullable=True)
    status = Column(String, nullable=False, default="EXPECTED")  # SAFE, EXPECTED, LATE, MISSED_CHECK_IN, EMERGENCY
    parent_notified = Column(Boolean, nullable=False, default=False)


class CallResponseLog(Base):
    __tablename__ = "call_response_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    call_time = Column(Time, nullable=False)
    call_state = Column(String, nullable=False)  # CALL_ATTEMPTED, CALL_ANSWERED, CALL_MISSED, CALL_BACK_RECEIVED
    contact_name = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    notes = Column(String, nullable=True)

