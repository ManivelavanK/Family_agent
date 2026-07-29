import logging
from app.config import FATHER_AGENT_URL, CHILDREN_AGENT_URL, GRANDPARENT_AGENT_URL
from app.communication.client import send_event_to_agent
from app.communication.models import AgentEventPayload

logger = logging.getLogger(__name__)


def send_to_father(payload: AgentEventPayload) -> dict:
    return send_event_to_agent(FATHER_AGENT_URL, payload)


def send_to_children(payload: AgentEventPayload) -> dict:
    return send_event_to_agent(CHILDREN_AGENT_URL, payload)


def send_to_grandparent(payload: AgentEventPayload) -> dict:
    return send_event_to_agent(GRANDPARENT_AGENT_URL, payload)
