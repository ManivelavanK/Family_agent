import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.digital_twin import DigitalTwin
from app.ai.groq_service import _get_groq_client
from app.ai.llm import query_llm

logger = logging.getLogger(__name__)

def gather_student_context(db: Session, student_id: int) -> Dict[str, Any]:
    """Collects all relevant student data from the database for the twin."""
    from app.ai import tools
    return {
        "profile": tools.get_student_profile(db, student_id),
        "subjects": tools.get_subjects(db, student_id),
        "assignments": tools.get_assignments(db, student_id),
        "goals": tools.get_goals(db, student_id),
        "exams": tools.get_exams(db, student_id),
        "study_sessions": tools.get_study_sessions(db, student_id),
        "progress": tools.get_progress(db, student_id),
        "memories": tools.get_memory(db, student_id),
    }

def get_or_create_digital_twin(db: Session, student_id: int) -> DigitalTwin:
    """Gets or creates the digital twin record for the student."""
    twin = db.query(DigitalTwin).filter(DigitalTwin.student_id == student_id).first()
    if not twin:
        student = db.query(Student).filter(Student.id == student_id).first()
        twin = DigitalTwin(
            student_id=student_id,
            learning_score=0.0,
            subject_mastery={},
            exam_readiness=0.0,
            focus_score=0.0,
            knowledge_gaps={},
            productivity_trend={},
            learning_style=student.learning_style if student else "Visual",
            weekly_capacity=0.0,
            confidence=0.0
        )
        db.add(twin)
        db.commit()
        db.refresh(twin)
    return twin

def calculate_fallback_metrics(context: Dict[str, Any], edu_level: str) -> Dict[str, Any]:
    """Computes basic metrics deterministically if the LLM fails."""
    # Homework/Assignments
    assigns = context.get("assignments", [])
    total_assigns = len(assigns)
    completed_assigns = sum(1 for a in assigns if a.get("status") == "Completed")
    hw_rate = completed_assigns / total_assigns if total_assigns > 0 else 1.0

    # Focus
    sessions = context.get("study_sessions", [])
    focus_scores = [s.get("focus_score", 100) for s in sessions if s.get("focus_score") is not None]
    avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 80.0

    # Exams
    exams = context.get("exams", [])
    readiness_scores = [e.get("readiness_score", 50) for e in exams if e.get("readiness_score") is not None]
    avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 60.0

    # Weekly hours
    progress = context.get("progress", [])
    weekly_hours = sum(p.get("study_hours", 0) for p in progress[:7])

    profile = context.get("profile", {})
    metadata = profile.get("profile_metadata", {})

    twin_metrics = {}
    if edu_level == "SCHOOL":
        twin_metrics = {
            "homework_completion_rate": round(hw_rate, 2),
            "attendance_rate": 0.95,  # default placeholder
            "unit_test_average": round(avg_readiness / 100.0, 2),
            "reading_progress": metadata.get("reading_progress", "Not started"),
            "study_habits": metadata.get("study_habits", "Developing consistency")
        }
    else:  # COLLEGE
        coding_platforms = metadata.get("coding_platforms", {})
        twin_metrics = {
            "coding_platforms_score": 0.70 if coding_platforms else 0.0,
            "projects_completed_count": len(metadata.get("projects", [])),
            "hackathons_count": len(metadata.get("hackathons", [])),
            "certifications_count": len(metadata.get("certifications", [])),
            "resume_score": metadata.get("resume_score", 0.75),
            "internship_status": metadata.get("internship_tracking", "Not started"),
            "interview_readiness": metadata.get("interview_prep", 0.60)
        }

    return {
        "learning_score": round((hw_rate + avg_focus/100.0 + avg_readiness/100.0) / 3, 2),
        "subject_mastery": {s.get("name", "Subject"): 0.75 for s in context.get("subjects", [])},
        "exam_readiness": round(avg_readiness / 100.0, 2),
        "focus_score": round(avg_focus / 100.0, 2),
        "knowledge_gaps": {},
        "productivity_trend": {"weeks": ["Week 1"], "hours": [weekly_hours]},
        "learning_style": profile.get("learning_style", "Visual"),
        "weekly_capacity": weekly_hours,
        "confidence": 0.70,
        "twin_metrics": twin_metrics
    }

