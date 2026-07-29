import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.vitals import Vitals
from app.models.activity import Activity
from app.models.nutrition import Nutrition
from app.schemas.analytics import AnalyticsSummaryResponse, VitalsSummary, ActivitySummary

logger = logging.getLogger(__name__)


def get_analytics_summary(db: Session) -> AnalyticsSummaryResponse:
    # 1. Vitals validation
    vitals_count = db.query(Vitals).count()
    if vitals_count == 0:
        vitals_result = "No vitals data"
    else:
        vitals_avg = db.query(
            func.avg(Vitals.blood_pressure_systolic).label("sys"),
            func.avg(Vitals.blood_pressure_diastolic).label("dia"),
            func.avg(Vitals.heart_rate).label("hr"),
            func.avg(Vitals.blood_sugar).label("bs"),
        ).first()
        vitals_result = VitalsSummary(
            avg_systolic=round(vitals_avg.sys, 2) if vitals_avg.sys else None,
            avg_diastolic=round(vitals_avg.dia, 2) if vitals_avg.dia else None,
            avg_heart_rate=round(vitals_avg.hr, 2) if vitals_avg.hr else None,
            avg_blood_sugar=round(vitals_avg.bs, 2) if vitals_avg.bs else None,
        )

    # 2. Activity validation
    activity_count = db.query(Activity).count()
    if activity_count == 0:
        activity_result = "No activity data"
    else:
        activity_totals = db.query(
            func.sum(Activity.steps).label("steps"),
            func.avg(Activity.sleep_hours).label("sleep"),
            func.sum(Activity.duration_minutes).label("duration"),
        ).first()
        activity_result = ActivitySummary(
            total_steps=int(activity_totals.steps) if activity_totals.steps else 0,
            avg_sleep_hours=round(activity_totals.sleep, 2) if activity_totals.sleep else 0.0,
            total_active_minutes=int(activity_totals.duration) if activity_totals.duration else 0,
        )

    # 3. Nutrition validation
    nutrition_count = db.query(Nutrition).count()
    if nutrition_count == 0:
        calories_result = "No nutrition data"
        water_result = "No nutrition data"
    else:
        calories_sum = db.query(func.sum(Nutrition.calories)).scalar() or 0.0
        water_sum = db.query(func.sum(Nutrition.water_ml)).scalar() or 0
        calories_result = float(calories_sum)
        water_result = int(water_sum)

    return AnalyticsSummaryResponse(
        vitals=vitals_result,
        activity=activity_result,
        nutrition_calories=calories_result,
        water_intake_ml=water_result
    )
