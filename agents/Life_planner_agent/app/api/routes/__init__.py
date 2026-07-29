from app.api.routes.health import router as health_router
from app.api.routes.plans import router as plans_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.budget import router as budget_router
from app.api.routes.itinerary import router as itinerary_router
from app.api.routes.participants import router as participants_router
from app.api.routes.ai import router as ai_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.memory import router as memory_router
from app.api.routes.reflections import router as reflections_router
from app.api.routes.guests import router as guests_router
from app.api.routes.routines import router as routines_router
from app.api.routes.planner_agent import router as planner_agent_router

__all__ = [
    "plans_router", "tasks_router", "budget_router",
    "itinerary_router", "participants_router", "health_router",
    "ai_router", "calendar_router", "memory_router", "reflections_router",
    "guests_router", "routines_router", "planner_agent_router"
]
