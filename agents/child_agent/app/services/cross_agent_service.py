import logging
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.attendance import Attendance
from app.models.screen_time import ScreenTimeLog
from app.models.pocket_money import ChildExpense, SavingGoal
from app.models.exam import Exam
from app.models.activity import Activity
from app.models.schedule import ScheduleItem, HolidayCalendar
from app.models.nutrition import MotherAgentBridgeEvent
from app.models.safety import CheckInLog
from app.services.notification_service import NotificationService, NotificationType

from app.schemas.cross_agent import (
    ChildSummaryResponse,
    ChildSummaryItem,
    ChildExpenseCreate,
    ChildExpenseResponse,
    ChildEducationExpenseCreate,
    ChildEducationExpenseResponse,
    FamilyEventsResponse,
    FamilyEventItem,
    ChildGroceryNeedsResponse,
    GroceryNeedItem,
    ChildCheckInCreate,
    ChildCheckInResponse,
    ChildAlertCreate,
    ChildAlertResponse,
)

logger = logging.getLogger(__name__)

def get_child_summaries_for_family(db: Session, family_id: str) -> ChildSummaryResponse:
    children = db.query(ChildProfile).filter(ChildProfile.family_id == family_id).all()
    summaries = []

    for child in children:
        # 1. Homework pending count
        pending_hw = db.query(Homework).filter(
            Homework.child_id == child.id,
            Homework.completion_status == False
        ).count()

        # 2. Attendance rate
        attendance_records = db.query(Attendance).filter(Attendance.child_id == child.id).all()
        if attendance_records:
            present_count = sum(1 for r in attendance_records if r.status.upper() in ("PRESENT", "EXCUSED"))
            attendance_rate = (present_count / len(attendance_records)) * 100.0
        else:
            attendance_rate = 100.0

        # 3. Screen time average
        screen_logs = db.query(ScreenTimeLog).filter(ScreenTimeLog.child_id == child.id).all()
        if screen_logs:
            total_minutes = sum(
                s.mobile + s.gaming + s.tv + s.social_media + s.study_screen_time + s.other
                for s in screen_logs
            )
            average_screen_time = (total_minutes / len(screen_logs)) / 60.0
        else:
            average_screen_time = 0.0

        # 4. Saving goals progress
        goals = db.query(SavingGoal).filter(SavingGoal.child_id == child.id).all()
        goals_progress = []
        for g in goals:
            pct = (g.current_saved / g.target_amount * 100.0) if g.target_amount > 0 else 100.0
            goals_progress.append({
                "title": g.title,
                "target_amount": g.target_amount,
                "current_saved": g.current_saved,
                "percentage_complete": pct,
                "target_date": g.target_date.isoformat() if g.target_date else None
            })

        summaries.append(
            ChildSummaryItem(
                child_id=child.id,
                name=child.name,
                age=child.age,
                education_stage=child.education_stage or "Unknown",
                attendance_rate=round(attendance_rate, 2),
                pending_homework_count=pending_hw,
                average_screen_time_hours=round(average_screen_time, 2),
                saving_goals_progress=goals_progress,
            )
        )

    return ChildSummaryResponse(family_id=family_id, summaries=summaries)

from fastapi import HTTPException

