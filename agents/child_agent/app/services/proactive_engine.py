import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.study import StudySession
from app.models.exam import Exam
from app.models.attendance import Attendance
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense, SavingGoal
from app.models.safety import SafetyProfile, CheckInLog
from app.models.nutrition import NutritionLog
from app.models.notification import NotificationLog

from app.ai.context_builder import ChildContextBuilder
from app.schemas.context import ChildContext
from app.schemas.proactive_insight import ChildInsight, ProactiveAnalysisReport
from app.services.notification_service import NotificationService, NotificationType
from app.services.parent_notification_service import ParentNotificationService

logger = logging.getLogger(__name__)


# Cooldown buffer (in hours) to prevent duplicate notifications for identical event_types
DEFAULT_COOLDOWN_HOURS = 12


class ProactiveChildIntelligenceEngine:
    """
    Phase 5: Proactive Child Intelligence Engine.
    Periodically analyzes child context to proactively detect academic, wellness, financial, and safety events.
    Applies strict de-duplication/cooldown logic to avoid redundant notifications.
    """

    def __init__(self, db: Session, cooldown_hours: int = DEFAULT_COOLDOWN_HOURS):
        self.db = db
        self.cooldown_hours = cooldown_hours

    def is_in_cooldown(self, child_id: int, event_type: str) -> bool:
        """
        Checks if a notification/insight of event_type was logged within cooldown_hours window.
        """
        cutoff = datetime.utcnow() - timedelta(hours=self.cooldown_hours)
        recent_notif = (
            self.db.query(NotificationLog)
            .filter(
                NotificationLog.child_id == child_id,
                NotificationLog.notification_type == event_type,
                NotificationLog.created_at >= cutoff,
            )
            .first()
        )
        return recent_notif is not None

    def analyze_child(self, child_id: int) -> ProactiveAnalysisReport:
        child = self.db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            raise ValueError(f"Child profile with ID {child_id} not found.")

        builder = ChildContextBuilder(db=self.db, child_id=child_id)
        context = builder.build(include_ml_predictions=False)

        insights: List[ChildInsight] = []
        now_iso = datetime.utcnow().isoformat()
        today = date.today()

        # ----------------------------------------------------
        # 1. ACADEMIC DETECTIONS
        # ----------------------------------------------------
        # Homework Overdue
        if context.homework.overdue_count > 0:
            insights.append(
                ChildInsight(
                    event_type="HOMEWORK_OVERDUE",
                    severity="HIGH",
                    child_id=child_id,
                    explanation=f"{context.homework.overdue_count} homework assignment(s) are overdue.",
                    evidence={"overdue_count": context.homework.overdue_count, "overdue_items": context.homework.overdue_items},
                    recommended_action="Set aside 30 minutes immediately to complete overdue assignments.",
                    parent_notification_required=True,
                    child_notification_required=True,
                    created_at=now_iso,
                )
            )

        # Homework Deadline Approaching
        elif context.homework.pending_count > 0:
            insights.append(
                ChildInsight(
                    event_type="HOMEWORK_DEADLINE_APPROACHING",
                    severity="MEDIUM",
                    child_id=child_id,
                    explanation=f"You have {context.homework.pending_count} pending homework assignment(s).",
                    evidence={"pending_count": context.homework.pending_count, "pending_subjects": context.homework.pending_subjects},
                    recommended_action="Plan a study session today to finish pending assignments early.",
                    parent_notification_required=False,
                    child_notification_required=True,
                    created_at=now_iso,
                )
            )

        # Exam Approaching with Insufficient Preparation
        exams = self.db.query(Exam).filter(Exam.child_id == child_id, Exam.exam_date >= today).all()
        for exam in exams:
            days_left = (exam.exam_date - today).days
            if days_left <= 7 and exam.preparation_percentage < 60:
                insights.append(
                    ChildInsight(
                        event_type="EXAM_INSUFFICIENT_PREPARATION",
                        severity="HIGH",
                        child_id=child_id,
                        explanation=f"Upcoming exam '{exam.exam_name}' in {days_left} day(s) has only {exam.preparation_percentage}% preparation completed.",
                        evidence={"exam_name": exam.exam_name, "days_left": days_left, "preparation_percentage": exam.preparation_percentage},
                        recommended_action="Start daily 45-minute structured revision blocks for this subject.",
                        parent_notification_required=True,
                        child_notification_required=True,
                        created_at=now_iso,
                    )
                )

        # Declining Focus / Poor Study Consistency
        if context.study.total_sessions > 0 and context.study.avg_focus_score and context.study.avg_focus_score < 65.0:
            insights.append(
                ChildInsight(
                    event_type="DECLINING_FOCUS",
                    severity="MEDIUM",
                    child_id=child_id,
                    explanation=f"Average study focus score has dropped to {context.study.avg_focus_score}/100.",
                    evidence={"avg_focus_score": context.study.avg_focus_score, "total_sessions": context.study.total_sessions},
                    recommended_action="Take shorter focus intervals (20 mins study, 5 mins break) and remove distraction sources.",
                    parent_notification_required=False,
                    child_notification_required=True,
                    created_at=now_iso,
                )
            )

        # ----------------------------------------------------
        # 2. WELLNESS DETECTIONS
        # ----------------------------------------------------
        # Excessive Screen Time
        if context.screen_time.avg_daily_minutes > 120.0 or context.screen_time.screen_time_exceeded:
            insights.append(
                ChildInsight(
                    event_type="EXCESSIVE_SCREEN_TIME",
                    severity="HIGH",
                    child_id=child_id,
                    explanation=f"Average daily screen time is {context.screen_time.avg_daily_minutes} minutes, exceeding standard health limits.",
                    evidence={"avg_daily_minutes": context.screen_time.avg_daily_minutes, "late_night_count": context.screen_time.late_night_count},
                    recommended_action="Set daily screen limit and turn off digital screens 1 hour before sleep.",
                    parent_notification_required=True,
                    child_notification_required=True,
                    created_at=now_iso,
                )
            )

        # Nutrition / Hydration Warning
        if context.nutrition.avg_water_ml < 1000 or context.nutrition.breakfast_consistency_pct < 60.0:
            insights.append(
                ChildInsight(
                    event_type="NUTRITION_HYDRATION_CONCERN",
                    severity="MEDIUM",
                    child_id=child_id,
                    explanation=f"Hydration intake averages {context.nutrition.avg_water_ml} ml/day and breakfast consistency is {context.nutrition.breakfast_consistency_pct}%.",
                    evidence={"avg_water_ml": context.nutrition.avg_water_ml, "breakfast_consistency_pct": context.nutrition.breakfast_consistency_pct},
                    recommended_action="Drink a glass of water every morning and maintain a nutritious breakfast routine.",
                    parent_notification_required=True,
                    child_notification_required=True,
                    created_at=now_iso,
                )
            )

        # ----------------------------------------------------
        # 3. FINANCE DETECTIONS
        # ----------------------------------------------------
        # Saving Goal Falling Behind
        for goal in context.pocket_money.saving_goals:
            if goal.get("progress_pct", 100) < 30.0 and context.pocket_money.total_spent > context.pocket_money.total_saved:
                insights.append(
                    ChildInsight(
                        event_type="SAVING_GOAL_FALLING_BEHIND",
                        severity="MEDIUM",
                        child_id=child_id,
                        explanation=f"Saving goal '{goal.get('title')}' is only {goal.get('progress_pct')}% complete.",
                        evidence={"goal_title": goal.get("title"), "progress_pct": goal.get("progress_pct"), "total_spent": context.pocket_money.total_spent},
                        recommended_action="Allocate 20% of pocket allowance to your saving goal before non-essential spending.",
                        parent_notification_required=False,
                        child_notification_required=True,
                        created_at=now_iso,
                    )
                )

        # ----------------------------------------------------
        # 4. SAFETY DETECTIONS
        # ----------------------------------------------------
        if context.safety.check_in_status in ("OVERDUE", "EMERGENCY"):
            insights.append(
                ChildInsight(
                    event_type="SAFETY_STATUS_ATTENTION",
                    severity="CRITICAL",
                    child_id=child_id,
                    explanation=f"Safety check-in status is {context.safety.check_in_status}.",
                    evidence={"check_in_status": context.safety.check_in_status, "last_check_in_note": context.safety.last_check_in_note},
                    recommended_action="Check location status immediately and contact guardian.",
                    parent_notification_required=True,
                    child_notification_required=True,
                    created_at=now_iso,
                )
            )

        # ----------------------------------------------------
        # DE-DUPLICATION & COOLDOWN FILTERING
        # ----------------------------------------------------
        new_logged_count = 0
        skipped_count = 0
        final_insights: List[ChildInsight] = []

        for insight in insights:

            if self.is_in_cooldown(child_id=child_id, event_type=insight.event_type):
                skipped_count += 1
                logger.info(f"Skipping insight '{insight.event_type}' for child {child_id} due to cooldown.")
            else:
                final_insights.append(insight)
                # Log notification in DB to track cooldown window
                NotificationService.send_notification(
                    db=self.db,
                    child_id=child_id,
                    title=f"Proactive Alert: {insight.event_type.replace('_', ' ').title()}",
                    message=insight.explanation,
                    notification_type=insight.event_type,
                    channel="IN_APP",
                )

                # Automatic WhatsApp dispatch if parent notification required (STEP 8)
                if insight.parent_notification_required:
                    p_service = ParentNotificationService(db=self.db)
                    p_service.dispatch_parent_whatsapp(
                        child_id=child_id,
                        notification_type=insight.event_type,
                        template_data={
                            "message": insight.explanation,
                            "explanation": insight.explanation,
                            "recommended_action": insight.recommended_action,
                        },
                        is_safety_emergency=(insight.severity == "CRITICAL"),
                    )

                new_logged_count += 1


        return ProactiveAnalysisReport(
            child_id=child_id,
            total_insights_detected=len(insights),
            new_insights_logged=new_logged_count,
            cooldown_skipped_insights=skipped_count,
            insights=final_insights,
        )
