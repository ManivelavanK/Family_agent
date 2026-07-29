import logging
import numpy as np
from datetime import date, timedelta, datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.study import StudySession, StudyMaterial
from app.models.exam import Exam
from app.models.attendance import Attendance
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog
from app.models.activity import Activity
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense, SavingGoal
from app.models.safety import SafetyProfile, CheckInLog
from app.models.nutrition import NutritionLog, MotherAgentBridgeEvent
from app.models.schedule import ScheduleItem, HolidayCalendar
from app.models.notification import NotificationLog

from app.services.age_adaptation_service import classify_age_group
from app.ml import predictor
from app.ai import groq_service

from app.schemas.context import (
    ChildContext,
    PrivacyFilteredProfile,
    HomeworkSummaryContext,
    StudySummaryContext,
    ExamSummaryContext,
    AttendanceSummaryContext,
    ScreenTimeSummaryContext,
    HealthRoutineSummaryContext,
    ActivitiesSummaryContext,
    PocketMoneySummaryContext,
    SafetySummaryContext,
    NutritionSummaryContext,
    ScheduleSummaryContext,
    RecentNotificationContext,
    PreviousRecommendationContext,
)

logger = logging.getLogger(__name__)

# Constants for context size limiting
MAX_RECENT_NOTIFICATIONS = 5
MAX_LIST_ITEMS = 5


