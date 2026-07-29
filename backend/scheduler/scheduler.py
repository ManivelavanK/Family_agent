import logging
from datetime import datetime
from typing import List, Optional
from backend.scheduler.models import ScheduledTask
from backend.scheduler.queue import TaskPriorityQueue

logger = logging.getLogger("orchestrator.scheduler")

class TaskScheduler:
    def __init__(self, task_queue: TaskPriorityQueue):
        self.queue = task_queue

    async def schedule_task(self, task: ScheduledTask):
        """Schedules a new task by pushing it to the priority queue."""
        logger.info(f"Scheduling task '{task.task_id}' (Priority: {task.priority})")
        await self.queue.push(task)

    async def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return await self.queue.get_task(task_id)

    async def get_all_tasks(self) -> List[ScheduledTask]:
        return await self.queue.get_all()

    async def cancel_task(self, task_id: str) -> bool:
        logger.info(f"Requesting cancellation for task '{task_id}'.")
        return await self.queue.cancel(task_id)

    async def retry_task(self, task_id: str) -> bool:
        """Manually resets a failed or cancelled task back to QUEUED status for immediate execution."""
        task = await self.queue.get_task(task_id)
        if not task:
            return False
            
        if task.status in ["FAILED", "CANCELLED"]:
            task.status = "QUEUED"
            task.retry_count = 0
            task.scheduled_time = datetime.utcnow()
            task.logs.append("Task manually re-submitted for execution by user.")
            logger.info(f"Task '{task_id}' manually re-submitted for execution.")
            return True
        return False
