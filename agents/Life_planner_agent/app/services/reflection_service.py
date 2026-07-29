from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.reflection import PlanReflection
from app.schemas.reflection import PlanReflectionCreate

class ReflectionService:
    @staticmethod
    def create_reflection(db: Session, reflection_in: PlanReflectionCreate) -> PlanReflection:
        db_reflection = PlanReflection(**reflection_in.model_dump())
        db.add(db_reflection)
        db.commit()
        db.refresh(db_reflection)
        return db_reflection

    @staticmethod
    def get_reflections_by_plan(db: Session, plan_id: int) -> List[PlanReflection]:
        return db.query(PlanReflection).filter(PlanReflection.plan_id == plan_id).all()