def update_academic_digital_twin(db: Session, student_id: int) -> Dict[str, Any]:
    """Gathers context, runs AI reasoning to generate a twin, and persists it."""
    context = gather_student_context(db, student_id)
    edu_level = (context["profile"].get("education_level") or "SCHOOL").upper()
    
    client = _get_groq_client()
    twin_data = None

    if client:
        system_prompt = f"""
You are the KinNest Academic Digital Twin AI Generator.
Your job is to analyze the student's database context (profile, subjects, assignments/projects, study sessions, progress, exams, and memory) and construct their Academic Digital Twin.

You must adapt the metrics and analysis based on the student's education level:
1. SCHOOL: Focus on school-specific metrics (homework completion rate, attendance rate, unit test average, reading progress, study habits).
2. COLLEGE: Focus on college-specific metrics (coding platforms activity/score, projects completed count, hackathons count, certifications count, resume score, internship status, interview readiness).

Generate a valid JSON object matching this schema exactly:
{{
  "learning_score": 0.85,
  "subject_mastery": {{"Mathematics": 0.90, "Physics": 0.80}},
  "exam_readiness": 0.75,
  "focus_score": 0.88,
  "knowledge_gaps": {{"Physics": ["Electromagnetism"], "Mathematics": ["Calculus"]}},
  "productivity_trend": {{"weeks": ["Week 1", "Week 2"], "hours": [10.5, 12.0]}},
  "learning_style": "Visual & Practical",
  "weekly_capacity": 15.0,
  "confidence": 0.85,
  "twin_metrics": {{
    # If SCHOOL, include:
    "homework_completion_rate": 0.92,
    "attendance_rate": 0.95,
    "unit_test_average": 0.88,
    "reading_progress": "string summary",
    "study_habits": "string summary"
    # If COLLEGE, include:
    "coding_platforms_score": 0.78,
    "projects_completed_count": 3,
    "hackathons_count": 2,
    "certifications_count": 1,
    "resume_score": 0.80,
    "internship_status": "string summary",
    "interview_readiness": 0.70
  }}
}}
"""
        user_prompt = f"Student Context JSON:\n{json.dumps(context, default=str, indent=2)}"
        try:
            res = query_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_json=True,
                temperature=0.2
            )
            twin_data = json.loads(res)
        except Exception as e:
            logger.error(f"AI Digital Twin generation failed: {e}. Using fallback calculation.")

    if not twin_data:
        twin_data = calculate_fallback_metrics(context, edu_level)

    # Persist in DB
    twin = get_or_create_digital_twin(db, student_id)
    twin.learning_score = twin_data["learning_score"]
    twin.subject_mastery = twin_data["subject_mastery"]
    twin.exam_readiness = twin_data["exam_readiness"]
    twin.focus_score = twin_data["focus_score"]
    twin.knowledge_gaps = twin_data["knowledge_gaps"]
    twin.productivity_trend = twin_data["productivity_trend"]
    twin.learning_style = twin_data["learning_style"]
    twin.weekly_capacity = twin_data["weekly_capacity"]
    twin.confidence = twin_data["confidence"]
    
    prod_trend = dict(twin_data["productivity_trend"])
    prod_trend["twin_metrics"] = twin_data["twin_metrics"]
    twin.productivity_trend = prod_trend
    
    db.commit()
    db.refresh(twin)
    
    twin_dict = {
        "id": twin.id,
        "student_id": twin.student_id,
        "learning_score": twin.learning_score,
        "subject_mastery": twin.subject_mastery,
        "exam_readiness": twin.exam_readiness,
        "focus_score": twin.focus_score,
        "knowledge_gaps": twin.knowledge_gaps,
        "productivity_trend": twin.productivity_trend.get("weeks", []),
        "productivity_hours": twin.productivity_trend.get("hours", []),
        "learning_style": twin.learning_style,
        "weekly_capacity": twin.weekly_capacity,
        "confidence": twin.confidence,
        "twin_metrics": twin_data["twin_metrics"]
    }
    return twin_dict
