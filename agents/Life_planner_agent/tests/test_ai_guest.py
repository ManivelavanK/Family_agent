import datetime
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.services.guest_service import GuestService
from app.schemas.guest import GuestCreate, GuestUpdate
from app.models.memory import PlannerMemory, MemoryType
from app.services.plan_service import PlanService

def test_guest_crud_and_family_isolation(client, db_session):
    guest_a = GuestService.create_guest(db_session, GuestCreate(
        family_id="family_A",
        name="Uncle Bob",
        relationship="Uncle",
        adults=2,
        children=1,
        food_preferences="Vegetarian"
    ))

    guest_b = GuestService.create_guest(db_session, GuestCreate(
        family_id="family_B",
        name="Aunt Mary",
        relationship="Aunt",
        adults=1,
        children=0
    ))

    # Get guests for family A
    res_a = client.get("/api/v1/guests?family_id=family_A")
    assert res_a.status_code == 200
    data_a = res_a.json()["data"]
    assert len(data_a) == 1
    assert data_a[0]["name"] == "Uncle Bob"

    # Family A attempting to fetch Family B's guest -> 404
    res_cross = client.get(f"/api/v1/guests/{guest_b.id}?family_id=family_A")
    assert res_cross.status_code == 404

    # Update guest
    up_res = client.put(f"/api/v1/guests/{guest_a.id}?family_id=family_A", json={"notes": "Arriving by train"})
    assert up_res.status_code == 200
    assert up_res.json()["data"]["notes"] == "Arriving by train"

    # Delete guest
    del_res = client.delete(f"/api/v1/guests/{guest_a.id}?family_id=family_A")
    assert del_res.status_code == 200

@patch("app.ai.groq_client.Groq")
def test_ai_guest_planning_from_natural_language(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "guest_profile": {
                "name": "Uncle's Family",
                "relationship": "Uncle",
                "adults": 4,
                "children": 2,
                "arrival": "Next Friday",
                "departure": "Next Monday"
            },
            "stay_plan": {
                "guest_summary": "3-day stay for 6 family members (4 adults, 2 kids)",
                "accommodation_plan": "Prepare guest bedroom and living room sofa bed",
                "food_plan": "Vegetarian lunches, special kids snacks",
                "transport_plan": "Station pickup on Friday afternoon",
                "preparation_tasks": [
                    {
                        "title": "Clean Guest Bedroom",
                        "category": "CLEANING",
                        "due_date": null,
                        "estimated_cost": 0.0
                    }
                ],
                "daily_itinerary": [
                    {
                        "day_number": 1,
                        "date": null,
                        "focus": "Arrival & Rest",
                        "morning_activity": "Bed preparation",
                        "afternoon_activity": "Station pickup",
                        "evening_activity": "Welcome dinner at home",
                        "meals_plan": "Home-cooked South Indian dinner"
                    }
                ],
                "budget_breakdown": [
                    {
                        "category": "Grocery",
                        "estimated_cost": 5000.0,
                        "notes": "Extra milk, fruits, and snacks"
                    }
                ],
                "children_activities": ["Visit local park", "Board games evening"],
                "contingency_suggestions": ["Extra mattress ready in living room"]
            },
            "draft_plan": {
                "title": "Uncle Family Visit Stay Plan",
                "plan_type": "EVENT",
                "description": "3-day guest visit",
                "number_of_people": 6,
                "budget": 5000.0,
                "tasks": [],
                "budget_breakdown": [],
                "itinerary": [],
                "participants": []
            },
            "missing_information": ["Exact train arrival time"],
            "recommendations": ["Confirm dietary restrictions before Thursday"],
            "reasoning": "Planned stay itinerary balancing adult relaxation and kids activities.",
            "confidence": 0.92,
            "risks": ["Bedding shortage if extra guest arrives"],
            "supporting_facts": ["4 adults and 2 children requested"]
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/guest/plan", json={
        "family_id": "default_family",
        "message": "My uncle's family is coming next Friday and staying for 3 days. There will be 4 adults and 2 children."
    })

    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["guest_profile"]["adults"] == 4
    assert res_data["guest_profile"]["children"] == 2
    assert len(res_data["stay_plan"]["children_activities"]) == 2
    assert res_data["draft_plan"] is not None

