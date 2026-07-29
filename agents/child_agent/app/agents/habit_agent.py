import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm

class HabitAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        sys_prompt = "You are the KinNest Habit Agent. Analyze student's study sessions and consistency scores, and provide motivational advice on focus streaks and routines."
        user_prompt = f"Query: '{query}'\n\nStudy Sessions:\n{json.dumps(context.get('study_sessions', []), default=str)}"
        answer = query_llm(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["study_sessions"],
            "action": None
        }
