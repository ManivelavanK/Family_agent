import json
import logging
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import KINNEST_SUPERVISOR_SELECTION_PROMPT, KINNEST_SUPERVISOR_PROMPT
from app.communication.supervisor_schemas import (
    SupervisorRequest,
    SupervisorResponse,
    SupervisorAgentSelection,
    SupervisorAgentResponse,
    AgentHealthStatus
)
from app.communication.agent_registry import agent_registry
from app.services.family_context_service import FamilyContextService
from app.ai.context.retriever import ContextRetriever

logger = logging.getLogger("kinnest.ai.supervisor_agent")

class AISupervisorAgent:
    def __init__(self):
        self.groq = groq_service

    def select_relevant_agents(self, message: str) -> List[SupervisorAgentSelection]:
        logger.info(f"AI Supervisor selecting relevant agents for message: '{message}'")
        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_SUPERVISOR_SELECTION_PROMPT},
            {"role": "user", "content": f"USER REQUEST: {message}"}
        ]

        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            # Support root list, wrapped dictionary, or single dict
            items = []
            if isinstance(raw_json, list):
                items = raw_json
            elif isinstance(raw_json, dict):
                for key in ["agents", "selection", "selected_agents", "items"]:
                    if key in raw_json and isinstance(raw_json[key], list):
                        items = raw_json[key]
                        break

            selections = []
            for item in items:
                try:
                    selections.append(SupervisorAgentSelection.model_validate(item))
                except Exception as val_err:
                    logger.warning(f"Failed to validate agent selection item {item}: {val_err}")

            if not selections:
                logger.info("Groq returned empty agent selections; falling back to default agent list")
                selections = [
                    SupervisorAgentSelection(agent="father", reason="Financial & budget context", required_capabilities=["financial"]),
                    SupervisorAgentSelection(agent="mother", reason="Household & food context", required_capabilities=["food"]),
                    SupervisorAgentSelection(agent="child", reason="Education & schedule context", required_capabilities=["education"])
                ]

            logger.info(f"AI Supervisor selected {len(selections)} agents: {[s.agent for s in selections]}")
            return selections
        except Exception as exc:
            logger.warning(f"Fallback to default agent selection due to error: {exc}")
            # Safe default fallback: select father, mother, child
            return [
                SupervisorAgentSelection(agent="father", reason="Default financial context", required_capabilities=["financial"]),
                SupervisorAgentSelection(agent="mother", reason="Default household context", required_capabilities=["food"]),
                SupervisorAgentSelection(agent="child", reason="Default education schedule context", required_capabilities=["education"])
            ]

    async def process_request_async(
        self,
        db: Session,
        request: SupervisorRequest
    ) -> SupervisorResponse:
        logger.info(f"AI Supervisor processing request for family '{request.family_id}': '{request.message}'")

        # 1. AI agent selection
        selections = self.select_relevant_agents(request.message)
        selected_agent_names = [s.agent.lower() for s in selections]

        # 2. Parallel agent context gathering
        agent_responses: List[SupervisorAgentResponse] = await FamilyContextService.get_selected_agents_context(
            selected_agents=selected_agent_names,
            family_id=request.family_id
        )

        available_agents = [r.agent for r in agent_responses if r.available]
        unavailable_agents = [r.agent for r in agent_responses if not r.available]

        # 3. Retrieve local database context (Plans, Calendar, Memories, Guests, Routines)
        db_context = ContextRetriever.get_planning_context(db, family_id=request.family_id)

        # 4. Synthesize prompt context for Groq
        full_context = {
            "family_id": request.family_id,
            "selected_agents": selected_agent_names,
            "available_agent_data": {r.agent: r.response for r in agent_responses if r.available},
            "unavailable_agents": unavailable_agents,
            "database_context": db_context
        }

        client = self.groq.get_client()
        messages = [
            {"role": "system", "content": KINNEST_SUPERVISOR_PROMPT},
            {"role": "system", "content": f"FULL FACTUAL FAMILY CONTEXT:\n{json.dumps(full_context, default=str)}"},
            {"role": "user", "content": f"USER REQUEST: {request.message}"}
        ]

        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3000
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            rec = raw_json.get("recommendation", {})
            confidence = raw_json.get("confidence", 0.90)
            requires_approval = raw_json.get("requires_approval", True)
            next_action = raw_json.get("next_action", "REVIEW_RECOMMENDATION")

            # 5. Handle execution if explicit approval is granted
            if request.approved and request.execute:
                logger.info("Explicit user approval provided; executing supervisor recommendation...")
                requires_approval = False
                next_action = "EXECUTED"

            return SupervisorResponse(
                success=True,
                message="KinNest supervisor analysis completed successfully",
                request=request,
                selected_agents=selected_agent_names,
                agent_responses=agent_responses,
                available_agents=available_agents,
                unavailable_agents=unavailable_agents,
                family_context=full_context,
                recommendation=rec,
                confidence=confidence,
                requires_approval=requires_approval,
                next_action=next_action
            )
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq supervisor response: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI supervisor service returned invalid or malformed JSON format."
            )
        except Exception as exc:
            logger.error(f"Error in supervisor processing: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI supervisor error: {str(exc)}"
            )

    def process_request(self, db: Session, request: SupervisorRequest) -> SupervisorResponse:
        return asyncio.run(self.process_request_async(db, request))

    async def get_agents_health_async(self, family_id: str = "default_family") -> List[AgentHealthStatus]:
        all_agents = agent_registry.list_all_agents()
        agent_names = [a.name.split()[0].lower() for a in all_agents]

        from app.communication.agent_client import agent_client
        responses = await FamilyContextService.get_selected_agents_context(agent_names, family_id)

        health_list = []
        for agent_obj, res in zip(all_agents, responses):
            health_list.append(AgentHealthStatus(
                agent=res.agent,
                url=agent_obj.base_url,
                available=res.available,
                capabilities=agent_obj.capabilities,
                response_time_ms=res.response_time_ms
            ))
        return health_list

supervisor_agent = AISupervisorAgent()
