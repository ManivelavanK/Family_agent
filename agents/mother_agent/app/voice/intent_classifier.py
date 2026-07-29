import logging

logger = logging.getLogger(__name__)

INTENT_KEYWORDS = {
    "Emergency": ["emergency", "help", "sos", "pain", "accident", "ambulance", "hurt"],
    "Stock Query": ["stock", "quantity", "inventory", "available", "do we have", "how many"],
    "Recipe Suggestion": ["recipe", "cook", "meal", "dinner", "suggest a recipe", "dish"],
    "AI Kitchen Assistant": ["store", "storage", "substitute", "substitution", "cook prep", "tips", "how to cut"],
    "Alert Status": ["alert", "alerts", "warning", "warnings", "any issue", "low stock", "expired"]
}


def classify_intent(text: str) -> str:
    text_lower = text.lower()
    logger.info("Classifying grocery intent for text query: '%s'", text)

    # First check emergency
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

    logger.info("No explicit keywords matched. Falling back to General Conversational Chat.")
    return "General Conversational Chat"
