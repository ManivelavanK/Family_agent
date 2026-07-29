from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app.models.nutrition import NutritionLog, MotherAgentBridgeEvent
from app.schemas.nutrition import (
    NutritionLogCreate,
    NutritionSummaryResponse,
    MotherAgentBridgeEventCreate,
)

# --- Nutrition Log CRUD ---

def create_or_update_nutrition_log(db: Session, log_in: NutritionLogCreate) -> NutritionLog:
    db_log = db.query(NutritionLog).filter(
        NutritionLog.child_id == log_in.child_id,
        NutritionLog.date == log_in.date
    ).first()

    if not db_log:
        db_log = NutritionLog(
            child_id=log_in.child_id,
            date=log_in.date,
            breakfast_eaten=log_in.breakfast_eaten if log_in.breakfast_eaten is not None else True,
            breakfast_details=log_in.breakfast_details,
            lunch_eaten=log_in.lunch_eaten if log_in.lunch_eaten is not None else True,
            lunch_details=log_in.lunch_details,
            snack_eaten=log_in.snack_eaten if log_in.snack_eaten is not None else True,
            snack_details=log_in.snack_details,
            dinner_eaten=log_in.dinner_eaten if log_in.dinner_eaten is not None else True,
            dinner_details=log_in.dinner_details,
            water_ml=log_in.water_ml if log_in.water_ml is not None else 1500,
            water_glasses=log_in.water_glasses if log_in.water_glasses is not None else 6,
            meal_notes=log_in.meal_notes
        )
        db.add(db_log)
    else:
        if log_in.breakfast_eaten is not None:
            db_log.breakfast_eaten = log_in.breakfast_eaten
        if log_in.breakfast_details is not None:
            db_log.breakfast_details = log_in.breakfast_details
        if log_in.lunch_eaten is not None:
            db_log.lunch_eaten = log_in.lunch_eaten
        if log_in.lunch_details is not None:
            db_log.lunch_details = log_in.lunch_details
        if log_in.snack_eaten is not None:
            db_log.snack_eaten = log_in.snack_eaten
        if log_in.snack_details is not None:
            db_log.snack_details = log_in.snack_details
        if log_in.dinner_eaten is not None:
            db_log.dinner_eaten = log_in.dinner_eaten
        if log_in.dinner_details is not None:
            db_log.dinner_details = log_in.dinner_details
        if log_in.water_ml is not None:
            db_log.water_ml = log_in.water_ml
        if log_in.water_glasses is not None:
            db_log.water_glasses = log_in.water_glasses
        if log_in.meal_notes is not None:
            db_log.meal_notes = log_in.meal_notes

    db.commit()
    db.refresh(db_log)
    return db_log

def get_child_nutrition_logs(db: Session, child_id: int, limit: int = 14) -> List[NutritionLog]:
    return db.query(NutritionLog).filter(
        NutritionLog.child_id == child_id
    ).order_by(NutritionLog.date.desc()).limit(limit).all()

def get_nutrition_log_by_date(db: Session, child_id: int, log_date: datetime.date) -> Optional[NutritionLog]:
    return db.query(NutritionLog).filter(
        NutritionLog.child_id == child_id,
        NutritionLog.date == log_date
    ).first()


# --- Analytics, Consistency & Reminders ---

