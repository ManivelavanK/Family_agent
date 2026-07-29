import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.activity import Activity
from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.study import StudySession
from app.schemas.activity import ActivityCreate, AgendaItem, AgendaDay
from app.services.age_adaptation_service import classify_age_group

# --- Activity CRUD ---

def create_activity(db: Session, activity_in: ActivityCreate) -> Activity:
    db_activity = Activity(
        child_id=activity_in.child_id,
        title=activity_in.title,
        activity_type=activity_in.activity_type,
        date=activity_in.date,
        start_time=activity_in.start_time,
        end_time=activity_in.end_time,
        location=activity_in.location,
        priority=activity_in.priority,
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activities_by_child_id(db: Session, child_id: int) -> List[Activity]:
    return db.query(Activity).filter(Activity.child_id == child_id).order_by(Activity.date.asc(), Activity.start_time.asc()).all()

def get_activity_by_id(db: Session, activity_id: int) -> Optional[Activity]:
    return db.query(Activity).filter(Activity.id == activity_id).first()

def update_activity(db: Session, activity_id: int, activity_in: ActivityCreate) -> Optional[Activity]:
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return None
    for field, value in activity_in.model_dump().items():
        setattr(db_activity, field, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def delete_activity(db: Session, activity_id: int) -> bool:
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return False
    db.delete(db_activity)
    db.commit()
    return True


# --- Agenda Compilation & Conflict Detection ---

def build_agenda_for_range(db: Session, child_id: int, start_date: datetime.date, end_date: datetime.date) -> List[AgendaDay]:
    child_profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child_profile:
        return []

    age_group = classify_age_group(child_profile.age)
    is_college = (age_group == "COLLEGE")

    # Determine wake and sleep times from profile (or use defaults)
    wake_t = child_profile.daily_wake_time or datetime.time(7, 0)
    sleep_t = child_profile.daily_sleep_time or datetime.time(22, 0)

    # Fetch database events for the date range
    activities = db.query(Activity).filter(
        Activity.child_id == child_id,
        Activity.date >= start_date,
        Activity.date <= end_date
    ).all()

    homework_list = db.query(Homework).filter(
        Homework.child_id == child_id,
        Homework.due_date >= start_date,
        Homework.due_date <= end_date,
        Homework.completion_status == False
    ).all()

    exams = db.query(Exam).filter(
        Exam.child_id == child_id,
        Exam.exam_date >= start_date,
        # Fetch exams within 7 days of the end date for proactive prep scheduling
        Exam.exam_date <= (end_date + datetime.timedelta(days=7))
    ).all()

    study_sessions = db.query(StudySession).filter(
        StudySession.child_id == child_id,
        StudySession.start_time >= datetime.datetime.combine(start_date, datetime.time.min),
        StudySession.end_time <= datetime.datetime.combine(end_date, datetime.time.max)
    ).all()

    agenda_days = []
    current_date = start_date
    while current_date <= end_date:
        day_items: List[AgendaItem] = []

        # 1. Sleep blocks
        day_items.append(AgendaItem(title="Night Sleep", type="Sleep", start_time=datetime.time(0, 0), end_time=wake_t, priority="High"))
        day_items.append(AgendaItem(title="Bedtime Sleep", type="Sleep", start_time=sleep_t, end_time=datetime.time(23, 59), priority="High"))

        # 2. Meal blocks
        day_items.append(AgendaItem(title="Breakfast", type="Meal", start_time=datetime.time(7, 30), end_time=datetime.time(8, 0), priority="Medium"))
        day_items.append(AgendaItem(title="Lunch", type="Meal", start_time=datetime.time(13, 0), end_time=datetime.time(13, 30), priority="Medium"))
        day_items.append(AgendaItem(title="Dinner", type="Meal", start_time=datetime.time(19, 30), end_time=datetime.time(20, 0), priority="Medium"))

        # 3. School/College schedule (Mon-Fri)
        is_weekday = current_date.weekday() < 5
        if is_weekday:
            if is_college:
                day_items.append(AgendaItem(title="College Lectures", type="College", start_time=datetime.time(9, 0), end_time=datetime.time(16, 0), priority="High"))
            else:
                day_items.append(AgendaItem(title="School Hours", type="School", start_time=datetime.time(8, 30), end_time=datetime.time(15, 0), priority="High"))

        # 4. Homework check
        hw_due_today = [h for h in homework_list if h.due_date == current_date]
        if hw_due_today:
            subjects_str = ", ".join(set(h.subject for h in hw_due_today))
            day_items.append(AgendaItem(title=f"Homework: {subjects_str}", type="Homework", start_time=datetime.time(16, 30), end_time=datetime.time(17, 30), priority="High"))

        # 5. Exam Preparation check (if an exam is upcoming within 7 days)
        exams_upcoming = [e for e in exams if current_date <= e.exam_date <= (current_date + datetime.timedelta(days=7))]
        if exams_upcoming:
            exams_str = ", ".join(set(e.subject for e in exams_upcoming))
            day_items.append(AgendaItem(title=f"Exam Prep: {exams_str}", type="Exam Prep", start_time=datetime.time(17, 30), end_time=datetime.time(19, 0), priority="High"))

        # 6. Logged Study Sessions for this day
        study_today = [s for s in study_sessions if s.start_time.date() == current_date]
        for s in study_today:
            day_items.append(
                AgendaItem(
                    title=f"Study Session: {s.subject} - {s.topic}",
                    type="Study Session",
                    start_time=s.start_time.time(),
                    end_time=s.end_time.time(),
                    priority="Medium"
                )
            )

        # 7. Registered Activities
        acts_today = [a for a in activities if a.date == current_date]
        for a in acts_today:
            day_items.append(
                AgendaItem(
                    title=a.title,
                    type=a.activity_type,
                    start_time=a.start_time,
                    end_time=a.end_time,
                    priority=a.priority
                )
            )

        # Sort day items by start time
        day_items.sort(key=lambda x: x.start_time)

        # Conflict Detection
        # Check overlaps: if item A start < item B end AND item B start < item A end
        conflicting_indices = set()
        for i in range(len(day_items)):
            for j in range(i + 1, len(day_items)):
                item_i = day_items[i]
                item_j = day_items[j]
                
                # Check overlap
                if item_i.start_time < item_j.end_time and item_j.start_time < item_i.end_time:
                    conflicting_indices.add(i)
                    conflicting_indices.add(j)
                    
                    # Update descriptions
                    desc_i = f"Conflicts with {item_j.title} ({item_j.start_time.strftime('%H:%M')}-{item_j.end_time.strftime('%H:%M')})"
                    desc_j = f"Conflicts with {item_i.title} ({item_i.start_time.strftime('%H:%M')}-{item_i.end_time.strftime('%H:%M')})"
                    
                    item_i.conflict_description = (item_i.conflict_description + "; " + desc_i) if item_i.conflict_description else desc_i
                    item_j.conflict_description = (item_j.conflict_description + "; " + desc_j) if item_j.conflict_description else desc_j

        for idx in conflicting_indices:
            day_items[idx].is_conflict = True

        agenda_days.append(
            AgendaDay(
                date=current_date,
                items=day_items,
                total_conflicting_items=len(conflicting_indices)
            )
        )

        current_date += datetime.timedelta(days=1)

    return agenda_days
