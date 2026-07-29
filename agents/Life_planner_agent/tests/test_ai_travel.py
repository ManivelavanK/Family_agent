import datetime
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.models.memory import PlannerMemory, MemoryType
from app.models.calendar import CalendarEvent, EventType
from app.services.plan_service import PlanService

def test_missing_groq_api_key_travel_planning(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    res = client.post("/api/v1/ai/travel/plan", json={
        "family_id": "default_family",
        "message": "Plan a 4-day family trip to Ooty."
    })
    assert res.status_code == 503
    assert "Groq API key is missing" in res.json()["detail"]

@patch("app.ai.groq_client.Groq")
def test_natural_language_travel_extraction_and_plan_a_b(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "travel_plan": {
                "title": "Ooty Family Refreshing Getaway",
                "destination": "Ooty",
                "summary": "4-day family vacation to Ooty for 6 people under 30,000 INR",
                "requirements": {
                    "destination": "Ooty",
                    "origin": "Chennai",
                    "start_date": "2026-08-15",
                    "end_date": "2026-08-18",
                    "duration_days": 4,
                    "traveler_count": 6,
                    "adults": 4,
                    "children": 2,
                    "infants": 0,
                    "budget": 30000.0,
                    "transport_preference": "Train",
                    "accommodation_preference": "Resort",
                    "trip_style": "Nature & Relaxation",
                    "special_requirements": null
                },
                "trip_style": "Nature & Relaxation",
                "travel_pace": "BALANCED",
                "daily_itinerary": [
                    {
                        "day_number": 1,
                        "date": "2026-08-15",
                        "focus": "Arrival & Botanical Garden",
                        "morning": "Overnight train arrival & check-in",
                        "afternoon": "Stroll at Ooty Lake",
                        "evening": "Tea factory visit & rest",
                        "meals": "Breakfast at hotel, Lunch at lake cafe",
                        "travel_notes": "Take local cab to hotel",
                        "estimated_daily_cost": 5000.0,
                        "family_considerations": "Keep afternoon pace gentle for kids"
                    }
                ],
                "budget": {
                    "transport": 8000.0,
                    "accommodation": 12000.0,
                    "food": 6000.0,
                    "activities": 2000.0,
                    "local_transport": 1000.0,
                    "emergency_contingency": 1000.0,
                    "estimated_total": 30000.0,
                    "budget_assessment": "Realistic budget allocation for 6 people",
                    "reasoning": "Allocated 40% for accommodation and 26% for train travel."
                },
                "packing_list": [
                    {
                        "category": "Clothing",
                        "items": ["Warm jackets", "Sweaters", "Comfortable walking shoes"],
                        "reasoning": "Ooty hill station weather requires warm layers.",
                        "priority": "HIGH"
                    }
                ],
                "risks": [
                    {
                        "risk": "Hill transit motion sickness",
                        "severity": "MEDIUM",
                        "reasoning": "Winding mountain roads to Ooty",
                        "mitigation": "Carry motion sickness medication"
                    }
                ],
                "plan_a_summary": "Primary outdoor sightseeing and nature walk itinerary.",
                "plan_b_contingency": {
                    "title": "Indoor & Heritage Tea Museum Alternative",
                    "description": "Indoor alternative in case of heavy hill rains.",
                    "tradeoffs": "Less outdoor lake walking, more museum and indoor tea tasting.",
                    "estimated_cost": 28000.0,
                    "why_recommended": "Protects trip experience during rainy hill weather."
                },
                "alternatives": [],
                "family_considerations": ["Gentle walking pace for multi-generational group"],
                "calendar_considerations": ["No overlapping family events during August 15-18"],
                "memory_influences": []
            },
            "draft_plan": {
                "title": "Ooty Family Vacation",
                "plan_type": "TRAVEL",
                "description": "4-day Ooty trip",
                "start_date": "2026-08-15",
                "end_date": "2026-08-18",
                "number_of_people": 6,
                "budget": 30000.0,
                "tasks": [],
                "budget_breakdown": [],
                "itinerary": [],
                "participants": []
            },
            "missing_information": [],
            "recommendations": ["Book toy train tickets 30 days in advance"],
            "reasoning": "Extracted requirements for 6 travelers, generated Plan A/Plan B contingency, and allocated 30,000 INR budget.",
            "confidence": 0.94
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/travel/plan", json={
        "family_id": "default_family",
        "message": "Plan a 4-day family trip to Ooty for 6 people with a budget of 30000 INR from August 15 to August 18."
    })

    assert res.status_code == 200
    res_data = res.json()["data"]
    plan = res_data["travel_plan"]
    assert plan["destination"] == "Ooty"
    assert plan["travel_pace"] == "BALANCED"
    assert plan["plan_b_contingency"]["title"] == "Indoor & Heritage Tea Museum Alternative"
    assert len(plan["packing_list"]) == 1
    assert len(plan["risks"]) == 1

