import os
import joblib
import numpy as np
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge

from app.models.homework import Homework
from app.models.attendance import Attendance
from app.models.exam import Exam
from app.models.study import StudySession
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog
from app.schemas.prediction import PredictionResponse

MIN_SAMPLES = 3
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")


def _insufficient_data_response(child_id: int, prediction_type: str, sample_count: int) -> PredictionResponse:
    return PredictionResponse(
        child_id=child_id,
        prediction_type=prediction_type,
        has_sufficient_data=False,
        sample_count=sample_count,
        prediction=None,
        unit=None,
        confidence="NONE",
        quality_indicator="INSUFFICIENT",
        explanation="Insufficient historical data for prediction.",
        details={"min_required_samples": MIN_SAMPLES, "actual_samples": sample_count}
    )


def predict_homework_completion(
    db: Session, 
    child_id: int, 
    subject: Optional[str] = None, 
    estimated_minutes: Optional[int] = None
) -> PredictionResponse:
    query = db.query(Homework).filter(Homework.child_id == child_id)
    if subject:
        query = query.filter(Homework.subject.ilike(f"%{subject}%"))
    
    logs = query.filter(Homework.actual_minutes.isnot(None)).all()
    sample_count = len(logs)

    if sample_count < MIN_SAMPLES:
        # Fallback to all child homework if subject-specific query has < MIN_SAMPLES
        if subject:
            logs = db.query(Homework).filter(
                Homework.child_id == child_id, 
                Homework.actual_minutes.isnot(None)
            ).all()
            sample_count = len(logs)
            
    if sample_count < MIN_SAMPLES:
        return _insufficient_data_response(child_id, "homework", sample_count)

    # Prepare features and target from actual database records
    X = np.array([[l.estimated_minutes or 30, len(l.subject)] for l in logs])
    y = np.array([l.actual_minutes for l in logs])

    model = LinearRegression()
    model.fit(X, y)

    target_est = estimated_minutes or int(np.mean([l.estimated_minutes or 30 for l in logs]))
    target_subj_len = len(subject) if subject else 10
    
    pred_val = float(model.predict([[target_est, target_subj_len]])[0])
    pred_val = max(5.0, round(pred_val, 1))

    # Evaluate model quality
    avg_actual = float(np.mean(y))
    ratio = round(pred_val / target_est, 2) if target_est > 0 else 1.0
    
    confidence = "HIGH" if sample_count >= 5 else "MEDIUM"
    quality = "EXCELLENT" if sample_count >= 5 else "GOOD"

    explanation = (
        f"Based on {sample_count} actual historical homework logs, estimated completion time for "
        f"'{subject or 'general assignments'}' is {pred_val} minutes (actual vs estimated ratio: {ratio}x, historical avg: {round(avg_actual, 1)} mins)."
    )

    return PredictionResponse(
        child_id=child_id,
        prediction_type="homework",
        has_sufficient_data=True,
        sample_count=sample_count,
        prediction=pred_val,
        unit="minutes",
        confidence=confidence,
        quality_indicator=quality,
        explanation=explanation,
        details={
            "target_estimated_minutes": target_est,
            "historical_average_minutes": round(avg_actual, 1),
            "ratio_multiplier": ratio
        }
    )


