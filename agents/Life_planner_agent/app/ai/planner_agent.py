import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.schemas import AIPlanningResponse, AIContextSelectionResponse
from app.ai.prompts import KINNEST_CONTEXT_SELECTION_PROMPT
from app.ai.context.retriever import ContextRetriever
from app.ai.tool_registry import tool_registry
from app.services.family_context_service import FamilyContextService

logger = logging.getLogger("kinnest.ai.planner")

class AIPlannerAgent:
    def __init__(self):
        self.groq = groq_service
        self.tools = tool_registry

    def select_required_context(self, message: str) -> AIContextSelectionResponse:
        client = self.groq.get_client()
        messages = [
            {"role": "system", "content": KINNEST_CONTEXT_SELECTION_PROMPT},
            {"role": "user", "content": message}
        ]
        try:
            logger.info("Invoking Groq for AI Context Selection")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500
            )
            raw_content = response.choices[0].message.content
            return AIContextSelectionResponse.model_validate(json.loads(raw_content))
        except Exception as exc:
            logger.warning(f"AI Context Selection failed, falling back to default domains: {exc}")
            return AIContextSelectionResponse(
                required_agent_domains=["father", "mother", "child", "grandparent", "baby"],
                reasoning="Fallback to retrieving all available family agent domains due to context selection error."
            )

    def process_planning_request(
        self,
        db: Session,
        message: str,
        plan_id: Optional[int] = None,
        family_id: str = "default_family"
    ) -> AIPlanningResponse:
        logger.info(f"AI Planner processing message: '{message}' for family '{family_id}'")

        # 1. AI Context Selection
        selection = self.select_required_context(message)
        logger.info(f"AI selected domains: {selection.required_agent_domains}")

        # 2. Retrieve Cross-Agent Context
        family_ctx = FamilyContextService.get_aggregated_family_context_sync(
            family_id=family_id,
            required_domains=selection.required_agent_domains
        )

        # 3. Retrieve Combined Database + Calendar + Memory Context
        context = ContextRetriever.get_planning_context(
            db,
            plan_id=plan_id,
            family_id=family_id,
            family_agent_context=family_ctx.model_dump()
        )

        # 4. Invoke Groq API for Family-Aware Plan Generation
        raw_response = self.groq.generate_structured_plan(
            user_message=message,
            context=context
        )

        # 5. Validate against Pydantic schema
        try:
            validated_plan = AIPlanningResponse.model_validate(raw_response)
            
            # Enrich response with context metadata if not populated by LLM
            if not validated_plan.context_sources:
                validated_plan.context_sources = family_ctx.available_sources + ["planner_memory", "calendar"]

            logger.info(f"Successfully validated AI planning response. Plan type: {validated_plan.plan_type}")
            return validated_plan
        except ValidationError as exc:
            logger.error(f"AI response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI response validation error: {str(exc)}"
            )

planner_agent = AIPlannerAgent()
