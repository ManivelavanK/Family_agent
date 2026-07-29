import datetime
import pytest
from app.services.routine_service import RoutineService
from app.schemas.routine import FamilyRoutineCreate, FamilyRoutineUpdate
from app.models.routine import RoutinePriority, RoutineStatus

def test_routine_crud_and_family_isolation(client, db_session):
    now = datetime.datetime.now(datetime.timezone.utc)
    r1 = RoutineService.create_routine(db_session, FamilyRoutineCreate(
        family_id="family_A",
        member_name="Father",
        title="Office Work",
        scheduled_start=now,
        scheduled_end=now + datetime.timedelta(hours=8),
        priority=RoutinePriority.HIGH
    ))

    r2 = RoutineService.create_routine(db_session, FamilyRoutineCreate(
        family_id="family_B",
        member_name="Mother",
        title="Grocery Shopping",
        scheduled_start=now + datetime.timedelta(hours=2),
        scheduled_end=now + datetime.timedelta(hours=4)
    ))

    # Get routines for family A
    res_a = client.get("/api/v1/routines?family_id=family_A")
    assert res_a.status_code == 200
    data_a = res_a.json()["data"]
    assert len(data_a) == 1
    assert data_a[0]["title"] == "Office Work"

    # Family A cross-family access check -> 404
    res_cross = client.get(f"/api/v1/routines/{r2.id}?family_id=family_A")
    assert res_cross.status_code == 404

    # Update routine
    up_res = client.put(f"/api/v1/routines/{r1.id}?family_id=family_A", json={"status": "IN_PROGRESS"})
    assert up_res.status_code == 200
    assert up_res.json()["data"]["status"] == "IN_PROGRESS"

    # Delete routine
    del_res = client.delete(f"/api/v1/routines/{r1.id}?family_id=family_A")
    assert del_res.status_code == 200

def test_routine_date_and_range_filtering(client, db_session):
    today = datetime.date.today()
    s_time = datetime.datetime.combine(today, datetime.time(9, 0), tzinfo=datetime.timezone.utc)
    e_time = datetime.datetime.combine(today, datetime.time(11, 0), tzinfo=datetime.timezone.utc)

    RoutineService.create_routine(db_session, FamilyRoutineCreate(
        family_id="default_family",
        member_name="Sister",
        title="Study Session",
        scheduled_start=s_time,
        scheduled_end=e_time
    ))

    # Day filter endpoint
    res_day = client.get(f"/api/v1/routines/day/{today}?family_id=default_family")
    assert res_day.status_code == 200
    assert len(res_day.json()["data"]) == 1

    # Range filter endpoint
    res_range = client.get(f"/api/v1/routines/range?start_date={today}&end_date={today}&family_id=default_family")
    assert res_range.status_code == 200
    assert len(res_range.json()["data"]) == 1

def test_routine_conflict_detection(client, db_session):
    today = datetime.date.today()
    s1 = datetime.datetime.combine(today, datetime.time(10, 0), tzinfo=datetime.timezone.utc)
    e1 = datetime.datetime.combine(today, datetime.time(12, 0), tzinfo=datetime.timezone.utc)

    RoutineService.create_routine(db_session, FamilyRoutineCreate(
        family_id="default_family",
        member_name="Grandma",
        title="Doctor Appointment",
        scheduled_start=s1,
        scheduled_end=e1
    ))

    # Overlapping conflict check endpoint
    s2 = datetime.datetime.combine(today, datetime.time(11, 0), tzinfo=datetime.timezone.utc)
    e2 = datetime.datetime.combine(today, datetime.time(13, 0), tzinfo=datetime.timezone.utc)

    conf_res = client.post("/api/v1/routines/check-conflicts", params={
        "member_name": "Grandma",
        "scheduled_start": s2.isoformat(),
        "scheduled_end": e2.isoformat(),
        "family_id": "default_family"
    })
    assert conf_res.status_code == 200
    assert len(conf_res.json()["data"]) == 1
    assert conf_res.json()["data"][0]["title"] == "Doctor Appointment"
