from datetime import date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Contacts
class ContactInfo(BaseModel):
    name: str
    phone: str
    relation: Optional[str] = None
    service_type: Optional[str] = None  # e.g. Pediatrician, School Security, Family Doctor


# Safety Profile
class SafetyProfileBase(BaseModel):
    child_id: int
    trusted_contacts: Optional[List[ContactInfo]] = None
    parent_contacts: Optional[List[ContactInfo]] = None
    emergency_contacts: Optional[List[ContactInfo]] = None
    pickup_person: Optional[str] = None
    transport_info: Optional[str] = None  # School/college transport details
    usual_locations: Optional[List[str]] = None
    emergency_notes: Optional[str] = None
    escalation_threshold_minutes: Optional[int] = 15

class SafetyProfileCreate(SafetyProfileBase):
    pass

class SafetyProfileResponse(SafetyProfileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Expected Return Schedule
class ExpectedReturnCreate(BaseModel):
    child_id: int
    date: date
    expected_return_time: time
    location_note: Optional[str] = None


# Check-in Log
class CheckInCreate(BaseModel):
    child_id: int
    date: date
    actual_check_in_time: time
    location_note: Optional[str] = None
    status: Optional[str] = "SAFE"  # SAFE or EMERGENCY


class CheckInResponse(BaseModel):
    id: int
    child_id: int
    date: date
    expected_return_time: time
    actual_check_in_time: Optional[time] = None
    location_note: Optional[str] = None
    status: str  # SAFE, EXPECTED, LATE, MISSED_CHECK_IN, EMERGENCY
    parent_notified: bool
    model_config = ConfigDict(from_attributes=True)


# Call Response Abstraction
class CallResponseLogCreate(BaseModel):
    child_id: int
    date: date
    call_time: time
    call_state: str = Field(
        ..., 
        description="CALL_ATTEMPTED, CALL_ANSWERED, CALL_MISSED, CALL_BACK_RECEIVED"
    )
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

class CallResponseLogResponse(CallResponseLogCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Safety Alert & Escalation Response
class SafetyAlertResponse(BaseModel):
    status: str
    expected_return_time: Optional[time] = None
    minutes_late: int
    parent_notified: bool
    trusted_contacts: List[ContactInfo] = Field(default_factory=list)
    parent_contacts: List[ContactInfo] = Field(default_factory=list)
    emergency_contacts: List[ContactInfo] = Field(default_factory=list)
    pickup_person: Optional[str] = None
    transport_info: Optional[str] = None
    usual_locations: List[str] = Field(default_factory=list)
    emergency_notes: Optional[str] = None
    action_guidance: List[str] = Field(default_factory=list)
    privacy_disclaimer: str = Field(
        default="This safety system is family-controlled and privacy-conscious. It does NOT invoke automated emergency/police services or monitor exact GPS without explicit location data."
    )
    real_gps_provided: bool = False
    gps_coordinates: Optional[Dict[str, float]] = None

