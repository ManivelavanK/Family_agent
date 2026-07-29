import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import KINNEST_PROACTIVE_ANALYSIS_PROMPT
from app.ai.schemas import AIProactiveAnalysisResponse
from app.ai.context.retriever import ContextRetriever

logger = logging.getLogger("kinnest.ai.proactive_agent")

class AIProactivePlannerAgent:
    def __init__(self):
        self.groq = groq_service

    def analyze_proactive_context(
        self,
        db: Session,
        family_id: str = "default_family",
        lookahead_days: int = 30
    ) -> AIProactiveAnalysisResponse:
        logger.info(f"AI Proactive Planner analyzing context for family '{family_id}' with {lookahead_days}-day lookahead")

        # 1. Retrieve purely factual context
        context = ContextRetriever.get_planning_context(db, family_id=family_id)
        context["lookahead_days"] = lookahead_days

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_PROACTIVE_ANALYSIS_PROMPT},
            {"role": "user", "content": f"FACTUAL FAMILY CONTEXT:\n{json.dumps(context, default=str)}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for proactive analysis")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2048
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            validated = AIProactiveAnalysisResponse.model_validate(raw_json)
            logger.info(f"Successfully validated AI proactive analysis response. Generated {len(validated.insights)} insights.")
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq proactive analysis response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI proactive analysis service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Proactive analysis response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI proactive analysis validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in proactive analysis: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI proactive analysis service error: {str(exc)}"
            )

proactive_agent = AIProactivePlannerAgent()
