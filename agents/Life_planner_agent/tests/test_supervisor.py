import pytest
from unittest.mock import MagicMock, patch
from app.config import settings
from app.communication.supervisor_schemas import SupervisorRequest, SupervisorAgentSelection
from app.ai.supervisor_agent import supervisor_agent

def test_supervisor_agent_initialization():
    assert supervisor_agent is not None
    assert supervisor_agent.groq is not None

@patch("app.ai.groq_client.Groq")
def test_supervisor_ai_selection(mock_groq, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "agents": [
                {
                    "agent": "father",
                    "reason": "Budget verification",
                    "required_capabilities": ["financial"]
                },
                {
                    "agent": "mother",
                    "reason": "Food and stay preferences",
                    "required_capabilities": ["food"]
                }
            ]
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    selections = supervisor_agent.select_relevant_agents("Plan a trip to Ooty under 30000 INR.")
    assert len(selections) == 2
    assert selections[0].agent == "father"
    assert selections[1].agent == "mother"

@patch("app.ai.groq_client.Groq")
def test_supervisor_full_process_mock_mode(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    monkeypatch.setattr(settings, "AGENT_COMMUNICATION_MOCK", True)

    mock_sel_resp = MagicMock()
    mock_sel_resp.choices = [
        MagicMock(message=MagicMock(content="""{
            "agents": [
                {"agent": "father", "reason": "budget"},
                {"agent": "mother", "reason": "food"}
            ]
        }"""))
    ]
    mock_sup_resp = MagicMock()
    mock_sup_resp.choices = [
        MagicMock(message=MagicMock(content="""{
            "recommendation": {
                "title": "Family Trip to Ooty",
                "summary": "Unified family plan within 30,000 INR limit.",
                "financial_impact": "Fits within father's 35,000 INR budget ceiling",
                "schedule_impact": "No exam conflicts for child",
                "action_items": ["Book train tickets"],
                "contingencies": ["Indoor tea museum backup"]
            },
            "confidence": 0.94,
            "requires_approval": true,
            "next_action": "REVIEW_RECOMMENDATION",
            "reasoning": "Synthesized inputs from father, mother, child agents."
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.side_effect = [mock_sel_resp, mock_sup_resp]
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/supervisor", json={
        "family_id": "default_family",
        "message": "Plan a family trip to Ooty next month under 30,000 INR."
    })

    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["success"] is True
    assert "father" in res_data["selected_agents"]
    assert len(res_data["available_agents"]) > 0
    assert res_data["requires_approval"] is True

@patch("app.ai.groq_client.Groq")
@patch("httpx.AsyncClient.get")
def test_supervisor_real_httpx_mode(mock_httpx_get, mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    monkeypatch.setattr(settings, "AGENT_COMMUNICATION_MOCK", False)
    monkeypatch.setattr(settings, "FATHER_AGENT_URL", "http://father-agent:8001")
    monkeypatch.setattr(settings, "MOTHER_AGENT_URL", "http://mother-agent:8002")

    # Mock HTTP response for father agent and failure for mother agent
    mock_httpx_resp = MagicMock()
    mock_httpx_resp.status_code = 200
    mock_httpx_resp.json.return_value = {"data": {"budget": 40000.0}}

    async def side_effect(url, *args, **kwargs):
        url_str = str(url)
        if "father" in url_str or "8001" in url_str:
            return mock_httpx_resp
        raise Exception("Connection timeout to Mother agent")

    mock_httpx_get.side_effect = side_effect

    mock_sel_resp = MagicMock()
    mock_sel_resp.choices = [
        MagicMock(message=MagicMock(content="""{
            "agents": [
                {"agent": "father", "reason": "budget"},
                {"agent": "mother", "reason": "food"}
            ]
        }"""))
    ]
    mock_groq_resp = MagicMock()
    mock_groq_resp.choices = [
        MagicMock(message=MagicMock(content="""{
            "recommendation": {
                "title": "Adjusted Trip Plan",
                "summary": "Proceeding with father's budget data",
                "action_items": []
            },
            "confidence": 0.88,
            "requires_approval": true,
            "next_action": "REVIEW_RECOMMENDATION",
            "reasoning": "Handled unavailable mother agent safely."
        }"""))
    ]
    mock_groq_instance = MagicMock()
    mock_groq_instance.chat.completions.create.side_effect = [mock_sel_resp, mock_groq_resp]
    mock_groq.return_value = mock_groq_instance

    res = client.post("/api/v1/ai/supervisor", json={
        "family_id": "default_family",
        "message": "Plan a family trip."
    })

    assert res.status_code == 200
    res_data = res.json()["data"]
    assert "father" in res_data["available_agents"]
    assert "mother" in res_data["unavailable_agents"]

def test_supervisor_health_check_endpoint(client):
    res = client.get("/api/v1/ai/supervisor/agents?family_id=default_family")
    assert res.status_code == 200
    agents = res.json()["data"]
    assert len(agents) == 5
    agent_names = [a["agent"] for a in agents]
    assert "father" in agent_names
    assert "mother" in agent_names
