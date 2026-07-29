import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import KINNEST_CALENDAR_REASONING_PROMPT
from app.ai.schemas import AICalendarReasoningResponse, AICalendarReasoningRequest
from app.ai.context.retriever import ContextRetriever
from app.services.calendar_service import CalendarService

logger = logging.getLogger("kinnest.ai.calendar_reasoner")

class AICalendarReasoner:
    def __init__(self):
        self.groq = groq_service

    def reason_schedule(
        self,
        db: Session,
        req: AICalendarReasoningRequest
    ) -> AICalendarReasoningResponse:
        logger.info(f"AI Calendar Reasoner processing message: '{req.message}'")

        # 1. Gather factual context
        context = ContextRetriever.get_planning_context(db)

        # Factual conflict check if explicit datetimes provided
        conflict_facts = {}
        if req.requested_start and req.requested_end:
            conflict_res = CalendarService.check_conflicts(
                db=db,
                start_datetime=req.requested_start,
                end_datetime=req.requested_end
            )
            conflict_facts = conflict_res.model_dump(mode="json")
            context["factual_conflict_check"] = conflict_facts

        # 2. Invoke Groq with Calendar System Prompt
        client = self.groq.get_client()
        messages = [
            {"role": "system", "content": KINNEST_CALENDAR_REASONING_PROMPT},
            {
                "role": "system",
                "content": f"FACTUAL CONTEXT & CALENDAR DATA:\n{json.dumps(context, default=str)}"
            },
            {
                "role": "user",
                "content": f"REQUEST: {req.message}\nREQUESTED START: {req.requested_start}\nREQUESTED END: {req.requested_end}"
            }
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for calendar reasoning")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1500
            )
            raw_content = response.choices[0].message.content
            logger.info("Received raw response from Groq for calendar reasoning")
            raw_json = json.loads(raw_content)

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI calendar service returned invalid or malformed JSON format."
            )
        except Exception as exc:
            logger.error(f"Groq API error in calendar reasoning: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI calendar service error: {str(exc)}"
            )

        # 3. Validate against Pydantic schema
        try:
            validated = AICalendarReasoningResponse.model_validate(raw_json)
            logger.info(f"Successfully validated AI calendar reasoning response. Action: {validated.recommended_action}")
            return validated
        except ValidationError as exc:
            logger.error(f"Calendar reasoning response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI calendar reasoning validation error: {str(exc)}"
            )

calendar_reasoner = AICalendarReasoner()