def create_child_expense(db: Session, expense_in: ChildExpenseCreate) -> ChildExpense:
    child = db.query(ChildProfile).filter(ChildProfile.id == expense_in.child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    if child.family_id != expense_in.family_id:
        raise HTTPException(status_code=403, detail="Child does not belong to this family")

    expense_date = expense_in.date or date.today()
    db_expense = ChildExpense(
        family_id=expense_in.family_id,
        child_id=expense_in.child_id,
        amount=expense_in.amount,
        category=expense_in.category,
        description=expense_in.description,
        date=expense_date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    # Log details safely (without external connection)
    logger.info(f"[CROSS-AGENT] Child logged expense: {db_expense.amount} under category {db_expense.category} for Child ID {db_expense.child_id}")
    return db_expense

def create_education_expense(db: Session, education_expense_in: ChildEducationExpenseCreate) -> ChildExpense:
    child = db.query(ChildProfile).filter(ChildProfile.id == education_expense_in.child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    if child.family_id != education_expense_in.family_id:
        raise HTTPException(status_code=403, detail="Child does not belong to this family")

    expense_date = education_expense_in.date or date.today()
    
    # Save directly to ChildExpense table under 'Education' category
    db_expense = ChildExpense(
        family_id=education_expense_in.family_id,
        child_id=education_expense_in.child_id,
        amount=education_expense_in.amount,
        category="Education",
        description=f"[{education_expense_in.expense_type}] {education_expense_in.description or ''}".strip(),
        date=expense_date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    # Log information for future integration (Children -> Father connection)
    logger.info(
        f"[CROSS-AGENT] Education Expense proposal created (intended for Father): Type={education_expense_in.expense_type}, "
        f"Amount={education_expense_in.amount}, Description={education_expense_in.description} for Child ID {education_expense_in.child_id}"
    )
    return db_expense

def get_family_events(db: Session, family_id: str) -> FamilyEventsResponse:
    children = db.query(ChildProfile).filter(ChildProfile.family_id == family_id).all()
    events = []

    for child in children:
        # Exams
        exams = db.query(Exam).filter(Exam.child_id == child.id).all()
        for ex in exams:
            events.append(
                FamilyEventItem(
                    child_id=child.id,
                    child_name=child.name,
                    event_type="EXAM",
                    title=f"Exam: {ex.exam_name} ({ex.subject})",
                    date=ex.exam_date,
                    description=f"Subject: {ex.subject}"
                )
            )

        # Activities
        activities = db.query(Activity).filter(Activity.child_id == child.id).all()
        for act in activities:
            events.append(
                FamilyEventItem(
                    child_id=child.id,
                    child_name=child.name,
                    event_type="ACTIVITY",
                    title=f"Activity: {act.title} ({act.activity_type})",
                    date=act.date,
                    start_time=act.start_time,
                    end_time=act.end_time,
                    location=act.location,
                    description=act.priority
                )
            )

        # Schedule items (for current week scheduling representation)
        schedules = db.query(ScheduleItem).filter(ScheduleItem.child_id == child.id).all()
        # Map weekday schedule items to family events representation (for reference/current day)
        for s in schedules:
            events.append(
                FamilyEventItem(
                    child_id=child.id,
                    child_name=child.name,
                    event_type="SCHEDULE_ITEM",
                    title=f"Class: {s.subject} ({s.schedule_type})",
                    date=date.today(),  # Placeholder representing routine scheduling
                    start_time=s.start_time,
                    end_time=s.end_time,
                    location=s.room,
                    description=f"Teacher: {s.teacher or 'N/A'}"
                )
            )

        # Holidays
        holidays = db.query(HolidayCalendar).filter(HolidayCalendar.child_id == child.id).all()
        for h in holidays:
            events.append(
                FamilyEventItem(
                    child_id=child.id,
                    child_name=child.name,
                    event_type="HOLIDAY",
                    title=f"Holiday: {h.title}",
                    date=h.date,
                    description=h.description
                )
            )

    return FamilyEventsResponse(family_id=family_id, events=events)

def get_grocery_needs(db: Session, family_id: str) -> ChildGroceryNeedsResponse:
    children = db.query(ChildProfile).filter(ChildProfile.family_id == family_id).all()
    needs = []

    for child in children:
        bridge_events = db.query(MotherAgentBridgeEvent).filter(MotherAgentBridgeEvent.child_id == child.id).all()
        for e in bridge_events:
            needs.append(
                GroceryNeedItem(
                    child_id=child.id,
                    child_name=child.name,
                    event_name=e.event_name,
                    date=e.date,
                    recommendation=e.child_recommendation,
                    items=e.mother_agent_grocery_items or [],
                )
            )

    return ChildGroceryNeedsResponse(family_id=family_id, needs=needs)

def create_or_update_check_in(db: Session, check_in_in: ChildCheckInCreate) -> CheckInLog:
    check_in_date = check_in_in.date or date.today()
    db_log = db.query(CheckInLog).filter(
        CheckInLog.child_id == check_in_in.child_id,
        CheckInLog.date == check_in_date
    ).first()

    if db_log:
        db_log.expected_return_time = check_in_in.expected_return_time
        db_log.actual_check_in_time = check_in_in.actual_check_in_time
        db_log.location_note = check_in_in.location_note
        db_log.status = check_in_in.status
    else:
        db_log = CheckInLog(
            child_id=check_in_in.child_id,
            date=check_in_date,
            expected_return_time=check_in_in.expected_return_time,
            actual_check_in_time=check_in_in.actual_check_in_time,
            location_note=check_in_in.location_note,
            status=check_in_in.status,
            parent_notified=False
        )
        db.add(db_log)

    db.commit()
    db.refresh(db_log)

    logger.info(f"[CROSS-AGENT] Child Check-In recorded for Child ID {db_log.child_id}: Status={db_log.status}")
    return db_log

def trigger_child_alert(db: Session, alert_in: ChildAlertCreate) -> ChildAlertResponse:
    # 1. Send / persist notification alert
    title = f"Safety Alert: {alert_in.alert_type}"
    msg = f"Alert triggered for Child ID {alert_in.child_id}: {alert_in.message}. Location: {alert_in.location_note or 'Unknown'}."
    
    notification_log = NotificationService.send_notification(
        db=db,
        child_id=alert_in.child_id,
        title=title,
        message=msg,
        notification_type=NotificationType.SAFETY_WARNING.value,
        channel="PUSH",
    )

    logger.warning(f"[CROSS-AGENT] Child Alert triggered! Type={alert_in.alert_type}, Message={alert_in.message} for Child ID {alert_in.child_id}")
    
    return ChildAlertResponse(
        id=notification_log.id,
        child_id=alert_in.child_id,
        alert_type=alert_in.alert_type,
        message=alert_in.message,
        channel="PUSH",
        status="LOGGED",
        created_at=notification_log.created_at,
    )
