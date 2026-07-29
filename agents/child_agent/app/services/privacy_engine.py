import logging
from typing import Dict, Any, List, Optional
from app.schemas.privacy import PrivacyCategory, ViewerRole, VisibilityPolicy, ParentSummaryOutput
from app.schemas.context import ChildContext

logger = logging.getLogger(__name__)

# Default Configurable Visibility Policies
DEFAULT_VISIBILITY_POLICIES: Dict[PrivacyCategory, VisibilityPolicy] = {
    PrivacyCategory.ACADEMIC: VisibilityPolicy(
        category=PrivacyCategory.ACADEMIC,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.PARENT, ViewerRole.FAMILY_AGENT, ViewerRole.AI_SUPERVISOR],
        allow_raw_text=True,
        allow_summary=True,
        bypass_on_safety_alert=False,
    ),
    PrivacyCategory.PUBLIC_TO_PARENT: VisibilityPolicy(
        category=PrivacyCategory.PUBLIC_TO_PARENT,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.PARENT, ViewerRole.FAMILY_AGENT, ViewerRole.AI_SUPERVISOR],
        allow_raw_text=True,
        allow_summary=True,
        bypass_on_safety_alert=False,
    ),
    PrivacyCategory.SUMMARY_ONLY: VisibilityPolicy(
        category=PrivacyCategory.SUMMARY_ONLY,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.PARENT, ViewerRole.FAMILY_AGENT, ViewerRole.AI_SUPERVISOR],
        allow_raw_text=False,
        allow_summary=True,
        bypass_on_safety_alert=False,
    ),
    PrivacyCategory.CHILD_PRIVATE: VisibilityPolicy(
        category=PrivacyCategory.CHILD_PRIVATE,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.AI_SUPERVISOR],  # Excludes PARENT from allowed_roles
        allow_raw_text=True,  # Allowed for CHILD and AI_SUPERVISOR, blocked for PARENT via allowed_roles
        allow_summary=True,
        bypass_on_safety_alert=True,
    ),

    PrivacyCategory.MEDICAL_SENSITIVE: VisibilityPolicy(
        category=PrivacyCategory.MEDICAL_SENSITIVE,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.PARENT, ViewerRole.AI_SUPERVISOR],
        allow_raw_text=False,
        allow_summary=True,
        bypass_on_safety_alert=True,
    ),
    PrivacyCategory.FINANCIAL: VisibilityPolicy(
        category=PrivacyCategory.FINANCIAL,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.PARENT, ViewerRole.FATHER_AGENT, ViewerRole.AI_SUPERVISOR],
        allow_raw_text=True,
        allow_summary=True,
        bypass_on_safety_alert=False,
    ),
    PrivacyCategory.SAFETY_CRITICAL: VisibilityPolicy(
        category=PrivacyCategory.SAFETY_CRITICAL,
        allowed_roles=[ViewerRole.CHILD, ViewerRole.PARENT, ViewerRole.FAMILY_AGENT, ViewerRole.MOTHER_AGENT, ViewerRole.FATHER_AGENT, ViewerRole.AI_SUPERVISOR],
        allow_raw_text=True,
        allow_summary=True,
        bypass_on_safety_alert=True,
    ),
}


class PrivacyPolicyEngine:
    """
    Privacy Policy Engine governing visibility and data filtration between Child, Parent, Family Agents, and AI Supervisor.
    """

    def __init__(self, policies: Optional[Dict[PrivacyCategory, VisibilityPolicy]] = None):
        self.policies = policies or DEFAULT_VISIBILITY_POLICIES

    def can_access(
        self,
        role: ViewerRole,
        category: PrivacyCategory,
        is_raw_text: bool = False,
        is_safety_emergency: bool = False,
    ) -> bool:
        policy = self.policies.get(category)
        if not policy:
            return False

        # Safety-critical bypass rule
        if is_safety_emergency and policy.bypass_on_safety_alert:
            return True

        if role not in policy.allowed_roles:
            return False

        if is_raw_text and not policy.allow_raw_text:
            return False

        return True


class ChildPrivateDataFilter:
    """
    Filters raw sensitive child data (private diary entries, medical notes, raw phone contacts) before output.
    """

    def __init__(self, engine: Optional[PrivacyPolicyEngine] = None):
        self.engine = engine or PrivacyPolicyEngine()

    def sanitize_for_viewer(
        self,
        data: Dict[str, Any],
        viewer_role: ViewerRole,
        is_safety_emergency: bool = False,
    ) -> Dict[str, Any]:
        sanitized = data.copy()

        # 1. Private diary entries protection
        if "diary_entries" in sanitized or "diary_text" in sanitized:
            if not self.engine.can_access(viewer_role, PrivacyCategory.CHILD_PRIVATE, is_raw_text=True, is_safety_emergency=is_safety_emergency):
                sanitized.pop("diary_entries", None)
                sanitized.pop("diary_text", None)
                sanitized["diary_privacy_note"] = "Raw diary text hidden per child privacy policy."

        # 2. Medical / Allergy raw specifics
        if "allergies" in sanitized or "blood_group" in sanitized:
            if not self.engine.can_access(viewer_role, PrivacyCategory.MEDICAL_SENSITIVE, is_raw_text=True, is_safety_emergency=is_safety_emergency):
                sanitized.pop("allergies", None)
                sanitized.pop("blood_group", None)

        # 3. Emergency contacts / Parent phone numbers
        if "parent_contact" in sanitized or "emergency_contact" in sanitized:
            if viewer_role not in (ViewerRole.PARENT, ViewerRole.AI_SUPERVISOR) and not is_safety_emergency:
                sanitized.pop("parent_contact", None)
                sanitized.pop("emergency_contact", None)

        return sanitized


