import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.consumption import Consumption
from app.models.grocery_item import GroceryItem
from app.schemas.consumption import ConsumptionCreate
from app.services.memory_service import save_memory
from app.services.pattern_service import generate_consumption_memory

logger = logging.getLogger(__name__)


def add_consumption(db: Session, consumption: ConsumptionCreate) -> Consumption:
    record = Consumption(
        item_name=consumption.item_name.strip(),
        quantity_used=consumption.quantity_used,
        unit=consumption.unit.strip(),
        consumption_date=consumption.consumption_date,
    )
    db.add(record)

    # Case-insensitive inventory deduction
    item = (
        db.query(GroceryItem)
        .filter(func.lower(GroceryItem.name) == consumption.item_name.lower())
        .with_for_update()
        .first()
    )

    if item:
        item.quantity = max(item.quantity - consumption.quantity_used, 0.0)
        logger.info(
            "Deducted %.2f %s from '%s'. Remaining: %.2f",
            consumption.quantity_used, consumption.unit, item.name, item.quantity,
        )
    else:
        logger.warning(
            "Item '%s' not found in inventory during consumption.", consumption.item_name
        )

    db.commit()
    db.refresh(record)

    # Side-effects: memory updates — failures must NOT roll back the committed record
    try:
        generate_consumption_memory(db, consumption.item_name)
    except Exception as e:
        logger.error("Pattern memory generation failed for '%s': %s", consumption.item_name, e)

    try:
        total_consumed = (
            db.query(func.sum(Consumption.quantity_used))
            .filter(func.lower(Consumption.item_name) == consumption.item_name.lower())
            .scalar()
        ) or 0.0

        total_records = (
            db.query(func.count(Consumption.id))
            .filter(func.lower(Consumption.item_name) == consumption.item_name.lower())
            .scalar()
        ) or 0

        if total_records > 0:
            avg = round(total_consumed / total_records, 2)
            save_memory(
                db,
                "consumption_pattern",
                consumption.item_name,
                f"Average consumption is {avg} {consumption.unit} per usage",
            )
    except Exception as e:
        logger.error("Memory save failed for '%s': %s", consumption.item_name, e)

    return record


def get_consumption_history(db: Session) -> list[Consumption]:
    return db.query(Consumption).order_by(Consumption.consumption_date.desc()).all()
