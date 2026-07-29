from typing import List, Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.memory import PlannerMemory, MemoryType
from app.schemas.memory import PlannerMemoryCreate, PlannerMemoryUpdate

class MemoryService:
    @staticmethod
    def create_memory(db: Session, memory_in: PlannerMemoryCreate) -> PlannerMemory:
        db_memory = PlannerMemory(**memory_in.model_dump())
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        return db_memory

    @staticmethod
    def get_memory_by_id(db: Session, memory_id: int, family_id: str = "default_family") -> Optional[PlannerMemory]:
        return db.query(PlannerMemory).filter(
            and_(
                PlannerMemory.id == memory_id,
                PlannerMemory.family_id == family_id
            )
        ).first()

    @staticmethod
    def get_all_memories(db: Session, family_id: str = "default_family", skip: int = 0, limit: int = 100) -> List[PlannerMemory]:
        return db.query(PlannerMemory).filter(
            PlannerMemory.family_id == family_id
        ).order_by(PlannerMemory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_memory(db: Session, memory_id: int, memory_in: PlannerMemoryUpdate, family_id: str = "default_family") -> Optional[PlannerMemory]:
        db_memory = MemoryService.get_memory_by_id(db, memory_id, family_id=family_id)
        if not db_memory:
            return None
        
        update_data = memory_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_memory, field, value)
        
        db.commit()
        db.refresh(db_memory)
        return db_memory

    @staticmethod
    def delete_memory(db: Session, memory_id: int, family_id: str = "default_family") -> bool:
        db_memory = MemoryService.get_memory_by_id(db, memory_id, family_id=family_id)
        if not db_memory:
            return False
        db.delete(db_memory)
        db.commit()
        return True

    @staticmethod
    def get_memories_by_type(db: Session, memory_type: MemoryType, family_id: str = "default_family") -> List[PlannerMemory]:
        return db.query(PlannerMemory).filter(
            and_(
                PlannerMemory.family_id == family_id,
                PlannerMemory.memory_type == memory_type
            )
        ).order_by(PlannerMemory.importance.desc(), PlannerMemory.created_at.desc()).all()

    @staticmethod
    def get_relevant_memories(db: Session, family_id: str = "default_family", limit: int = 10) -> List[PlannerMemory]:
        return db.query(PlannerMemory).filter(
            PlannerMemory.family_id == family_id
        ).order_by(PlannerMemory.importance.desc(), PlannerMemory.created_at.desc()).limit(limit).all()
