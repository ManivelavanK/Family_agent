import asyncio
import logging
from backend.event_router.router import EventRouterHistory
from backend.event_router.dispatcher import EventDispatcher

logger = logging.getLogger("orchestrator.event_router")

# Global singleton stores
event_history = EventRouterHistory()
event_dispatcher = EventDispatcher(event_history)

async def event_router_background_worker():
    """Background task polling loop running every 30 seconds to retry failed dispatches."""
    logger.info("Event Router background worker started.")
    while True:
        try:
            await asyncio.sleep(30)  # Wait 30 seconds between runs
            await event_history.retry_failed_dispatches(event_dispatcher)
        except asyncio.CancelledError:
            logger.info("Event Router background worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in Event Router background worker: {e}", exc_info=True)
