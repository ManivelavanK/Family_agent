from sqlalchemy import Column, Integer, String, Date, Float, DateTime, Index
from datetime import datetime, timezone
from app.database.database import Base


class Purchase(Base):
    __tablename__ = "purchase_history"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False, index=True)
    category = Column(String(100))
    quantity = Column(Float, nullable=False)
    unit = Column(String(50))
    price = Column(Float)
    purchase_date = Column(Date)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


_purchase_item_date_idx = Index(
    "idx_purchase_item_date",
    "item_name",
    "purchase_date",
)
