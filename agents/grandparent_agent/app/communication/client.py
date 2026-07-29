import logging
import httpx
from app.communication.models import AgentEventPayload

logger = logging.getLogger(__name__)


def send_event_to_agent(target_url: str, payload: AgentEventPayload) -> dict:
    """
    Delivers event payloads to the specified agent URL.
    Gracefully falls back to a mock delivery status if the target host is offline.
    """
    logger.info("Outgoing communication: Dispatching event to: %s", target_url)
    logger.info("Payload: %s", payload.model_dump())

    try:
        # Use a short timeout of 2 seconds for local peer checking
        response = httpx.post(
            target_url,
            json=payload.model_dump(),
            timeout=2.0
        )
        logger.info("Outgoing communication: Response code: %d", response.status_code)
        return {
            "status": "Delivered",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.warning("Outgoing communication: Target agent is offline. Falling back to mock delivery.")
        return {
            "status": "Mock Delivered (Target offline)",
            "target_url": target_url,
            "reason": str(e)
        }
    except Exception as e:
        logger.exception("Outgoing communication: Encountered unexpected failure during send")
        return {
            "status": "Failed",
            "reason": str(e)
        }