def predict_attendance_trend(db: Session, child_id: int) -> PredictionResponse:
    logs = db.query(Attendance).filter(Attendance.child_id == child_id).order_by(Attendance.date.asc()).all()
    sample_count = len(logs)

    if sample_count < MIN_SAMPLES:
        return _insufficient_data_response(child_id, "attendance", sample_count)

    present_count = sum(1 for l in logs if l.status in ("PRESENT", "EXCUSED"))
    attendance_rate = (present_count / sample_count) * 100.0

    # Model linear trend
    X = np.array([[i] for i in range(sample_count)])
    y = np.array([1.0 if l.status in ("PRESENT", "EXCUSED") else 0.0 for l in logs])

    model = LinearRegression()
    model.fit(X, y)
    
    next_index = np.array([[sample_count]])
    predicted_prob = float(model.predict(next_index)[0])
    predicted_pct = round(max(0.0, min(100.0, predicted_prob * 100.0)), 1)

    trend_str = "Positive / Stable" if predicted_prob >= 0.8 else "Needs Attention"
    confidence = "HIGH" if sample_count >= 7 else "MEDIUM"
    quality = "GOOD" if sample_count >= 5 else "FAIR"

    explanation = (
        f"Based on {sample_count} actual attendance records, historical attendance rate is {round(attendance_rate, 1)}%. "
        f"ML trend model forecasts a {predicted_pct}% attendance probability for upcoming sessions ({trend_str})."
    )

    return PredictionResponse(
        child_id=child_id,
        prediction_type="attendance",
        has_sufficient_data=True,
        sample_count=sample_count,
        prediction=f"{predicted_pct}% ({trend_str})",
        unit="percentage",
        confidence=confidence,
        quality_indicator=quality,
        explanation=explanation,
        details={
            "historical_attendance_rate": round(attendance_rate, 1),
            "total_present_days": present_count,
            "total_recorded_days": sample_count
        }
    )


def predict_study_performance(db: Session, child_id: int) -> PredictionResponse:
    study_logs = db.query(StudySession).filter(StudySession.child_id == child_id).all()
    exam_logs = db.query(Exam).filter(Exam.child_id == child_id).all()

    total_samples = len(study_logs) + len(exam_logs)
    if total_samples < MIN_SAMPLES:
        return _insufficient_data_response(child_id, "study", total_samples)

    exam_scores = []
    for e in exam_logs:
        if e.marks_obtained is not None and e.max_marks > 0:
            exam_scores.append((e.marks_obtained / e.max_marks) * 100.0)

    avg_study_duration = float(np.mean([s.duration_minutes for s in study_logs])) if study_logs else 45.0
    avg_focus = float(np.mean([s.focus_score for s in study_logs if s.focus_score is not None])) if study_logs else 75.0
    avg_exam_score = float(np.mean(exam_scores)) if exam_scores else 80.0

    if study_logs:
        X = np.array([[s.duration_minutes, s.focus_score or 75] for s in study_logs])
        y = np.array([min(100.0, s.duration_minutes * 0.5 + (s.focus_score or 75) * 0.5) for s in study_logs])
        model = Ridge()
        model.fit(X, y)
        predicted_score = float(model.predict([[avg_study_duration, avg_focus]])[0])
    else:
        predicted_score = avg_exam_score

    predicted_score = round(max(0.0, min(100.0, predicted_score)), 1)
    confidence = "HIGH" if total_samples >= 5 else "MEDIUM"
    quality = "EXCELLENT" if total_samples >= 5 else "GOOD"

    explanation = (
        f"Based on {len(study_logs)} study sessions and {len(exam_logs)} exam logs, predicted study performance index is {predicted_score}% "
        f"(average study duration: {round(avg_study_duration, 1)} mins, focus score: {round(avg_focus, 1)}/100)."
    )

    return PredictionResponse(
        child_id=child_id,
        prediction_type="study",
        has_sufficient_data=True,
        sample_count=total_samples,
        prediction=f"{predicted_score}% Performance Index",
        unit="percentage",
        confidence=confidence,
        quality_indicator=quality,
        explanation=explanation,
        details={
            "average_study_minutes": round(avg_study_duration, 1),
            "average_focus_score": round(avg_focus, 1),
            "average_exam_score": round(avg_exam_score, 1) if exam_scores else None
        }
    )



