from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import datetime

from app.models.schedule import ScheduleItem, HolidayCalendar
from app.models.profile import ChildProfile
from app.schemas.schedule import (
    ScheduleItemCreate,
    HolidayCalendarCreate,
    TodayScheduleResponse,
    WeekScheduleResponse,
    HolidayCalendarResponse,
    ScheduleItemResponse,
)
from app.services.age_adaptation_service import classify_age_group

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# --- Schedule Item CRUD ---

def create_schedule_item(db: Session, item_in: ScheduleItemCreate) -> ScheduleItem:
    # Resolve education_stage if not provided
    stage = item_in.education_stage
    if not stage:
        profile = db.query(ChildProfile).filter(ChildProfile.id == item_in.child_id).first()
        if profile:
            stage = "COLLEGE" if profile.age >= 18 else "SCHOOL"
        else:
            stage = "SCHOOL"

    db_item = ScheduleItem(
        child_id=item_in.child_id,
        day_of_week=item_in.day_of_week.capitalize(),
        subject=item_in.subject,
        start_time=item_in.start_time,
        end_time=item_in.end_time,
        room=item_in.room,
        teacher=item_in.teacher,
        transport_info=item_in.transport_info,
        schedule_type=item_in.schedule_type or ("LECTURE" if stage == "COLLEGE" else "PERIOD"),
        education_stage=stage
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_child_schedule(db: Session, child_id: int) -> List[ScheduleItem]:
    return db.query(ScheduleItem).filter(
        ScheduleItem.child_id == child_id
    ).order_by(ScheduleItem.start_time.asc()).all()

def delete_schedule_item(db: Session, item_id: int) -> bool:
    item = db.query(ScheduleItem).filter(ScheduleItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


# --- Holiday Calendar CRUD ---

def add_holiday(db: Session, holiday_in: HolidayCalendarCreate) -> HolidayCalendar:
    db_holiday = HolidayCalendar(
        child_id=holiday_in.child_id,
        date=holiday_in.date,
        title=holiday_in.title,
        description=holiday_in.description,
        is_no_school=holiday_in.is_no_school if holiday_in.is_no_school is not None else True
    )
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

def get_holidays(db: Session, child_id: int) -> List[HolidayCalendar]:
    return db.query(HolidayCalendar).filter(
        HolidayCalendar.child_id == child_id
    ).order_by(HolidayCalendar.date.asc()).all()


# --- Generate Today's Schedule ---

def generate_today_schedule(db: Session, child_id: int, target_date: Optional[datetime.date] = None) -> TodayScheduleResponse:
    eval_date = target_date or datetime.date.today()
    day_name = eval_date.strftime("%A")  # e.g., Monday

    # Check child profile to determine education stage
    profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    stage = "COLLEGE" if (profile and profile.age >= 18) else "SCHOOL"

    # Check Holiday Calendar
    holiday = db.query(HolidayCalendar).filter(
        HolidayCalendar.child_id == child_id,
        HolidayCalendar.date == eval_date
    ).first()

    is_holiday = False
    holiday_info = None
    if holiday:
        is_holiday = holiday.is_no_school
        holiday_info = HolidayCalendarResponse.model_validate(holiday)

    # Query schedule items for child for today's day of week
    items = db.query(ScheduleItem).filter(
        ScheduleItem.child_id == child_id,
        ScheduleItem.day_of_week == day_name
    ).order_by(ScheduleItem.start_time.asc()).all()

    schedule_responses = [ScheduleItemResponse.model_validate(i) for i in items]

    # Extract bus / transport timings
    bus_timings = [
        item for item in schedule_responses 
        if item.schedule_type in ("BUS", "COMMUTE") or item.transport_info is not None
    ]

    # Build human readable summary according to education stage
    if is_holiday:
        summary_str = f"Today ({day_name}, {eval_date}) is a Holiday: {holiday.title}. No classes or timetable scheduled."
    elif not schedule_responses:
        summary_str = f"No classes scheduled for today ({day_name})."
    else:
        if stage == "SCHOOL":
            periods_count = sum(1 for i in schedule_responses if i.schedule_type == "PERIOD")
            bus_str = f" Bus pickup at {bus_timings[0].start_time.strftime('%H:%M')}." if bus_timings else ""
            summary_str = f"School Timetable for {day_name}: {len(schedule_responses)} items ({periods_count} periods, assembly & activities).{bus_str}"
        else:  # COLLEGE
            lectures_count = sum(1 for i in schedule_responses if i.schedule_type in ("LECTURE", "LAB"))
            commute_str = f" Commute info: {bus_timings[0].transport_info or 'Metro/Bus'}." if bus_timings else ""
            summary_str = f"College Timetable for {day_name}: {len(schedule_responses)} sessions ({lectures_count} lectures/labs, project & club activities).{commute_str}"

    return TodayScheduleResponse(
        child_id=child_id,
        date=eval_date,
        day_of_week=day_name,
        is_holiday=is_holiday,
        holiday_info=holiday_info,
        education_stage=stage,
        schedule_items=schedule_responses,
        bus_timings=bus_timings,
        summary=summary_str
    )


# --- Generate Week Schedule ---

def generate_week_schedule(db: Session, child_id: int) -> WeekScheduleResponse:
    profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    stage = "COLLEGE" if (profile and profile.age >= 18) else "SCHOOL"

    items = db.query(ScheduleItem).filter(
        ScheduleItem.child_id == child_id
    ).order_by(ScheduleItem.start_time.asc()).all()

    grouped: Dict[str, List[ScheduleItemResponse]] = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }

    for item in items:
        day_key = item.day_of_week.lower()
        if day_key in grouped:
            grouped[day_key].append(ScheduleItemResponse.model_validate(item))

    return WeekScheduleResponse(
        child_id=child_id,
        education_stage=stage,
        monday=grouped["monday"],
        tuesday=grouped["tuesday"],
        wednesday=grouped["wednesday"],
        thursday=grouped["thursday"],
        friday=grouped["friday"],
        saturday=grouped["saturday"],
        sunday=grouped["sunday"]
    )
