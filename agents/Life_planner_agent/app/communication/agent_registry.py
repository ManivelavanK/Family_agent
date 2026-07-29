from typing import Dict, List, Optional
from app.config import settings
from app.communication.schemas import AgentCapabilities

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentCapabilities] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        self._agents["father"] = AgentCapabilities(
            name="Father Agent",
            base_url=settings.FATHER_AGENT_URL,
            capabilities=["financial", "budget", "savings"],
            is_mock=settings.AGENT_COMMUNICATION_MOCK
        )
        self._agents["mother"] = AgentCapabilities(
            name="Mother Agent",
            base_url=settings.MOTHER_AGENT_URL,
            capabilities=["food", "grocery", "nutrition"],
            is_mock=settings.AGENT_COMMUNICATION_MOCK
        )
        self._agents["child"] = AgentCapabilities(
            name="Child Agent",
            base_url=settings.CHILD_AGENT_URL,
            capabilities=["education", "exams", "child_schedule"],
            is_mock=settings.AGENT_COMMUNICATION_MOCK
        )
        self._agents["grandparent"] = AgentCapabilities(
            name="Grandparent Agent",
            base_url=settings.GRANDPARENT_AGENT_URL,
            capabilities=["health", "mobility", "appointments"],
            is_mock=settings.AGENT_COMMUNICATION_MOCK
        )
        self._agents["baby"] = AgentCapabilities(
            name="Baby Care Agent",
            base_url=settings.BABY_AGENT_URL,
            capabilities=["feeding", "sleep", "baby_care"],
            is_mock=settings.AGENT_COMMUNICATION_MOCK
        )

    def get_agent(self, name: str) -> Optional[AgentCapabilities]:
        return self._agents.get(name.lower())

    def get_agents_by_capability(self, capability: str) -> List[AgentCapabilities]:
        cap_lower = capability.lower()
        return [
            agent for agent in self._agents.values()
            if any(cap_lower in c.lower() for c in agent.capabilities)
        ]

    def list_all_agents(self) -> List[AgentCapabilities]:
        return list(self._agents.values())

agent_registry = AgentRegistry()
