import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def evaluate_blood_pressure(systolic: int) -> Optional[Dict[str, str]]:
    if systolic > 140:
        return {
            "severity": "High",
            "title": "High Blood Pressure",
            "description": "Blood pressure is above the recommended level.",
            "recommended_action": "Consult your physician."
        }
    return None


def evaluate_blood_sugar(sugar: float) -> Optional[Dict[str, str]]:
    if sugar > 180:
        return {
            "severity": "High",
            "title": "High Blood Sugar",
            "description": "Blood sugar is above the recommended level.",
            "recommended_action": "Reduce sugar intake and consult your doctor."
        }
    return None


def evaluate_heart_rate(heart_rate: int) -> Optional[Dict[str, str]]:
    if heart_rate > 100:
        return {
            "severity": "High",
            "title": "High Heart Rate",
            "description": "Heart rate is elevated.",
            "recommended_action": "Rest and monitor your heart rate."
        }
    return None


def evaluate_sleep_hours(sleep_hours: float) -> Optional[Dict[str, str]]:
    if sleep_hours < 6:
        return {
            "severity": "Medium",
            "title": "Poor Sleep",
            "description": "Sleep duration is below the recommended 6 hours.",
            "recommended_action": "Avoid screens before bed and maintain a sleep schedule."
        }
    return None


def evaluate_water_intake(water_ml: int) -> Optional[Dict[str, str]]:
    if water_ml < 1500:
        return {
            "severity": "Medium",
            "title": "Low Water Intake",
            "description": "Hydration level is insufficient.",
            "recommended_action": "Increase water intake."
        }
    return None


def evaluate_medicine_missed(is_missed: bool, med_name: str = "") -> Optional[Dict[str, str]]:
    if is_missed:
        name_info = f" ({med_name})" if med_name else ""
        return {
            "severity": "High",
            "title": "Missed Medication",
            "description": f"Scheduled medication dose{name_info} has been missed.",
            "recommended_action": "Take your scheduled medication or contact a caregiver."
        }
    return None
