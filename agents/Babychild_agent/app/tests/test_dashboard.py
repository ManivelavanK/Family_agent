import pytest
from datetime import date, timedelta
from unittest.mock import patch

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile
    payload = {
        "family_id": 101,
        "name": "Dashboard Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=20))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]

def test_get_dashboard_summary_success(client, test_baby_id):
    response = client.get(f"/api/v1/dashboard/summary/{test_baby_id}?family_id=101")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "baby_profile" in data["data"]
    assert "feeding_summary" in data["data"]
    assert "sleep_summary" in data["data"]
    assert "latest_growth" in data["data"]
    assert "latest_health" in data["data"]
    assert "next_vaccination" in data["data"]

def test_get_dashboard_alerts_success(client, test_baby_id):
    response = client.get(f"/api/v1/dashboard/alerts/{test_baby_id}?family_id=101")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "alerts" in data["data"]

def test_get_dashboard_recommendations_success(client, test_baby_id):
    with patch("app.ai.groq_service.call_groq") as mock_call:
        mock_call.return_value = "Ensure regular feedings and monitor nap cycles."
        response = client.get(f"/api/v1/dashboard/recommendations/{test_baby_id}?family_id=101")
        
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["recommendations"] == "Ensure regular feedings and monitor nap cycles."

def test_get_dashboard_invalid_baby(client):
    response = client.get("/api/v1/dashboard/summary/9999?family_id=101")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_dashboard_invalid_family(client, test_baby_id):
    response = client.get(f"/api/v1/dashboard/summary/{test_baby_id}?family_id=999")
    assert response.status_code == 403
    assert "forbidden" in response.text.lower() or "not belong" in response.text.lower()
