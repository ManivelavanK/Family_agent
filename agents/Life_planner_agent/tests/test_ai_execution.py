import datetime
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.ai.schemas import AIPlanDraft, AITaskDraft, AIBudgetItemDraft, AIItineraryItemDraft, AIParticipantDraft
from app.services.plan_service import PlanService

def test_execution_requires_approval(client):
    draft = {
        "title": "Unapproved Trip",
        "plan_type": "TRAVEL",
        "number_of_people": 2,
        "budget": 10000.0,
        "tasks": [],
        "budget_breakdown": [],
        "itinerary": [],
        "participants": []
    }
    # Unapproved request -> approved: false
    res = client.post("/api/v1/ai/plan/execute", json={
        "approved": False,
        "family_id": "family_A",
        "draft_plan": draft
    })
    assert res.status_code == 400
    assert "Explicit approval" in res.json()["detail"]

def test_successful_plan_execution(client, db_session):
    draft = {
        "title": "Executed Birthday Bash",
        "plan_type": "EVENT",
        "description": "Party for 10 people",
        "start_date": "2026-09-10",
        "end_date": "2026-09-10",
        "number_of_people": 10,
        "budget": 15000.0,
        "location": "Community Center",
        "tasks": [
            {
                "title": "Order Cake",
                "description": "Chocolate cake",
                "due_date": "2026-09-08",
                "priority": "HIGH",
                "estimated_cost": 2000.0
            }
        ],
        "budget_breakdown": [
            {
                "category": "Catering",
                "description": "Buffet lunch",
                "estimated_amount": 8000.0,
                "status": "ESTIMATED"
            }
        ],
        "itinerary": [
            {
                "date": "2026-09-10",
                "start_time": "12:00:00",
                "end_time": "15:00:00",
                "activity": "Party Celebration",
                "location": "Community Center",
                "estimated_cost": 10000.0,
                "notes": "Bring gift table"
            }
        ],
        "participants": [
            {
                "name": "Uncle John",
                "relationship": "Uncle"
            }
        ]
    }

    res = client.post("/api/v1/ai/plan/execute", json={
        "approved": True,
        "family_id": "family_A",
        "draft_plan": draft
    })
    assert res.status_code == 201
    summary = res.json()["data"]
    plan_id = summary["plan_id"]
    assert summary["created"]["tasks"] == 1
    assert summary["created"]["budget_items"] == 1
    assert summary["created"]["itinerary_items"] == 1
    assert summary["created"]["participants"] == 1
    assert summary["created"]["calendar_events"] == 1

    # Verify Plan exists in database
    db_plan = PlanService.get_plan_by_id(db_session, plan_id)
    assert db_plan is not None
    assert db_plan.title == "Executed Birthday Bash"
    assert len(db_plan.tasks) == 1
    assert len(db_plan.calendar_events) == 1

@patch("app.ai.groq_client.Groq")
def test_ai_plan_revision(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    plan_res = client.post("/api/v1/plans", json={"plan_type": "EVENT", "title": "Birthday Party"})
    plan_id = plan_res.json()["data"]["id"]

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "revised_draft": {
                "title": "Revised Birthday Party",
                "plan_type": "EVENT",
                "description": "Revised with less decoration",
                "start_date": null,
                "end_date": null,
                "number_of_people": 15,
                "budget": 10000.0,
                "location": null,
                "tasks": [],
                "budget_breakdown": [
                    {
                        "category": "Food",
                        "description": "Increased food budget",
                        "estimated_amount": 7000.0,
                        "status": "ESTIMATED"
                    },
                    {
                        "category": "Decoration",
                        "description": "Reduced decoration budget",
                        "estimated_amount": 3000.0,
                        "status": "ESTIMATED"
                    }
                ],
                "itinerary": [],
                "participants": []
            },
            "changes_explanation": "Reallocated 2000 INR from decoration to food.",
            "calendar_impact": [],
            "reasoning": "User requested reallocating decoration budget towards food."
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/plan/revise", json={
        "plan_id": plan_id,
        "message": "Reduce decoration spending and give more budget to food.",
        "family_id": "default_family"
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert "Reallocated" in res_data["changes_explanation"]
    assert res_data["revised_draft"]["title"] == "Revised Birthday Party"

@patch("app.ai.groq_client.Groq")
def test_ai_plan_optimization(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    plan_res = client.post("/api/v1/plans", json={"plan_type": "TRAVEL", "title": "Ooty Trip"})
    plan_id = plan_res.json()["data"]["id"]

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "optimized_draft": {
                "title": "Optimized Ooty Trip",
                "plan_type": "TRAVEL",
                "description": "Optimized for budget under 25000 INR",
                "number_of_people": 4,
                "budget": 25000.0,
                "tasks": [],
                "budget_breakdown": [],
                "itinerary": [],
                "participants": []
            },
            "optimization_summary": "Reduced accommodation choices to budget lodge.",
            "reasoning": "Switched hotel category to meet budget constraint."
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/plan/optimize", json={
        "plan_id": plan_id,
        "optimization_goal": "Reduce this trip to Rs 25000",
        "family_id": "default_family"
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["optimized_draft"]["budget"] == 25000.0

@patch("app.ai.groq_client.Groq")
def test_ai_plan_quality_analysis(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    plan_res = client.post("/api/v1/plans", json={"plan_type": "FUNCTION", "title": "Wedding Reception"})
    plan_id = plan_res.json()["data"]["id"]

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "budget_score": 8.5,
            "schedule_score": 9.0,
            "family_fit_score": 8.0,
            "preparation_score": 7.5,
            "risk_score": 8.8,
            "overall_score": 8.4,
            "strengths": ["Well structured timeline", "Clear participant list"],
            "concerns": ["Catering buffer is narrow"],
            "recommendations": ["Add 10% catering contingency"],
            "reasoning": "High overall quality with minor catering contingency recommendation."
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post(f"/api/v1/ai/plan/analyze/{plan_id}?family_id=default_family")
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["overall_score"] == 8.4
    assert len(res_data["strengths"]) == 2
