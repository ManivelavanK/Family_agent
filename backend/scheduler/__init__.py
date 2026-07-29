from backend.scheduler.queue import TaskPriorityQueue
from backend.scheduler.scheduler import TaskScheduler
from backend.scheduler.worker import SchedulerWorker

# Global singleton stores
task_queue = TaskPriorityQueue()
scheduler = TaskScheduler(task_queue)
scheduler_worker = SchedulerWorker(task_queue)
