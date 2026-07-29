import pytest
from unittest.mock import patch, MagicMock
from app.services import notification_service

def test_send_test_notification_success(client):
    payload = {
        "phone_number": "+919876543210",
        "message": "Hello from Baby Agent"
    }
    
    with patch("app.notification.twilio_service.Client") as mock_twilio:
        mock_msg = MagicMock()
        mock_msg.sid = "SM12345"
        mock_msg.status = "queued"
        mock_twilio.return_value.messages.create.return_value = mock_msg
        
        response = client.post("/api/v1/notifications/test", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["sid"] == "SM12345"

def test_send_test_notification_failure(client):
    payload = {
        "phone_number": "+919876543210",
        "message": "Hello from Baby Agent"
    }
    
    with patch("app.notification.twilio_service.Client") as mock_twilio:
        mock_twilio.return_value.messages.create.side_effect = Exception("Twilio credential invalid.")
        response = client.post("/api/v1/notifications/test", json=payload)
        
    assert response.status_code == 500
    assert "failed to send test notification" in response.json()["detail"].lower()

def test_notification_templates():
    # Test formatting and dispatch structure
    with patch("app.notification.twilio_service.send_whatsapp_message") as mock_send:
        mock_send.return_value = {"sid": "SM999"}
        
        # 1. Feeding alert
        notification_service.send_feeding_alert("+12345", "John", 4.5)
        mock_send.assert_called_with("+12345", "⚠️ Alert: Feeding is overdue for John. It has been more than 4.5 hours since the last feeding.")

        # 2. Fever alert
        notification_service.send_fever_alert("+12345", "John", 38.6)
        mock_send.assert_called_with("+12345", "🚨 Health Warning: High temperature of 38.6°C detected for John. Please monitor closely.")

        # 3. Vaccine alert
        notification_service.send_vaccination_reminder("+12345", "John", "MMR", "2026-08-01")
        mock_send.assert_called_with("+12345", "📅 Vaccination Reminder: MMR is due for John on 2026-08-01. Please schedule an appointment.")

        # 4. Daily summary
        notification_service.send_daily_summary("+12345", "John", "Slept 10h, fed 3 times.")
        mock_send.assert_called_with("+12345", "📝 Daily Summary for John:\nSlept 10h, fed 3 times.")
