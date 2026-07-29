import asyncio
import logging
from backend.workflow.engine import WorkflowEngine

logger = logging.getLogger("orchestrator.workflow")

# Global singleton engine instance
workflow_engine = WorkflowEngine()

async def workflow_background_worker():
    """Background task polling loop running every 10 seconds to resume/retry workflows."""
    logger.info("Workflow Engine background worker started.")
    while True:
        try:
            await asyncio.sleep(10)  # Wait 10 seconds between runs
            await workflow_engine.check_and_resume_workflows()
        except asyncio.CancelledError:
            logger.info("Workflow background worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in workflow background worker: {e}", exc_info=True)
