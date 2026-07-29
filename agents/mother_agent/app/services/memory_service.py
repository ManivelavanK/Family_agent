import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.memory import AgentMemory
from app.schemas.memory import MemoryCreate

logger = logging.getLogger(__name__)


def add_memory(db: Session, memory: MemoryCreate) -> AgentMemory:
    record = AgentMemory(
        user_role=memory.user_role,
        memory_type=memory.memory_type,
        item_name=memory.item_name,
        memory_value=memory.memory_value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Memory added: type='%s', item='%s'.", memory.memory_type, memory.item_name)
    return record


def save_memory(db: Session, memory_type: str, item_name: str, value: str) -> AgentMemory:
    record = AgentMemory(
        user_role="mother",
        memory_type=memory_type,
        item_name=item_name,
        memory_value=value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_memories(db: Session) -> list[AgentMemory]:
    return db.query(AgentMemory).order_by(AgentMemory.created_at.desc()).all()


def get_item_memory(db: Session, item_name: str) -> list[AgentMemory]:
    return (
        db.query(AgentMemory)
        .filter(func.lower(AgentMemory.item_name) == item_name.lower())
        .order_by(AgentMemory.created_at.desc())
        .all()
    )
