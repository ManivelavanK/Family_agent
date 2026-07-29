import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import KINNEST_GUEST_PLANNING_PROMPT
from app.ai.schemas import AIGuestPlanningResponse
from app.ai.context.retriever import ContextRetriever
from app.services.guest_service import GuestService

logger = logging.getLogger("kinnest.ai.guest_agent")

class AIGuestPlanningAgent:
    def __init__(self):
        self.groq = groq_service

    def plan_guest_visit(
        self,
        db: Session,
        message: str,
        family_id: str = "default_family",
        guest_id: Optional[int] = None
    ) -> AIGuestPlanningResponse:
        logger.info(f"AI Guest Agent planning visit for family '{family_id}': '{message}'")

        # 1. Retrieve database, memory, and calendar context
        context = ContextRetriever.get_planning_context(db, family_id=family_id)

        # 2. Attach specific guest record if provided
        if guest_id:
            guest = GuestService.get_guest_by_id(db, guest_id, family_id)
            if guest:
                context["target_guest_record"] = guest.to_dict()

        client = self.groq.get_client()

        messages = [
            {"role": "system", "content": KINNEST_GUEST_PLANNING_PROMPT},
            {"role": "system", "content": f"FACTUAL FAMILY & CALENDAR CONTEXT:\n{json.dumps(context, default=str)}"},
            {"role": "user", "content": f"GUEST VISIT REQUEST: {message}"}
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for guest visit planning")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3000
            )
            raw_content = response.choices[0].message.content
            raw_json = json.loads(raw_content)

            validated = AIGuestPlanningResponse.model_validate(raw_json)
            logger.info(f"Successfully validated AI guest planning response for '{validated.guest_profile.name}'")
            return validated

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq guest response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI guest planning service returned invalid or malformed JSON format."
            )
        except ValidationError as exc:
            logger.error(f"Guest planning response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI guest planning validation error: {str(exc)}"
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Groq API error in guest planning: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI guest planning service error: {str(exc)}"
            )

guest_agent = AIGuestPlanningAgent()