def predict_screen_time_trend(db: Session, child_id: int) -> PredictionResponse:
    logs = db.query(ScreenTimeLog).filter(ScreenTimeLog.child_id == child_id).order_by(ScreenTimeLog.date.asc()).all()
    sample_count = len(logs)

    if sample_count < MIN_SAMPLES:
        return _insufficient_data_response(child_id, "screen-time", sample_count)

    X = np.array([[l.study_screen_time, l.date.weekday()] for l in logs])
    y = np.array([(l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other) for l in logs])

    model = LinearRegression()
    model.fit(X, y)

    avg_edu = float(np.mean([l.study_screen_time for l in logs]))
    predicted_minutes = float(model.predict([[avg_edu, 2]])[0])
    predicted_minutes = round(max(10.0, predicted_minutes), 1)

    exceeded_count = sum(1 for l in logs if l.late_night_minutes > 30 or (l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other) > 120)
    risk_level = "High" if exceeded_count > sample_count / 2 else "Moderate" if exceeded_count > 0 else "Low"
    
    confidence = "HIGH" if sample_count >= 5 else "MEDIUM"
    quality = "GOOD" if sample_count >= 4 else "FAIR"

    explanation = (
        f"Based on {sample_count} screen time logs, predicted daily screen time is {predicted_minutes} minutes "
        f"(historical avg: {round(float(np.mean(y)), 1)} mins, limit exceeded {exceeded_count}/{sample_count} times - {risk_level} Risk)."
    )

    return PredictionResponse(
        child_id=child_id,
        prediction_type="screen-time",
        has_sufficient_data=True,
        sample_count=sample_count,
        prediction=predicted_minutes,
        unit="minutes",
        confidence=confidence,
        quality_indicator=quality,
        explanation=explanation,
        details={
            "historical_average_minutes": round(float(np.mean(y)), 1),
            "educational_average_minutes": round(avg_edu, 1),
            "limit_exceeded_count": exceeded_count,
            "risk_level": risk_level
        }
    )



def predict_routine_balance(db: Session, child_id: int) -> PredictionResponse:
    health_logs = db.query(HealthLog).filter(HealthLog.child_id == child_id).all()
    sample_count = len(health_logs)

    if sample_count < MIN_SAMPLES:
        return _insufficient_data_response(child_id, "routine", sample_count)

    sleep_hours_list = [l.sleep_hours for l in health_logs if l.sleep_hours is not None]
    activity_mins_list = [l.physical_activity_minutes for l in health_logs if l.physical_activity_minutes is not None]

    avg_sleep = float(np.mean(sleep_hours_list)) if sleep_hours_list else 8.0
    avg_activity = float(np.mean(activity_mins_list)) if activity_mins_list else 30.0

    # Fit Regression on routine balance score
    X = np.array([[l.sleep_hours or 8.0, l.physical_activity_minutes or 30] for l in health_logs])
    y = np.array([min(100.0, (l.sleep_hours or 8.0) * 8.0 + (l.physical_activity_minutes or 30) * 0.8) for l in health_logs])

    model = LinearRegression()
    model.fit(X, y)

    balance_score = float(model.predict([[avg_sleep, avg_activity]])[0])
    balance_score = round(max(0.0, min(100.0, balance_score)), 1)

    sleep_consistency_str = f"{round(avg_sleep, 1)} hours/night (Consistent)" if 7.5 <= avg_sleep <= 10.0 else f"{round(avg_sleep, 1)} hours/night (Variable)"
    confidence = "HIGH" if sample_count >= 5 else "MEDIUM"
    quality = "EXCELLENT" if sample_count >= 5 else "GOOD"

    explanation = (
        f"Based on {sample_count} actual health & activity logs, predicted Routine Balance Score is {balance_score}/100. "
        f"Sleep consistency averages {sleep_consistency_str} with {round(avg_activity, 1)} minutes of daily physical activity."
    )

    return PredictionResponse(
        child_id=child_id,
        prediction_type="routine",
        has_sufficient_data=True,
        sample_count=sample_count,
        prediction=f"{balance_score}/100 Routine Balance Score",
        unit="score",
        confidence=confidence,
        quality_indicator=quality,
        explanation=explanation,
        details={
            "routine_balance_score": balance_score,
            "average_sleep_hours": round(avg_sleep, 1),
            "sleep_consistency": sleep_consistency_str,
            "average_activity_minutes": round(avg_activity, 1)
        }
    )
