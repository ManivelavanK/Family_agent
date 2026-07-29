import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import (
    KINNEST_PLAN_REVISION_PROMPT,
    KINNEST_PLAN_OPTIMIZE_PROMPT,
    KINNEST_PLAN_QUALITY_ANALYSIS_PROMPT
)
from app.ai.schemas import (
    AIPlanRevisionResponse,
    AIPlanOptimizeResponse,
    AIPlanQualityAnalysisResponse
)
from app.ai.context.retriever import ContextRetriever
from app.services.plan_service import PlanService

logger = logging.getLogger("kinnest.ai.executor_agent")

class AIExecutorAgent:
    def __init__(self):
        self.groq = groq_service

    def revise_plan(
        self,
        db: Session,
        plan_id: int,
        message: str,
        family_id: str = "default_family"
    ) -> AIPlanRevisionResponse:
        logger.info(f"AI Executor Agent revising plan #{plan_id} with instruction: '{message}'")
        
        plan = PlanService.get_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with ID {plan_id} not found"
            )

        context = ContextRetriever.get_planning_context(db, plan_id=plan_id)
        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_PLAN_REVISION_PROMPT},
            {"role": "system", "content": f"CONTEXT & EXISTING PLAN:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"REVISION INSTRUCTION: {message}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for plan revision")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2048
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            validated = AIPlanRevisionResponse.model_validate(raw_json)
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq revision response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI revision service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Plan revision response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI plan revision validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in plan revision: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI revision service error: {str(exc)}"
            )

    def optimize_plan(
        self,
        db: Session,
        plan_id: int,
        goal: str,
        family_id: str = "default_family"
    ) -> AIPlanOptimizeResponse:
        logger.info(f"AI Executor Agent optimizing plan #{plan_id} with goal: '{goal}'")
        
        plan = PlanService.get_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with ID {plan_id} not found"
            )

        context = ContextRetriever.get_planning_context(db, plan_id=plan_id)
        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_PLAN_OPTIMIZE_PROMPT},
            {"role": "system", "content": f"CONTEXT & EXISTING PLAN:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"OPTIMIZATION GOAL: {goal}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for plan optimization")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2048
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            validated = AIPlanOptimizeResponse.model_validate(raw_json)
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq optimization response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI optimization service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Plan optimization response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI plan optimization validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in plan optimization: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI optimization service error: {str(exc)}"
            )

    def analyze_plan_quality(
        self,
        db: Session,
        plan_id: int,
        family_id: str = "default_family"
    ) -> AIPlanQualityAnalysisResponse:
        logger.info(f"AI Executor Agent analyzing quality for plan #{plan_id}")

        plan = PlanService.get_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with ID {plan_id} not found"
            )

        context = ContextRetriever.get_planning_context(db, plan_id=plan_id)
        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_PLAN_QUALITY_ANALYSIS_PROMPT},
            {"role": "user", "content": f"PLAN DETAILS & CONTEXT:\n{json.dumps(context, default=str)}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for quality analysis")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1500
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            validated = AIPlanQualityAnalysisResponse.model_validate(raw_json)
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq quality analysis response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI quality analysis service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Plan quality analysis response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI plan quality analysis validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in quality analysis: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI quality analysis service error: {str(exc)}"
            )

executor_agent = AIExecutorAgent()
