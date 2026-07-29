from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime, timezone
from app.database.database import Base


class AgentMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_role = Column(String(50), default="family")
    memory_type = Column(String(100), nullable=False, index=True)
    item_name = Column(String(100), nullable=True, index=True)
    memory_value = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


_memory_item_type_idx = Index(
    "idx_memory_item_type",
    "item_name",
    "memory_type",
)
