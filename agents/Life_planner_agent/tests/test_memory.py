from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.services.memory_service import MemoryService
from app.schemas.memory import PlannerMemoryCreate
from app.ai.tool_registry import tool_registry

def test_memory_crud_and_family_isolation(client, db_session):
    # Create memory for family A
    mem_a = MemoryService.create_memory(db_session, PlannerMemoryCreate(
        family_id="family_A",
        memory_type="PREFERENCE",
        title="Family A Preference",
        content="Prefer quiet beach resorts",
        importance=4
    ))
    
    # Create memory for family B
    mem_b = MemoryService.create_memory(db_session, PlannerMemoryCreate(
        family_id="family_B",
        memory_type="PREFERENCE",
        title="Family B Preference",
        content="Prefer mountain hiking",
        importance=5
    ))

    # Get memories for Family A -> should return only family A's memory
    res_a = client.get("/api/v1/memory?family_id=family_A")
    assert res_a.status_code == 200
    data_a = res_a.json()["data"]
    assert len(data_a) == 1
    assert data_a[0]["title"] == "Family A Preference"

    # Family A attempting to access Family B's memory directly -> 404 Not Found
    res_cross = client.get(f"/api/v1/memory/{mem_b.id}?family_id=family_A")
    assert res_cross.status_code == 404

    # Delete memory
    del_res = client.delete(f"/api/v1/memory/{mem_a.id}?family_id=family_A")
    assert del_res.status_code == 200

@patch("app.ai.groq_client.Groq")
def test_ai_memory_extraction_persistent_preference(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "should_remember": true,
            "reasoning": "User expressed persistent destination and crowd preference for future trips.",
            "memories": [
                {
                    "memory_type": "DESTINATION_PREFERENCE",
                    "title": "Quiet Hill Station Preference",
                    "content": "Family prefers quiet hill stations and dislikes crowded tourist spots.",
                    "importance": 4,
                    "source_type": "CONVERSATION",
                    "source_id": null
                }
            ]
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/memory/extract", json={
        "text_content": "We prefer hill stations and don't like very crowded tourist places.",
        "family_id": "family_A"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["should_remember"] is True
    assert len(data["memories"]) == 1
    assert data["memories"][0]["memory_type"] == "DESTINATION_PREFERENCE"

@patch("app.ai.groq_client.Groq")
def test_ai_memory_extraction_temporary_statement(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "should_remember": false,
            "reasoning": "Statement is a one-time temporary action request without persistent preference value.",
            "memories": []
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/memory/extract", json={
        "text_content": "Plan something for tomorrow afternoon.",
        "family_id": "family_A"
    })
    assert res.status_code == 200
    assert res.json()["data"]["should_remember"] is False
    assert len(res.json()["data"]["memories"]) == 0

def test_plan_reflection_and_automatic_memory(client):
    # Create plan
    plan_res = client.post("/api/v1/plans", json={"plan_type": "EVENT", "title": "Annual Birthday Party"})
    plan_id = plan_res.json()["data"]["id"]

    with patch("app.ai.groq_client.Groq") as mock_groq:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="""{
                "should_remember": true,
                "reasoning": "Post-event lesson learned regarding food waste.",
                "memories": [
                    {
                        "memory_type": "LESSON_LEARNED",
                        "title": "Reduce Birthday Party Food Quantities",
                        "content": "Excess food waste reported in previous birthday party; reduce estimates for future parties.",
                        "importance": 4,
                        "source_type": "PLAN_REFLECTION",
                        "source_id": """ + str(plan_id) + """
                    }
                ]
            }"""))
        ]
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_instance

        # Post Reflection
        ref_res = client.post("/api/v1/reflections", json={
            "plan_id": plan_id,
            "rating": 4,
            "what_went_well": "Decorations were great",
            "what_went_wrong": "Food was too much",
            "feedback": "We wasted a lot of catering food",
            "future_suggestions": "Order less food next time"
        })
        assert ref_res.status_code == 201

        # Check that reflection was retrieved
        get_ref = client.get(f"/api/v1/reflections/{plan_id}")
        assert get_ref.status_code == 200
        assert len(get_ref.json()["data"]) == 1

def test_tool_registry_memory_execution(db_session):
    MemoryService.create_memory(db_session, PlannerMemoryCreate(
        family_id="default_family",
        memory_type="BUDGET_PATTERN",
        title="Food Budget Pattern",
        content="Always keep 10% contingency for food",
        importance=5
    ))

    get_relevant = tool_registry.get_tool("get_relevant_memories")
    memories = get_relevant(db_session, family_id="default_family")
    assert len(memories) >= 1
    assert any(m["title"] == "Food Budget Pattern" for m in memories)

def test_ai_personalization_with_family_memory(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Add persistent family memory
    MemoryService.create_memory(db_session, PlannerMemoryCreate(
        family_id="default_family",
        memory_type="DESTINATION_PREFERENCE",
        title="Quiet Hill Station Preference",
        content="Family prefers quiet hill stations and dislikes crowded tourist places.",
        importance=5
    ))

    with patch("app.ai.groq_client.Groq") as mock_groq:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="""{
                "plan_type": "TRAVEL",
                "title": "Quiet Hill Station Family Vacation",
                "intent": "Plan family vacation based on destination preferences",
                "requirements": {
                    "destination": "Kodaikanal",
                    "duration_days": 4,
                    "people": 4,
                    "budget": 40000.0,
                    "start_date": null,
                    "end_date": null,
                    "location": "Kodaikanal",
                    "special_notes": "Personalized based on memory preference for quiet hill stations"
                },
                "missing_information": ["travel dates"],
                "preferences": ["quiet environment", "hill station"],
                "constraints": [],
                "reasoning_summary": "Retrieved memory indicating family prefers quiet hill stations over crowded places.",
                "recommendations": ["Book eco-resort off main town center"],
                "draft_plan": null,
                "next_action": "NEED_MORE_INFO"
            }"""))
        ]
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_instance

        response = client.post("/api/v1/ai/plan", json={"message": "Plan a family vacation."})
        assert response.status_code == 200
        res_data = response.json()["data"]
        assert res_data["plan_type"] == "TRAVEL"
        assert "quiet hill stations" in res_data["reasoning_summary"]
