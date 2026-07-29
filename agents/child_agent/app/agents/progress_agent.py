import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm

class ProgressAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        sys_prompt = "You are the KinNest Progress Agent. Review academic progress logs, study hours, consistency scores, and grades to provide performance updates."
        user_prompt = f"Query: '{query}'\n\nProgress logs:\n{json.dumps(context.get('progress', []), default=str)}"
        answer = query_llm(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["progress"],
            "action": None
        }
