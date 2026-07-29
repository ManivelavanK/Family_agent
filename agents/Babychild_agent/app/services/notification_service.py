from app.notification import twilio_service
import logging

logger = logging.getLogger(__name__)

def send_feeding_alert(to_phone: str, baby_name: str, hours: float) -> dict:
    body = f"⚠️ Alert: Feeding is overdue for {baby_name}. It has been more than {hours} hours since the last feeding."
    return twilio_service.send_whatsapp_message(to_phone, body)

def send_fever_alert(to_phone: str, baby_name: str, temp: float) -> dict:
    body = f"🚨 Health Warning: High temperature of {temp}°C detected for {baby_name}. Please monitor closely."
    return twilio_service.send_whatsapp_message(to_phone, body)

def send_vaccination_reminder(to_phone: str, baby_name: str, vaccine_name: str, due_date: str) -> dict:
    body = f"📅 Vaccination Reminder: {vaccine_name} is due for {baby_name} on {due_date}. Please schedule an appointment."
    return twilio_service.send_whatsapp_message(to_phone, body)

def send_daily_summary(to_phone: str, baby_name: str, summary_text: str) -> dict:
    body = f"📝 Daily Summary for {baby_name}:\n{summary_text}"
    return twilio_service.send_whatsapp_message(to_phone, body)
