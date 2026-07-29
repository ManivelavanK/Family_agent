from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime, timezone
from app.database.database import Base


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False, index=True)
    store_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


_price_item_store_idx = Index(
    "idx_price_item_store",
    "item_name",
    "store_name",
)
