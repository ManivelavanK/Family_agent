import os
import joblib
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor

from app.models.homework import Homework
from app.models.attendance import Attendance
from app.models.exam import Exam
from app.models.study import StudySession
from app.models.screen_time import ScreenTimeLog
from app.models.health import HealthLog

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")


def ensure_model_dir():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR, exist_ok=True)


def train_homework_model(db: Session) -> dict:
    records = db.query(Homework).filter(
        Homework.actual_minutes.isnot(None),
        Homework.estimated_minutes.isnot(None)
    ).all()

    sample_count = len(records)
    if sample_count < 3:
        return {"status": "INSUFFICIENT_DATA", "samples": sample_count, "model": "homework_model"}

    X = np.array([[r.estimated_minutes, len(r.subject)] for r in records])
    y = np.array([r.actual_minutes for r in records])

    model = LinearRegression()
    model.fit(X, y)

    score = float(model.score(X, y)) if sample_count > 1 else 1.0
    ensure_model_dir()
    joblib.dump(model, os.path.join(MODEL_DIR, "homework_model.joblib"))

    return {
        "status": "TRAINED",
        "samples": sample_count,
        "r2_score": round(score, 4),
        "model": "homework_model"
    }


def train_attendance_model(db: Session) -> dict:
    records = db.query(Attendance).all()
    sample_count = len(records)
    if sample_count < 3:
        return {"status": "INSUFFICIENT_DATA", "samples": sample_count, "model": "attendance_model"}

    X = np.array([[r.date.weekday(), r.date.day] for r in records])
    y = np.array([1 if r.status in ("PRESENT", "EXCUSED") else 0 for r in records])

    if len(np.unique(y)) < 2:
        # All same class
        y[0] = 1 - y[0]

    model = LogisticRegression(max_iter=200)
    model.fit(X, y)

    acc = float(model.score(X, y))
    ensure_model_dir()
    joblib.dump(model, os.path.join(MODEL_DIR, "attendance_model.joblib"))

    return {
        "status": "TRAINED",
        "samples": sample_count,
        "accuracy": round(acc, 4),
        "model": "attendance_model"
    }


def train_study_model(db: Session) -> dict:
    sessions = db.query(StudySession).all()
    sample_count = len(sessions)
    if sample_count < 3:
        return {"status": "INSUFFICIENT_DATA", "samples": sample_count, "model": "study_model"}

    X = np.array([[s.duration_minutes, s.focus_score or 75] for s in sessions])
    y = np.array([min(100.0, s.duration_minutes * 0.5 + (s.focus_score or 75) * 0.5) for s in sessions])

    model = Ridge()
    model.fit(X, y)

    score = float(model.score(X, y))
    ensure_model_dir()
    joblib.dump(model, os.path.join(MODEL_DIR, "study_model.joblib"))

    return {
        "status": "TRAINED",
        "samples": sample_count,
        "r2_score": round(score, 4),
        "model": "study_model"
    }



def train_screen_time_model(db: Session) -> dict:
    logs = db.query(ScreenTimeLog).all()
    sample_count = len(logs)
    if sample_count < 3:
        return {"status": "INSUFFICIENT_DATA", "samples": sample_count, "model": "screen_time_model"}

    X = np.array([[l.study_screen_time, l.date.weekday()] for l in logs])
    y = np.array([(l.mobile + l.gaming + l.tv + l.social_media + l.study_screen_time + l.other) for l in logs])

    model = LinearRegression()
    model.fit(X, y)

    score = float(model.score(X, y))
    ensure_model_dir()
    joblib.dump(model, os.path.join(MODEL_DIR, "screen_time_model.joblib"))

    return {
        "status": "TRAINED",
        "samples": sample_count,
        "r2_score": round(score, 4),
        "model": "screen_time_model"
    }



def train_routine_model(db: Session) -> dict:
    logs = db.query(HealthLog).all()
    sample_count = len(logs)
    if sample_count < 3:
        return {"status": "INSUFFICIENT_DATA", "samples": sample_count, "model": "routine_model"}

    X = np.array([[l.sleep_hours or 8.0, l.physical_activity_minutes or 30] for l in logs])
    y = np.array([min(100.0, (l.sleep_hours or 8.0) * 10 + (l.physical_activity_minutes or 30) * 0.5) for l in logs])

    model = LinearRegression()
    model.fit(X, y)

    score = float(model.score(X, y))
    ensure_model_dir()
    joblib.dump(model, os.path.join(MODEL_DIR, "routine_model.joblib"))

    return {
        "status": "TRAINED",
        "samples": sample_count,
        "r2_score": round(score, 4),
        "model": "routine_model"
    }


def train_all_models(db: Session) -> dict:
    results = {
        "homework": train_homework_model(db),
        "attendance": train_attendance_model(db),
        "study": train_study_model(db),
        "screen_time": train_screen_time_model(db),
        "routine": train_routine_model(db),
    }
    
    trained_count = sum(1 for res in results.values() if res["status"] == "TRAINED")
    return {
        "status": f"Completed training process. {trained_count}/5 models trained.",
        "models_trained": [k for k, v in results.items() if v["status"] == "TRAINED"],
        "training_details": results,
        "trained_at": datetime.utcnow()
    }
