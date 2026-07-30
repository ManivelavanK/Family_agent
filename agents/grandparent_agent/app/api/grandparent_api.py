from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api/grandparent", tags=["Grandparent Dashboard API"])

# In-memory store for grandparent dashboard state
GRANDPARENT_STATE = {
    "vitals": {
        "blood_pressure": {"value": "137/79 mmHg", "subtitle": "Stable", "badge": "Warning", "status": "warning"},
        "blood_sugar": {"value": "135.5 mg/dL", "subtitle": "Normal post-meal", "badge": "Normal", "status": "normal"},
        "heart_rate": {"value": "65 bpm", "subtitle": "Excellent", "badge": "Normal", "status": "normal"},
        "body_temp": {"value": "99.4 °F", "subtitle": "Normal", "badge": "Normal", "status": "normal"},
        "water_intake": {"value": "1200 ml", "subtitle": "Target: 2000ml", "badge": "Warning", "status": "warning"}
    },
    "medications": {
        "value": "6 Prescribed",
        "subtitle": "Next: Metformin 8:30 PM",
        "badge": "3 Taken"
    },
    "visits": {
        "value": "Dr. Srinivasa Raghavan",
        "subtitle": "Diabetologist & Endocrinologist",
        "badge": "2026-08-05"
    },
    "activity": {
        "value": "3200 steps",
        "subtitle": "Walking done",
        "badge": "Goal: 5000"
    }
}

@router.get("/vitals")
def get_vitals():
    return GRANDPARENT_STATE["vitals"]

@router.get("/medications")
def get_medications():
    return GRANDPARENT_STATE["medications"]

@router.get("/visits")
def get_visits():
    return GRANDPARENT_STATE["visits"]

@router.get("/activity")
def get_activity():
    return GRANDPARENT_STATE["activity"]

@router.post("/emergency")
def trigger_emergency():
    # In a real system, this would trigger SMS/WhatsApp logic to contacts
    return {
        "success": True, 
        "message": "Emergency SOS triggered! Primary contacts (Dr. Mani, Family) have been notified with your live location."
    }
