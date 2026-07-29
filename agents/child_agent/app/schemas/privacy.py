from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PrivacyCategory(str, Enum):
    PUBLIC_TO_PARENT = "PUBLIC_TO_PARENT"
    SUMMARY_ONLY = "SUMMARY_ONLY"
    CHILD_PRIVATE = "CHILD_PRIVATE"
    SAFETY_CRITICAL = "SAFETY_CRITICAL"
    MEDICAL_SENSITIVE = "MEDICAL_SENSITIVE"
    FINANCIAL = "FINANCIAL"
    ACADEMIC = "ACADEMIC"


class ViewerRole(str, Enum):
    CHILD = "CHILD"
    PARENT = "PARENT"
    FAMILY_AGENT = "FAMILY_AGENT"
    AI_SUPERVISOR = "AI_SUPERVISOR"
    MOTHER_AGENT = "MOTHER_AGENT"
    FATHER_AGENT = "FATHER_AGENT"


class VisibilityPolicy(BaseModel):
    category: PrivacyCategory
    allowed_roles: List[ViewerRole]
    allow_raw_text: bool = False
    allow_summary: bool = True
    bypass_on_safety_alert: bool = False


class ParentSummaryOutput(BaseModel):
    child_id: int
    academic_summary: Dict[str, Any]
    study_summary: Dict[str, Any]
    screen_time_summary: Dict[str, Any]
    wellness_summary: Dict[str, Any]
    financial_summary: Dict[str, Any]
    safety_summary: Dict[str, Any]
    alerts_requiring_parent: List[str]
