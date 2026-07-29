"""
Father Agent Client — KinNest Cross-Agent Integration Bridge

This module handles OUTBOUND HTTP communication FROM the Children Agent TO the Father Agent.

Architecture Rules:
- No direct imports from Father Agent source code.
- Communication via HTTP REST APIs only.
- If Father Agent is offline, fail gracefully with a clear status message.
- Never expose private student AI conversations to the Father Agent.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

FATHER_AGENT_BASE_URL = os.getenv("FATHER_AGENT_URL", "http://localhost:8001")
REQUEST_TIMEOUT_SECONDS = 5


def _is_father_agent_online() -> bool:
    """Ping the Father Agent health endpoint to determine availability."""
    try:
        response = requests.get(f"{FATHER_AGENT_BASE_URL}/health", timeout=REQUEST_TIMEOUT_SECONDS)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_family_financial_context(child_id: int) -> Optional[Dict[str, Any]]:
    """
    Request any child-relevant financial context from the Father Agent.
    Returns None gracefully if Father Agent is offline or data unavailable.
    
    NOTE: The Father Agent controls what financial data is shared.
    Children Agent does NOT have direct database access to Father Agent.
    """
    if not _is_father_agent_online():
        logger.warning("Father Agent is offline. Skipping financial context fetch.")
        return None

    try:
        response = requests.get(
            f"{FATHER_AGENT_BASE_URL}/api/v1/family/child-context/{child_id}",
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Father Agent returned {response.status_code} for child {child_id}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Father Agent context: {e}")
        return None


def notify_father_agent(child_id: int, event_type: str, summary: str) -> bool:
    """
    Send an academic event notification to the Father Agent (e.g., goal completed, exam passed).
    Returns False gracefully if Father Agent is offline.
    """
    if not _is_father_agent_online():
        logger.warning("Father Agent is offline. Skipping notification dispatch.")
        return False

    try:
        payload = {
            "child_id": child_id,
            "event_type": event_type,
            "summary": summary
        }
        response = requests.post(
            f"{FATHER_AGENT_BASE_URL}/api/v1/family/child-event",
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        return response.status_code in (200, 201)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error notifying Father Agent: {e}")
        return False
