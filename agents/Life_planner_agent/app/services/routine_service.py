import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.routine import FamilyRoutine, RoutineStatus
from app.schemas.routine import FamilyRoutineCreate, FamilyRoutineUpdate

class RoutineService:
    @staticmethod
    def create_routine(db: Session, routine_in: FamilyRoutineCreate) -> FamilyRoutine:
        routine = FamilyRoutine(
            family_id=routine_in.family_id,
            member_name=routine_in.member_name,
            title=routine_in.title,
            description=routine_in.description,
            scheduled_start=routine_in.scheduled_start,
            scheduled_end=routine_in.scheduled_end,
            priority=routine_in.priority,
            status=routine_in.status,
            category=routine_in.category
        )
        db.add(routine)
        db.commit()
        db.refresh(routine)
        return routine

    @staticmethod
    def get_routine_by_id(db: Session, routine_id: int, family_id: str = "default_family") -> Optional[FamilyRoutine]:
        return db.query(FamilyRoutine).filter(
            FamilyRoutine.id == routine_id,
            FamilyRoutine.family_id == family_id
        ).first()

    @staticmethod
    def get_all_routines(db: Session, family_id: str = "default_family", limit: int = 100) -> List[FamilyRoutine]:
        return db.query(FamilyRoutine).filter(
            FamilyRoutine.family_id == family_id
        ).order_by(FamilyRoutine.scheduled_start.asc()).limit(limit).all()

    @staticmethod
    def get_routines_for_date(db: Session, target_date: datetime.date, family_id: str = "default_family") -> List[FamilyRoutine]:
        start_dt = datetime.datetime.combine(target_date, datetime.time.min, tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime.combine(target_date, datetime.time.max, tzinfo=datetime.timezone.utc)
        return db.query(FamilyRoutine).filter(
            FamilyRoutine.family_id == family_id,
            FamilyRoutine.scheduled_start <= end_dt,
            FamilyRoutine.scheduled_end >= start_dt
        ).order_by(FamilyRoutine.scheduled_start.asc()).all()

    @staticmethod
    def get_routines_in_range(
        db: Session,
        start_date: datetime.date,
        end_date: datetime.date,
        family_id: str = "default_family"
    ) -> List[FamilyRoutine]:
        start_dt = datetime.datetime.combine(start_date, datetime.time.min, tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max, tzinfo=datetime.timezone.utc)
        return db.query(FamilyRoutine).filter(
            FamilyRoutine.family_id == family_id,
            FamilyRoutine.scheduled_start <= end_dt,
            FamilyRoutine.scheduled_end >= start_dt
        ).order_by(FamilyRoutine.scheduled_start.asc()).all()

    @staticmethod
    def update_routine(
        db: Session,
        routine_id: int,
        routine_in: FamilyRoutineUpdate,
        family_id: str = "default_family"
    ) -> Optional[FamilyRoutine]:
        routine = RoutineService.get_routine_by_id(db, routine_id, family_id)
        if not routine:
            return None

        update_data = routine_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(routine, field, value)

        db.commit()
        db.refresh(routine)
        return routine

    @staticmethod
    def delete_routine(db: Session, routine_id: int, family_id: str = "default_family") -> bool:
        routine = RoutineService.get_routine_by_id(db, routine_id, family_id)
        if not routine:
            return False
        db.delete(routine)
        db.commit()
        return True

    @staticmethod
    def check_routine_conflicts(
        db: Session,
        member_name: str,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
        family_id: str = "default_family",
        exclude_routine_id: Optional[int] = None
    ) -> List[FamilyRoutine]:
        query = db.query(FamilyRoutine).filter(
            FamilyRoutine.family_id == family_id,
            FamilyRoutine.member_name == member_name,
            FamilyRoutine.status != RoutineStatus.SKIPPED,
            or_(
                and_(FamilyRoutine.scheduled_start < end_datetime, FamilyRoutine.scheduled_end > start_datetime)
            )
        )
        if exclude_routine_id:
            query = query.filter(FamilyRoutine.id != exclude_routine_id)
        return query.all()
