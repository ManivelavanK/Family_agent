import logging

logger = logging.getLogger(__name__)

# Map intents to a set of matching keywords
INTENT_KEYWORDS = {
    "Emergency": ["emergency", "help", "sos", "hurt", "pain", "doctor", "accident", "ambulance"],
    "Medicine Query": ["medicine", "tablet", "dose", "pill", "refill", "medication", "prescribe", "take"],
    "Appointment Query": ["appointment", "doctor", "hospital", "visit", "clinic", "physician", "dentist"],
    "Vitals Query": ["blood pressure", "bp", "sugar", "heart rate", "pulse", "temperature", "systolic", "diastolic", "vitals"],
    "Memory Journal": ["journal", "remember", "today", "write", "diary", "reflection", "log"],
    "General Health Recommendation": ["recommend", "healthy", "food", "eat", "diet", "exercise", "nutrition"],
    "Reminder Query": ["reminder", "alarm", "schedule", "active", "remind"],
    "WhatsApp Dispatch": ["send my health report", "message", "whatsapp", "notify my daughter", "notify my son", "text ravi"]
}


def classify_intent(text: str) -> str:
    """
    Classifies a string query into one of the supported intents.
    Returns 'General Health Recommendation' as a fallback if no keywords match.
    """
    text_lower = text.lower()
    logger.info("Classifying intent for text query: '%s'", text)

    # First check emergency as it's critical
    for keyword in INTENT_KEYWORDS["Emergency"]:
        if keyword in text_lower:
            logger.info("Intent classified: Emergency")
            return "Emergency"

    for intent, keywords in INTENT_KEYWORDS.items():
        if intent == "Emergency":
            continue
        for keyword in keywords:
            if keyword in text_lower:
                logger.info("Intent classified: %s", intent)
                return intent

    logger.info("No explicit keywords matched. Falling back to General Health Recommendation.")
    return "General Health Recommendation"
