import numpy as np
from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from app.models.profile import ChildProfile
from app.models.homework import Homework
from app.models.exam import Exam
from app.models.attendance import Attendance
from app.models.study import StudySession
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog
from app.models.activity import Activity
from app.models.pocket_money import PocketMoneyAllowance, ChildExpense, SavingGoal
from app.models.safety import SafetyProfile, CheckInLog
from app.services.age_adaptation_service import classify_age_group
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    ComprehensiveRecommendation,
)
from app.ml import predictor
from app.ai import groq_service


def generate_recommendation_for_child(
    db: Session, request: RecommendationRequest
) -> RecommendationResponse:
    child_id = request.child_id
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ValueError(f"Child profile with ID {child_id} not found.")

    age_group = classify_age_group(child.age)

    # --- STEP 1 & STEP 2: Collect Structured Data & Run Deterministic Calculations ---
    # Homework deterministic summary
    hw_logs = db.query(Homework).filter(Homework.child_id == child_id).all()
    pending_hw = [h for h in hw_logs if not h.completion_status]
    overdue_hw = [h for h in pending_hw if h.due_date < date.today()]
    high_priority_hw = [h for h in pending_hw if h.priority == "HIGH"]

    hw_summary = {
        "total_homework": len(hw_logs),
        "completed_count": len(hw_logs) - len(pending_hw),
        "pending_count": len(pending_hw),
        "overdue_count": len(overdue_hw),
        "high_priority_count": len(high_priority_hw),
    }

    # Attendance deterministic summary
    att_logs = db.query(Attendance).filter(Attendance.child_id == child_id).all()
    total_att = len(att_logs)
    present_att = sum(1 for a in att_logs if a.status in ("PRESENT", "EXCUSED", "Present"))
    absent_att = sum(1 for a in att_logs if a.status in ("ABSENT", "Absent"))
    att_pct = round((present_att / total_att) * 100.0, 1) if total_att > 0 else 100.0

    att_summary = {
        "total_days_recorded": total_att,
        "present_days": present_att,
        "absent_days": absent_att,
        "attendance_percentage": att_pct,
    }

    # Exams deterministic summary
    exam_logs = db.query(Exam).filter(Exam.child_id == child_id).all()
    exam_scores = [
        (e.marks_obtained / e.max_marks) * 100.0
        for e in exam_logs
        if e.marks_obtained is not None and e.max_marks > 0
    ]
    avg_exam_score = round(float(np.mean(exam_scores)), 1) if exam_scores else None

    exam_summary = {
        "total_exams_recorded": len(exam_logs),
        "average_exam_percentage": avg_exam_score,
    }

    # Study Sessions deterministic summary
    study_logs = db.query(StudySession).filter(StudySession.child_id == child_id).all()
    study_mins = [s.duration_minutes for s in study_logs if s.duration_minutes]
    focus_scores = [s.focus_score for s in study_logs if s.focus_score is not None]

    study_summary = {
        "total_sessions": len(study_logs),
        "total_study_minutes": sum(study_mins),
        "avg_session_minutes": round(float(np.mean(study_mins)), 1) if study_mins else 0.0,
        "avg_focus_score": round(float(np.mean(focus_scores)), 1) if focus_scores else None,
    }

    # Screen Time deterministic summary
    screen_logs = db.query(ScreenTimeLog).filter(ScreenTimeLog.child_id == child_id).all()
    daily_screen_mins = [
        (l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other)
        for l in screen_logs
    ]
    edu_mins = [l.study_screen_time for l in screen_logs]
    late_night_count = sum(1 for l in screen_logs if l.late_night_minutes > 0)

    screen_summary = {
        "total_logs": len(screen_logs),
        "avg_daily_screen_time_minutes": round(float(np.mean(daily_screen_mins)), 1) if daily_screen_mins else 0.0,
        "avg_educational_minutes": round(float(np.mean(edu_mins)), 1) if edu_mins else 0.0,
        "late_night_screen_episodes": late_night_count,
    }

    # Health & Routine deterministic summary
    health_logs = db.query(HealthLog).filter(HealthLog.child_id == child_id).all()
    sleep_list = [h.sleep_hours for h in health_logs if h.sleep_hours is not None]
    water_list = [h.water_intake_ml for h in health_logs if h.water_intake_ml is not None]
    activity_list = [h.physical_activity_minutes for h in health_logs if h.physical_activity_minutes is not None]

    health_summary = {
        "total_health_logs": len(health_logs),
        "avg_sleep_hours": round(float(np.mean(sleep_list)), 1) if sleep_list else 8.0,
        "avg_water_intake_ml": round(float(np.mean(water_list)), 1) if water_list else 1500,
        "avg_physical_activity_minutes": round(float(np.mean(activity_list)), 1) if activity_list else 30,
    }

    # Pocket Money deterministic summary
    allowances = db.query(PocketMoneyAllowance).filter(PocketMoneyAllowance.child_id == child_id).all()
    expenses = db.query(ChildExpense).filter(ChildExpense.child_id == child_id).all()
    saving_goals = db.query(SavingGoal).filter(SavingGoal.child_id == child_id).all()

    total_allowance = sum(a.amount for a in allowances)
    total_spent = sum(e.amount for e in expenses)
    total_saved = sum(g.current_saved for g in saving_goals)

    pocket_summary = {
        "total_allowance": round(total_allowance, 2),
        "total_spent": round(total_spent, 2),
        "total_saved": round(total_saved, 2),
        "active_saving_goals_count": len(saving_goals),
    }

    # Safety status deterministic summary
    safety_profile = db.query(SafetyProfile).filter(SafetyProfile.child_id == child_id).first()
    check_ins = db.query(CheckInLog).filter(CheckInLog.child_id == child_id).order_by(CheckInLog.date.desc()).all()
    latest_check_in = check_ins[0] if check_ins else None

    safety_summary = {
        "has_safety_profile": safety_profile is not None,
        "check_in_status": latest_check_in.status if latest_check_in else "SAFE",
        "emergency_contacts_count": len(safety_profile.emergency_contacts) if safety_profile and safety_profile.emergency_contacts else 0,
        "trusted_contacts_count": len(safety_profile.trusted_contacts) if safety_profile and safety_profile.trusted_contacts else 0,
    }

    # Activities deterministic summary
    activity_logs = db.query(Activity).filter(Activity.child_id == child_id).all()
    activities_summary = {
        "total_activities_count": len(activity_logs),
        "activity_types": list(set(a.activity_type for a in activity_logs)) if activity_logs else [],
        "high_priority_activities_count": sum(1 for a in activity_logs if a.priority == "High"),
    }

    deterministic_summary = {
        "profile": {
            "child_id": child.id,
            "name": child.name,
            "age": child.age,
            "age_group": age_group,
            "education_stage": child.education_stage,
            "class_or_year": getattr(child, "class_or_year", None),
        },
        "homework_summary": hw_summary,
        "attendance_summary": att_summary,
        "exam_summary": exam_summary,
        "study_summary": study_summary,
        "screen_time_summary": screen_summary,
        "health_summary": health_summary,
        "activities_summary": activities_summary,
        "pocket_money_summary": pocket_summary,
        "safety_summary": safety_summary,
    }

    # --- STEP 3: Optionally Obtain ML Predictions ---
    ml_data = None
    if request.include_ml_predictions:
        ml_data = {
            "homework_prediction": predictor.predict_homework_completion(db, child_id).model_dump(),
            "attendance_prediction": predictor.predict_attendance_trend(db, child_id).model_dump(),
            "study_prediction": predictor.predict_study_performance(db, child_id).model_dump(),
            "screen_time_prediction": predictor.predict_screen_time_trend(db, child_id).model_dump(),
            "routine_prediction": predictor.predict_routine_balance(db, child_id).model_dump(),
        }

    # --- STEP 4: Build Normalized Privacy-Aware Context and Send to Groq ---
    from app.ai.context_builder import ChildContextBuilder
    builder = ChildContextBuilder(db=db, child_id=child_id)
    child_context = builder.build(include_ml_predictions=request.include_ml_predictions)

    full_context = {
        **deterministic_summary,
        "ml_predictions": ml_data,
        "requested_focus_areas": request.focus_areas,
        "child_context": child_context.model_dump(),
    }

    raw_ai_out = groq_service.generate_ai_recommendations(full_context)
    generated_by = raw_ai_out.pop("_generated_by", "Groq AI Reasoning Engine")

    # --- STEP 5, 6 & 7: Receive, Validate & Return Structured Output ---
    ai_recommendations = ComprehensiveRecommendation(
        study_suggestions=raw_ai_out.get("study_suggestions", []),
        homework_prioritization=raw_ai_out.get("homework_prioritization", []),
        time_management=raw_ai_out.get("time_management", []),
        daily_motivation=raw_ai_out.get("daily_motivation", f"Keep up the great effort, {child.name}!"),
        healthy_routine_advice=raw_ai_out.get("healthy_routine_advice", []),
        screen_time_advice=raw_ai_out.get("screen_time_advice", []),
        saving_suggestions=raw_ai_out.get("saving_suggestions", []),
        parent_recommendations=raw_ai_out.get("parent_recommendations", []),
        exam_preparation_suggestions=raw_ai_out.get("exam_preparation_suggestions", []),
        relaxation_suggestions=raw_ai_out.get("relaxation_suggestions", []),
    )

    return RecommendationResponse(
        child_id=child.id,
        child_name=child.name,
        age=child.age,
        age_group=age_group,
        education_stage=child.education_stage,
        deterministic_summary=deterministic_summary,
        ml_predictions=ml_data,
        ai_recommendations=ai_recommendations,
        generated_by=generated_by,
    )