class ChildContextBuilder:
    """
    Deterministic, privacy-aware context builder for the KinNest Child Agent.
    Aggregates multi-domain data, applies privacy filtering, handles missing data,
    limits context payload size, and returns a normalized ChildContext model.
    """

    def __init__(self, db: Session, child_id: int):
        self.db = db
        self.child_id = child_id

    def build(
        self,
        include_ml_predictions: bool = True,
        max_notifications: int = MAX_RECENT_NOTIFICATIONS,
        max_items_per_list: int = MAX_LIST_ITEMS,
    ) -> ChildContext:
        child = self.db.query(ChildProfile).filter(ChildProfile.id == self.child_id).first()
        if not child:
            raise ValueError(f"Child profile with ID {self.child_id} not found.")

        # 1. Privacy-Aware Profile Filter
        age_group = classify_age_group(child.age)
        profile_context = PrivacyFilteredProfile(
            child_id=child.id,
            name=child.name,
            age=child.age,
            age_group=age_group,
            education_stage=child.education_stage or "Unknown",
            class_or_year=child.class_or_year,
            interests=(child.interests if isinstance(child.interests, list) else [])[:max_items_per_list],
            career_interest=child.career_interest,
            daily_wake_time=child.daily_wake_time.strftime("%H:%M") if child.daily_wake_time else None,
            daily_sleep_time=child.daily_sleep_time.strftime("%H:%M") if child.daily_sleep_time else None,
        )

        # 2. Homework Context & Summarization
        hw_logs = self.db.query(Homework).filter(Homework.child_id == self.child_id).all()
        pending_hw = [h for h in hw_logs if not h.completion_status]
        completed_hw = [h for h in hw_logs if h.completion_status]
        overdue_hw = [h for h in pending_hw if h.due_date and h.due_date < date.today()]
        high_priority_hw = [h for h in pending_hw if h.priority == "HIGH"]
        pending_subjects = list(set([h.subject for h in pending_hw if h.subject]))[:max_items_per_list]
        
        overdue_items = [
            {
                "id": h.id,
                "title": h.title,
                "subject": h.subject,
                "due_date": h.due_date.isoformat() if h.due_date else None,
                "priority": h.priority,
            }
            for h in overdue_hw[:max_items_per_list]
        ]

        homework_context = HomeworkSummaryContext(
            total_count=len(hw_logs),
            pending_count=len(pending_hw),
            completed_count=len(completed_hw),
            overdue_count=len(overdue_hw),
            high_priority_count=len(high_priority_hw),
            pending_subjects=pending_subjects,
            overdue_items=overdue_items,
        )

        # 3. Study Sessions Context
        study_logs = self.db.query(StudySession).filter(StudySession.child_id == self.child_id).all()
        study_mins = [s.duration_minutes for s in study_logs if s.duration_minutes]
        focus_scores = [s.focus_score for s in study_logs if s.focus_score is not None]
        materials_count = self.db.query(StudyMaterial).filter(StudyMaterial.child_id == self.child_id).count()
        recent_subjects = list(set([s.subject for s in study_logs if s.subject]))[:max_items_per_list]

        study_context = StudySummaryContext(
            total_sessions=len(study_logs),
            total_study_minutes=sum(study_mins),
            avg_session_minutes=round(float(np.mean(study_mins)), 1) if study_mins else 0.0,
            avg_focus_score=round(float(np.mean(focus_scores)), 1) if focus_scores else None,
            materials_count=materials_count,
            recent_subjects_studied=recent_subjects,
        )

        # 4. Exam Context
        exam_logs = self.db.query(Exam).filter(Exam.child_id == self.child_id).all()
        today = date.today()
        upcoming_exams = [e for e in exam_logs if e.exam_date and e.exam_date >= today]
        scores = [
            float(getattr(e, "preparation_percentage", 80))
            for e in exam_logs
            if getattr(e, "preparation_percentage", None) is not None
        ]


        upcoming_exam_list = [
            {
                "id": e.id,
                "exam_name": e.exam_name,
                "subject": e.subject,
                "exam_date": e.exam_date.isoformat() if e.exam_date else None,
            }
            for e in sorted(upcoming_exams, key=lambda x: x.exam_date)[:max_items_per_list]
        ]

        exam_context = ExamSummaryContext(
            total_exams=len(exam_logs),
            upcoming_count=len(upcoming_exams),
            avg_exam_percentage=round(float(np.mean(scores)), 1) if scores else None,
            upcoming_exams=upcoming_exam_list,
        )

        # 5. Attendance Context
        att_logs = self.db.query(Attendance).filter(Attendance.child_id == self.child_id).all()
        present_count = sum(1 for a in att_logs if a.status and a.status.upper() in ("PRESENT", "EXCUSED"))
        absent_count = sum(1 for a in att_logs if a.status and a.status.upper() in ("ABSENT"))
        att_pct = round((present_count / len(att_logs)) * 100.0, 1) if att_logs else 100.0

        attendance_context = AttendanceSummaryContext(
            total_days=len(att_logs),
            present_days=present_count,
            absent_days=absent_count,
            attendance_percentage=att_pct,
        )

        # 6. Screen Time Context
        screen_logs = self.db.query(ScreenTimeLog).filter(ScreenTimeLog.child_id == self.child_id).all()
        if screen_logs:
            daily_mins = [
                (l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other)
                for l in screen_logs
            ]
            edu_mins = [l.study_screen_time for l in screen_logs]
            late_night = sum(1 for l in screen_logs if l.late_night_minutes > 0)
            avg_daily = round(float(np.mean(daily_mins)), 1)
            avg_edu = round(float(np.mean(edu_mins)), 1)
        else:
            avg_daily = 0.0
            avg_edu = 0.0
            late_night = 0

        screen_context = ScreenTimeSummaryContext(
            avg_daily_minutes=avg_daily,
            avg_educational_minutes=avg_edu,
            late_night_count=late_night,
            screen_time_exceeded=avg_daily > 120.0,  # default threshold check
        )

        # 7. Health & Routine Context
        health_logs = self.db.query(HealthLog).filter(HealthLog.child_id == self.child_id).all()
        if health_logs:
            sleep_hours = [h.sleep_hours for h in health_logs if h.sleep_hours is not None]
            water_intake = [h.water_intake_ml for h in health_logs if h.water_intake_ml is not None]
            activity_mins = [h.physical_activity_minutes for h in health_logs if h.physical_activity_minutes is not None]
            avg_sleep = round(float(np.mean(sleep_hours)), 1) if sleep_hours else 8.0
            avg_water = int(np.mean(water_intake)) if water_intake else 1500
            avg_act = int(np.mean(activity_mins)) if activity_mins else 30
        else:
            avg_sleep = 8.0
            avg_water = 1500
            avg_act = 30

        health_context = HealthRoutineSummaryContext(
            avg_sleep_hours=avg_sleep,
            avg_water_intake_ml=avg_water,
            avg_activity_minutes=avg_act,
            health_alerts_count=0,
        )

        # 8. Activities Context
        activities = self.db.query(Activity).filter(Activity.child_id == self.child_id).all()
        upcoming_activities = [
            {
                "id": a.id,
                "title": a.title,
                "category": a.activity_type,
                "date": a.date.isoformat() if a.date else None,
                "start_time": a.start_time.strftime("%H:%M") if a.start_time else None,
            }
            for a in activities if a.date and a.date >= today
        ][:max_items_per_list]

        activities_context = ActivitiesSummaryContext(
            total_activities_count=len(activities),
            upcoming_activities=upcoming_activities,
        )

        # 9. Pocket Money & Savings Context
        allowances = self.db.query(PocketMoneyAllowance).filter(PocketMoneyAllowance.child_id == self.child_id).all()
        expenses = self.db.query(ChildExpense).filter(ChildExpense.child_id == self.child_id).all()
        goals = self.db.query(SavingGoal).filter(SavingGoal.child_id == self.child_id).all()

        total_allowance = sum(a.amount for a in allowances)
        total_spent = sum(e.amount for e in expenses)
        total_saved = sum(g.current_saved for g in goals)

        goals_summary = [
            {
                "id": g.id,
                "title": g.title,
                "target_amount": g.target_amount,
                "current_saved": g.current_saved,
                "progress_pct": round((g.current_saved / g.target_amount * 100.0), 1) if g.target_amount > 0 else 100.0,
            }
            for g in goals[:max_items_per_list]
        ]

        pocket_money_context = PocketMoneySummaryContext(
            allowance_total=total_allowance,
            total_spent=total_spent,
            total_saved=total_saved,
            active_goals_count=len(goals),
            saving_goals=goals_summary,
        )

        # 10. Safety Context
        check_ins = self.db.query(CheckInLog).filter(CheckInLog.child_id == self.child_id).order_by(CheckInLog.id.desc()).all()
        safety_profile = self.db.query(SafetyProfile).filter(SafetyProfile.child_id == self.child_id).first()

        last_note = check_ins[0].location_note if check_ins else None
        current_status = check_ins[0].status if check_ins else "SAFE"

        safety_context = SafetySummaryContext(
            check_in_status=current_status,
            emergency_contact_registered=bool(child.emergency_contact or child.parent_contact),
            active_alerts_count=1 if current_status in ("OVERDUE", "EMERGENCY") else 0,
            last_check_in_note=last_note,
        )

        # 11. Nutrition & Hydration Context
        nutrition_logs = self.db.query(NutritionLog).filter(NutritionLog.child_id == self.child_id).all()
        bridge_events = self.db.query(MotherAgentBridgeEvent).filter(MotherAgentBridgeEvent.child_id == self.child_id).all()

        if nutrition_logs:
            breakfast_pct = round((sum(1 for n in nutrition_logs if n.breakfast_eaten) / len(nutrition_logs)) * 100.0, 1)
            water_avg = int(np.mean([n.water_ml for n in nutrition_logs if n.water_ml is not None]))
        else:
            breakfast_pct = 100.0
            water_avg = 1500

        nutrition_context = NutritionSummaryContext(
            breakfast_consistency_pct=breakfast_pct,
            avg_water_ml=water_avg,
            bridge_events_count=len(bridge_events),
        )

        # 12. Daily Schedule Context
        schedule_items = self.db.query(ScheduleItem).filter(ScheduleItem.child_id == self.child_id).all()
        today_items = [
            {
                "id": s.id,
                "title": s.subject,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "category": s.schedule_type,
            }
            for s in schedule_items
        ][:max_items_per_list]

        holidays = self.db.query(HolidayCalendar).filter(HolidayCalendar.date >= today).all()

        schedule_context = ScheduleSummaryContext(
            today_items_count=len(today_items),
            upcoming_holidays_count=len(holidays),
            today_schedule=today_items,
        )

        # 13. Recent Notifications
        notifications = (
            self.db.query(NotificationLog)
            .filter(NotificationLog.child_id == self.child_id)
            .order_by(NotificationLog.created_at.desc())
            .limit(max_notifications)
            .all()
        )

        notification_context = [
            RecentNotificationContext(
                id=n.id,
                title=n.title,
                message=n.message,
                notification_type=n.notification_type,
                created_at=n.created_at.isoformat(),
            )
            for n in notifications
        ]

        # 14. Previous Recommendations Context
        previous_recs = None
        try:
            fallback = groq_service.generate_fallback_recommendations({
                "profile": {"name": child.name, "age_group": age_group},
                "homework_summary": {"pending_count": len(pending_hw)},
                "health_summary": {"avg_sleep_hours": avg_sleep, "avg_water_intake_ml": avg_water},
                "screen_time_summary": {"avg_daily_screen_time_minutes": avg_daily},
                "pocket_money_summary": {"total_saved": total_saved},
                "safety_summary": {"check_in_status": current_status},
            })
            previous_recs = PreviousRecommendationContext(
                daily_motivation=fallback.get("daily_motivation"),
                study_suggestions=fallback.get("study_suggestions", [])[:2],
                healthy_routine_advice=fallback.get("healthy_routine_advice", [])[:2],
                screen_time_advice=fallback.get("screen_time_advice", [])[:2],
                parent_recommendations=fallback.get("parent_recommendations", [])[:2],
            )
        except Exception as e:
            logger.warning(f"Could not load previous recommendations for context: {e}")

        # 15. ML Predictions (Optional)
        ml_preds = None
        if include_ml_predictions:
            try:
                hw_pred = predictor.predict_homework_completion(self.db, self.child_id)
                att_pred = predictor.predict_attendance_trend(self.db, self.child_id)
                study_pred = predictor.predict_study_performance(self.db, self.child_id)
                screen_pred = predictor.predict_screen_time_trend(self.db, self.child_id)
                routine_pred = predictor.predict_routine_balance(self.db, self.child_id)

                ml_preds = {
                    "homework_time_mins": hw_pred.prediction if hw_pred.has_sufficient_data else None,
                    "attendance_trend": att_pred.prediction if att_pred.has_sufficient_data else None,
                    "study_performance_index": study_pred.prediction if study_pred.has_sufficient_data else None,
                    "screen_time_trend_mins": screen_pred.prediction if screen_pred.has_sufficient_data else None,
                    "routine_balance_score": routine_pred.prediction if routine_pred.has_sufficient_data else None,
                }
            except Exception as e:
                logger.warning(f"Error computing ML predictions for context: {e}")

        return ChildContext(
            profile=profile_context,
            homework=homework_context,
            study=study_context,
            exams=exam_context,
            attendance=attendance_context,
            screen_time=screen_context,
            health=health_context,
            activities=activities_context,
            pocket_money=pocket_money_context,
            safety=safety_context,
            nutrition=nutrition_context,
            schedule=schedule_context,
            recent_notifications=notification_context,
            previous_recommendations=previous_recs,
            ml_predictions=ml_preds,
        )
