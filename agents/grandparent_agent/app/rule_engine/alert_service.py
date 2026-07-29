import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

# Import models
from app.models.vitals import Vitals
from app.models.activity import Activity
from app.models.nutrition import Nutrition
from app.models.medicine import Medicine

# Import rule evaluators
from app.rule_engine.health_rules import (
    evaluate_blood_pressure,
    evaluate_blood_sugar,
    evaluate_heart_rate,
    evaluate_sleep_hours,
    evaluate_water_intake,
    evaluate_medicine_missed
)

logger = logging.getLogger(__name__)


def evaluate_rules_and_generate_alerts(db: Session) -> list[dict]:
    """
    Fetches the latest data for vitals, activity, nutrition, and medicine schedules
    from the database, runs them through the rule engine, and returns active alerts.
    """
    logger.info("Intelligent Rule Engine: Commencing check on all health logs...")
    alerts = []

    # 1. Blood Pressure & Blood Sugar & Heart Rate
    last_vital = db.query(Vitals).order_by(Vitals.timestamp.desc()).first()
    if last_vital:
        bp_alert = evaluate_blood_pressure(last_vital.blood_pressure_systolic)
        if bp_alert:
            alerts.append(bp_alert)

        bs_alert = evaluate_blood_sugar(last_vital.blood_sugar)
        if bs_alert:
            alerts.append(bs_alert)

        hr_alert = evaluate_heart_rate(last_vital.heart_rate)
        if hr_alert:
            alerts.append(hr_alert)

    # 2. Sleep Hours
    last_activity = db.query(Activity).order_by(Activity.date.desc()).first()
    if last_activity:
        sleep_alert = evaluate_sleep_hours(last_activity.sleep_hours)
        if sleep_alert:
            alerts.append(sleep_alert)

    # 3. Water Intake
    last_nutrition = db.query(Nutrition).order_by(Nutrition.timestamp.desc()).first()
    if last_nutrition:
        target_date = last_nutrition.timestamp.date()
        total_water = db.query(func.sum(Nutrition.water_ml)).filter(
            func.date(Nutrition.timestamp) == target_date
        ).scalar() or 0
        
        water_alert = evaluate_water_intake(total_water)
        if water_alert:
            alerts.append(water_alert)
    else:
        # If no nutrition is logged at all, trigger warning
        water_alert = evaluate_water_intake(0)
        if water_alert:
            alerts.append(water_alert)

    # 4. Medicine Missed (Check if any active medicine is out of inventory / cannot be taken)
    active_meds = db.query(Medicine).filter(Medicine.is_active == True).all()
    for med in active_meds:
        if med.inventory_count == 0:
            med_alert = evaluate_medicine_missed(is_missed=True, med_name=med.name)
            if med_alert:
                alerts.append(med_alert)

    logger.info("Intelligent Rule Engine: Completed. Generated %d alert(s)", len(alerts))
    return alerts
