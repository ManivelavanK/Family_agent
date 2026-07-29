import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.models.safety import SafetyProfile, CheckInLog, CallResponseLog
from app.schemas.safety import (
    SafetyProfileCreate,
    ExpectedReturnCreate,
    CheckInCreate,
    CallResponseLogCreate,
    SafetyAlertResponse,
    ContactInfo,
)

# --- Safety Profile CRUD ---

def create_or_update_profile(db: Session, profile_in: SafetyProfileCreate) -> SafetyProfile:
    db_profile = db.query(SafetyProfile).filter(SafetyProfile.child_id == profile_in.child_id).first()
    
    # Serialize Contact lists to JSON-safe dictionaries
    trusted = [c.model_dump() for c in profile_in.trusted_contacts] if profile_in.trusted_contacts else None
    parents = [c.model_dump() for c in profile_in.parent_contacts] if profile_in.parent_contacts else None
    emergency = [c.model_dump() for c in profile_in.emergency_contacts] if profile_in.emergency_contacts else None
    escalation_mins = profile_in.escalation_threshold_minutes if profile_in.escalation_threshold_minutes is not None else 15

    if not db_profile:
        db_profile = SafetyProfile(
            child_id=profile_in.child_id,
            trusted_contacts=trusted,
            parent_contacts=parents,
            emergency_contacts=emergency,
            pickup_person=profile_in.pickup_person,
            transport_info=profile_in.transport_info,
            usual_locations=profile_in.usual_locations,
            emergency_notes=profile_in.emergency_notes,
            escalation_threshold_minutes=escalation_mins,
        )
        db.add(db_profile)
    else:
        db_profile.trusted_contacts = trusted
        db_profile.parent_contacts = parents
        db_profile.emergency_contacts = emergency
        db_profile.pickup_person = profile_in.pickup_person
        db_profile.transport_info = profile_in.transport_info
        db_profile.usual_locations = profile_in.usual_locations
        db_profile.emergency_notes = profile_in.emergency_notes
        db_profile.escalation_threshold_minutes = escalation_mins
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_profile_by_child_id(db: Session, child_id: int) -> Optional[SafetyProfile]:
    return db.query(SafetyProfile).filter(SafetyProfile.child_id == child_id).first()


# --- Expected Return and Check-In operations ---

def set_expected_return(db: Session, expected_in: ExpectedReturnCreate) -> CheckInLog:
    db_log = db.query(CheckInLog).filter(
        CheckInLog.child_id == expected_in.child_id,
        CheckInLog.date == expected_in.date
    ).first()
    
    if not db_log:
        db_log = CheckInLog(
            child_id=expected_in.child_id,
            date=expected_in.date,
            expected_return_time=expected_in.expected_return_time,
            location_note=expected_in.location_note,
            status="EXPECTED",
            parent_notified=False
        )
        db.add(db_log)
    else:
        db_log.expected_return_time = expected_in.expected_return_time
        db_log.location_note = expected_in.location_note
        if db_log.actual_check_in_time is None and db_log.status != "EMERGENCY":
            db_log.status = "EXPECTED"
            
    db.commit()
    db.refresh(db_log)
    return db_log

def record_check_in(db: Session, check_in_in: CheckInCreate) -> Optional[CheckInLog]:
    db_log = db.query(CheckInLog).filter(
        CheckInLog.child_id == check_in_in.child_id,
        CheckInLog.date == check_in_in.date
    ).first()
    
    target_status = check_in_in.status or "SAFE"

    if not db_log:
        db_log = CheckInLog(
            child_id=check_in_in.child_id,
            date=check_in_in.date,
            expected_return_time=check_in_in.actual_check_in_time,
            actual_check_in_time=check_in_in.actual_check_in_time,
            location_note=check_in_in.location_note,
            status=target_status,
            parent_notified=False
        )
        db.add(db_log)
    else:
        db_log.actual_check_in_time = check_in_in.actual_check_in_time
        db_log.status = target_status
        if check_in_in.location_note:
            db_log.location_note = check_in_in.location_note
            
    db.commit()
    db.refresh(db_log)
    return db_log


# --- Call logs abstraction ---

