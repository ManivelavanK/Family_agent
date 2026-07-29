import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.study import StudySession
from app.models.homework import Homework
from app.models.screen_time import ScreenTimeLog
from app.schemas.feedback import RecommendationOutcome, ChildPersonalizationProfile

logger = logging.getLogger(__name__)

# In-memory feedback stores
RECOMMENDATION_OUTCOMES_STORE: List[Dict[str, Any]] = []
PERSONALIZATION_PROFILES_STORE: Dict[int, Dict[str, Any]] = {}


class RecommendationFeedbackService:
    """
    Phase 11: Tracks Recommendation -> Action -> Outcome.
    Evaluates whether recommendations helped or were ignored, and updates personalization history.
    """

    def __init__(self, db: Session):
        self.db = db

    def record_recommendation(
        self,
        recommendation_id: str,
        child_id: int,
        category: str,
        suggested_action: str,
    ) -> RecommendationOutcome:
        outcome = RecommendationOutcome(
            recommendation_id=recommendation_id,
            child_id=child_id,
            category=category,
            suggested_action=suggested_action,
            outcome_status="PENDING",
            effectiveness_score=0.0,
        )
        RECOMMENDATION_OUTCOMES_STORE.append(outcome.model_dump())
        return outcome

    def evaluate_recommendations(self, child_id: int) -> List[RecommendationOutcome]:
        evaluations: List[RecommendationOutcome] = []
        now = datetime.utcnow()

        # Fetch recent child activity to observe actual behavior
        study_logs = self.db.query(StudySession).filter(StudySession.child_id == child_id).all()
        hw_logs = self.db.query(Homework).filter(Homework.child_id == child_id).all()

        profile_data = PERSONALIZATION_PROFILES_STORE.get(child_id, {
            "child_id": child_id,
            "optimal_study_duration_mins": 45,
            "preferred_study_time": "AFTERNOON",
            "planning_style": "BALANCED",
            "reminder_frequency": "MODERATE",
            "recommendation_difficulty": "MODERATE",
            "communication_style": "ENCOURAGING",
            "ignored_patterns_count": {},
            "successful_categories_count": {},
        })

        for rec in RECOMMENDATION_OUTCOMES_STORE:
            if rec["child_id"] != child_id or rec["outcome_status"] != "PENDING":
                continue

            cat = rec["category"]
            action = rec["suggested_action"].lower()

            if "study" in cat.lower() or "study" in action:
                # Check actual study sessions logged
                recent_study = [s for s in study_logs if s.duration_minutes and s.duration_minutes >= 30]
                if recent_study:
                    avg_focus = sum(s.focus_score for s in recent_study if s.focus_score) / len(recent_study) if recent_study else 70
                    rec["outcome_status"] = "SUCCESSFUL"
                    rec["effectiveness_score"] = min(100.0, avg_focus + 10.0)
                    rec["observed_action"] = f"Logged {len(recent_study)} study session(s) with avg focus {avg_focus:.1f}"
                    profile_data["successful_categories_count"][cat] = profile_data["successful_categories_count"].get(cat, 0) + 1
                else:
                    rec["outcome_status"] = "IGNORED"
                    rec["effectiveness_score"] = 0.0
                    rec["observed_action"] = "No study session recorded following recommendation"
                    profile_data["ignored_patterns_count"][cat] = profile_data["ignored_patterns_count"].get(cat, 0) + 1

            elif "homework" in cat.lower() or "assignment" in action:
                completed = [h for h in hw_logs if h.completion_status]
                if completed:
                    rec["outcome_status"] = "SUCCESSFUL"
                    rec["effectiveness_score"] = 90.0
                    rec["observed_action"] = f"Completed {len(completed)} assignment(s)"
                    profile_data["successful_categories_count"][cat] = profile_data["successful_categories_count"].get(cat, 0) + 1
                else:
                    rec["outcome_status"] = "IGNORED"
                    rec["effectiveness_score"] = 10.0
                    rec["observed_action"] = "Assignments remain pending"
                    profile_data["ignored_patterns_count"][cat] = profile_data["ignored_patterns_count"].get(cat, 0) + 1
            else:
                rec["outcome_status"] = "PARTIAL"
                rec["effectiveness_score"] = 50.0

            rec["evaluated_at"] = now.isoformat()
            evaluations.append(RecommendationOutcome(**rec))

        PERSONALIZATION_PROFILES_STORE[child_id] = profile_data
        return evaluations


class AdaptiveRecommendationEngine:
    """
    Adapts and personalizes future AI recommendations based on historical feedback and learning loops.
    Adjusts:
    - Study duration
    - Preferred study times
    - Planning style
    - Reminder frequency
    - Recommendation difficulty
    - Communication style
    """

    def __init__(self, db: Session):
        self.db = db
        self.feedback_service = RecommendationFeedbackService(db=db)

    def adapt_recommendations(self, child_id: int, base_recommendations: List[str]) -> List[str]:
        # 1. Evaluate pending outcomes first to reflect latest observation
        self.feedback_service.evaluate_recommendations(child_id)

        profile = PERSONALIZATION_PROFILES_STORE.get(child_id, {})
        ignored_map = profile.get("ignored_patterns_count", {})

        adapted: List[str] = []
        for rec in base_recommendations:
            rec_lower = rec.lower()

            # Pattern Adaptation: If long study sessions repeatedly ignored, adapt to bite-sized 25-min Pomodoro
            if ("45" in rec or "60" in rec or "study" in rec_lower) and ignored_map.get("STUDY", 0) >= 2:
                profile["optimal_study_duration_mins"] = 25
                profile["planning_style"] = "FLEXIBLE"
                profile["recommendation_difficulty"] = "EASY"
                adapted.append("1. Start with a bite-sized 25-minute study block today to build momentum easily.")

            # Pattern Adaptation: If screen time suggestions ignored, shift to encouraging outdoor alternatives
            elif "screen" in rec_lower and ignored_map.get("SCREEN_TIME", 0) >= 2:
                profile["communication_style"] = "PLAYFUL"
                adapted.append("2. How about a fun 20-minute outdoor break or game before getting back to screen time?")

            else:
                adapted.append(rec)

        PERSONALIZATION_PROFILES_STORE[child_id] = profile
        return adapted

    @staticmethod
    def get_personalization_profile(child_id: int) -> ChildPersonalizationProfile:
        raw = PERSONALIZATION_PROFILES_STORE.get(child_id, {"child_id": child_id})
        return ChildPersonalizationProfile(**raw)
