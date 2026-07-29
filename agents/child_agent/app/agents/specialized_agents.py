import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.schemas.context import ChildContext
from app.agents import (
    education_agent,
    finance_agent,
    routine_agent,
    safety_agent,
    wellness_agent,
)

logger = logging.getLogger(__name__)


class SpecializedAgent:
    """Base class for all specialized domain agents."""
    name: str = "BaseAgent"
    domain: str = "general"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        raise NotImplementedError


class EducationAgent(SpecializedAgent):
    name = "EducationAgent"
    domain = "EDUCATION"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        res = education_agent.handle_query(db, child_id, query)
        res["agent_name"] = self.name
        res["domain"] = self.domain
        res["context_summary"] = f"Pending homework: {context.homework.pending_count}, Overdue: {context.homework.overdue_count}"
        return res


class StudyCoachAgent(SpecializedAgent):
    name = "StudyCoachAgent"
    domain = "STUDY_COACH"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        focus_info = f"Avg Focus Score: {context.study.avg_focus_score or 'N/A'}"
        advice = "Try 25-minute Pomodoro study intervals with short 5-minute hydration breaks."
        return {
            "agent": "Study Coach Agent",
            "agent_name": self.name,
            "domain": self.domain,
            "reply": f"Study Coach Advice: {advice} ({focus_info})",
            "actions": {
                "recommended_technique": "Pomodoro (25/5)",
                "total_study_minutes": context.study.total_study_minutes,
                "avg_focus_score": context.study.avg_focus_score,
            }
        }


class ExamPlannerAgent(SpecializedAgent):
    name = "ExamPlannerAgent"
    domain = "EXAM_PLANNER"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        upcoming_count = context.exams.upcoming_count
        exams_list = [e.get("exam_name", "Exam") for e in context.exams.upcoming_exams]
        return {
            "agent": "Exam Planner Agent",
            "agent_name": self.name,
            "domain": self.domain,
            "reply": f"Exam Plan: You have {upcoming_count} upcoming exam(s) ({', '.join(exams_list) if exams_list else 'None'}). Prioritize past-paper revisions.",
            "actions": {
                "upcoming_exams_count": upcoming_count,
                "recommended_action": "Create 7-day revision calendar",
            }
        }


class WellnessAgent(SpecializedAgent):
    name = "WellnessAgent"
    domain = "WELLNESS"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        res = wellness_agent.handle_query(db, child_id, query)
        res["agent_name"] = self.name
        res["domain"] = self.domain
        return res


class ScreenTimeAgent(SpecializedAgent):
    name = "ScreenTimeAgent"
    domain = "SCREEN_TIME"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        res = routine_agent.handle_query(db, child_id, query)
        res["agent"] = "Screen Time Agent"
        res["agent_name"] = self.name
        res["domain"] = self.domain
        res["actions"]["avg_daily_screen_time_minutes"] = context.screen_time.avg_daily_minutes
        return res


class FinanceAgent(SpecializedAgent):
    name = "FinanceAgent"
    domain = "FINANCE"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        res = finance_agent.handle_query(db, child_id, query)
        res["agent_name"] = self.name
        res["domain"] = self.domain
        return res


class SafetyAgent(SpecializedAgent):
    name = "SafetyAgent"
    domain = "SAFETY"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        res = safety_agent.handle_query(db, child_id, query)
        res["agent_name"] = self.name
        res["domain"] = self.domain
        return res


class ActivityAgent(SpecializedAgent):
    name = "ActivityAgent"
    domain = "ACTIVITY"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        act_count = context.activities.total_activities_count
        return {
            "agent": "Activity Agent",
            "agent_name": self.name,
            "domain": self.domain,
            "reply": f"Activity Schedule: You have {act_count} registered activity/activities. Remember to balance practice with relaxation.",
            "actions": {
                "total_activities": act_count,
                "upcoming_activities_count": len(context.activities.upcoming_activities),
            }
        }


class ParentCommunicationAgent(SpecializedAgent):
    name = "ParentCommunicationAgent"
    domain = "PARENT_COMMUNICATION"

    def execute(self, db: Session, child_id: int, query: str, context: ChildContext) -> Dict[str, Any]:
        reasons = []
        if context.homework.overdue_count > 0:
            reasons.append(f"{context.homework.overdue_count} overdue homework item(s)")
        if context.screen_time.screen_time_exceeded:
            reasons.append(f"high screen time ({context.screen_time.avg_daily_minutes} mins/day)")
        if context.safety.check_in_status in ("OVERDUE", "EMERGENCY"):
            reasons.append(f"safety alert status: {context.safety.check_in_status}")

        summary = ", ".join(reasons) if reasons else "routine weekly status update"
        return {
            "agent": "Parent Communication Agent",
            "agent_name": self.name,
            "domain": self.domain,
            "reply": f"Parent Notification Draft: Prepared guardian summary regarding {summary}.",
            "actions": {
                "requires_parent_notification": len(reasons) > 0,
                "notification_summary": summary,
            }
        }
