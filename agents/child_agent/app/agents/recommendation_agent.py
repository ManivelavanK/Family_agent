import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm

class RecommendationAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        sys_prompt = """You are the KinNest Study Recommendation Agent.
Given the student's profile, subjects, upcoming exams, assignments, and goals, identify a target subject, focus topic, suggested duration (e.g. 30, 45, or 60 minutes), and a detailed reasoning explanation.
Output a JSON matching this structure:
{
  "subject": "Mathematics",
  "duration_minutes": 45,
  "topic": "Quadratic Equations",
  "reason": "You have an exam coming up in 5 days and your readiness score is low."
}
Return ONLY valid JSON.
"""
        user_prompt = f"Query: '{query}'\n\nContext:\n{json.dumps(context, default=str)}"
        answer = query_llm(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_json=True
        )
        return {
            "answer": answer,
            "data_sources": ["subjects", "exams", "assignments"],
            "action": {"type": "study_recommendation", "payload": answer}
        }
