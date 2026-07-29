import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.ai.context_builder import ChildContextBuilder
from app.schemas.context import ChildContext
from app.schemas.privacy import ViewerRole, PrivacyCategory
from app.services.privacy_engine import PrivacyPolicyEngine, ChildPrivateDataFilter, ParentSummaryGenerator
from app.services.parent_notification_service import ParentNotificationService
from app.ai.groq_service import _get_groq_client
from app.schemas.ai_intelligence import (
    ChildAIInsight,
    ParentNotificationDecision,
    ChildAIIntelligenceReport,
)

logger = logging.getLogger(__name__)


class ChildIntelligenceService:
    """
    AI-Powered Child Intelligence Service.
    Pipeline:
    Child Data -> Context Aggregator -> AI Intelligence Engine (LLM Reasoning) -> Structured Recommendation -> Privacy/Safety Filter -> Action Decision -> Parent Notification / WhatsApp -> Store Intelligence Event
    """

    def __init__(self, db: Session):
        self.db = db
        self.privacy_engine = PrivacyPolicyEngine()
        self.data_filter = ChildPrivateDataFilter(engine=self.privacy_engine)
        self.parent_summary_gen = ParentSummaryGenerator(engine=self.privacy_engine)

    def generate_fallback_report(self, child_id: int, context: ChildContext) -> ChildAIIntelligenceReport:
        """
        Deterministic Rule-Based Fallback when LLM is unavailable or fails.
        Guarantees 100% API availability.
        """
        child_name = context.profile.name

        # Determine overall status
        if context.safety.check_in_status in ("OVERDUE", "EMERGENCY") or context.homework.overdue_count > 0:
            overall_status = "NEEDS_ATTENTION"
        elif context.screen_time.avg_daily_minutes > 120.0 or context.homework.pending_count > 0:
            overall_status = "MODERATE"
        else:
            overall_status = "GOOD"

        insights: List[ChildAIInsight] = []
        rec_actions: List[str] = []

        if context.homework.overdue_count > 0:
            insights.append(
                ChildAIInsight(
                    child_id=child_id,
                    insight_type="HOMEWORK_RISK",
                    severity="HIGH",
                    title="Overdue Homework Alert",
                    explanation=f"{child_name} has {context.homework.overdue_count} overdue homework assignment(s).",
                    evidence=[f"{context.homework.overdue_count} overdue assignment(s)"],
                    recommendation="Prioritize completing overdue tasks immediately.",
                    suggested_action="Schedule a dedicated 45-minute homework completion session today.",
                    parent_notification_required=True,
                    child_notification=f"Let's complete your overdue assignment today {child_name}!",
                    confidence=0.95,
                )
            )
            rec_actions.append("Complete overdue assignments first.")

        if context.screen_time.avg_daily_minutes > 120.0:
            insights.append(
                ChildAIInsight(
                    child_id=child_id,
                    insight_type="SCREEN_TIME_IMBALANCE",
                    severity="MEDIUM",
                    title="Screen Time Elevated",
                    explanation=f"Daily recreational screen time is elevated ({context.screen_time.avg_daily_minutes} mins/day).",
                    evidence=[f"Avg daily screen time: {context.screen_time.avg_daily_minutes} mins"],
                    recommendation="Balance screen usage with outdoor physical activities.",
                    suggested_action="Take a 30-minute screen-free outdoor break.",
                    parent_notification_required=False,
                    child_notification="Remember to take screen breaks after study sessions!",
                    confidence=0.90,
                )
            )
            rec_actions.append("Keep recreational screen time below 60 minutes.")

        if not rec_actions:
            rec_actions.append("Maintain current positive study and routine habits.")

        # Parent Notification Decision
        parent_summary_out = self.parent_summary_gen.generate_parent_summary(context)
        should_notify = any(i.parent_notification_required for i in insights) or context.safety.check_in_status in ("OVERDUE", "EMERGENCY")

        notif_decision = ParentNotificationDecision(
            should_notify=should_notify,
            notification_type="HOMEWORK_OVERDUE" if context.homework.overdue_count > 0 else "WEEKLY_CHILD_SUMMARY",
            severity="HIGH" if context.homework.overdue_count > 0 else "MEDIUM",
            safe_message=f"KinNest Update for {child_name}: {parent_summary_out.alerts_requiring_parent[0] if parent_summary_out.alerts_requiring_parent else 'All routines are progressing well.'}",
            reason="Homework overdue or routine update required.",
            channel="WHATSAPP",
        )

        return ChildAIIntelligenceReport(
            child_id=child_id,
            overall_status=overall_status,
            key_insights=insights,
            academic_status={"pending_homework": context.homework.pending_count, "overdue_homework": context.homework.overdue_count},
            wellbeing_status={"avg_sleep_hours": context.health.avg_sleep_hours, "screen_time_mins": context.screen_time.avg_daily_minutes},
            routine_status={"study_sessions": context.study.total_sessions, "total_study_mins": context.study.total_study_minutes},
            financial_status={"allowance": context.pocket_money.allowance_total, "remaining_balance": context.pocket_money.allowance_total - context.pocket_money.total_spent},
            safety_status={"check_in_status": context.safety.check_in_status},
            recommended_actions=rec_actions,
            parent_notification_decision=notif_decision,
        )

    def analyze_child_intelligence(self, child_id: int, trigger_parent_whatsapp: bool = False) -> ChildAIIntelligenceReport:
        # Step 1: Context Aggregator

        builder = ChildContextBuilder(db=self.db, child_id=child_id)
        context = builder.build(include_ml_predictions=True)

        client = _get_groq_client()
        if not client:
            report = self.generate_fallback_report(child_id, context)
            if trigger_parent_whatsapp and report.parent_notification_decision.should_notify:
                p_service = ParentNotificationService(db=self.db)
                p_service.dispatch_parent_whatsapp(
                    child_id=child_id,
                    notification_type=report.parent_notification_decision.notification_type,
                    template_data={"message": report.parent_notification_decision.safe_message},
                    is_safety_emergency=(report.parent_notification_decision.severity == "CRITICAL"),
                )
            return report

        # Step 2 & 3: LLM Reasoning over Aggregated Context
        context_dict = context.model_dump()
        prompt_content = f"""
You are the KinNest Child Intelligence AI Engine.
Analyze the comprehensive aggregated child context below:

AGGREGATED CHILD CONTEXT:
{json.dumps(context_dict, indent=2, default=str)}

TASK:
Identify academic, wellness, routine, financial, and safety insights.
STRICT PRIVACY RULES:
1. NEVER diagnose medical conditions or accuse the child.
2. NEVER include raw diary text or personal thoughts in parent notifications.
3. Classify information into safe parent-facing summaries.

Return ONLY a JSON object adhering to this schema:
{{
  "overall_status": "EXCELLENT|GOOD|MODERATE|NEEDS_ATTENTION",
  "key_insights": [
    {{
      "insight_type": "HOMEWORK_RISK|EXAM_RISK|SCREEN_TIME_IMBALANCE|ROUTINE_IMBALANCE|WELLNESS_CONCERN|POSITIVE_ACHIEVEMENT",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "title": "string",
      "explanation": "string",
      "evidence": ["string"],
      "recommendation": "string",
      "suggested_action": "string",
      "parent_notification_required": boolean,
      "child_notification": "string",
      "confidence": 0.9
    }}
  ],
  "recommended_actions": ["string"],
  "parent_notification_decision": {{
    "should_notify": boolean,
    "notification_type": "HOMEWORK_REMINDER|HOMEWORK_OVERDUE|EXAM_APPROACHING|SAFETY_ALERT|WEEKLY_CHILD_SUMMARY",
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "safe_message": "string",
    "reason": "string"
  }}
}}
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a child intelligence AI system. Output strictly raw JSON."},
                    {"role": "user", "content": prompt_content},
                ],
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            parsed = json.loads(response.choices[0].message.content.strip())
            
            raw_insights = parsed.get("key_insights", [])
            ai_insights = []
            for item in raw_insights:
                item["child_id"] = child_id
                ai_insights.append(ChildAIInsight(**item))

            raw_decision = parsed.get("parent_notification_decision", {})
            raw_decision["channel"] = "WHATSAPP"
            notif_decision = ParentNotificationDecision(**raw_decision)

            # Step 5 & 6: Privacy Filter & Parent Decision
            # Sanitize message body to prevent raw diary leakage
            sanitized_msg = self.data_filter.sanitize_for_viewer(
                {"safe_message": notif_decision.safe_message}, viewer_role=ViewerRole.PARENT
            ).get("safe_message", notif_decision.safe_message)
            notif_decision.safe_message = sanitized_msg

            report = ChildAIIntelligenceReport(
                child_id=child_id,
                overall_status=parsed.get("overall_status", "GOOD"),
                key_insights=ai_insights,
                academic_status={"pending_homework": context.homework.pending_count, "overdue_homework": context.homework.overdue_count},
                wellbeing_status={"avg_sleep_hours": context.health.avg_sleep_hours, "screen_time_mins": context.screen_time.avg_daily_minutes},
                routine_status={"study_sessions": context.study.total_sessions, "total_study_mins": context.study.total_study_minutes},
                financial_status={"allowance": context.pocket_money.allowance_total, "remaining_balance": context.pocket_money.allowance_total - context.pocket_money.total_spent},
                safety_status={"check_in_status": context.safety.check_in_status},
                recommended_actions=parsed.get("recommended_actions", []),
                parent_notification_decision=notif_decision,
            )

            # Step 7: Twilio WhatsApp Dispatch if required
            if trigger_parent_whatsapp and report.parent_notification_decision.should_notify:
                p_service = ParentNotificationService(db=self.db)
                p_service.dispatch_parent_whatsapp(
                    child_id=child_id,
                    notification_type=report.parent_notification_decision.notification_type,
                    template_data={"message": report.parent_notification_decision.safe_message},
                    is_safety_emergency=(report.parent_notification_decision.severity == "CRITICAL"),
                )

            return report

        except Exception as e:
            logger.error(f"Child AI Intelligence Engine LLM error: {e}. Falling back to rule-based engine.")
            report = self.generate_fallback_report(child_id, context)
            if trigger_parent_whatsapp and report.parent_notification_decision.should_notify:
                p_service = ParentNotificationService(db=self.db)
                p_service.dispatch_parent_whatsapp(
                    child_id=child_id,
                    notification_type=report.parent_notification_decision.notification_type,
                    template_data={"message": report.parent_notification_decision.safe_message},
                    is_safety_emergency=(report.parent_notification_decision.severity == "CRITICAL"),
                )
            return report
