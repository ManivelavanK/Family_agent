import json
import logging
from typing import Dict, Any, Optional
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.config import settings
from app.ai.groq_client import groq_service
from app.ai.prompts import KINNEST_MEMORY_EXTRACTION_PROMPT
from app.ai.schemas import AIMemoryExtractionResponse

logger = logging.getLogger("kinnest.ai.memory_agent")

class AIMemoryAgent:
    def __init__(self):
        self.groq = groq_service

    def analyze_for_memories(
        self,
        text_content: str,
        context_type: str = "USER_STATEMENT",
        context_id: Optional[int] = None
    ) -> AIMemoryExtractionResponse:
        logger.info(f"AI Memory Agent analyzing text content (type: {context_type})")

        client = self.groq.get_client()
        messages = [
            {"role": "system", "content": KINNEST_MEMORY_EXTRACTION_PROMPT},
            {
                "role": "user",
                "content": f"CONTEXT TYPE: {context_type}\nCONTEXT ID: {context_id}\nTEXT CONTENT:\n{text_content}"
            }
        ]

        try:
            logger.info(f"Invoking Groq model '{settings.GROQ_MODEL}' for memory extraction")
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )
            raw_content = response.choices[0].message.content
            logger.info("Received raw memory extraction response from Groq")
            raw_json = json.loads(raw_content)

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq memory extraction response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI memory service returned invalid or malformed JSON format."
            )
        except Exception as exc:
            logger.error(f"Groq API error in memory extraction: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI memory service error: {str(exc)}"
            )

        try:
            validated = AIMemoryExtractionResponse.model_validate(raw_json)
            logger.info(f"Successfully validated AI memory extraction response. Should remember: {validated.should_remember}")
            return validated
        except ValidationError as exc:
            logger.error(f"Memory extraction response failed schema validation: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI memory extraction validation error: {str(exc)}"
            )

memory_agent = AIMemoryAgent()