@patch("app.ai.groq_client.Groq")
def test_guest_planning_with_memory_and_calendar(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Insert memory regarding uncle's food preference
    db_session.add(PlannerMemory(
        family_id="default_family",
        memory_type=MemoryType.FOOD_PREFERENCE,
        title="Uncle Food Preference",
        content="Uncle's family prefers strictly vegetarian food without garlic.",
        importance=5
    ))
    db_session.commit()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "guest_profile": {
                "name": "Uncle's Family",
                "relationship": "Uncle",
                "adults": 2,
                "children": 0,
                "arrival": null,
                "departure": null
            },
            "stay_plan": {
                "guest_summary": "Uncle visit plan tailored to vegetarian preference",
                "accommodation_plan": "Guest bedroom",
                "food_plan": "Strictly vegetarian meals without garlic",
                "transport_plan": "Pickup from airport",
                "preparation_tasks": [],
                "daily_itinerary": [],
                "budget_breakdown": [],
                "children_activities": [],
                "contingency_suggestions": []
            },
            "draft_plan": null,
            "missing_information": [],
            "recommendations": [],
            "reasoning": "Utilized retrieved family memory for uncle's no-garlic vegetarian food preference.",
            "confidence": 0.95,
            "risks": [],
            "supporting_facts": ["Retrieved memory 'Uncle Food Preference'"]
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/guest/plan", json={
        "family_id": "default_family",
        "message": "Uncle is visiting this weekend."
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert "vegetarian" in res_data["stay_plan"]["food_plan"].lower()

def test_approved_guest_plan_execution(client, db_session):
    draft_plan = {
        "title": "Approved Uncle Visit Plan",
        "plan_type": "EVENT",
        "description": "3-day family guest visit",
        "start_date": "2026-08-14",
        "end_date": "2026-08-16",
        "number_of_people": 6,
        "budget": 6000.0,
        "location": "Home",
        "tasks": [
            {
                "title": "Buy Grocery & Fruits",
                "description": "Guest preparations",
                "due_date": "2026-08-13",
                "priority": "HIGH",
                "estimated_cost": 4000.0
            }
        ],
        "budget_breakdown": [
            {
                "category": "Grocery",
                "estimated_amount": 4000.0,
                "status": "ESTIMATED"
            }
        ],
        "itinerary": [
            {
                "date": "2026-08-14",
                "start_time": "16:00:00",
                "end_time": "18:00:00",
                "activity": "Station Pickup",
                "location": "Railway Station",
                "estimated_cost": 500.0,
                "notes": "Pick up Uncle family"
            }
        ],
        "participants": [
            {
                "name": "Uncle Bob",
                "relationship": "Uncle"
            }
        ]
    }

    # Execute approved plan
    exec_res = client.post("/api/v1/ai/plan/execute", json={
        "approved": True,
        "family_id": "default_family",
        "draft_plan": draft_plan
    })
    assert exec_res.status_code == 201
    plan_id = exec_res.json()["data"]["plan_id"]

    db_plan = PlanService.get_plan_by_id(db_session, plan_id)
    assert db_plan is not None
    assert db_plan.title == "Approved Uncle Visit Plan"
    assert len(db_plan.tasks) == 1

def test_unapproved_guest_execution_rejection(client):
    draft_plan = {
        "title": "Unapproved Guest Plan",
        "plan_type": "EVENT",
        "number_of_people": 4,
        "budget": 2000.0,
        "tasks": [],
        "budget_breakdown": [],
        "itinerary": [],
        "participants": []
    }
    exec_res = client.post("/api/v1/ai/plan/execute", json={
        "approved": False,
        "family_id": "default_family",
        "draft_plan": draft_plan
    })
    assert exec_res.status_code == 400
    assert "Explicit approval" in exec_res.json()["detail"]

def test_malformed_groq_guest_response(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    with patch("app.ai.groq_client.Groq") as mock_groq:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Malformed plain text response"))
        ]
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_instance

        res = client.post("/api/v1/ai/guest/plan", json={
            "family_id": "default_family",
            "message": "Uncle visiting next week"
        })
        assert res.status_code == 502
        assert "invalid or malformed JSON" in res.json()["detail"]