def get_nutrition_summary(db: Session, child_id: int, days: int = 7) -> NutritionSummaryResponse:
    logs = get_child_nutrition_logs(db=db, child_id=child_id, limit=days)
    total_days = len(logs)

    # Mother Agent Event Recommendations
    bridge_events = get_mother_agent_bridge_events(db=db, child_id=child_id)
    mother_recs = []
    for ev in bridge_events:
        items_str = ", ".join(ev.mother_agent_grocery_items) if ev.mother_agent_grocery_items else "extra hydration & energetic snacks"
        mother_recs.append(
            f"Event '{ev.event_name}' on {ev.date}: Children Agent recommends '{ev.child_recommendation}'. "
            f"Mother Agent suggested grocery sync: {items_str}."
        )

    if total_days == 0:
        return NutritionSummaryResponse(
            child_id=child_id,
            total_days_analyzed=0,
            meal_consistency="No logs recorded yet (100% default baseline)",
            meal_consistency_score=1.0,
            water_consistency="No logs recorded yet (100% default baseline)",
            water_consistency_score=1.0,
            skipped_meals_detected=[],
            has_skipped_meals=False,
            basic_nutrition_reminders=[
                "Start tracking daily meals and hydration for personalized routine tips.",
                "Aim for balanced meals with protein, healthy fats, and complex carbohydrates.",
                "Drink 6-8 glasses of fresh water daily."
            ],
            mother_agent_event_recommendations=mother_recs
        )


    # 1. Meal Consistency Calculation
    expected_main_meals = total_days * 3  # Breakfast, Lunch, Dinner
    actual_main_meals = sum(
        (1 if log.breakfast_eaten else 0) + 
        (1 if log.lunch_eaten else 0) + 
        (1 if log.dinner_eaten else 0) 
        for log in logs
    )
    meal_score = round(actual_main_meals / expected_main_meals, 2) if expected_main_meals > 0 else 1.0
    
    if meal_score >= 0.85:
        meal_status_str = "High meal regularity"
    elif meal_score >= 0.65:
        meal_status_str = "Moderate meal regularity"
    else:
        meal_status_str = "Irregular meal pattern detected"
    meal_consistency_desc = f"{int(meal_score * 100)}% ({meal_status_str})"

    # 2. Water Consistency Calculation
    target_water_ml = 1500
    avg_water = sum(log.water_ml for log in logs) / total_days
    water_score = min(1.0, round(avg_water / target_water_ml, 2))
    water_consistency_desc = f"{int(water_score * 100)}% (Average {int(avg_water)} ml / day)"

    # 3. Meal Skipping Detection
    skipped_breakfasts = sum(1 for log in logs if not log.breakfast_eaten)
    skipped_lunches = sum(1 for log in logs if not log.lunch_eaten)
    skipped_dinners = sum(1 for log in logs if not log.dinner_eaten)

    skipped_warnings = []
    if skipped_breakfasts > 0:
        skipped_warnings.append(
            f"Breakfast was skipped {skipped_breakfasts} time(s) in the past {total_days} days. "
            "Eating breakfast boosts morning focus and physical stamina."
        )
    if skipped_lunches > 0:
        skipped_warnings.append(
            f"Lunch was skipped {skipped_lunches} time(s) in the past {total_days} days. "
            "A nourishing lunch helps sustain afternoon study energy."
        )
    if skipped_dinners > 0:
        skipped_warnings.append(
            f"Dinner was skipped {skipped_dinners} time(s) in the past {total_days} days."
        )

    has_skipped = len(skipped_warnings) > 0

    # 4. Basic Nutrition Reminders
    reminders = [
        "Hydration Tip: Drink a glass of water right after waking up and between meals.",
        "Routine Reminder: Eat colorful fruits and fresh vegetables every day for vitamins and fiber.",
        "Energy Balance: Include healthy snacks (nuts, fruit, yogurt) to maintain steady energy levels."
    ]
    if water_score < 0.7:
        reminders.insert(0, "Hydration Warning: Increase daily water intake towards 6-8 glasses to prevent fatigue.")

    # 5. Mother Agent Event Recommendations
    bridge_events = get_mother_agent_bridge_events(db=db, child_id=child_id)
    mother_recs = []
    for ev in bridge_events:
        items_str = ", ".join(ev.mother_agent_grocery_items) if ev.mother_agent_grocery_items else "extra hydration & energetic snacks"
        mother_recs.append(
            f"Event '{ev.event_name}' on {ev.date}: Children Agent recommends '{ev.child_recommendation}'. "
            f"Mother Agent suggested grocery sync: {items_str}."
        )

    return NutritionSummaryResponse(
        child_id=child_id,
        total_days_analyzed=total_days,
        meal_consistency=meal_consistency_desc,
        meal_consistency_score=meal_score,
        water_consistency=water_consistency_desc,
        water_consistency_score=water_score,
        skipped_meals_detected=skipped_warnings,
        has_skipped_meals=has_skipped,
        basic_nutrition_reminders=reminders,
        mother_agent_event_recommendations=mother_recs
    )


# --- Mother Agent Integration Bridge ---

def create_mother_agent_bridge_event(db: Session, event_in: MotherAgentBridgeEventCreate) -> MotherAgentBridgeEvent:
    default_grocery = event_in.mother_agent_grocery_items
    if not default_grocery:
        if "sports" in event_in.event_name.lower():
            default_grocery = ["Fruit snacks", "Energy bars", "Hydration electrolyte drinks"]
        else:
            default_grocery = ["Fresh fruit", "Whole grain sandwiches", "Bottled water"]

    db_event = MotherAgentBridgeEvent(
        child_id=event_in.child_id,
        date=event_in.date,
        event_name=event_in.event_name,
        child_recommendation=event_in.child_recommendation or "Need extra snack/water.",
        mother_agent_grocery_items=default_grocery,
        status="PENDING_MOTHER_AGENT_SYNC"
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_mother_agent_bridge_events(db: Session, child_id: int) -> List[MotherAgentBridgeEvent]:
    return db.query(MotherAgentBridgeEvent).filter(
        MotherAgentBridgeEvent.child_id == child_id
    ).order_by(MotherAgentBridgeEvent.date.desc()).all()
