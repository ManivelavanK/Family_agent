from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.plan import Plan, PlanTask, BudgetItem, ItineraryItem, Participant
from app.schemas.plan import (
    PlanCreate, PlanUpdate,
    PlanTaskCreate, PlanTaskUpdate,
    BudgetItemCreate, BudgetItemUpdate,
    ItineraryItemCreate, ItineraryItemUpdate,
    ParticipantCreate, ParticipantUpdate
)

class PlanService:
    @staticmethod
    def create_plan(db: Session, plan_in: PlanCreate) -> Plan:
        db_plan = Plan(**plan_in.model_dump())
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: int) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.id == plan_id).first()

    @staticmethod
    def get_all_plans(db: Session, skip: int = 0, limit: int = 100) -> List[Plan]:
        return db.query(Plan).offset(skip).limit(limit).all()

    @staticmethod
    def update_plan(db: Session, plan_id: int, plan_in: PlanUpdate) -> Optional[Plan]:
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return None
        
        update_data = plan_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_plan, field, value)
        
        db.commit()
        db.refresh(db_plan)
        return db_plan

    @staticmethod
    def delete_plan(db: Session, plan_id: int) -> bool:
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return False
        db.delete(db_plan)
        db.commit()
        return True

class TaskService:
    @staticmethod
    def create_task(db: Session, plan_id: int, task_in: PlanTaskCreate) -> PlanTask:
        db_task = PlanTask(plan_id=plan_id, **task_in.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_tasks_by_plan(db: Session, plan_id: int) -> List[PlanTask]:
        return db.query(PlanTask).filter(PlanTask.plan_id == plan_id).all()

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[PlanTask]:
        return db.query(PlanTask).filter(PlanTask.id == task_id).first()

    @staticmethod
    def update_task(db: Session, task_id: int, task_in: PlanTaskUpdate) -> Optional[PlanTask]:
        db_task = TaskService.get_task_by_id(db, task_id)
        if not db_task:
            return None
        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        db_task = TaskService.get_task_by_id(db, task_id)
        if not db_task:
            return False
        db.delete(db_task)
        db.commit()
        return True

class BudgetService:
    @staticmethod
    def create_budget_item(db: Session, plan_id: int, item_in: BudgetItemCreate) -> BudgetItem:
        db_item = BudgetItem(plan_id=plan_id, **item_in.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def get_budget_by_plan(db: Session, plan_id: int) -> List[BudgetItem]:
        return db.query(BudgetItem).filter(BudgetItem.plan_id == plan_id).all()

    @staticmethod
    def get_budget_item_by_id(db: Session, item_id: int) -> Optional[BudgetItem]:
        return db.query(BudgetItem).filter(BudgetItem.id == item_id).first()

    @staticmethod
    def update_budget_item(db: Session, item_id: int, item_in: BudgetItemUpdate) -> Optional[BudgetItem]:
        db_item = BudgetService.get_budget_item_by_id(db, item_id)
        if not db_item:
            return None
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def delete_budget_item(db: Session, item_id: int) -> bool:
        db_item = BudgetService.get_budget_item_by_id(db, item_id)
        if not db_item:
            return False
        db.delete(db_item)
        db.commit()
        return True

class ItineraryService:
    @staticmethod
    def create_itinerary_item(db: Session, plan_id: int, item_in: ItineraryItemCreate) -> ItineraryItem:
        db_item = ItineraryItem(plan_id=plan_id, **item_in.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def get_itinerary_by_plan(db: Session, plan_id: int) -> List[ItineraryItem]:
        return db.query(ItineraryItem).filter(ItineraryItem.plan_id == plan_id).all()

    @staticmethod
    def get_itinerary_item_by_id(db: Session, item_id: int) -> Optional[ItineraryItem]:
        return db.query(ItineraryItem).filter(ItineraryItem.id == item_id).first()

    @staticmethod
    def update_itinerary_item(db: Session, item_id: int, item_in: ItineraryItemUpdate) -> Optional[ItineraryItem]:
        db_item = ItineraryService.get_itinerary_item_by_id(db, item_id)
        if not db_item:
            return None
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def delete_itinerary_item(db: Session, item_id: int) -> bool:
        db_item = ItineraryService.get_itinerary_item_by_id(db, item_id)
        if not db_item:
            return False
        db.delete(db_item)
        db.commit()
        return True

class ParticipantService:
    @staticmethod
    def create_participant(db: Session, plan_id: int, p_in: ParticipantCreate) -> Participant:
        db_p = Participant(plan_id=plan_id, **p_in.model_dump())
        db.add(db_p)
        db.commit()
        db.refresh(db_p)
        return db_p

    @staticmethod
    def get_participants_by_plan(db: Session, plan_id: int) -> List[Participant]:
        return db.query(Participant).filter(Participant.plan_id == plan_id).all()

    @staticmethod
    def get_participant_by_id(db: Session, p_id: int) -> Optional[Participant]:
        return db.query(Participant).filter(Participant.id == p_id).first()

    @staticmethod
    def update_participant(db: Session, p_id: int, p_in: ParticipantUpdate) -> Optional[Participant]:
        db_p = ParticipantService.get_participant_by_id(db, p_id)
        if not db_p:
            return None
        update_data = p_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_p, field, value)
        db.commit()
        db.refresh(db_p)
        return db_p

    @staticmethod
    def delete_participant(db: Session, p_id: int) -> bool:
        db_p = ParticipantService.get_participant_by_id(db, p_id)
        if not db_p:
            return False
        db.delete(db_p)
        db.commit()
        return True
