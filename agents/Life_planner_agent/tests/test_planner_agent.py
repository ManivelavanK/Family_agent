import datetime
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.models.planner_extensions import GoalCategory, HabitCategory

def test_goals_crud(client):
    # 1. Create a goal
    res = client.post("/api/v1/planner/goals", json={
        "title": "Study Python",
        "description": "Learn advanced structures",
        "category": "ACADEMIC",
        "progress": 20.0,
        "deadline": str(datetime.date.today() + datetime.timedelta(days=5)),
        "family_id": "default_family"
    })
    assert res.status_code == 201
    goal_data = res.json()["data"]
    assert goal_data["title"] == "Study Python"
    goal_id = goal_data["id"]

    # 2. Get goals
    res_get = client.get("/api/v1/planner/goals?family_id=default_family")
    assert res_get.status_code == 200
    assert len(res_get.json()["data"]) >= 1

    # 3. Update goal progress
    res_up = client.put(f"/api/v1/planner/goals/{goal_id}", json={
        "progress": 65.0
    })
    assert res_up.status_code == 200
    assert res_up.json()["data"]["progress"] == 65.0

    # 4. Delete goal
    res_del = client.delete(f"/api/v1/planner/goals/{goal_id}")
    assert res_del.status_code == 200

def test_habits_and_logging(client):
    # 1. Create habit
    res = client.post("/api/v1/planner/habits", json={
        "title": "Drink Water Daily",
        "category": "WATER",
        "family_id": "default_family"
    })
    assert res.status_code == 201
    habit_data = res.json()["data"]
    assert habit_data["title"] == "Drink Water Daily"
    habit_id = habit_data["id"]

    # 2. Log habit completion for today
    res_log = client.post(f"/api/v1/planner/habits/{habit_id}/log", json={
        "date": str(datetime.date.today()),
        "completed": True
    })
    assert res_log.status_code == 200
    assert res_log.json()["data"]["completed"] is True

    # 3. Fetch habits list
    res_list = client.get("/api/v1/planner/habits?family_id=default_family")
    assert res_list.status_code == 200
    assert len(res_list.json()["data"]) >= 1

def test_digital_twin_metrics(client):
    res = client.get("/api/v1/planner/twin?family_id=default_family")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "planning_score" in data
    assert "routine_consistency" in data
    assert "stress_level" in data

@patch("app.ai.groq_client.Groq")
def test_planner_agent_natural_language_endpoint(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "intent": "Academic Performance Planning",
            "strategy": "Retrieve academic events and memories.",
            "tools_to_call": ["get_goals", "detect_conflicts"],
            "family_agents_to_query": ["child"],
            "capabilities": ["Academic Tracking"],
            "response": "I have set your daily study session and verified no calendar conflicts remain.",
            "action_items": ["Study session blocked at 4 PM", "Reschedule family dinner to 7 PM"],
            "agents_used": ["PlannerAgent", "ChildAgent"],
            "tools_used": ["CalendarConflictDetector", "SemanticMemory"],
            "confidence": 0.95
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/planner/agent", json={
        "message": "Optimize my schedule next week for child exams.",
        "family_id": "default_family"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert "ai_response" in data
    assert len(data["action_items"]) == 2
    assert data["execution_trace"]["intent"] == "Academic Performance Planning"
