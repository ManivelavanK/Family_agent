import asyncio
import logging
from backend.context.manager import SharedContextManager

logger = logging.getLogger("orchestrator.context")

# Global singleton manager instance
context_manager = SharedContextManager()

async def context_ttl_cleanup_worker():
    """Background task polling loop running every 5 minutes to clear expired context objects."""
    logger.info("Shared Context TTL cleanup worker started.")
    while True:
        try:
            await asyncio.sleep(300)  # Wait 5 minutes between runs
            await context_manager.cleanup_expired_contexts()
        except asyncio.CancelledError:
            logger.info("Context cleanup worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in context cleanup loop: {e}", exc_info=True)
