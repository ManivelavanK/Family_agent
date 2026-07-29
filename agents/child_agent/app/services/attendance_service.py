import math
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, AttendanceSummaryResponse, AttendanceRiskResponse

def create_attendance(db: Session, attendance_in: AttendanceCreate) -> Attendance:
    db_attendance = Attendance(
        child_id=attendance_in.child_id,
        date=attendance_in.date,
        subject=attendance_in.subject,
        status=attendance_in.status.capitalize(),  # Normalize case
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def get_attendance_by_child_id(db: Session, child_id: int) -> List[Attendance]:
    return db.query(Attendance).filter(Attendance.child_id == child_id).order_by(Attendance.date.asc()).all()

def generate_attendance_summary(db: Session, child_id: int) -> AttendanceSummaryResponse:
    records = get_attendance_by_child_id(db, child_id)
    
    days_present = 0
    days_absent = 0
    days_on_leave = 0
    
    subject_counts: Dict[str, Dict[str, int]] = {}
    monthly_counts: Dict[str, Dict[str, int]] = {}
    
    for r in records:
        status_val = r.status.capitalize()
        
        # Total counts
        if status_val == "Present":
            days_present += 1
        elif status_val == "Absent":
            days_absent += 1
        elif status_val == "Leave":
            days_on_leave += 1
            
        # Subject-wise tracking
        if r.subject not in subject_counts:
            subject_counts[r.subject] = {"present": 0, "absent": 0}
        if status_val == "Present":
            subject_counts[r.subject]["present"] += 1
        elif status_val == "Absent":
            subject_counts[r.subject]["absent"] += 1
            
        # Monthly tracking
        month_str = r.date.strftime("%Y-%m")
        if month_str not in monthly_counts:
            monthly_counts[month_str] = {"present": 0, "absent": 0}
        if status_val == "Present":
            monthly_counts[month_str]["present"] += 1
        elif status_val == "Absent":
            monthly_counts[month_str]["absent"] += 1
            
    # Calculate overall attendance percentage (Leave is excluded from active base)
    total_active = days_present + days_absent
    overall_percentage = (days_present / total_active * 100.0) if total_active > 0 else 100.0
    
    # Calculate subject-wise percentages
    subject_pct: Dict[str, float] = {}
    for sub, counts in subject_counts.items():
        sub_active = counts["present"] + counts["absent"]
        subject_pct[sub] = round((counts["present"] / sub_active * 100.0), 1) if sub_active > 0 else 100.0
        
    # Calculate monthly percentages
    monthly_pct: Dict[str, float] = {}
    for mon, counts in monthly_counts.items():
        mon_active = counts["present"] + counts["absent"]
        monthly_pct[mon] = round((counts["present"] / mon_active * 100.0), 1) if mon_active > 0 else 100.0
        
    return AttendanceSummaryResponse(
        days_present=days_present,
        days_absent=days_absent,
        days_on_leave=days_on_leave,
        attendance_percentage=round(overall_percentage, 1),
        subject_wise_attendance=subject_pct,
        monthly_attendance=monthly_pct
    )

def evaluate_attendance_risk(db: Session, child_id: int, target_threshold: float = 75.0) -> AttendanceRiskResponse:
    summary = generate_attendance_summary(db, child_id)
    pct = summary.attendance_percentage
    
    # Determine risk level
    if pct >= 90.0:
        risk_level = "LOW"
    elif pct >= 80.0:
        risk_level = "MEDIUM"
    elif pct >= 75.0:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
        
    present = summary.days_present
    absent = summary.days_absent
    active = present + absent
    
    target_ratio = target_threshold / 100.0
    
    classes_can_miss = 0
    classes_needed_to_recover = 0
    
    if active > 0:
        if pct >= target_threshold:
            # How many consecutive classes can be missed before dropping below target
            # present / (active + M) >= target_ratio  ==> M <= present / target_ratio - active
            val = present / target_ratio - active
            classes_can_miss = max(0, math.floor(val))
        else:
            # How many consecutive present classes needed to reach target
            # (present + R) / (active + R) >= target_ratio  ==> R >= (target_ratio * active - present) / (1 - target_ratio)
            val = (target_ratio * active - present) / (1.0 - target_ratio)
            classes_needed_to_recover = max(0, math.ceil(val))
    else:
        # No attendance recorded yet
        if target_threshold > 0:
            classes_can_miss = 0
            classes_needed_to_recover = 0
            
    return AttendanceRiskResponse(
        attendance_percentage=pct,
        risk_level=risk_level,
        classes_can_miss=classes_can_miss,
        classes_needed_to_recover=classes_needed_to_recover
    )
