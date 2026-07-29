import json
import datetime
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import KINNEST_ROUTINE_PLANNING_PROMPT
from app.ai.schemas import AIRoutinePlanningResponse
from app.ai.context.retriever import ContextRetriever

logger = logging.getLogger("kinnest.ai.routine_agent")

class AIRoutinePlanningAgent:
    def __init__(self):
        self.groq = groq_service

    def plan_routine(
        self,
        db: Session,
        message: str,
        family_id: str = "default_family",
        target_date: Optional[datetime.date] = None
    ) -> AIRoutinePlanningResponse:
        t_date = target_date or datetime.date.today() + datetime.timedelta(days=1)
        logger.info(f"AI Routine Agent planning daily schedule for family '{family_id}' on {t_date}: '{message}'")

        # 1. Retrieve comprehensive factual context
        context = ContextRetriever.get_planning_context(db, family_id=family_id)
        context["target_date"] = str(t_date)

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_ROUTINE_PLANNING_PROMPT},
            {"role": "system", "content": f"FACTUAL FAMILY & SCHEDULE CONTEXT:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"ROUTINE REQUEST FOR {t_date}: {message}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for routine planning reasoning")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3000
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            # Ensure target_date and family_id consistency if LLM omits them
            if "target_date" not in raw_json or not raw_json["target_date"]:
                raw_json["target_date"] = str(t_date)
            if "family_id" not in raw_json or not raw_json["family_id"]:
                raw_json["family_id"] = family_id

            validated = AIRoutinePlanningResponse.model_validate(raw_json)
            logger.info(f"Successfully validated AI routine planning response for {validated.target_date} with {len(validated.routine_items)} items")
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq routine response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI routine planning service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Routine planning response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI routine planning validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in routine planning: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI routine planning service error: {str(exc)}"
            )

routine_agent = AIRoutinePlanningAgent()
