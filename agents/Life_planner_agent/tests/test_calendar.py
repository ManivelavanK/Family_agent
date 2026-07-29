import datetime
import pytest
from app.ai.tool_registry import tool_registry

def test_calendar_crud_lifecycle(client):
    payload = {
        "title": "Doctor Appointment",
        "description": "Annual health checkup",
        "event_type": "APPOINTMENT",
        "start_datetime": "2026-08-10T10:00:00Z",
        "end_datetime": "2026-08-10T11:00:00Z",
        "all_day": False,
        "location": "City Clinic",
        "status": "SCHEDULED"
    }
    create_res = client.post("/api/v1/calendar/events", json=payload)
    assert create_res.status_code == 201
    event_id = create_res.json()["data"]["id"]
    assert create_res.json()["data"]["title"] == "Doctor Appointment"

    # Get event by ID
    get_res = client.get(f"/api/v1/calendar/events/{event_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == event_id

    # Update event
    update_res = client.put(f"/api/v1/calendar/events/{event_id}", json={"status": "CONFIRMED"})
    assert update_res.status_code == 200
    assert update_res.json()["data"]["status"] == "CONFIRMED"

    # Delete event
    del_res = client.delete(f"/api/v1/calendar/events/{event_id}")
    assert del_res.status_code == 200

def test_calendar_validation_invalid_datetime_range(client):
    payload = {
        "title": "Invalid Meeting",
        "start_datetime": "2026-08-10T12:00:00Z",
        "end_datetime": "2026-08-10T10:00:00Z"  # end before start
    }
    response = client.post("/api/v1/calendar/events", json=payload)
    assert response.status_code == 422
    assert response.json()["success"] is False

def test_calendar_queries_day_and_range(client):
    payload_a = {
        "title": "Morning Yoga",
        "event_type": "PERSONAL",
        "start_datetime": "2026-08-15T07:00:00Z",
        "end_datetime": "2026-08-15T08:00:00Z"
    }
    payload_b = {
        "title": "Family Picnic",
        "event_type": "FAMILY_EVENT",
        "start_datetime": "2026-08-16T12:00:00Z",
        "end_datetime": "2026-08-16T16:00:00Z"
    }
    client.post("/api/v1/calendar/events", json=payload_a)
    client.post("/api/v1/calendar/events", json=payload_b)

    # Query daily events
    day_res = client.get("/api/v1/calendar/day/2026-08-15")
    assert day_res.status_code == 200
    assert len(day_res.json()["data"]) == 1
    assert day_res.json()["data"][0]["title"] == "Morning Yoga"

    # Query range events
    range_res = client.get("/api/v1/calendar/range?start_date=2026-08-15&end_date=2026-08-16")
    assert range_res.status_code == 200
    assert len(range_res.json()["data"]) == 2

def test_calendar_factual_conflict_detection(client):
    # Event A: 10:00 to 12:00
    client.post("/api/v1/calendar/events", json={
        "title": "Team Meeting",
        "start_datetime": "2026-08-20T10:00:00Z",
        "end_datetime": "2026-08-20T12:00:00Z"
    })

    # Test 1: Overlapping time (11:00 to 13:00) -> Conflict YES
    check_overlap = client.post("/api/v1/calendar/check-conflicts", json={
        "start_datetime": "2026-08-20T11:00:00Z",
        "end_datetime": "2026-08-20T13:00:00Z"
    })
    assert check_overlap.status_code == 200
    res_data = check_overlap.json()["data"]
    assert res_data["has_conflict"] is True
    assert len(res_data["conflicts"]) == 1
    assert res_data["conflicts"][0]["title"] == "Team Meeting"

    # Test 2: Adjacent boundary (12:00 to 13:00) -> Conflict NO
    check_adjacent = client.post("/api/v1/calendar/check-conflicts", json={
        "start_datetime": "2026-08-20T12:00:00Z",
        "end_datetime": "2026-08-20T13:00:00Z"
    })
    assert check_adjacent.status_code == 200
    assert check_adjacent.json()["data"]["has_conflict"] is False

def test_ai_tool_registry_calendar_execution(db_session):
    from app.services.calendar_service import CalendarService
    from app.schemas.calendar import CalendarEventCreate

    # Seed test calendar event directly
    CalendarService.create_event(db_session, CalendarEventCreate(
        title="Dentist Visit",
        event_type="APPOINTMENT",
        start_datetime=datetime.datetime(2026, 9, 1, 10, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2026, 9, 1, 11, 0, tzinfo=datetime.timezone.utc)
    ))

    # Execute tools registered in ToolRegistry
    get_upcoming = tool_registry.get_tool("get_upcoming_calendar_events")
    upcoming_res = get_upcoming(db_session)
    assert len(upcoming_res) >= 1
    assert any(e["title"] == "Dentist Visit" for e in upcoming_res)

    check_conflicts = tool_registry.get_tool("check_calendar_conflicts")
    conflict_res = check_conflicts(
        db_session,
        "2026-09-01T10:30:00+00:00",
        "2026-09-01T11:30:00+00:00"
    )
    assert conflict_res["has_conflict"] is True
