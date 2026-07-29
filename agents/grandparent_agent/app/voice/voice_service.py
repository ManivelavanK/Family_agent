import logging
import time
from sqlalchemy.orm import Session

# Import services
from app.services.profile_service import get_profile
from app.services.medicine_service import get_medicines
from app.services.reminder_service import get_reminders
from app.services.recommendation_service import get_personalized_recommendations
from app.models.vitals import Vitals
from app.models.appointment import Appointment
from app.models.profile import Profile
from app.voice.intent_classifier import classify_intent
from app.services.notification_service import send_notification
from app.ai.groq_service import add_journal_entry

logger = logging.getLogger(__name__)


def process_voice_query(db: Session, text: str) -> dict:
    """
    Orchestration layer. Receives transcribed text, detects intent,
    executes the relevant service, and returns structured data and speech output.
    """
    start_time = time.time()
    intent = classify_intent(text)
    logger.info("Voice Service: Intent classified as '%s'", intent)

    response_text = ""
    service_called = ""
    payload = {}

    try:
        if intent == "Medicine Query":
            service_called = "Medicine Service"
            meds = get_medicines(db, active_only=True)
            if not meds:
                response_text = "You have no active medicines listed in your schedule."
            else:
                med_list = [f"{m.name} ({m.dosage}, {m.time_of_day})" for m in meds]
                response_text = f"Your active medications are: {', '.join(med_list)}."
            payload = {"medicines": [m.name for m in meds]}

        elif intent == "Vitals Query":
            service_called = "Vitals Service"
            last_vital = db.query(Vitals).order_by(Vitals.timestamp.desc()).first()
            if not last_vital:
                response_text = "No vital signs logs found. Please log your blood pressure or sugar."
            else:
                response_text = (
                    f"Your latest blood pressure is {last_vital.blood_pressure_systolic} over "
                    f"{last_vital.blood_pressure_diastolic} mmHg. Your heart rate is {last_vital.heart_rate} bpm."
                )
            payload = last_vital.__dict__ if last_vital else {}
            payload.pop("_sa_instance_state", None)

        elif intent == "Appointment Query":
            service_called = "Appointment Service"
            appointments = db.query(Appointment).order_by(Appointment.appointment_time.asc()).all()
            if not appointments:
                response_text = "You have no scheduled appointments."
            else:
                next_app = appointments[0]
                response_text = f"Your next appointment is with {next_app.doctor_name} ({next_app.specialty}) on {next_app.appointment_time.strftime('%B %d at %I:%M %p')}."
            payload = {"appointments_count": len(appointments)}

        elif intent == "Reminder Query":
            service_called = "Reminder Service"
            reminders = get_reminders(active_only=True)
            if not reminders:
                response_text = "You have no active reminders."
            else:
                rem_list = [f"{r.title} scheduled for {r.trigger_time.strftime('%I:%M %p')}" for r in reminders]
                response_text = f"Your active reminders are: {', '.join(rem_list)}."
            payload = {"reminders": [r.title for r in reminders]}

        elif intent == "Emergency":
            service_called = "Emergency Service"
            profile = db.query(Profile).first()
            if not profile or not profile.emergency_contact_phone:
                response_text = "Emergency triggered, but no contact details are configured."
            else:
                alert_body = f"CRITICAL: Emergency voice alert triggered. Please contact {profile.name} immediately."
                send_notification("CRITICAL EMERGENCY VOICE TRIGGERED", alert_body, "Emergency")
                response_text = f"Emergency alert sent. Notifying your contact, {profile.emergency_contact_name} immediately."
            payload = {"emergency_triggered": True}

        elif intent == "Memory Journal":
            service_called = "Memory Service"
            # Log the voice request as a daily journal entry context
            add_journal_entry(text)
            response_text = "Your journal reflection has been recorded to your cognitive memory."
            payload = {"journal_entry": text}

        elif intent == "WhatsApp Dispatch":
            service_called = "WhatsApp Notification Service"
            recipient = config.DEFAULT_FAMILY_PHONE
            text_lower = text.lower()
            
            if "daughter" in text_lower:
                response_contact = "daughter"
            elif "son" in text_lower:
                response_contact = "son"
            elif "ravi" in text_lower:
                response_contact = "Ravi"
            else:
                response_contact = "family"

            # Extract message details
            if "that" in text_lower:
                message_content = text.split("that", 1)[1].strip()
            elif "health report" in text_lower:
                # Fetch latest vitals details to format report
                last_vital = db.query(Vitals).order_by(Vitals.timestamp.desc()).first()
                bp_str = f"{last_vital.blood_pressure_systolic}/{last_vital.blood_pressure_diastolic}" if last_vital else "120/80"
                sugar_val = last_vital.blood_sugar if last_vital else 95.0
                message_content = f"Here is my latest health summary: BP: {bp_str}, Sugar: {sugar_val} mg/dL."
            else:
                message_content = text

            # Trigger WhatsApp dispatch
            from app.notification.whatsapp_service import send_message
            send_message(recipient, message_content)
            
            response_text = f"I have sent the WhatsApp message to your {response_contact}."
            payload = {"whatsapp_sent": True, "message": message_content, "recipient": response_contact}

        else:  # General Health Recommendation
            service_called = "Recommendation Service"
            recs = get_personalized_recommendations(db)
            if recs.recommendations:
                suggestions = [r.suggestion for r in recs.recommendations]
                response_text = f"Here is your health recommendation: {', '.join(suggestions)}"
            else:
                response_text = "Your vitals and activities look perfect. Keep up the good work!"
            payload = recs.model_dump()

    except Exception as e:
        logger.exception("Error executing service logic inside Voice orchestrator")
        response_text = "I encountered an error executing that request. Please try again."
        payload = {"error": str(e)}

    execution_time = time.time() - start_time
    logger.info("Voice Service: Execution time: %.4fs, Service called: %s", execution_time, service_called)

    return {
        "text_response": response_text,
        "intent": intent,
        "service_called": service_called,
        "execution_time_seconds": round(execution_time, 4),
        "payload": payload
    }


