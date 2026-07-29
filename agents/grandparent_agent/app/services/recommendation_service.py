import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.vitals import Vitals
from app.models.activity import Activity
from app.models.nutrition import Nutrition
from app.schemas.recommendation import RecommendationResponse, RecommendationItem

logger = logging.getLogger(__name__)


def get_personalized_recommendations(db: Session) -> RecommendationResponse:
    logger.info("Recommendation Engine: Evaluating rule-based checks on patient logs")
    recommendations = []

    # 1. Blood Sugar & Heart Rate
    last_vitals = db.query(Vitals).order_by(Vitals.timestamp.desc()).first()
    if last_vitals:
        if last_vitals.blood_sugar > 180:
            recommendations.append(RecommendationItem(
                category="Diet",
                suggestion="Reduce sugar intake. Consult physician.",
                rationale=f"High blood sugar detected ({last_vitals.blood_sugar} mg/dL)."
            ))
        if last_vitals.heart_rate > 100:
            recommendations.append(RecommendationItem(
                category="Fitness",
                suggestion="Rest and monitor your pulse.",
                rationale=f"Elevated heart rate detected ({last_vitals.heart_rate} bpm)."
            ))

    # 2. Sleep Duration
    last_activity = db.query(Activity).order_by(Activity.date.desc()).first()
    if last_activity:
        if last_activity.sleep_hours < 6:
            recommendations.append(RecommendationItem(
                category="Sleep",
                suggestion="Aim for 7-8 hours of sleep. Try a calming tea or relaxation exercises before bed.",
                rationale=f"Sleep duration is insufficient ({last_activity.sleep_hours} hours)."
            ))

    # 3. Water Intake
    last_nutrition = db.query(Nutrition).order_by(Nutrition.timestamp.desc()).first()
    if last_nutrition:
        target_date = last_nutrition.timestamp.date()
        total_water = db.query(func.sum(Nutrition.water_ml)).filter(
            func.date(Nutrition.timestamp) == target_date
        ).scalar() or 0
        
        if total_water < 1500:
            recommendations.append(RecommendationItem(
                category="Diet",
                suggestion="Increase hydration.",
                rationale=f"Water intake ({total_water}ml) is below 1500ml."
            ))

    if not recommendations:
        recommendations.append(RecommendationItem(
            category="General",
            suggestion="Maintain your regular daily wellness routine.",
            rationale="All parameters checked (blood sugar, heart rate, sleep, water intake) are normal."
        ))

    logger.info("Recommendation Engine: Successfully generated %d wellness recommendation(s)", len(recommendations))
    return RecommendationResponse(
        summary=f"Rule-based health recommendation engine completed. {len(recommendations)} suggestion(s) issued.",
        recommendations=recommendations
    )