@patch("app.ai.groq_client.Groq")
def test_family_memory_personalization_in_travel(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Add memory: family dislikes crowded places
    db_session.add(PlannerMemory(
        family_id="default_family",
        memory_type=MemoryType.DESTINATION_PREFERENCE,
        title="Quiet Vacation Preference",
        content="Family dislikes crowded commercial tourist spots; prefers quiet nature retreats.",
        importance=5
    ))
    db_session.commit()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "travel_plan": {
                "title": "Quiet Nature Family Retreat",
                "destination": "Coonoor",
                "summary": "Quiet retreat personalized based on family memory",
                "requirements": {
                    "destination": "Coonoor",
                    "duration_days": 3,
                    "budget": 25000.0
                },
                "trip_style": "Peaceful Nature",
                "travel_pace": "RELAXED",
                "daily_itinerary": [],
                "budget": {
                    "transport": 5000.0,
                    "accommodation": 12000.0,
                    "food": 5000.0,
                    "activities": 2000.0,
                    "local_transport": 1000.0,
                    "emergency_contingency": 0.0,
                    "estimated_total": 25000.0,
                    "budget_assessment": "Good budget fit",
                    "reasoning": "Prioritized quiet boutique stay over commercial resort."
                },
                "packing_list": [],
                "risks": [],
                "plan_a_summary": "Quiet Coonoor estate walk",
                "plan_b_contingency": {
                    "title": "Estate indoor tea lounge",
                    "description": "Quiet indoor alternative",
                    "tradeoffs": "None",
                    "estimated_cost": 25000.0,
                    "why_recommended": "Protects peaceful experience"
                },
                "alternatives": [],
                "family_considerations": ["Selected off-beat quiet destination"],
                "calendar_considerations": [],
                "memory_influences": ["Retrieved memory: Family dislikes crowded commercial spots"]
            },
            "draft_plan": null,
            "missing_information": [],
            "recommendations": [],
            "reasoning": "Personalized trip destination to Coonoor based on retrieved memory preference for quiet nature retreats.",
            "confidence": 0.95
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/travel/plan", json={
        "family_id": "default_family",
        "message": "Plan our next family weekend getaway."
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert "Peaceful Nature" in res_data["travel_plan"]["trip_style"]
    assert len(res_data["travel_plan"]["memory_influences"]) == 1

@patch("app.ai.groq_client.Groq")
def test_calendar_aware_travel_planning(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Add overlapping calendar event
    cal = CalendarEvent(
        title="Grandparent Health Checkup",
        event_type=EventType.APPOINTMENT,
        start_datetime=datetime.datetime(2026, 8, 16, 10, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2026, 8, 16, 12, 0, tzinfo=datetime.timezone.utc)
    )
    db_session.add(cal)
    db_session.commit()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "travel_plan": {
                "title": "Adjusted Family Trip",
                "destination": "Yercaud",
                "summary": "Trip planned considering August 16 appointment",
                "requirements": {
                    "destination": "Yercaud"
                },
                "trip_style": "Short Getaway",
                "travel_pace": "BALANCED",
                "daily_itinerary": [],
                "budget": {
                    "transport": 4000.0,
                    "accommodation": 8000.0,
                    "food": 4000.0,
                    "activities": 2000.0,
                    "local_transport": 1000.0,
                    "emergency_contingency": 1000.0,
                    "estimated_total": 20000.0,
                    "budget_assessment": "Sufficient",
                    "reasoning": "Standard allocation"
                },
                "packing_list": [],
                "risks": [],
                "plan_a_summary": "Departure on August 17 after appointment",
                "plan_b_contingency": {
                    "title": "Local day trip alternative",
                    "description": "Alternative if appointment cannot be rescheduled",
                    "tradeoffs": "Shorter duration",
                    "estimated_cost": 15000.0,
                    "why_recommended": "Avoids missing doctor checkup"
                },
                "alternatives": [],
                "family_considerations": [],
                "calendar_considerations": ["Conflict flagged: Grandparent Health Checkup on August 16"],
                "memory_influences": []
            },
            "draft_plan": null,
            "missing_information": [],
            "recommendations": ["Reschedule appointment or adjust start date to August 17"],
            "reasoning": "Identified calendar conflict on August 16 and adjusted start recommendations.",
            "confidence": 0.91
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/travel/plan", json={
        "family_id": "default_family",
        "message": "Plan a family trip from August 15 to August 18."
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert len(res_data["travel_plan"]["calendar_considerations"]) == 1

@patch("app.ai.groq_client.Groq")
def test_travel_quality_analysis(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "family_suitability_score": 9.0,
            "itinerary_realism_score": 8.5,
            "budget_quality_score": 8.8,
            "travel_pace_score": 9.2,
            "overall_score": 8.9,
            "strengths": ["Excellent relaxed pace for children and adults", "Clear Plan B contingency"],
            "weaknesses": ["Tight local transport buffer"],
            "risks": ["Potential hill station rain"],
            "improvements": ["Add 30 min buffer for station transfer"],
            "reasoning": "High overall score due to realistic pace and clear Plan B backup.",
            "confidence": 0.95
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    sample_travel_plan = {
        "title": "Ooty Trip",
        "destination": "Ooty",
        "summary": "4-day trip",
        "requirements": {"destination": "Ooty"},
        "trip_style": "Relaxed",
        "travel_pace": "RELAXED",
        "daily_itinerary": [],
        "budget": {
            "transport": 5000.0,
            "accommodation": 10000.0,
            "food": 5000.0,
            "activities": 2000.0,
            "local_transport": 1000.0,
            "emergency_contingency": 1000.0,
            "estimated_total": 24000.0,
            "budget_assessment": "Good",
            "reasoning": "Balanced"
        },
        "packing_list": [],
        "risks": [],
        "plan_a_summary": "Outdoor sightseeing",
        "plan_b_contingency": {
            "title": "Indoor museum",
            "description": "Rain alternative",
            "tradeoffs": "Indoor only",
            "estimated_cost": 22000.0,
            "why_recommended": "Rain fallback"
        },
        "alternatives": [],
        "family_considerations": [],
        "calendar_considerations": [],
        "memory_influences": []
    }

    res = client.post("/api/v1/ai/travel/analyze?family_id=default_family", json=sample_travel_plan)
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["overall_score"] == 8.9
    assert len(res_data["strengths"]) == 2

def test_approved_travel_plan_execution(client, db_session):
    draft_plan = {
        "title": "Approved Ooty Vacation Plan",
        "plan_type": "TRAVEL",
        "description": "4-day trip to Ooty",
        "start_date": "2026-08-15",
        "end_date": "2026-08-18",
        "number_of_people": 6,
        "budget": 30000.0,
        "location": "Ooty",
        "tasks": [
            {
                "title": "Book Train Tickets",
                "description": "Round trip Chennai to Ooty",
                "due_date": "2026-08-01",
                "priority": "HIGH",
                "estimated_cost": 8000.0
            }
        ],
        "budget_breakdown": [
            {
                "category": "Accommodation",
                "estimated_amount": 12000.0,
                "status": "ESTIMATED"
            }
        ],
        "itinerary": [
            {
                "date": "2026-08-15",
                "start_time": "09:00:00",
                "end_time": "12:00:00",
                "activity": "Botanical Garden Walk",
                "location": "Ooty Botanical Garden",
                "estimated_cost": 500.0,
                "notes": "Gentle stroll"
            }
        ],
        "participants": [
            {
                "name": "Father",
                "relationship": "Father"
            }
        ]
    }

    res = client.post("/api/v1/ai/plan/execute", json={
        "approved": True,
        "family_id": "default_family",
        "draft_plan": draft_plan
    })
    assert res.status_code == 201
    plan_id = res.json()["data"]["plan_id"]

    db_plan = PlanService.get_plan_by_id(db_session, plan_id)
    assert db_plan is not None
    assert db_plan.title == "Approved Ooty Vacation Plan"
    assert db_plan.plan_type.value == "TRAVEL"
    assert len(db_plan.tasks) == 1
