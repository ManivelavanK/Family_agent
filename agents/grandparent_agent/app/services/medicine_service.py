import logging
from sqlalchemy.orm import Session
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate
from app.services.notification_service import send_notification

logger = logging.getLogger(__name__)


def add_medicine(db: Session, item: MedicineCreate) -> Medicine:
    existing = db.query(Medicine).filter(Medicine.name.ilike(item.name)).first()
    if existing:
        existing.inventory_count += item.inventory_count
        existing.dosage = item.dosage
        existing.frequency = item.frequency
        existing.time_of_day = item.time_of_day
        existing.is_active = True
    else:
        existing = Medicine(
            name=item.name.strip(),
            dosage=item.dosage,
            frequency=item.frequency,
            time_of_day=item.time_of_day,
            inventory_count=item.inventory_count,
            is_active=True
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    logger.info("Medicine '%s' added/updated.", existing.name)
    return existing


def get_medicines(db: Session, active_only: bool = True) -> list[Medicine]:
    query = db.query(Medicine)
    if active_only:
        query = query.filter(Medicine.is_active == True)
    return query.all()


def update_medicine(db: Session, med_id: int, update_data: MedicineUpdate) -> Medicine:
    med = db.query(Medicine).filter(Medicine.id == med_id).first()
    if not med:
        raise ValueError(f"Medicine with ID {med_id} not found.")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(med, field, value)

    db.commit()
    db.refresh(med)
    logger.info("Updated medicine ID %d.", med_id)
    return med


def take_dose(db: Session, med_name: str) -> Medicine:
    med = db.query(Medicine).filter(Medicine.name.ilike(med_name), Medicine.is_active == True).first()
    if not med:
        raise ValueError(f"Active medicine '{med_name}' not found.")

    if med.inventory_count <= 0:
        send_notification("Refill Reminder", f"Inventory for {med.name} is empty! Please refill immediately.", "Warning")
        raise ValueError(f"No inventory left for '{med_name}' to take dose.")

    med.inventory_count -= 1
    db.commit()
    db.refresh(med)

    if med.inventory_count <= 5:
        send_notification("Low Stock Alert", f"Low stock for {med.name}. Only {med.inventory_count} remaining.", "Warning")

    logger.info("Dose of '%s' recorded. Remaining: %d", med.name, med.inventory_count)
    return med


def check_refill_alerts(db: Session):
    low_stock_meds = db.query(Medicine).filter(Medicine.inventory_count <= 5, Medicine.is_active == True).all()
    for med in low_stock_meds:
        send_notification("Refill Needed", f"Medicine '{med.name}' is low on stock ({med.inventory_count} doses remaining).", "Warning")


def delete_medicine(db: Session, med_id: int) -> bool:
    med = db.query(Medicine).filter(Medicine.id == med_id).first()
    if not med:
        return False
    db.delete(med)
    db.commit()
    logger.info("Deleted medicine ID %d.", med_id)
    return True


def get_medication_intelligence(db: Session) -> list[dict]:
    logger.info("Medicine Intelligence: Analyzing active prescriptions...")
    meds = db.query(Medicine).filter(Medicine.is_active == True).all()
    intelligence_reports = []
    
    for med in meds:
        refill_req = med.inventory_count <= 5
        missed_status = med.inventory_count == 0
        
        # Determine warning
        if missed_status:
            warning_msg = f"Out of stock! Doses of {med.name} are missed. Please refill immediately."
        elif refill_req:
            warning_msg = f"Refill required: Only {med.inventory_count} tablets remaining!"
        else:
            warning_msg = "Inventory normal."

        intelligence_reports.append({
            "name": med.name,
            "next_dose": med.time_of_day,
            "remaining_tablets": med.inventory_count,
            "refill_required": refill_req,
            "missed": missed_status,
            "warning": warning_msg
        })
        
    return intelligence_reports


def get_low_stock_refills(db: Session) -> list[dict]:
    logger.info("Medicine Refill: Compiling list of low stock medicines...")
    meds = db.query(Medicine).filter(
        Medicine.is_active == True,
        Medicine.inventory_count <= 5
    ).all()
    
    return [
        {
            "name": med.name,
            "remaining_tablets": med.inventory_count,
            "refill_required": True
        }
        for med in meds
    ]

