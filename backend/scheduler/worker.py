import asyncio
import logging
from datetime import datetime, timedelta
from backend.scheduler.models import ScheduledTask
from backend.scheduler.queue import TaskPriorityQueue
from backend.scheduler.executor import TaskExecutor

logger = logging.getLogger("orchestrator.scheduler.worker")

class SchedulerWorker:
    def __init__(self, task_queue: TaskPriorityQueue):
        self.queue = task_queue

    async def start(self):
        """Starts the continuous background task polling worker loop."""
        logger.info("Task Scheduler background worker started.")
        while True:
            try:
                # Poll queue for eligible next task
                task = await self.queue.pop_next()
                if not task:
                    await asyncio.sleep(2.0)  # Wait 2 seconds before checking again
                    continue

                logger.info(f"Picked up task {task.task_id} for execution (Priority: {task.priority})")
                
                # Execute task target action
                await TaskExecutor.execute_task(task)
                
                # Evaluate results and apply retry policy
                if task.status == "FAILED":
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = "RETRYING"
                        
                        # Reschedule for future retry execution
                        task.scheduled_time = datetime.utcnow() + timedelta(seconds=task.retry_delay)
                        task.logs.append(f"Task execution failed. Rescheduling retry {task.retry_count}/{task.max_retries} at {task.scheduled_time.isoformat()}")
                        logger.info(f"Task {task.task_id} failed. Scheduled retry {task.retry_count}/{task.max_retries}.")
                    else:
                        task.logs.append(f"Task failed and exhausted all {task.max_retries} retries.")
                        logger.warning(f"Task {task.task_id} failed permanently after max retries.")
                elif task.status == "WAITING":
                    # Reschedule waiting tasks so they get processed again in the future
                    task.status = "QUEUED"
                    task.scheduled_time = datetime.utcnow() + timedelta(seconds=5.0) # check again in 5 seconds
                    task.logs.append("Task waiting on workflow steps. Re-queueing check in 5 seconds.")
                
            except asyncio.CancelledError:
                logger.info("Scheduler worker loop cancelled.")
                break
            except Exception as e:
                logger.error(f"Error in scheduler worker cycle: {e}", exc_info=True)
                await asyncio.sleep(2.0)
