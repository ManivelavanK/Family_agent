import time
import asyncio
import logging
from backend.scheduler.models import ScheduledTask
from backend.workflow.registry import registry as workflow_registry
from backend.workflow.executor import WorkflowExecutor

logger = logging.getLogger("orchestrator.scheduler.executor")

class TaskExecutor:
    @staticmethod
    async def execute_task(task: ScheduledTask):
        """Resolves task target type and calls the appropriate handler executor."""
        start_time = time.time()
        task.logs.append("Executing target payload action.")
        
        # 1. Check if the task wraps a workflow execution
        if task.workflow_id and task.workflow_name:
            instance = workflow_registry.get_instance(task.workflow_id)
            blueprint = workflow_registry.definitions.get(task.workflow_name)
            
            if not instance or not blueprint:
                err = f"Workflow metadata missing: instance={bool(instance)}, blueprint={bool(blueprint)}."
                task.status = "FAILED"
                task.logs.append(err)
                logger.error(err)
                return

            try:
                task.logs.append(f"Resuming workflow run '{task.workflow_name}' via Workflow Executor.")
                # Run the workflow executor sequentially
                await WorkflowExecutor.execute_instance(instance, blueprint)
                
                # Reflect workflow state to task state
                task.logs.extend(instance.logs)
                if instance.status == "COMPLETED":
                    task.status = "COMPLETED"
                elif instance.status == "FAILED":
                    task.status = "FAILED"
                elif instance.status == "WAITING":
                    task.status = "WAITING"
                else:
                    task.status = "COMPLETED"  # Default fallback
            except Exception as e:
                task.status = "FAILED"
                err = f"Exception executing workflow inside scheduler task: {e}"
                task.logs.append(err)
                logger.error(err, exc_info=True)
        else:
            # 2. Handle manual / direct tasks
            task.logs.append("Executing manual task payload action.")
            # Simulated dummy work time
            await asyncio.sleep(0.5)
            task.status = "COMPLETED"

        task.execution_duration = time.time() - start_time
        task.logs.append(f"Task completed. Execution Time: {task.execution_duration:.4f}s.")
