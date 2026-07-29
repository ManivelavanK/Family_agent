import logging

logger = logging.getLogger(__name__)

TEMPLATES = {
    "medicine": "Reminder: {name}, please take your dose of {medicine} scheduled for {time}.",
    "emergency": "CRITICAL EMERGENCY ALERT: Emergency triggered for grandparent. Reason: {reason}. Severity: {severity}. Notes: {notes}",
    "appointment": "Reminder: Doctor visit with {doctor} ({specialty}) scheduled on {time}.",
    "low_stock": "Warning: Low inventory for {medicine}. Only {count} doses left. Please refill soon.",
    "weekly_report": "Weekly Health Summary: Average BP: {bp}, Sugar Avg: {sugar}. Complete PDF report download link: {url}",
    "daily_summary": "Daily Wellness Summary: Average BP: {bp}, Sleep: {sleep} hours, Water Intake: {water} ml. Health status: {status}."
}


def render_template(template_type: str, variables: dict) -> str:
    """
    Renders a message template by substituting variables.
    Falls back to a custom parameter dump if format keys fail.
    """
    template = TEMPLATES.get(template_type, "Notification Alert: {message}")
    try:
        return template.format(**variables)
    except KeyError as e:
        logger.warning("Template rendering warning: Missing variable %s. Dumping parameters directly.", e)
        # Safe fallback
        param_str = ", ".join(f"{k}: {v}" for k, v in variables.items())
        return f"Notification Type: {template_type}. Details: {param_str}"
