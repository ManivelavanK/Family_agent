import logging
import time
from sqlalchemy.orm import Session
from app.voice.intent_classifier import classify_intent
from app.models.grocery_item import GroceryItem
from app.models.alert import KitchenAlert
from app.models.settings import HouseholdSettings
from app.services.recipe_service import suggest_recipe
from app.ai.llm import call_llm
from app.ai.prompts import SYSTEM_CONVERSATIONAL

logger = logging.getLogger(__name__)


def process_voice_query(db: Session, text: str) -> dict:
    start_time = time.time()
    intent = classify_intent(text)
    logger.info("Voice Service: Intent classified as '%s'", intent)

    response_text = ""
    service_called = ""
    payload = {}

    try:
        if intent == "Stock Query":
            service_called = "Inventory Service"
            items = db.query(GroceryItem).all()
            if not items:
                response_text = "Your kitchen inventory is currently empty."
            else:
                stock_summary = [f"{item.name} ({item.quantity} {item.unit})" for item in items[:5]]
                response_text = f"You have: {', '.join(stock_summary)}."
                if len(items) > 5:
                    response_text += f" and {len(items) - 5} more items."
            payload = {"items_count": len(items)}

        elif intent == "Recipe Suggestion":
            service_called = "Recipe Service"
            try:
                recipe = suggest_recipe(db)
                response_text = recipe.get("recipe_suggestion", "I couldn't generate a recipe suggestion right now.")
                payload = {"success": True}
            except Exception as e:
                response_text = f"I failed to retrieve recipes: {str(e)}."
                payload = {"error": str(e)}

        elif intent == "AI Kitchen Assistant":
            service_called = "Kitchen Assistant Service"
            from app.services.kitchen_assistant import answer_kitchen_query
            response_text = answer_kitchen_query(text)
            payload = {"kitchen_query": text}

        elif intent == "Alert Status":
            service_called = "Rule Engine Alert Service"
            active_alerts = db.query(KitchenAlert).filter(KitchenAlert.status == "Active").all()
            if not active_alerts:
                response_text = "All kitchen parameters are normal. No active alerts."
            else:
                alert_list = [f"{a.title} ({a.severity})" for a in active_alerts]
                response_text = f"Active alerts are: {', '.join(alert_list)}."
            payload = {"alerts_count": len(active_alerts)}

        elif intent == "Emergency":
            service_called = "Emergency Notification Service"
            settings = db.query(HouseholdSettings).first()
            phone = settings.primary_contact_phone if settings else "the configured contact"
            from app.notification.whatsapp_service import send_message
            send_message(phone, "URGENT EMERGENCY KITCHEN ALERT TRIGGERED!")
            response_text = "Critical emergency triggered. Dispatching safety notification to your contact."
            payload = {"emergency_notified": True}

        else:  # Conversational Chat fallback
            service_called = "LLM Conversational Service"
            items = db.query(GroceryItem).all()
            stock_str = ", ".join([f"{i.name}: {i.quantity}" for i in items[:10]])
            user_prompt = f"Kitchen stock status: {stock_str}\nUser asks: {text}"
            response_text = call_llm(SYSTEM_CONVERSATIONAL, user_prompt)
            payload = {"conversational": True}

    except Exception as e:
        logger.exception("Error processing voice query")
        response_text = f"An error occurred while processing your request: {str(e)}"
        payload = {"error": str(e)}

    exec_time = round(time.time() - start_time, 4)
    return {
        "text_response": response_text,
        "intent": intent,
        "service_called": service_called,
        "execution_time_seconds": exec_time,
        "payload": payload
    }
