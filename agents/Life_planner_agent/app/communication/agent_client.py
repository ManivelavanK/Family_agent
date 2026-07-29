import logging
from typing import Optional, Dict, Any
import httpx
from app.config import settings
from app.communication.agent_registry import agent_registry
from app.communication.schemas import (
    FatherContext, MotherContext, ChildContext, GrandparentContext, BabyContext
)

logger = logging.getLogger("kinnest.communication.client")

class AgentClientService:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    async def get_father_context(self, family_id: str) -> Optional[FatherContext]:
        agent = agent_registry.get_agent("father")
        if settings.AGENT_COMMUNICATION_MOCK:
            logger.info(f"[MOCK MODE] Returning mock FatherContext for family {family_id}")
            return FatherContext(
                available_budget=35000.0,
                monthly_savings_goal=10000.0,
                financial_notes="Trip budget ceiling approved up to 35,000 INR."
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{agent.base_url}/api/v1/context?family_id={family_id}")
                if res.status_code == 200:
                    return FatherContext.model_validate(res.json().get("data", {}))
        except Exception as exc:
            logger.warning(f"Failed to retrieve context from Father Agent: {exc}")
        return None

    async def get_mother_context(self, family_id: str) -> Optional[MotherContext]:
        agent = agent_registry.get_agent("mother")
        if settings.AGENT_COMMUNICATION_MOCK:
            logger.info(f"[MOCK MODE] Returning mock MotherContext for family {family_id}")
            return MotherContext(
                food_preferences=["Vegetarian", "South Indian Buffet", "Home-style meals"],
                grocery_budget_limit=8000.0,
                dietary_restrictions=["No artificial preservatives", "Mild spice"]
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{agent.base_url}/api/v1/context?family_id={family_id}")
                if res.status_code == 200:
                    return MotherContext.model_validate(res.json().get("data", {}))
        except Exception as exc:
            logger.warning(f"Failed to retrieve context from Mother Agent: {exc}")
        return None

    async def get_child_context(self, family_id: str) -> Optional[ChildContext]:
        agent = agent_registry.get_agent("child")
        if settings.AGENT_COMMUNICATION_MOCK:
            logger.info(f"[MOCK MODE] Returning mock ChildContext for family {family_id}")
            return ChildContext(
                upcoming_exams=[
                    {"subject": "Mathematics", "date": "2026-08-18", "importance": "HIGH"}
                ],
                extracurricular_schedule=[
                    {"activity": "Swimming coaching", "days": ["Tuesday", "Thursday"], "time": "17:00-18:30"}
                ]
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{agent.base_url}/api/v1/context?family_id={family_id}")
                if res.status_code == 200:
                    return ChildContext.model_validate(res.json().get("data", {}))
        except Exception as exc:
            logger.warning(f"Failed to retrieve context from Child Agent: {exc}")
        return None

    async def get_grandparent_context(self, family_id: str) -> Optional[GrandparentContext]:
        agent = agent_registry.get_agent("grandparent")
        if settings.AGENT_COMMUNICATION_MOCK:
            logger.info(f"[MOCK MODE] Returning mock GrandparentContext for family {family_id}")
            return GrandparentContext(
                mobility_level="LOW_WALKING",
                doctor_appointments=[
                    {"type": "Cardiology Checkup", "date": "2026-08-12", "time": "10:00:00"}
                ],
                health_notes="Prefers itinerary activities with minimal stair climbing and frequent rest stops."
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{agent.base_url}/api/v1/context?family_id={family_id}")
                if res.status_code == 200:
                    return GrandparentContext.model_validate(res.json().get("data", {}))
        except Exception as exc:
            logger.warning(f"Failed to retrieve context from Grandparent Agent: {exc}")
        return None

    async def get_baby_context(self, family_id: str) -> Optional[BabyContext]:
        agent = agent_registry.get_agent("baby")
        if settings.AGENT_COMMUNICATION_MOCK:
            logger.info(f"[MOCK MODE] Returning mock BabyContext for family {family_id}")
            return BabyContext(
                feeding_schedule="Every 3 hours",
                sleep_routine="Afternoon nap 13:00 to 15:00",
                special_care_notes="Stroller required for outdoor movement."
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{agent.base_url}/api/v1/context?family_id={family_id}")
                if res.status_code == 200:
                    return BabyContext.model_validate(res.json().get("data", {}))
        except Exception as exc:
            logger.warning(f"Failed to retrieve context from Baby Care Agent: {exc}")
        return None

    async def get_agent_response(self, agent_name: str, family_id: str) -> "SupervisorAgentResponse":
        import time
        from app.communication.supervisor_schemas import SupervisorAgentResponse

        agent = agent_registry.get_agent(agent_name)
        if not agent:
            return SupervisorAgentResponse(
                agent=agent_name,
                available=False,
                error=f"Agent '{agent_name}' is not registered in AgentRegistry"
            )

        start_t = time.time()
        if settings.AGENT_COMMUNICATION_MOCK:
            elapsed_ms = round((time.time() - start_t) * 1000, 2)
            mock_method_name = f"get_{agent_name.lower()}_context"
            mock_method = getattr(self, mock_method_name, None)
            if mock_method:
                ctx = await mock_method(family_id)
                return SupervisorAgentResponse(
                    agent=agent_name,
                    available=True,
                    response=ctx.model_dump() if ctx else {},
                    response_time_ms=elapsed_ms
                )
            return SupervisorAgentResponse(
                agent=agent_name,
                available=True,
                response={"status": "mock_active"},
                response_time_ms=elapsed_ms
            )

        if not agent.base_url:
            return SupervisorAgentResponse(
                agent=agent_name,
                available=False,
                error=f"Agent '{agent_name}' base URL is not configured."
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{agent.base_url}/api/v1/context?family_id={family_id}"
                res = await client.get(url)
                elapsed_ms = round((time.time() - start_t) * 1000, 2)
                if res.status_code == 200:
                    data = res.json().get("data", res.json())
                    return SupervisorAgentResponse(
                        agent=agent_name,
                        available=True,
                        response=data,
                        response_time_ms=elapsed_ms
                    )
                return SupervisorAgentResponse(
                    agent=agent_name,
                    available=False,
                    error=f"HTTP {res.status_code}: {res.text}",
                    response_time_ms=elapsed_ms
                )
        except Exception as exc:
            elapsed_ms = round((time.time() - start_t) * 1000, 2)
            logger.warning(f"Connection failure to agent '{agent_name}': {exc}")
            return SupervisorAgentResponse(
                agent=agent_name,
                available=False,
                error=f"Agent endpoint unavailable: {str(exc)}",
                response_time_ms=elapsed_ms
            )

agent_client_service = AgentClientService()
agent_client = agent_client_service
