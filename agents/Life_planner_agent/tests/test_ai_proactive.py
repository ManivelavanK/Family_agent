import datetime
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.models.calendar import CalendarEvent, EventType, EventStatus
from app.models.plan import Plan, PlanTask, TaskPriority
from app.models.memory import PlannerMemory, MemoryType
from app.scheduler.proactive_scheduler import proactive_scheduler
from app.ai.proactive_agent import proactive_agent

@patch("app.ai.groq_client.Groq")
def test_proactive_analysis_no_insights(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "insights": [],
            "reasoning_summary": "All family plans and calendar schedules are up to date with no pending items.",
            "evaluated_facts_count": 0
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/proactive/analyze", json={
        "family_id": "default_family",
        "lookahead_days": 30
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert len(res_data["insights"]) == 0
    assert "up to date" in res_data["reasoning_summary"]

@patch("app.ai.groq_client.Groq")
def test_proactive_analysis_upcoming_event_and_incomplete_prep(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Create upcoming calendar event
    cal_event = CalendarEvent(
        title="Sister's Birthday",
        event_type=EventType.BIRTHDAY,
        start_datetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12),
        end_datetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=12, hours=3)
    )
    db_session.add(cal_event)

    # Create plan with overdue preparation task
    plan = Plan(title="Birthday Party", plan_type="EVENT", budget=10000.0)
    db_session.add(plan)
    db_session.flush()

    task = PlanTask(
        plan_id=plan.id,
        title="Book Catering Service",
        due_date=datetime.date.today() - datetime.timedelta(days=2),
        priority=TaskPriority.HIGH
    )
    db_session.add(task)
    db_session.commit()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "insights": [
                {
                    "title": "Sister's Birthday catering is overdue",
                    "priority": "HIGH",
                    "category": "TASK_OVERDUE",
                    "reasoning": "Catering booking task was due 2 days ago for Sister's Birthday coming up in 12 days.",
                    "supporting_facts": ["Task 'Book Catering Service' is overdue", "Event 'Sister's Birthday' in 12 days"],
                    "recommended_action": "Confirm catering vendor immediately or assign backup task owner.",
                    "confidence": 0.95,
                    "related_plan_id": """ + str(plan.id) + """,
                    "related_event_id": """ + str(cal_event.id) + """,
                    "related_task_id": """ + str(task.id) + """
                }
            ],
            "reasoning_summary": "Identified critical overdue catering task blocking upcoming birthday event.",
            "evaluated_facts_count": 3
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/proactive/analyze", json={
        "family_id": "default_family",
        "lookahead_days": 30
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert len(res_data["insights"]) == 1
    insight = res_data["insights"][0]
    assert insight["priority"] == "HIGH"
    assert insight["category"] == "TASK_OVERDUE"

@patch("app.ai.groq_client.Groq")
def test_memory_driven_proactive_recommendation(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Add memory regarding food waste
    mem = PlannerMemory(
        family_id="default_family",
        memory_type=MemoryType.FOOD_PREFERENCE,
        title="Excess Party Catering Waste",
        content="Previous birthday party resulted in 30% food waste; reduce guest portion estimates.",
        importance=5
    )
    db_session.add(mem)
    db_session.commit()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "insights": [
                {
                    "title": "Adjust upcoming party catering estimates based on past reflection",
                    "priority": "MEDIUM",
                    "category": "MEMORY_RECURRENCE",
                    "reasoning": "Family memory records 30% catering food waste in past parties.",
                    "supporting_facts": ["Memory 'Excess Party Catering Waste' records 30% food waste"],
                    "recommended_action": "Reduce planned catering order by 20% to prevent food waste.",
                    "confidence": 0.88,
                    "related_plan_id": null,
                    "related_event_id": null,
                    "related_task_id": null
                }
            ],
            "reasoning_summary": "Leveraged historical memory to recommend proactive catering reduction.",
            "evaluated_facts_count": 2
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/proactive/analyze", json={
        "family_id": "default_family",
        "lookahead_days": 30
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["insights"][0]["category"] == "MEMORY_RECURRENCE"

def test_malformed_groq_proactive_response(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    with patch("app.ai.groq_client.Groq") as mock_groq:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Invalid non-json text response"))
        ]
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_instance

        res = client.post("/api/v1/ai/proactive/analyze", json={
            "family_id": "default_family",
            "lookahead_days": 30
        })
        assert res.status_code == 502
        assert "invalid or malformed JSON" in res.json()["detail"]

def test_missing_groq_key_proactive_analysis(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    res = client.post("/api/v1/ai/proactive/analyze", json={
        "family_id": "default_family",
        "lookahead_days": 30
    })
    assert res.status_code == 503
    assert "Groq API key is missing" in res.json()["detail"]

def test_proactive_scheduler_trigger(db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    with patch.object(proactive_agent, "analyze_proactive_context") as mock_agent_call:
        mock_agent_call.return_value = MagicMock(insights=[])
        proactive_scheduler.trigger_proactive_analysis_job()
        assert mock_agent_call.called
