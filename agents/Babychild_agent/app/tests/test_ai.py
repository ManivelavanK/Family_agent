import pytest
from datetime import date, timedelta
from unittest.mock import patch

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile
    payload = {
        "family_id": 101,
        "name": "AI Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=20))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]

def test_ask_ai_assistant_success(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "family_id": 101,
        "question": "How is my baby today?"
    }
    
    with patch("app.ai.groq_service.call_groq") as mock_call:
        mock_call.return_value = "Your baby is doing fantastic today!"
        response = client.post("/api/v1/ai/ask", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["answer"] == "Your baby is doing fantastic today!"
    mock_call.assert_called_once()

def test_ask_ai_assistant_invalid_baby(client):
    payload = {
        "baby_id": 9999,
        "family_id": 101,
        "question": "How is my baby today?"
    }
    response = client.post("/api/v1/ai/ask", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_ask_ai_assistant_invalid_family(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "family_id": 999,  # invalid family_id
        "question": "How is my baby today?"
    }
    response = client.post("/api/v1/ai/ask", json=payload)
    assert response.status_code == 403
    assert "forbidden" in response.text.lower() or "not belong" in response.text.lower()

def test_ask_ai_assistant_groq_failure(client, test_baby_id):
    payload = {
        "baby_id": test_baby_id,
        "family_id": 101,
        "question": "How is my baby today?"
    }
    
    with patch("app.ai.groq_service.call_groq") as mock_call:
        mock_call.side_effect = Exception("Connection error to Groq servers.")
        response = client.post("/api/v1/ai/ask", json=payload)
        
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()
