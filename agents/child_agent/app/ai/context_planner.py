import json
import logging
from typing import Dict, Any, List

from app.ai.llm import query_llm
from app.ai.prompts import CONTEXT_PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ContextPlanner:
    """LLM‑driven planning module.

    It receives the raw user query together with the student ID and a DB session,
    builds a full context (profile, subjects, assignments, goals, exams, study
    sessions, progress, memories) and asks the LLM to produce a structured plan.
    The plan contains intent, confidence, required tools, agents, execution order
    and any action proposal.
    """

    def __init__(self, db):
        self.db = db

    def _gather_context(self, student_id: int) -> Dict[str, Any]:
        """Collect all relevant data for the planner.
        This mirrors the existing `SupervisorAgent.gather_context` logic so the
        planner works with a complete snapshot of the student state.
        """
        from app.ai import tools  # Import here to avoid circular imports
        return {
            "profile": tools.get_student_profile(self.db, student_id),
            "subjects": tools.get_subjects(self.db, student_id),
            "assignments": tools.get_assignments(self.db, student_id),
            "goals": tools.get_goals(self.db, student_id),
            "exams": tools.get_exams(self.db, student_id),
            "study_sessions": tools.get_study_sessions(self.db, student_id),
            "progress": tools.get_progress(self.db, student_id),
            "memories": tools.get_memory(self.db, student_id),
        }

    def plan(self, student_id: int, query: str) -> Dict[str, Any]:
        """Generate a planning JSON structure.

        The LLM is instructed (via `CONTEXT_PLANNER_SYSTEM_PROMPT`) to output a
        JSON object with the following fields:
        `intent`, `confidence`, `tools_used`, `agents_used`,
        `execution_sequence`, `requires_confirmation` and optional `action`.
        """
        from app.ai import tools
        # 1. Query the profile first to detect age and education level
        profile = tools.get_student_profile(self.db, student_id)
        if not profile:
            # Fallback if no student profile
            age = 15
            edu_level = "SCHOOL"
        else:
            age = profile.get("age") or 15
            edu_level = (profile.get("education_level") or "SCHOOL").upper()

        # 2. Use age and education level to select tools before executing them
        selected_tools = ["get_student_profile", "get_subjects", "get_study_sessions", "get_progress", "get_memory"]
        if edu_level == "SCHOOL":
            selected_tools.extend(["get_assignments", "get_exams"])
        else:  # COLLEGE
            selected_tools.extend(["get_assignments", "get_goals", "get_exams"])

        # 3. Gather selected context fields from database
        context = {
            "profile": profile,
            "subjects": tools.get_subjects(self.db, student_id) if "get_subjects" in selected_tools else [],
            "assignments": tools.get_assignments(self.db, student_id) if "get_assignments" in selected_tools else [],
            "goals": tools.get_goals(self.db, student_id) if "get_goals" in selected_tools else [],
            "exams": tools.get_exams(self.db, student_id) if "get_exams" in selected_tools else [],
            "study_sessions": tools.get_study_sessions(self.db, student_id) if "get_study_sessions" in selected_tools else [],
            "progress": tools.get_progress(self.db, student_id) if "get_progress" in selected_tools else [],
            "memories": tools.get_memory(self.db, student_id) if "get_memory" in selected_tools else [],
        }

        user_prompt = (
            f"Student Query: '{query}'\n"
            f"Detected Student Age: {age}\n"
            f"Detected Education Level: {edu_level}\n"
            f"Context-Selected Database Tools: {selected_tools}\n\n"
            f"Context:\n{json.dumps(context, default=str, indent=2)}"
        )
        try:
            response_str = query_llm(
                system_prompt=CONTEXT_PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_json=True,
                temperature=0.0,
            )
            plan = json.loads(response_str)
            return plan
        except Exception as e:
            logger.error(f"ContextPlanner failed: {e}")
            # Fallback minimal plan
            return {
                "intent": "fallback",
                "confidence": 0.0,
                "tools_used": selected_tools,
                "agents_used": ["TutorAgent"],
                "execution_sequence": [],
                "requires_confirmation": False,
                "action": None,
            }