def create_call_log(db: Session, log_in: CallResponseLogCreate) -> CallResponseLog:
    db_log = CallResponseLog(
        child_id=log_in.child_id,
        date=log_in.date,
        call_time=log_in.call_time,
        call_state=log_in.call_state,
        contact_name=log_in.contact_name,
        contact_phone=log_in.contact_phone,
        notes=log_in.notes
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_call_logs(db: Session, child_id: int) -> List[CallResponseLog]:
    return db.query(CallResponseLog).filter(CallResponseLog.child_id == child_id).order_by(CallResponseLog.call_time.desc()).all()


# --- Safety status evaluations and escalations ---

def evaluate_child_safety_status(db: Session, child_id: int, current_time: Optional[datetime.time] = None) -> Optional[CheckInLog]:
    today = datetime.date.today()
    db_log = db.query(CheckInLog).filter(
        CheckInLog.child_id == child_id,
        CheckInLog.date == today
    ).first()
    
    if not db_log:
        return None
    
    if db_log.status == "EMERGENCY":
        db_log.parent_notified = True
        db.commit()
        return db_log

    if db_log.actual_check_in_time is not None:
        db_log.status = "SAFE"
        db.commit()
        return db_log
        
    profile = get_profile_by_child_id(db, child_id)
    escalation_mins = profile.escalation_threshold_minutes if (profile and profile.escalation_threshold_minutes) else 15

    eval_time = current_time or datetime.datetime.now().time()
    
    now_dt = datetime.datetime.combine(today, eval_time)
    expected_dt = datetime.datetime.combine(today, db_log.expected_return_time)
    
    diff_seconds = (now_dt - expected_dt).total_seconds()
    
    if diff_seconds > 0:
        minutes_late = int(diff_seconds / 60)
        if minutes_late > escalation_mins:
            db_log.status = "MISSED_CHECK_IN"
            db_log.parent_notified = True
        else:
            db_log.status = "LATE"
    else:
        db_log.status = "EXPECTED"
        
    db.commit()
    return db_log

def generate_safety_alerts(db: Session, child_id: int, current_time: Optional[datetime.time] = None) -> SafetyAlertResponse:
    today = datetime.date.today()
    
    log = evaluate_child_safety_status(db, child_id, current_time)
    profile = get_profile_by_child_id(db, child_id)
    
    trusted_contacts_list = []
    parent_contacts_list = []
    emergency_contacts_list = []
    emergency_notes_str = ""
    usual_locations_list = []
    pickup_person_str = None
    transport_info_str = None
    
    if profile:
        emergency_notes_str = profile.emergency_notes or ""
        usual_locations_list = profile.usual_locations or []
        pickup_person_str = profile.pickup_person
        transport_info_str = profile.transport_info
        
        if profile.trusted_contacts:
            trusted_contacts_list = [ContactInfo(**c) for c in profile.trusted_contacts]
        if profile.parent_contacts:
            parent_contacts_list = [ContactInfo(**c) for c in profile.parent_contacts]
        if profile.emergency_contacts:
            emergency_contacts_list = [ContactInfo(**c) for c in profile.emergency_contacts]

    if not log:
        return SafetyAlertResponse(
            status="SAFE",
            minutes_late=0,
            parent_notified=False,
            trusted_contacts=trusted_contacts_list,
            parent_contacts=parent_contacts_list,
            emergency_contacts=emergency_contacts_list,
            pickup_person=pickup_person_str,
            transport_info=transport_info_str,
            usual_locations=usual_locations_list,
            emergency_notes=emergency_notes_str,
            action_guidance=["No scheduled return for today. Child status is recorded as SAFE."]
        )
        
    status_val = log.status
    
    eval_time = current_time or datetime.datetime.now().time()
    now_dt = datetime.datetime.combine(today, eval_time)
    expected_dt = datetime.datetime.combine(today, log.expected_return_time)
    diff_seconds = (now_dt - expected_dt).total_seconds()
    minutes_late = max(0, int(diff_seconds / 60)) if diff_seconds > 0 else 0

    guidance = []
    if status_val == "SAFE":
        guidance.append("Status SAFE: Child has checked in. No immediate action required.")
    elif status_val == "EXPECTED":
        guidance.append(f"Status EXPECTED: Child expected to return by {log.expected_return_time.strftime('%H:%M')}.")
    elif status_val == "LATE":
        guidance.append("Step 1: Remind Child. Send a check-in reminder notification or place a call to the child's mobile phone.")
        guidance.append("Step 2: Monitor time. An escalation to MISSED_CHECK_IN alert will trigger if the child exceeds the safety grace window.")
    elif status_val in ("MISSED_CHECK_IN", "EMERGENCY"):
        guidance.append("Step 1: Remind child immediately via automated in-app banner, SMS, or direct call.")
        
        parent_str = ", ".join(f"{p.name} ({p.phone})" for p in parent_contacts_list) if parent_contacts_list else "Parent / Guardian contacts"
        guidance.append(f"Step 2: Notify parent contacts: {parent_str}.")
        
        trusted_str = ", ".join(f"{t.name} ({t.phone} - {t.relation or 'Trusted'})" for t in trusted_contacts_list) if trusted_contacts_list else "No trusted contacts listed"
        guidance.append(f"Step 3: Show trusted contact list for local assistance: {trusted_str}.")
        
        locs_str = ", ".join(usual_locations_list) if usual_locations_list else "None registered"
        guidance.append(f"Step 4: Emergency Action Guidance — Check usual locations: {locs_str}.")
        
        if pickup_person_str:
            guidance.append(f"Check with designated pickup person: {pickup_person_str}.")
        if transport_info_str:
            guidance.append(f"Verify school/college transport info: {transport_info_str}.")
        if emergency_contacts_list:
            em_formatted = ", ".join(f"{ec.name} ({ec.phone} - {ec.service_type or 'Emergency'})" for ec in emergency_contacts_list)
            guidance.append(f"Family-controlled emergency contact list: {em_formatted}.")
            
        guidance.append(
            "IMPORTANT: This backend system does NOT execute automatic police or 911 calls. "
            "All emergency actions remain strictly family-controlled and privacy-conscious."
        )

    return SafetyAlertResponse(
        status=status_val,
        expected_return_time=log.expected_return_time,
        minutes_late=minutes_late,
        parent_notified=log.parent_notified,
        trusted_contacts=trusted_contacts_list,
        parent_contacts=parent_contacts_list,
        emergency_contacts=emergency_contacts_list,
        pickup_person=pickup_person_str,
        transport_info=transport_info_str,
        usual_locations=usual_locations_list,
        emergency_notes=emergency_notes_str,
        action_guidance=guidance,
        real_gps_provided=False
    )

