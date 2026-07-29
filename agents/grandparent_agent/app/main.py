import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database.database import create_tables

# ── Logging setup (must happen before any app imports) ──────────────────────
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
})

logger = logging.getLogger(__name__)

# ── App imports ──────────────────────────────────────────────────────────────
from app.database.database import create_tables
from app.scheduler.scheduler import start_scheduler, stop_scheduler

from app.api.profile import router as profile_router
from app.api.vitals import router as vitals_router
from app.api.medicine import router as medicine_router
from app.api.activity import router as activity_router
from app.api.nutrition import router as nutrition_router
from app.api.appointment import router as appointment_router
from app.api.insurance import router as insurance_router
from app.api.memory import router as memory_router
from app.api.recommendation import router as recommendation_router
from app.api.reminder import router as reminder_router
from app.api.emergency import router as emergency_router
from app.api.analytics import router as analytics_router
from app.api.forecast import router as forecast_router
from app.api.voice import router as voice_router
from app.api.rules import router as rules_router
from app.api.scheduler import router as scheduler_api_router
from app.api.communication import router as communication_router
from app.api.ml import router as ml_router
from app.api.report import router as report_router
from app.api.cognitive import router as cognitive_router
from app.api.notification import router as notification_router


# ── Lifespan (replaces deprecated @app.on_event) ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting KinNest Grandparent Agent...")
    create_tables()
    start_scheduler()
    
    # Print WhatsApp Service execution status
    from app.notification.whatsapp_service import check_service_mode
    check_service_mode()
    
    yield
    logger.info("Shutting down KinNest Grandparent Agent...")
    stop_scheduler()


# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="KinNest — Grandparent Agent",
    description="Smart wellness, memory care & emergency agent for grandparents.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An internal server error occurred."},
    )


# ── Routers ──────────────────────────────────────────────────────────────────
for router in [
    profile_router, vitals_router, medicine_router,
    activity_router, nutrition_router, appointment_router,
    insurance_router, memory_router, recommendation_router,
    reminder_router, emergency_router, analytics_router,
    forecast_router, voice_router, rules_router, scheduler_api_router,
    communication_router, ml_router, report_router, cognitive_router,
    notification_router,
]:
    app.include_router(router)


# ── Health & root ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"agent": "grandparent", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "agent": "grandparent"}
