import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm

class AssignmentAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        sys_prompt = "You are the KinNest Assignment Agent. Analyze pending assignments and advise the student on priorities, upcoming deadlines, and study targets."
        user_prompt = f"Query: '{query}'\n\nAssignments:\n{json.dumps(context.get('assignments', []), default=str)}"
        answer = query_llm(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["assignments"],
            "action": None
        }
