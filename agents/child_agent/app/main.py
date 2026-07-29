from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.schema import create_tables
from app.routes.student_routes import router as student_router
from app.routes.subject_routes import router as subject_router
from app.routes.assignment_routes import router as assignment_router
from app.routes.study_routes import router as study_router
from app.routes.goal_routes import router as goal_router
from app.routes.exam_routes import router as exam_router
from app.routes.progress_routes import router as progress_router
from app.routes.ai_routes import router as ai_router
from app.routes.family_routes import router as family_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="KinNest — Children Agent",
    description="Academic guardian and study helper agent for KinNest family",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend react client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(student_router)
app.include_router(subject_router)
app.include_router(assignment_router)
app.include_router(study_router)
app.include_router(goal_router)
app.include_router(exam_router)
app.include_router(progress_router)
app.include_router(ai_router)
app.include_router(family_router)

# Register app/api routers for Child Profile endpoints
from app.api.profile import router as api_profile_router
from app.api.activities import router as api_activities_router
from app.api.ai_intelligence import router as api_ai_intel_router
from app.api.attendance import router as api_attendance_router
from app.api.cross_agent import router as api_cross_agent_router
from app.api.dashboard import router as api_dashboard_router
from app.api.exams import router as api_exams_router
from app.api.health import router as api_health_router
from app.api.homework import router as api_homework_router
from app.api.notification import router as api_notification_router
from app.api.nutrition import router as api_nutrition_router
from app.api.pocket_money import router as api_pocket_money_router
from app.api.prediction import router as api_prediction_router
from app.api.recommendation import router as api_recommendation_router
from app.api.safety import router as api_safety_router
from app.api.schedule import router as api_schedule_router
from app.api.screen_time import router as api_screen_time_router
from app.api.study import router as api_study_router
from app.api.wellness import router as api_wellness_router
from app.api.whatsapp_webhook import router as api_whatsapp_router

app.include_router(api_profile_router)
app.include_router(api_activities_router)
app.include_router(api_ai_intel_router)
app.include_router(api_attendance_router)
app.include_router(api_cross_agent_router)
app.include_router(api_dashboard_router)
app.include_router(api_exams_router)
app.include_router(api_health_router)
app.include_router(api_homework_router)
app.include_router(api_notification_router)
app.include_router(api_nutrition_router)
app.include_router(api_pocket_money_router)
app.include_router(api_prediction_router)
app.include_router(api_recommendation_router)
app.include_router(api_safety_router)
app.include_router(api_schedule_router)
app.include_router(api_screen_time_router)
app.include_router(api_study_router)
app.include_router(api_wellness_router)
app.include_router(api_whatsapp_router)


@app.get("/")
def read_root():
    return {
        "agent": "KinNest Children Study Companion Agent",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}