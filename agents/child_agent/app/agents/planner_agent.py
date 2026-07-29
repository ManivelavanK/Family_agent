import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm
from app.ai.prompts import PLANNER_SYSTEM_PROMPT

class PlannerAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        user_prompt = (
            f"Query: '{query}'\n\n"
            f"Subjects: {json.dumps(context.get('subjects', []), default=str)}\n"
            f"Exams: {json.dumps(context.get('exams', []), default=str)}\n"
            f"Assignments: {json.dumps(context.get('assignments', []), default=str)}\n"
            f"Goals: {json.dumps(context.get('goals', []), default=str)}\n"
        )
        answer = query_llm(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["subjects", "exams", "assignments", "goals"],
            "action": None
        }
