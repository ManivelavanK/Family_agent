from unittest.mock import MagicMock, patch
import pytest
from app.config import settings

def test_missing_groq_api_key(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    response = client.post("/api/v1/ai/plan", json={"message": "Plan a party"})
    assert response.status_code == 503
    assert "Groq API key is missing" in response.json()["detail"]

@patch("app.ai.groq_client.Groq")
def test_ai_planning_party_mocked(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "plan_type": "EVENT",
            "title": "Sister's Birthday Party",
            "intent": "Plan birthday party for sister",
            "requirements": {
                "destination": null,
                "duration_days": 1,
                "people": 15,
                "budget": null,
                "start_date": null,
                "end_date": null,
                "location": null,
                "special_notes": null
            },
            "missing_information": ["exact date", "budget limit"],
            "preferences": ["family friendly"],
            "constraints": [],
            "reasoning_summary": "15 people event inferred as birthday party.",
            "recommendations": ["Book venue early"],
            "draft_plan": null,
            "next_action": "NEED_MORE_INFO"
        }"""))
    ]
    
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    response = client.post("/api/v1/ai/plan", json={"message": "Plan my sister's birthday for 15 people."})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert res_data["plan_type"] == "EVENT"
    assert res_data["requirements"]["people"] == 15
    assert "exact date" in res_data["missing_information"]

@patch("app.ai.groq_client.Groq")
def test_ai_planning_ooty_trip_mocked(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "plan_type": "TRAVEL",
            "title": "3-Day Family Ooty Trip",
            "intent": "Plan 3-day family trip to Ooty for 6 people under 30000 budget",
            "requirements": {
                "destination": "Ooty",
                "duration_days": 3,
                "people": 6,
                "budget": 30000.0,
                "start_date": null,
                "end_date": null,
                "location": "Ooty",
                "special_notes": "Family trip"
            },
            "missing_information": ["preferred travel dates"],
            "preferences": ["cozy hotel", "scenic spots"],
            "constraints": ["budget under 30000 INR"],
            "reasoning_summary": "Extracted travel details for Ooty for 6 family members.",
            "recommendations": ["Book Toy Train tickets in advance"],
            "draft_plan": {
                "title": "3-Day Family Ooty Trip",
                "plan_type": "TRAVEL",
                "description": "Scenic trip to Ooty for 6 people",
                "number_of_people": 6,
                "budget": 30000.0,
                "location": "Ooty",
                "tasks": [
                    {
                        "title": "Reserve Ooty hotel",
                        "description": "Book 2 family rooms",
                        "priority": "HIGH",
                        "estimated_cost": 15000.0
                    }
                ],
                "budget_breakdown": [
                    {
                        "category": "Accommodation",
                        "estimated_amount": 15000.0,
                        "status": "ESTIMATED"
                    }
                ],
                "itinerary": [],
                "participants": []
            },
            "next_action": "GENERATE_DRAFT"
        }"""))
    ]

    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    response = client.post("/api/v1/ai/plan", json={"message": "Plan a 3-day family trip to Ooty for 6 people under ₹30,000."})
    assert response.status_code == 200
    res_data = response.json()["data"]
    assert res_data["plan_type"] == "TRAVEL"
    assert res_data["requirements"]["destination"] == "Ooty"
    assert res_data["requirements"]["duration_days"] == 3
    assert res_data["requirements"]["people"] == 6
    assert res_data["requirements"]["budget"] == 30000.0

@patch("app.ai.groq_client.Groq")
def test_ai_malformed_json_response(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Invalid json text"))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    response = client.post("/api/v1/ai/plan", json={"message": "Plan something"})
    assert response.status_code == 502
    assert "invalid or malformed JSON format" in response.json()["detail"]
