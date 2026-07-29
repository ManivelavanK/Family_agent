import pytest
from datetime import date, timedelta
from unittest.mock import patch, AsyncMock
import io

@pytest.fixture
def test_baby_id(client):
    # Setup: Create a baby profile
    payload = {
        "family_id": 101,
        "name": "Voice Test Baby",
        "date_of_birth": str(date.today() - timedelta(days=20))
    }
    res = client.post("/api/v1/baby/create", json=payload)
    return res.json()["data"]["id"]

def test_voice_query_success(client, test_baby_id):
    # Mock files & bytes
    audio_file = io.BytesIO(b"fake audio data")
    audio_file.name = "question.wav"
    
    with patch("app.voice.speech_to_text.transcribe_audio") as mock_stt, \
         patch("app.voice.text_to_speech.synthesize_text", new_callable=AsyncMock) as mock_tts, \
         patch("app.services.ai_service.get_ai_insights") as mock_ai:
         
        mock_stt.return_value = "How is my baby today?"
        mock_ai.return_value = "Your baby is healthy and fed."
        mock_tts.return_value = "output_path.mp3"
        
        response = client.post(
            "/api/v1/voice/query",
            data={"baby_id": test_baby_id, "family_id": 101},
            files={"file": ("question.wav", audio_file, "audio/wav")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["recognized_text"] == "How is my baby today?"
    assert data["data"]["answer"] == "Your baby is healthy and fed."
    assert "output_" in data["data"]["audio_file_path"]

def test_voice_query_invalid_baby(client):
    audio_file = io.BytesIO(b"fake audio data")
    audio_file.name = "question.wav"
    
    response = client.post(
        "/api/v1/voice/query",
        data={"baby_id": 9999, "family_id": 101},
        files={"file": ("question.wav", audio_file, "audio/wav")}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_voice_query_invalid_family(client, test_baby_id):
    audio_file = io.BytesIO(b"fake audio data")
    audio_file.name = "question.wav"
    
    response = client.post(
        "/api/v1/voice/query",
        data={"baby_id": test_baby_id, "family_id": 999},  # mismatch
        files={"file": ("question.wav", audio_file, "audio/wav")}
    )
    
    assert response.status_code == 403
    assert "forbidden" in response.text.lower() or "not belong" in response.text.lower()
