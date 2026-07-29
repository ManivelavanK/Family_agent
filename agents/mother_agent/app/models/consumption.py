from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from datetime import datetime, timezone
from app.database.database import Base


class Consumption(Base):
    __tablename__ = "consumption_history"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False, index=True)
    quantity_used = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    consumption_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


_consumption_item_date_idx = Index(
    "idx_consumption_item_date",
    "item_name",
    "consumption_date",
)
