import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.schedule import ScheduleItem
from app.ai.context_builder import ChildContextBuilder
from app.schemas.context import ChildContext
from app.schemas.privacy import ViewerRole
from app.services.privacy_engine import ParentSummaryGenerator, ChildPrivateDataFilter
from app.schemas.intervention import (
    InterventionPlan,
    InterventionAction,
    InterventionHistoryRecord,
)

logger = logging.getLogger(__name__)

# In-memory store for intervention history & outcome tracking
INTERVENTION_HISTORY_STORE: List[Dict[str, Any]] = []


class AIFamilyInterventionEngine:
    """
    Phase 10: AI Family Intervention Engine.
    Converts complex multi-domain problems into coordinated, multi-agent intervention plans.
    Enforces Consent Boundaries: No secret device locking or unapproved punishments.
    Tracks intervention history and outcome evaluations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.summary_generator = ParentSummaryGenerator()
        self.data_filter = ChildPrivateDataFilter()

    def detect_multi_domain_problems(self, context: ChildContext) -> List[Dict[str, Any]]:
        problems: List[Dict[str, Any]] = []

        # Complex Scenario 1: Upcoming Exam + Low Study Consistency + High Screen Time
        if (
            context.exams.upcoming_count > 0
            and context.screen_time.avg_daily_minutes > 120.0
            and (context.study.total_sessions < 3 or (context.study.avg_focus_score and context.study.avg_focus_score < 70.0))
        ):
            problems.append({
                "problem": "Upcoming exam in 5 days combined with low study consistency and excessive screen time.",
                "evidence": [
                    f"{context.exams.upcoming_count} upcoming exam(s)",
                    f"Screen time averaging {context.screen_time.avg_daily_minutes} mins/day",
                    f"Study focus score: {context.study.avg_focus_score or 'N/A'}",
                ],
                "priority": "HIGH",
            })

        # Complex Scenario 2: Overdue Homework + Safety Concern + Parent Alert
        if context.homework.overdue_count > 0 and context.safety.check_in_status in ("OVERDUE", "EMERGENCY"):
            problems.append({
                "problem": "Safety check-in attention required alongside overdue homework assignments.",
                "evidence": [
                    f"Safety status: {context.safety.check_in_status}",
                    f"{context.homework.overdue_count} overdue homework item(s)",
                ],
                "priority": "CRITICAL",
            })

        # Scenario 3: Saving Goal Falling Behind + High Expense Rate
        if context.pocket_money.total_spent > context.pocket_money.total_saved and context.pocket_money.active_goals_count > 0:
            problems.append({
                "problem": "Financial saving goal falling behind due to rapid non-essential spending.",
                "evidence": [
                    f"Total spent: ₹{context.pocket_money.total_spent}",
                    f"Total saved: ₹{context.pocket_money.total_saved}",
                ],
                "priority": "MEDIUM",
            })

        return problems

    def generate_intervention_plan(self, child_id: int, problem_data: Dict[str, Any]) -> InterventionPlan:
        child = self.db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        child_name = child.name if child else f"Child #{child_id}"

        builder = ChildContextBuilder(db=self.db, child_id=child_id)
        context = builder.build(include_ml_predictions=False)

        plan_id = f"intv_{uuid.uuid4().hex[:8]}"
        problem_str = problem_data["problem"]
        evidence_list = problem_data.get("evidence", [])
        priority_val = problem_data.get("priority", "HIGH")

        actions: List[InterventionAction] = []
        selected_agents: List[str] = []

        # 1. Study Coach Agent
        selected_agents.append("StudyCoachAgent")
        actions.append(
            InterventionAction(
                agent_name="StudyCoachAgent",
                target_role="CHILD",
                action_type="RECOMMEND_SCHEDULE",
                description="Create a realistic 45-minute daily study schedule using Pomodoro focus intervals.",
                requires_parent_consent=False,
                requires_child_consent=True,
                status="PROPOSED",
            )
        )

        # 2. Screen-Time Agent
        selected_agents.append("ScreenTimeAgent")
        actions.append(
            InterventionAction(
                agent_name="ScreenTimeAgent",
                target_role="CHILD",
                action_type="RECOMMEND_SCREEN_REDUCTION",
                description="Recommend reducing recreational screen usage to 60 minutes until study targets are met (recommendation mode, NO secret locking or secretive punishments).",
                requires_parent_consent=False,
                requires_child_consent=True,
                status="PROPOSED",
            )
        )

        # 3. Activity Agent
        selected_agents.append("ActivityAgent")
        actions.append(
            InterventionAction(
                agent_name="ActivityAgent",
                target_role="CHILD",
                action_type="PRESERVE_BREAKS",
                description="Preserve 20-minute physical relaxation and sports breaks to prevent study burnout.",
                requires_parent_consent=False,
                requires_child_consent=False,
                status="PROPOSED",
            )
        )

        # 4. Parent Agent
        selected_agents.append("ParentCommunicationAgent")
        actions.append(
            InterventionAction(
                agent_name="ParentCommunicationAgent",
                target_role="PARENT",
                action_type="DRAFT_PARENT_SUMMARY",
                description="Send privacy-safe parent summary highlighting upcoming exam and recommended study support.",
                requires_parent_consent=False,
                requires_child_consent=False,
                status="PROPOSED",
            )
        )

        # 5. Child Agent
        selected_agents.append("WellnessAgent")
        actions.append(
            InterventionAction(
                agent_name="WellnessAgent",
                target_role="CHILD",
                action_type="SHOW_ENCOURAGEMENT",
                description=f"Display encouraging motivation: 'You've got this {child_name}! Consistency makes exam prep easy.'",
                requires_parent_consent=False,
                requires_child_consent=False,
                status="PROPOSED",
            )
        )

        # 6. Schedule Agent
        selected_agents.append("ScheduleAgent")
        actions.append(
            InterventionAction(
                agent_name="ScheduleAgent",
                target_role="SCHEDULE",
                action_type="ADD_STUDY_BLOCK",
                description="Add proposed study revision blocks to daily timetable upon child agreement.",
                requires_parent_consent=False,
                requires_child_consent=True,
                status="PROPOSED",
            )
        )

        # Generate Privacy-Safe Parent Message
        parent_summary_out = self.summary_generator.generate_parent_summary(context)
        parent_msg = (
            f"KinNest Intervention Summary ({child_name}):\n"
            f"Problem: {problem_str}\n"
            "Recommended Support: Encourage 45-minute structured daily study blocks and screen breaks.\n"
            "Note: All actions are consent-based. KinNest does not secretly lock devices or enforce punishments."
        )

        child_msg = f"Good morning {child_name}! Let's tackle your upcoming exam together with 45 minutes of focused study today. You can achieve great results!"

        follow_up_iso = (datetime.utcnow() + timedelta(days=2)).isoformat()

        plan = InterventionPlan(
            intervention_id=plan_id,
            child_id=child_id,
            problem=problem_str,
            evidence=evidence_list,
            selected_agents=selected_agents,
            actions=actions,
            child_message=child_msg,
            parent_message=parent_msg,
            priority=priority_val,
            expected_outcome="Improved study consistency, reduced screen distraction, and exam readiness within 48 hours.",
            follow_up_time=follow_up_iso,
        )

        # Log in intervention history
        hist_rec = {
            "intervention_id": plan_id,
            "child_id": child_id,
            "problem": problem_str,
            "priority": priority_val,
            "status": "ACTIVE",
            "outcome_rating": None,
            "created_at": plan.created_at,
            "updated_at": plan.created_at,
            "plan_payload": plan.model_dump(),
        }
        INTERVENTION_HISTORY_STORE.append(hist_rec)

        return plan

    @staticmethod
    def update_intervention_outcome(intervention_id: str, outcome_rating: str, status: str = "RESOLVED") -> Optional[Dict[str, Any]]:
        for rec in INTERVENTION_HISTORY_STORE:
            if rec["intervention_id"] == intervention_id:
                rec["status"] = status
                rec["outcome_rating"] = outcome_rating
                rec["updated_at"] = datetime.utcnow().isoformat()
                return rec
        return None

    @staticmethod
    def get_intervention_history(child_id: int) -> List[Dict[str, Any]]:
        return [r for r in INTERVENTION_HISTORY_STORE if r["child_id"] == child_id]
