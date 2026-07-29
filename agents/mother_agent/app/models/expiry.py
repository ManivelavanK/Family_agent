from sqlalchemy import Column, Integer, String, Date, DateTime, Index
from datetime import datetime, timezone
from app.database.database import Base


class ExpiryItem(Base):
    __tablename__ = "expiry_items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False, index=True)
    expiry_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


_expiry_item_date_idx = Index(
    "idx_expiry_item_date",
    "item_name",
    "expiry_date",
)
