from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.agents.supervisor_agent import SupervisorAgent
from app.ai.llm import query_llm
from app.ai.prompts import LEARNING_PATH_SYSTEM_PROMPT, WEAKNESS_DETECTOR_SYSTEM_PROMPT, STUDY_HEALTH_SYSTEM_PROMPT
from app.ai.tools import get_student_profile, get_subjects, get_assignments, get_goals, get_exams, get_study_sessions
from pydantic import BaseModel
import json
from typing import Optional

router = APIRouter(prefix="/api/v1/ai", tags=["AI Agent Intelligence"])

class AgentQuery(BaseModel):
    student_id: int
    query: str

class PathQuery(BaseModel):
    student_id: int
    skill_name: str

class QuizParams(BaseModel):
    subject: str
    topic: str
    difficulty: str = "Medium"

@router.post("/query")
def run_supervisor(payload: AgentQuery, db: Session = Depends(get_db)):
    supervisor = SupervisorAgent(db)
    return supervisor.execute(payload.student_id, payload.query)

@router.get("/study-now/{student_id}")
def study_now_recommendation(student_id: int, db: Session = Depends(get_db)):
    supervisor = SupervisorAgent(db)
    context = supervisor.gather_context(student_id)
    
    from app.agents.recommendation_agent import RecommendationAgent
    rec_agent = RecommendationAgent(db)
    result = rec_agent.run(student_id, "What should I study right now?", context)
    
    # Try parsing recommendation payload
    payload_str = result.get("action", {}).get("payload", "{}")
    try:
        recommendation = json.loads(payload_str)
    except Exception:
        recommendation = {
            "subject": "Mathematics",
            "duration_minutes": 45,
            "topic": "General Revision",
            "reason": "Keeping study habits consistent across core topics."
        }
    return recommendation

@router.post("/learning-path")
def generate_learning_path(payload: PathQuery, db: Session = Depends(get_db)):
    student = get_student_profile(db, payload.student_id)
    edu_level = student.get("education_level") or "SCHOOL"
    age = student.get("age") or 15
    user_prompt = (
        f"Student: {student['name']}, Age: {age}, Education Level: {edu_level}, "
        f"Grade: {student['grade']}, Goal: Learn '{payload.skill_name}'"
    )
    
    res = query_llm(
        system_prompt=LEARNING_PATH_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_json=True
    )
    
    try:
        return json.loads(res)
    except Exception:
        return {
            "title": f"Learning Path for {payload.skill_name}",
            "milestones": [
                {"title": "Foundations", "description": "Basic concepts and core theories."},
                {"title": "Intermediate Operations", "description": "Hands-on projects and tutorials."},
                {"title": "Advanced Applications", "description": "Build personal projects and study real-world implementations."}
            ]
        }

@router.get("/weaknesses/{student_id}")
def detect_weaknesses(student_id: int, db: Session = Depends(get_db)):
    supervisor = SupervisorAgent(db)
    context = supervisor.gather_context(student_id)
    
    user_prompt = f"Current Student Context:\n{json.dumps(context, default=str)}"
    res = query_llm(
        system_prompt=WEAKNESS_DETECTOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_json=False
    )
    return {"analysis": res}

@router.get("/daily-brief/{student_id}")
def get_daily_brief(student_id: int, db: Session = Depends(get_db)):
    supervisor = SupervisorAgent(db)
    context = supervisor.gather_context(student_id)
    
    profile = context.get("profile") or {}
    edu_level = (profile.get("education_level") or "SCHOOL").upper()
    age = profile.get("age") or 15
    meta = profile.get("profile_metadata") or {}

    base_summary = (
        f"Generate a daily brief for {profile.get('name', 'Student')} (Age: {age}, Education: {edu_level}).\n"
        f"Context summary:\n"
        f"- Subjects: {[s.get('name') for s in context.get('subjects', [])]}\n"
        f"- Pending assignments/tasks: {len([a for a in context.get('assignments', []) if a.get('status') == 'Pending'])}\n"
        f"- Upcoming exams/tests: {len(context.get('exams', []))}\n"
        f"- Goals: {len([g for g in context.get('goals', []) if g.get('status') == 'In Progress'])}\n"
    )

    if edu_level == "SCHOOL":
        profile_summary = (
            f"School Metrics:\n"
            f"- Study habits: {meta.get('study_habits', 'Developing routines')}\n"
            f"- Reading progress: {meta.get('reading_progress', 'No reading logs yet')}\n"
            f"- Unit tests: {meta.get('unit_tests', 'None scheduled')}\n"
        )
    else:  # COLLEGE
        profile_summary = (
            f"College & Career Metrics:\n"
            f"- Coding platform profiles: {meta.get('coding_platforms', {})}\n"
            f"- Projects: {meta.get('projects', [])}\n"
            f"- Hackathons: {meta.get('hackathons', [])}\n"
            f"- Certifications: {meta.get('certifications', [])}\n"
            f"- Resume status: {meta.get('resume', 'Draft')}\n"
            f"- Placements & Internships: {meta.get('internship_tracking', 'Not started')}\n"
        )

    user_prompt = base_summary + profile_summary + "\nEvaluate study health, routines and career preparation matching their academic stage."
    
    res = query_llm(
        system_prompt=STUDY_HEALTH_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_json=False
    )
    return {"brief": res}

@router.post("/quiz")
def generate_quiz(payload: QuizParams):
    sys_prompt = """You are the KinNest AI Quiz Agent. Generate a single study multiple-choice question.
Output ONLY a raw JSON object matching:
{
  "question": "question content",
  "options": ["A", "B", "C", "D"],
  "correct_answer": "exact correct option text matching one of options",
  "explanation": "why this is correct"
}
"""
    user_prompt = f"Subject: {payload.subject}, Topic: {payload.topic}, Difficulty: {payload.difficulty}"
    res = query_llm(
        system_prompt=sys_prompt,
        user_prompt=user_prompt,
        response_json=True
    )
    try:
        return json.loads(res)
    except Exception:
        return {
            "question": f"A sample question regarding {payload.topic}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "This is a placeholder fallback question because AI was busy."
        }
