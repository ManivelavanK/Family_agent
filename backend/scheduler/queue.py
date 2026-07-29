import asyncio
from datetime import datetime
from typing import List, Optional
from backend.scheduler.models import ScheduledTask
from backend.scheduler.priority import get_priority_weight

class TaskPriorityQueue:
    def __init__(self):
        self.tasks: List[ScheduledTask] = []
        self._lock = asyncio.Lock()

    async def push(self, task: ScheduledTask):
        """Adds a task to the queue and transitions status to QUEUED."""
        async with self._lock:
            task.status = "QUEUED"
            task.logs.append(f"Task pushed to Priority Queue (Priority: {task.priority}).")
            self.tasks.append(task)

    async def pop_next(self) -> Optional[ScheduledTask]:
        """Finds and pops the highest priority task that is eligible for execution (scheduled_time <= now)."""
        async with self._lock:
            now = datetime.utcnow()
            # Eligible tasks are those in QUEUED or PENDING status, and whose scheduled start time has passed
            eligible = [
                t for t in self.tasks 
                if t.status in ["QUEUED", "PENDING", "RETRYING"] and t.scheduled_time <= now
            ]
            
            if not eligible:
                return None
                
            # Sort: Priority weight (descending), then scheduled_time (ascending)
            eligible.sort(key=lambda t: (-get_priority_weight(t.priority), t.scheduled_time))
            selected = eligible[0]
            
            # Transition state to RUNNING
            selected.status = "RUNNING"
            selected.logs.append("Worker picked up task for execution.")
            return selected

    async def cancel(self, task_id: str) -> bool:
        """Transitions task status to CANCELLED if currently pending execution in the queue."""
        async with self._lock:
            for task in self.tasks:
                if task.task_id == task_id:
                    if task.status in ["PENDING", "QUEUED", "WAITING", "RETRYING"]:
                        task.status = "CANCELLED"
                        task.logs.append("Task execution cancelled in queue.")
                        return True
            return False

    async def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        async with self._lock:
            for task in self.tasks:
                if task.task_id == task_id:
                    return task
            return None

    async def get_all(self) -> List[ScheduledTask]:
        async with self._lock:
            return list(self.tasks)
