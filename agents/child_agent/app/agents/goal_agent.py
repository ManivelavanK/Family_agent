import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm

class GoalAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        sys_prompt = "You are the KinNest Goal Agent. Generate key academic strategies for student's goals based on their current status."
        user_prompt = f"Query: '{query}'\n\nGoals:\n{json.dumps(context.get('goals', []), default=str)}"
        answer = query_llm(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["goals"],
            "action": None
        }
