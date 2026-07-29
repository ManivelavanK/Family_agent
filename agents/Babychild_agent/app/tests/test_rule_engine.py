import pytest
from datetime import datetime, date, timedelta

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile to link alerts to
    payload = {
        "family_id": 1,
        "name": "Rule Engine Baby",
        "date_of_birth": str(date.today() - timedelta(days=60))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]


def test_no_alerts_when_healthy_and_fed(client, test_baby_id):
    # Log feeding (1 hour ago)
    client.post("/api/v1/feeding/create", json={
        "baby_id": test_baby_id,
        "feeding_type": "formula",
        "feeding_time": str(datetime.now() - timedelta(hours=1))
    })

    # Log sleep (9 hours total today)
    client.post("/api/v1/sleep/create", json={
        "baby_id": test_baby_id,
        "sleep_type": "night_sleep",
        "start_time": str(datetime.now() - timedelta(hours=9)),
        "end_time": str(datetime.now())
    })

    # Log health (normal temp)
    client.post("/api/v1/health/create", json={
        "baby_id": test_baby_id,
        "temperature_c": 36.6,
        "visit_date": str(date.today())
    })

    response = client.get(f"/api/v1/alerts/{test_baby_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Should not contain overdue feeding, poor sleep, or fever alert.
    # Note: if there is no vaccination due, alerts list should be empty.
    assert "Baby may need feeding." not in data["data"]["alerts"]
    assert "Baby slept less than recommended today." not in data["data"]["alerts"]
    assert "High temperature detected." not in data["data"]["alerts"]


def test_feeding_overdue_alert(client, test_baby_id):
    # Log feeding (5 hours ago)
    client.post("/api/v1/feeding/create", json={
        "baby_id": test_baby_id,
        "feeding_type": "formula",
        "feeding_time": str(datetime.now() - timedelta(hours=5))
    })

    response = client.get(f"/api/v1/alerts/{test_baby_id}")
    assert response.status_code == 200
    assert "Baby may need feeding." in response.json()["data"]["alerts"]


def test_poor_sleep_alert(client, test_baby_id):
    # Log sleep (only 4 hours today)
    client.post("/api/v1/sleep/create", json={
        "baby_id": test_baby_id,
        "sleep_type": "day_nap",
        "start_time": str(datetime.now() - timedelta(hours=4)),
        "end_time": str(datetime.now())
    })

    response = client.get(f"/api/v1/alerts/{test_baby_id}")
    assert response.status_code == 200
    assert "Baby slept less than recommended today." in response.json()["data"]["alerts"]


def test_fever_alert(client, test_baby_id):
    # Log health with fever
    client.post("/api/v1/health/create", json={
        "baby_id": test_baby_id,
        "temperature_c": 38.5,
        "visit_date": str(date.today())
    })

    response = client.get(f"/api/v1/alerts/{test_baby_id}")
    assert response.status_code == 200
    assert "High temperature detected." in response.json()["data"]["alerts"]


def test_vaccination_reminder_alert(client, test_baby_id):
    # Log vaccine due tomorrow
    client.post("/api/v1/vaccine/create", json={
        "baby_id": test_baby_id,
        "vaccine_name": "Flu",
        "due_date": str(date.today() + timedelta(days=1)),
        "status": "pending"
    })

    response = client.get(f"/api/v1/alerts/{test_baby_id}")
    assert response.status_code == 200
    assert "Vaccination due soon." in response.json()["data"]["alerts"]


def test_multiple_concurrent_alerts(client, test_baby_id):
    # Overdue feeding (5 hours ago)
    client.post("/api/v1/feeding/create", json={
        "baby_id": test_baby_id,
        "feeding_type": "formula",
        "feeding_time": str(datetime.now() - timedelta(hours=5))
    })

    # Fever
    client.post("/api/v1/health/create", json={
        "baby_id": test_baby_id,
        "temperature_c": 39.0,
        "visit_date": str(date.today())
    })

    # Poor sleep is triggered implicitly (0 hours sleep today)

    response = client.get(f"/api/v1/alerts/{test_baby_id}")
    assert response.status_code == 200
    alerts = response.json()["data"]["alerts"]
    assert "Baby may need feeding." in alerts
    assert "High temperature detected." in alerts
    assert "Baby slept less than recommended today." in alerts
