import datetime
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.models.memory import PlannerMemory, MemoryType
from app.models.calendar import CalendarEvent, EventType

def test_missing_groq_key_routine_planning(client, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    res = client.post("/api/v1/ai/routine/plan", json={
        "family_id": "default_family",
        "message": "Plan tomorrow for my family."
    })
    assert res.status_code == 503
    assert "Groq API key is missing" in res.json()["detail"]

@patch("app.ai.groq_client.Groq")
def test_natural_language_routine_planning(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "family_id": "default_family",
            "target_date": "2026-07-29",
            "daily_summary": "Balanced schedule prioritizing Grandma's medical checkup and Sister's exam preparation.",
            "routine_items": [
                {
                    "member_name": "Sister",
                    "title": "Exam Final Revision",
                    "category": "STUDY",
                    "start_time": "08:00",
                    "end_time": "11:00",
                    "priority": "HIGH",
                    "reason": "Prioritized ahead of afternoon exam",
                    "related_entity_type": null,
                    "related_entity_id": null
                },
                {
                    "member_name": "Grandma",
                    "title": "Hospital Checkup",
                    "category": "MEDICAL",
                    "start_time": "10:30",
                    "end_time": "12:30",
                    "priority": "CRITICAL",
                    "reason": "Fixed doctor appointment",
                    "related_entity_type": null,
                    "related_entity_id": null
                }
            ],
            "conflicts": [
                {
                    "member_name": "Mother",
                    "conflicting_items": ["Grocery shopping", "Accompanying Grandma to hospital"],
                    "conflict_reason": "Overlapping morning commitments between 10:30 and 12:00",
                    "suggested_resolution": "Move grocery shopping to 15:00"
                }
            ],
            "overloaded_members": ["Mother"],
            "recommendations": ["Shift grocery trip to late afternoon"],
            "missing_information": ["Transport arrangements for hospital trip"],
            "reasoning": "Balanced high-priority medical and exam commitments while resolving Mother's schedule overlap.",
            "confidence": 0.93,
            "next_action": "REVIEW_RECOMMENDATION"
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/routine/plan", json={
        "family_id": "default_family",
        "message": "Plan tomorrow for my family. Dad has office work, mom needs groceries, sister has an exam and grandma has a doctor appointment.",
        "target_date": "2026-07-29"
    })

    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["target_date"] == "2026-07-29"
    assert len(res_data["routine_items"]) == 2
    assert len(res_data["conflicts"]) == 1
    assert "Mother" in res_data["overloaded_members"]

@patch("app.ai.groq_client.Groq")
def test_family_memory_in_routine_planning(mock_groq, client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")

    db_session.add(PlannerMemory(
        family_id="default_family",
        memory_type=MemoryType.FOOD_PREFERENCE,
        title="Grandma Meal Preference",
        content="Grandma prefers having early lunch by 12:30 PM due to medicine schedule.",
        importance=5
    ))
    db_session.commit()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""{
            "family_id": "default_family",
            "target_date": "2026-07-29",
            "daily_summary": "Schedule accommodating Grandma's early lunch memory preference.",
            "routine_items": [
                {
                    "member_name": "Grandma",
                    "title": "Early Lunch & Medication",
                    "category": "MEAL",
                    "start_time": "12:00",
                    "end_time": "12:30",
                    "priority": "HIGH",
                    "reason": "Factored in memory preference for early lunch before medicines",
                    "related_entity_type": null,
                    "related_entity_id": null
                }
            ],
            "conflicts": [],
            "overloaded_members": [],
            "recommendations": [],
            "missing_information": [],
            "reasoning": "Incorporated retrieved planner memory regarding Grandma's early lunch preference.",
            "confidence": 0.95,
            "next_action": "REVIEW_RECOMMENDATION"
        }"""))
    ]
    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_response
    mock_groq.return_value = mock_instance

    res = client.post("/api/v1/ai/routine/plan", json={
        "family_id": "default_family",
        "message": "Plan tomorrow's lunch schedule."
    })
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert len(res_data["routine_items"]) == 1
    assert "Early Lunch" in res_data["routine_items"][0]["title"]
