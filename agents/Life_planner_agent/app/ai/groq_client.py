import json
import logging
from typing import Dict, Any, List
from fastapi import HTTPException, status
from groq import Groq
from app.config import settings
from app.ai.prompts import KINNEST_SYSTEM_PROMPT

logger = logging.getLogger("kinnest.ai.groq")

class GroqClientService:
    def __init__(self):
        self.model = settings.GROQ_MODEL
        self.timeout = settings.GROQ_TIMEOUT

    def get_client(self) -> Groq:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API key is missing or not configured in environment (GROQ_API_KEY)."
            )
        return Groq(api_key=api_key, timeout=self.timeout)

    def generate_structured_plan(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        client = self.get_client()
        
        messages = [
            {"role": "system", "content": KINNEST_SYSTEM_PROMPT}
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"DATABASE CONTEXT:\n{json.dumps(context, default=str)}"
            })

        messages.append({"role": "user", "content": user_message})

        try:
            logger.info(f"Invoking Groq model: {self.model}")
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2048
            )
            raw_content = response.choices[0].message.content
            logger.info("Successfully received Groq response")
            return json.loads(raw_content)

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Groq response as JSON: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI service returned invalid or malformed JSON format."
            )
        except Exception as exc:
            logger.error(f"Groq API error occurred: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq AI service error: {str(exc)}"
            )

groq_service = GroqClientService()
