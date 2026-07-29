import asyncio
import logging
from typing import List, Optional
from app.communication.agent_client import agent_client_service
from app.communication.schemas import FamilyAgentContext

logger = logging.getLogger("kinnest.services.family_context")

class FamilyContextService:
    @staticmethod
    async def get_aggregated_family_context(
        family_id: str,
        required_domains: Optional[List[str]] = None
    ) -> FamilyAgentContext:
        logger.info(f"Aggregating family context for '{family_id}' with domains: {required_domains}")

        # Default to all domains if not explicitly requested
        domains = [d.lower() for d in required_domains] if required_domains else ["father", "mother", "child", "grandparent", "baby"]
        
        ctx = FamilyAgentContext(family_id=family_id)

        # Retrieve concurrently
        tasks = []
        domain_keys = []

        if any(d in domains for d in ["father", "financial", "budget"]):
            tasks.append(agent_client_service.get_father_context(family_id))
            domain_keys.append("father")

        if any(d in domains for d in ["mother", "food", "grocery"]):
            tasks.append(agent_client_service.get_mother_context(family_id))
            domain_keys.append("mother")

        if any(d in domains for d in ["child", "education", "exams", "child_schedule"]):
            tasks.append(agent_client_service.get_child_context(family_id))
            domain_keys.append("child")

        if any(d in domains for d in ["grandparent", "health", "mobility", "appointments"]):
            tasks.append(agent_client_service.get_grandparent_context(family_id))
            domain_keys.append("grandparent")

        if any(d in domains for d in ["baby", "feeding", "sleep", "baby_care"]):
            tasks.append(agent_client_service.get_baby_context(family_id))
            domain_keys.append("baby")

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for key, res in zip(domain_keys, results):
                if isinstance(res, Exception) or res is None:
                    ctx.unavailable_sources.append(f"{key}_agent")
                    if isinstance(res, Exception):
                        ctx.retrieval_errors.append(f"{key}_agent: {str(res)}")
                else:
                    setattr(ctx, key, res)
                    ctx.available_sources.append(f"{key}_agent")

        logger.info(f"Family context aggregation finished. Available: {ctx.available_sources}, Unavailable: {ctx.unavailable_sources}")
        return ctx

    @staticmethod
    async def get_selected_agents_context(
        selected_agents: List[str],
        family_id: str
    ) -> List["SupervisorAgentResponse"]:
        tasks = [agent_client_service.get_agent_response(agent, family_id) for agent in selected_agents]
        if not tasks:
            return []
        results = await asyncio.gather(*tasks, return_exceptions=True)
        final_responses = []
        for agent_name, res in zip(selected_agents, results):
            if isinstance(res, Exception):
                from app.communication.supervisor_schemas import SupervisorAgentResponse
                final_responses.append(SupervisorAgentResponse(
                    agent=agent_name,
                    available=False,
                    error=str(res)
                ))
            else:
                final_responses.append(res)
        return final_responses

    @staticmethod
    def get_aggregated_family_context_sync(
        family_id: str,
        required_domains: Optional[List[str]] = None
    ) -> FamilyAgentContext:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # In an existing running event loop (e.g. inside FastAPI handler)
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(FamilyContextService.get_aggregated_family_context(family_id, required_domains))
        else:
            return loop.run_until_complete(FamilyContextService.get_aggregated_family_context(family_id, required_domains))
