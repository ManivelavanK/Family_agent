import json
import datetime
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import (
    KINNEST_TRAVEL_PLANNING_PROMPT,
    KINNEST_TRAVEL_REVISION_PROMPT,
    KINNEST_TRAVEL_OPTIMIZE_PROMPT,
    KINNEST_TRAVEL_QUALITY_PROMPT
)
from app.ai.schemas import (
    AITravelPlan,
    AITravelPlanningResponse,
    AITravelQualityAnalysisResponse
)
from app.ai.context.retriever import ContextRetriever

logger = logging.getLogger("kinnest.ai.travel_agent")

class AITravelAgent:
    def __init__(self):
        self.groq = groq_service

    def plan_travel_visit(
        self,
        db: Session,
        message: str,
        family_id: str = "default_family",
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None
    ) -> AITravelPlanningResponse:
        logger.info(f"AI Travel Agent planning trip for family '{family_id}': '{message}'")

        # 1. Retrieve database, memory, and calendar context
        context = ContextRetriever.get_planning_context(db, family_id=family_id)
        if start_date:
            context["requested_start_date"] = str(start_date)
        if end_date:
            context["requested_end_date"] = str(end_date)

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_TRAVEL_PLANNING_PROMPT},
            {"role": "system", "content": f"FACTUAL FAMILY & CALENDAR CONTEXT:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"TRAVEL REQUEST: {message}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for travel intelligence reasoning")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3500
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            validated = AITravelPlanningResponse.model_validate(raw_json)
            logger.info(f"Successfully validated AI travel planning response for destination '{validated.travel_plan.destination}'")
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq travel response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI travel planning service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Travel planning response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI travel planning validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in travel planning: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI travel planning service error: {str(exc)}"
            )

    def revise_travel_plan(
        self,
        db: Session,
        message: str,
        current_travel_plan: AITravelPlan,
        family_id: str = "default_family"
    ) -> AITravelPlanningResponse:
        logger.info(f"AI Travel Agent revising travel plan for family '{family_id}': '{message}'")
        context = ContextRetriever.get_planning_context(db, family_id=family_id)

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_TRAVEL_REVISION_PROMPT},
            {"role": "system", "content": f"EXISTING TRAVEL PLAN:\n{json.dumps(current_travel_plan.model_dump(), default=str)}"},
            {"role": "system", "content": f"FACTUAL FAMILY CONTEXT:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"REVISION INSTRUCTION: {message}"}
        ]

        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3500
            )
            raw_content = response.choices[0].message.content
            return AITravelPlanningResponse.model_validate(json.loads(raw_content))
        except Exception as exc:
            logger.error(f"Error in travel revision: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI travel revision error: {str(exc)}"
            )

    def optimize_travel_plan(
        self,
        db: Session,
        message: str,
        current_travel_plan: AITravelPlan,
        family_id: str = "default_family"
    ) -> AITravelPlanningResponse:
        logger.info(f"AI Travel Agent optimizing travel plan for family '{family_id}': '{message}'")
        context = ContextRetriever.get_planning_context(db, family_id=family_id)

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_TRAVEL_OPTIMIZE_PROMPT},
            {"role": "system", "content": f"EXISTING TRAVEL PLAN:\n{json.dumps(current_travel_plan.model_dump(), default=str)}"},
            {"role": "system", "content": f"FACTUAL FAMILY CONTEXT:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"OPTIMIZATION GOAL: {message}"}
        ]

        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3500
            )
            raw_content = response.choices[0].message.content
            return AITravelPlanningResponse.model_validate(json.loads(raw_content))
        except Exception as exc:
            logger.error(f"Error in travel optimization: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI travel optimization error: {str(exc)}"
            )

    def analyze_travel_quality(
        self,
        db: Session,
        current_travel_plan: AITravelPlan,
        family_id: str = "default_family"
    ) -> AITravelQualityAnalysisResponse:
        logger.info(f"AI Travel Agent analyzing quality for family '{family_id}'")
        context = ContextRetriever.get_planning_context(db, family_id=family_id)

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_TRAVEL_QUALITY_PROMPT},
            {"role": "system", "content": f"TRAVEL PLAN TO EVALUATE:\n{json.dumps(current_travel_plan.model_dump(), default=str)}"},
            {"role": "system", "content": f"FACTUAL CONTEXT:\n{json.dumps(context, default=str)}"}
        ]

        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2000
            )
            raw_content = response.choices[0].message.content
            return AITravelQualityAnalysisResponse.model_validate(json.loads(raw_content))
        except Exception as exc:
            logger.error(f"Error in travel quality analysis: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI travel quality analysis error: {str(exc)}"
            )

travel_agent = AITravelAgent()
