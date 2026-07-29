import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm
from app.ai.prompts import TUTOR_SYSTEM_PROMPT

class TutorAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        user_prompt = f"Student Query: '{query}'\n\nStudent Profile: {json.dumps(context.get('profile', {}), default=str)}"
        answer = query_llm(
            system_prompt=TUTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["profile"],
            "action": None
        }