class ParentSummaryGenerator:
    """
    Generates privacy-compliant summaries for parents.
    Exposes:
    - Homework (completed/pending, deadline, priority)
    - Study (duration, consistency, general progress)
    - Screen time (daily duration, trend, alerts)
    - Safety status (check-ins, escalations)
    - Wellness (high-level trend/mood, serious concern alerts ONLY - NO raw diary text)
    """

    def __init__(self, engine: Optional[PrivacyPolicyEngine] = None):
        self.engine = engine or PrivacyPolicyEngine()

    def generate_parent_summary(
        self,
        context: ChildContext,
        raw_diary_entries: Optional[List[Dict[str, Any]]] = None,
    ) -> ParentSummaryOutput:
        is_emergency = context.safety.check_in_status in ("OVERDUE", "EMERGENCY")

        # 1. Homework Summary for Parent
        academic_summary = {
            "completed_count": context.homework.completed_count,
            "pending_count": context.homework.pending_count,
            "overdue_count": context.homework.overdue_count,
            "pending_subjects": context.homework.pending_subjects,
            "overdue_items": context.homework.overdue_items,
        }

        # 2. Study Summary for Parent
        study_summary = {
            "total_study_minutes": context.study.total_study_minutes,
            "total_sessions": context.study.total_sessions,
            "avg_focus_score": context.study.avg_focus_score,
            "consistency_status": "Consistent" if context.study.total_sessions > 2 else "Needs Improvement",
        }

        # 3. Screen Time Summary for Parent
        screen_time_summary = {
            "average_daily_minutes": context.screen_time.avg_daily_minutes,
            "screen_time_exceeded": context.screen_time.screen_time_exceeded,
            "alert_triggered": context.screen_time.avg_daily_minutes > 120.0,
        }

        # 4. Wellness Summary for Parent (STRICT PRIVACY: Trend/Alert only, NO raw diary text)
        wellness_summary = {
            "mood_trend": "Stable / Energetic" if context.health.avg_sleep_hours >= 7.5 else "Fatigued",
            "sleep_average_hours": context.health.avg_sleep_hours,
            "hydration_ml": context.health.avg_water_intake_ml,
            "has_serious_wellness_concern": False,
        }

        # Inspect diary entries for severe flags if provided, but NEVER attach raw text
        if raw_diary_entries:
            for entry in raw_diary_entries:
                text_lower = str(entry.get("content", "")).lower()
                if any(w in text_lower for w in ["depressed", "hopeless", "hurt myself", "help me"]):
                    wellness_summary["has_serious_wellness_concern"] = True
                    wellness_summary["concern_alert"] = "Serious wellness flag detected in recent activity."
                    break

        # Emergency Escalation Rule for Private Content
        if is_emergency and self.engine.can_access(ViewerRole.PARENT, PrivacyCategory.CHILD_PRIVATE, is_raw_text=False, is_safety_emergency=True):
            wellness_summary["emergency_escalation_active"] = True

        # 5. Financial Summary for Parent
        financial_summary = {
            "total_allowance": context.pocket_money.allowance_total,
            "total_spent": context.pocket_money.total_spent,
            "total_saved": context.pocket_money.total_saved,
            "active_goals_count": context.pocket_money.active_goals_count,
        }

        # 6. Safety Summary for Parent
        safety_summary = {
            "check_in_status": context.safety.check_in_status,
            "last_check_in_note": context.safety.last_check_in_note,
            "emergency_contact_registered": context.safety.emergency_contact_registered,
        }

        # 7. Alerts Requiring Parent Action
        parent_alerts = []
        if context.homework.overdue_count > 0:
            parent_alerts.append(f"{context.homework.overdue_count} overdue assignment(s)")
        if screen_time_summary["alert_triggered"]:
            parent_alerts.append(f"Screen time limit exceeded ({context.screen_time.avg_daily_minutes} mins/day)")
        if is_emergency:
            parent_alerts.append(f"CRITICAL SAFETY ALERT: {context.safety.check_in_status}")
        if wellness_summary.get("has_serious_wellness_concern"):
            parent_alerts.append("Wellness concern detected requiring gentle conversation")

        return ParentSummaryOutput(
            child_id=context.profile.child_id,
            academic_summary=academic_summary,
            study_summary=study_summary,
            screen_time_summary=screen_time_summary,
            wellness_summary=wellness_summary,
            financial_summary=financial_summary,
            safety_summary=safety_summary,
            alerts_requiring_parent=parent_alerts,
        )
