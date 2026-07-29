from sqlalchemy.orm import Session
from app.ai.llm import query_llm
from app.ai.prompts import STUDY_HEALTH_SYSTEM_PROMPT
import json

class StudyAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        user_prompt = f"Query: '{query}'\n\nStudy Context:\n{json.dumps(context.get('study_sessions', []), default=str)}"
        answer = query_llm(
            system_prompt=STUDY_HEALTH_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["study_sessions"],
            "action": None
        }
