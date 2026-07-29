import pytest
from unittest.mock import MagicMock, patch
from app.config import settings
from app.communication.agent_registry import agent_registry
from app.communication.agent_client import agent_client_service
from app.services.family_context_service import FamilyContextService
from app.ai.tool_registry import tool_registry

def test_agent_registry_initialization():
    agents = agent_registry.list_all_agents()
    assert len(agents) == 5

    father = agent_registry.get_agent("father")
    assert father is not None
    assert father.name == "Father Agent"
    assert "financial" in father.capabilities

    mother_agents = agent_registry.get_agents_by_capability("food")
    assert len(mother_agents) >= 1
    assert mother_agents[0].name == "Mother Agent"

@pytest.mark.anyio
async def test_mock_mode_agent_client_retrieval():
    father_ctx = await agent_client_service.get_father_context("family_100")
    assert father_ctx is not None
    assert father_ctx.available_budget == 35000.0

    grandparent_ctx = await agent_client_service.get_grandparent_context("family_100")
    assert grandparent_ctx is not None
    assert grandparent_ctx.mobility_level == "LOW_WALKING"

    baby_ctx = await agent_client_service.get_baby_context("family_100")
    assert baby_ctx is not None
    assert "Stroller required" in baby_ctx.special_care_notes

@pytest.mark.anyio
async def test_family_context_aggregation_and_partial_failure(monkeypatch):
    # Enable non-mock mode for testing HTTP timeout/failure simulation
    monkeypatch.setattr(settings, "AGENT_COMMUNICATION_MOCK", False)

    async def mock_get_father(family_id):
        from app.communication.schemas import FatherContext
        return FatherContext(available_budget=50000.0)

    async def mock_get_child_error(family_id):
        raise Exception("Connection timeout to Child Agent")

    monkeypatch.setattr(agent_client_service, "get_father_context", mock_get_father)
    monkeypatch.setattr(agent_client_service, "get_child_context", mock_get_child_error)

    ctx = await FamilyContextService.get_aggregated_family_context("family_200", required_domains=["father", "child"])
    assert ctx.father is not None
    assert ctx.father.available_budget == 50000.0
    assert ctx.child is None
    assert "father_agent" in ctx.available_sources
    assert "child_agent" in ctx.unavailable_sources
    assert len(ctx.retrieval_errors) == 1

def test_tool_registry_cross_agent_execution():
    get_family_ctx = tool_registry.get_tool("get_family_context")
    res = get_family_ctx("family_300")
    assert res["family_id"] == "family_300"
    assert "father" in res

@patch("app.ai.groq_client.Groq")
def test_ai_family_aware_planning_integration(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response_selection = MagicMock()
    mock_response_selection.choices = [
        MagicMock(message=MagicMock(content="""{
            "required_agent_domains": ["father", "child", "grandparent"],
            "reasoning": "Selected financial, child exam, and grandparent mobility context."
        }"""))
    ]

    mock_response_plan = MagicMock()
    mock_response_plan.choices = [
        MagicMock(message=MagicMock(content="""{
            "plan_type": "TRAVEL",
            "title": "Family Friendly Ooty Vacation",
            "intent": "Plan multi-generational family vacation considering mobility and exams",
            "requirements": {
                "destination": "Ooty",
                "duration_days": 3,
                "people": 6,
                "budget": 35000.0,
                "start_date": null,
                "end_date": null,
                "location": "Ooty",
                "special_notes": "Tailored for low walking and avoiding exam dates"
            },
            "missing_information": ["exact travel dates"],
            "preferences": ["low walking routes", "scenic train"],
            "constraints": ["Grandparent low mobility", "Child upcoming math exam"],
            "reasoning_summary": "Retrieved Father budget ceiling (35,000 INR), Grandparent low mobility level, and Child math exam schedule.",
            "recommendations": ["Book hotel with elevator", "Schedule study breaks"],
            "draft_plan": null,
            "next_action": "NEED_MORE_INFO",
            "family_context_used": ["Father available budget", "Grandparent low mobility", "Child upcoming exam"],
            "context_influence": ["Kept budget under 35,000 INR", "Selected low walking spots", "Avoided exam week"],
            "context_sources": ["father_agent", "child_agent", "grandparent_agent", "planner_memory", "calendar"]
        }"""))
    ]

    mock_instance = MagicMock()
    # First call -> context selection; Second call -> plan generation
    mock_instance.chat.completions.create.side_effect = [mock_response_selection, mock_response_plan]
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/plan", json={
        "message": "Plan a 3-day family trip to Ooty for 6 people under 35,000 INR."
    })

    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["plan_type"] == "TRAVEL"
    assert "father_agent" in res_data["context_sources"]
    assert len(res_data["family_context_used"]) == 3
