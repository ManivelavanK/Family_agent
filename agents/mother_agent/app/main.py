import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

from app.api.inventory import router as inventory_router
from app.api.purchase import router as purchase_router
from app.api.consumption import router as consumption_router
from app.api.analyzer import router as analyzer_router
from app.api.expiry import router as expiry_router
from app.api.recipe import router as recipe_router
from app.api.waste import router as waste_router
from app.api.price import router as price_router
from app.api.forecast import router as forecast_router
from app.api.memory import router as memory_router
from app.api.prediction import router as prediction_router
from app.api.shopping import router as shopping_router
from app.api.planning import router as planning_router
from app.api.reflection import router as reflection_router
from app.api.ml import router as ml_router
from app.api.agent_bus import router as agent_bus_router
from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.dashboard import router as dashboard_router
from app.api.document_vault import router as vault_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router
from app.api.voice import router as voice_router
from app.api.kitchen_assistant import router as kitchen_assistant_router
from app.api.mother_api import router as mother_api_router



# ── Lifespan (replaces deprecated @app.on_event) ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting KinNest Mother Agent...")
    create_tables()
    start_scheduler()
    yield
    logger.info("Shutting down KinNest Mother Agent...")
    stop_scheduler()


# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="KinNest — Mother Agent",
    description="Smart family grocery & kitchen management agent.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
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
    inventory_router, purchase_router, consumption_router,
    analyzer_router, expiry_router, recipe_router, waste_router,
    price_router, forecast_router, memory_router, prediction_router,
    shopping_router, planning_router, reflection_router, ml_router, agent_bus_router,
    alerts_router, analytics_router, dashboard_router, vault_router,
    reports_router, settings_router, voice_router, kitchen_assistant_router,
    mother_api_router,
]:
    app.include_router(router)


# ── Health & root ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"agent": "mother", "status": "running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "agent": "mother"}