def run_conversational_chat(db: Session, text: str) -> dict:
    """
    Stateful conversational chat. Reads latest patient health logs,
    generates a personalized summary response using Groq, and compiles metadata.
    """
    from app.ai.llm import call_llm
    start_time = time.time()
    logger.info("Voice Service: Starting conversational chat evaluation for: '%s'", text)

    # 1. Fetch Vitals
    last_vital = db.query(Vitals).order_by(Vitals.timestamp.desc()).first()
    sys = last_vital.blood_pressure_systolic if last_vital else 120
    dia = last_vital.blood_pressure_diastolic if last_vital else 80
    sugar = last_vital.blood_sugar if last_vital else 95.0
    hr = last_vital.heart_rate if last_vital else 72

    # 2. Fetch Medicines
    active_meds = get_medicines(db, active_only=True)
    med_list = [f"{m.name} ({m.dosage} at {m.time_of_day})" for m in active_meds] if active_meds else ["None listed"]

    # 3. Fetch Activity
    last_activity = db.query(Activity).order_by(Activity.date.desc()).first()
    sleep = last_activity.sleep_hours if last_activity else 7.0
    steps = last_activity.steps if last_activity else 0

    # 4. Fetch daily nutrition sum
    last_nutrition = db.query(Nutrition).order_by(Nutrition.timestamp.desc()).first()
    if last_nutrition:
        target_date = last_nutrition.timestamp.date()
        calories = db.query(func.sum(Nutrition.calories)).filter(
            func.date(Nutrition.timestamp) == target_date
        ).scalar() or 2000.0
        water = db.query(func.sum(Nutrition.water_ml)).filter(
            func.date(Nutrition.timestamp) == target_date
        ).scalar() or 1800.0
    else:
        calories = 2000.0
        water = 1800.0

    # Construct LLM prompt
    system_prompt = (
        "You are a warm, friendly, and caring AI wellness coach for an elderly grandparent. "
        "Keep your response concise, clear, and reassuring. Speak directly to the grandparent. "
        "Do not use markdown formatting like bold asterisks or lists since this response will be read aloud."
    )
    user_prompt = (
        f"Grandparent logs today:\n"
        f"- Vitals: Blood pressure is {sys}/{dia} mmHg, Heart rate is {hr} bpm, Blood sugar is {sugar} mg/dL.\n"
        f"- Active Medicines: {', '.join(med_list)}.\n"
        f"- Activity: Slept {sleep} hours and walked {steps} steps.\n"
        f"- Nutrition: Drank {water}ml water and consumed {calories} calories.\n\n"
        f"Grandparent asks: '{text}'\n\n"
        f"Generate a friendly, natural spoken response addressing their query."
    )

    # Query LLM
    response_text = call_llm(system_prompt, user_prompt, json_response=False)
    
    # Clean response from asterisks or brackets
    response_text = response_text.replace("*", "").replace("[", "").replace("]", "").strip()

    execution_time = time.time() - start_time
    logger.info("Voice Service: Conversational response generated: '%s'", response_text)

    payload = {
        "vitals": {"bp": f"{sys}/{dia}", "sugar": sugar, "heart_rate": hr},
        "medicines": med_list,
        "activity": {"sleep": sleep, "steps": steps},
        "nutrition": {"water": water, "calories": calories}
    }

    return {
        "text_response": response_text,
        "intent": "Conversational Chat",
        "execution_time_seconds": round(execution_time, 4),
        "payload": payload
    }

