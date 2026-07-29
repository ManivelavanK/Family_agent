from sqlalchemy import Column, Integer, String, Float, DateTime, Index, func
from datetime import datetime, timezone
from app.database.database import Base


class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100))
    quantity = Column(Float, default=0.0, nullable=False)
    unit = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# Functional index for case-insensitive name lookups
_grocery_name_idx = Index("idx_grocery_items_name_lower", func.lower(GroceryItem.name))
