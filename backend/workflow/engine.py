import asyncio
import logging
from datetime import datetime, timezone, timedelta
from backend.workflow.registry import registry
from backend.workflow.executor import WorkflowExecutor
from backend.workflow.models import WorkflowInstance

# Import the Scheduler
from backend.scheduler import scheduler
from backend.scheduler.models import ScheduledTask

logger = logging.getLogger("orchestrator.workflow.engine")

class WorkflowEngine:
    def __init__(self):
        self.executor = WorkflowExecutor()

    async def trigger_workflow(self, name: str, payload: dict) -> WorkflowInstance:
        """Instantiates a workflow instance and schedules it as a priority task."""
        definition = registry.definitions.get(name)
        if not definition:
            raise ValueError(f"Workflow blueprint '{name}' does not exist.")
            
        instance = registry.create_instance(name, payload)
        
        # Create and schedule task
        task = ScheduledTask(
            workflow_id=instance.workflow_id,
            workflow_name=name,
            priority=payload.get("priority", "NORMAL"),
            payload=payload
        )
        await scheduler.schedule_task(task)
        
        return instance

    async def check_and_resume_workflows(self):
        """Clean up function for workflow engine (now managed primarily by the Scheduler worker)."""
        instances = registry.get_all_instances()
        now = datetime.utcnow()
        
        for instance in instances:
            definition = registry.definitions.get(instance.workflow_name)
            if not definition:
                continue

            # Expire abandoned workflows (> 1 hour)
            if instance.status in ["RUNNING", "WAITING"]:
                elapsed = now - instance.updated_time
                if elapsed > timedelta(hours=1):
                    logger.warning(f"Workflow '{instance.workflow_id}' has been inactive for {elapsed}. Transitioning to FAILED.")
                    instance.logs.append(f"Workflow timeout: inactive for {elapsed}. Expired by system.")
                    registry.update_status(instance.workflow_id, "FAILED")
