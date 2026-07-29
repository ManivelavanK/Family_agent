import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Logging setup ───────────────────────────────────────────────────────────
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

from app.api.baby_router import router as baby_router
from app.api.feeding_router import router as feeding_router
from app.api.sleep_router import router as sleep_router
from app.api.growth_router import router as growth_router
from app.api.health_router import router as health_router
from app.api.vaccine_router import router as vaccine_router
from app.api.dashboard_router import router as dashboard_router
from app.api.alerts_router import router as alerts_router
from app.api.ai_router import router as ai_router
from app.api.voice_router import router as voice_router
from app.api.notification_router import router as notification_router

# ── Lifespan context manager ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting KinNest Baby Agent...")
    try:
        create_tables()
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    start_scheduler()
    yield
    logger.info("Shutting down KinNest Baby Agent...")
    stop_scheduler()

# ── App initialization ───────────────────────────────────────────────────────
app = FastAPI(
    title="KinNest — Baby Agent",
    description="Smart baby care management agent for feeding, sleep, growth, health, and vaccines.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Enable CORS for frontend integration
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

# ── Include Routers ──────────────────────────────────────────────────────────
app.include_router(baby_router)
app.include_router(feeding_router)
app.include_router(sleep_router)
app.include_router(growth_router)
app.include_router(health_router)
app.include_router(vaccine_router)
app.include_router(dashboard_router)
app.include_router(alerts_router)
app.include_router(ai_router)
app.include_router(voice_router)
app.include_router(notification_router)

# ── Root & Health Check ──────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "agent": "babychild_agent",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health", tags=["Health"])
def health():
    return {
        "success": True,
        "message": "Baby Agent running"
    }
