import json
from sqlalchemy.orm import Session
from app.ai.llm import query_llm

class QuizAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, student_id: int, query: str, context: dict) -> dict:
        sys_prompt = """You are the KinNest AI Quiz Agent.
If the student asks to generate a quiz, output a valid JSON containing:
{
  "question": "The question content",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": "Option A/B/C/D",
  "explanation": "Brief explanation"
}
If they are answering a question, evaluate it.
Return ONLY raw JSON formatting if generating a quiz, or a text explanation if evaluating.
"""
        user_prompt = f"Query: '{query}'\n\nContext:\n{json.dumps(context.get('subjects', []), default=str)}"
        answer = query_llm(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_json=False
        )
        return {
            "answer": answer,
            "data_sources": ["subjects"],
            "action": None
        }
