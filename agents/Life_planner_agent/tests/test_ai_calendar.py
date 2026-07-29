from unittest.mock import MagicMock, patch
import pytest
import datetime
from app.config import settings
from app.services.calendar_service import CalendarService
from app.schemas.calendar import CalendarEventCreate
from app.ai.tool_registry import tool_registry

def test_missing_groq_key_calendar_reasoning(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    response = client.post("/api/v1/ai/calendar/reason", json={"message": "Plan birthday next Sunday"})
    assert response.status_code == 503
    assert "Groq API key is missing" in response.json()["detail"]

@patch("app.ai.groq_client.Groq")
def test_ai_calendar_reasoning_no_conflicts(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "conflict_detected": false,
            "conflict_summary": "No conflicts detected for Sunday evening.",
            "affected_events": [],
            "recommended_action": "PROCEED",
            "alternative_slots": [],
            "reasoning": "The requested time slot is completely open.",
            "confidence": 0.95,
            "missing_information": [],
            "next_action": "REVIEW_RECOMMENDATION"
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    response = client.post("/api/v1/ai/calendar/reason", json={
        "message": "Can we have sister's birthday party next Sunday 5 PM to 8 PM?",
        "requested_start": "2026-08-09T17:00:00Z",
        "requested_end": "2026-08-09T20:00:00Z"
    })
    assert response.status_code == 200
    res_data = response.json()["data"]
    assert res_data["conflict_detected"] is False
    assert res_data["recommended_action"] == "PROCEED"

@patch("app.ai.groq_client.Groq")
def test_ai_calendar_reasoning_with_conflict_and_alternatives(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    # Add conflicting child exam event
    CalendarService.create_event(db_session, CalendarEventCreate(
        title="Child Board Exam",
        event_type="STUDY_EXAM",
        start_datetime=datetime.datetime(2026, 8, 9, 10, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2026, 8, 9, 13, 0, tzinfo=datetime.timezone.utc)
    ))

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "conflict_detected": true,
            "conflict_summary": "Overlaps with Child Board Exam from 10:00 to 13:00.",
            "affected_events": [
                {
                    "event_id": 1,
                    "title": "Child Board Exam",
                    "start": "2026-08-09T10:00:00Z",
                    "end": "2026-08-09T13:00:00Z",
                    "event_type": "STUDY_EXAM"
                }
            ],
            "recommended_action": "MOVE_EVENT",
            "alternative_slots": [
                {
                    "start": "2026-08-09T15:00:00Z",
                    "end": "2026-08-09T18:00:00Z",
                    "suitability_reason": "Evening slot after exam allows preparation and rest."
                }
            ],
            "reasoning": "Exam preparation takes top priority for the child.",
            "confidence": 0.92,
            "missing_information": [],
            "next_action": "REVIEW_RECOMMENDATION"
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    response = client.post("/api/v1/ai/calendar/reason", json={
        "message": "Plan family lunch on Sunday 11 AM.",
        "requested_start": "2026-08-09T11:00:00Z",
        "requested_end": "2026-08-09T13:00:00Z"
    })
    assert response.status_code == 200
    res_data = response.json()["data"]
    assert res_data["conflict_detected"] is True
    assert res_data["recommended_action"] == "MOVE_EVENT"
    assert len(res_data["alternative_slots"]) == 1

@patch("app.ai.groq_client.Groq")
def test_ai_calendar_reasoning_malformed_json(mock_groq, client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Malformed text response"))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    response = client.post("/api/v1/ai/calendar/reason", json={"message": "Is Sunday free?"})
    assert response.status_code == 502
    assert "invalid or malformed JSON format" in response.json()["detail"]

def test_available_time_slots_tool(db_session):
    from app.services.calendar_service import CalendarService
    from app.schemas.calendar import CalendarEventCreate

    # Add busy slot 10:00 to 12:00
    CalendarService.create_event(db_session, CalendarEventCreate(
        title="Morning Workshop",
        start_datetime=datetime.datetime(2026, 8, 15, 10, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2026, 8, 15, 12, 0, tzinfo=datetime.timezone.utc)
    ))

    tool_func = tool_registry.get_tool("get_available_time_slots")
    slots = tool_func(db_session, "2026-08-15", duration_minutes=60)
    assert isinstance(slots, list)
    # Ensure 10:00-11:00 is NOT in free slots list
    for s in slots:
        assert "T10:00:00" not in s["start"]
