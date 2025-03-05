import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from fastapi import BackgroundTasks
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class TaskStatus(BaseModel):
    """Task status model"""
    id: str
    name: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: Optional[float] = None
    result: Optional[Any] = None

class TaskQueue:
    """Task queue manager"""
    def __init__(self):
        self._tasks: Dict[str, TaskStatus] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._max_workers = 3

    async def start_workers(self):
        """Start worker tasks"""
        for _ in range(self._max_workers):
            worker = asyncio.create_task(self._worker())
            self._workers.append(worker)

    async def stop_workers(self):
        """Stop worker tasks"""
        for _ in range(len(self._workers)):
            await self._queue.put(None)
        await asyncio.gather(*self._workers)
        self._workers.clear()

    async def _worker(self):
        """Worker process that executes tasks from the queue"""
        while True:
            task = await self._queue.get()
            if task is None:
                self._queue.task_done()
                break

            task_id, func, args, kwargs = task
            task_status = self._tasks[task_id]
            task_status.status = "running"
            task_status.started_at = datetime.now()

            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                task_status.status = "completed"
                task_status.completed_at = datetime.now()
                task_status.result = result
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                task_status.status = "failed"
                task_status.completed_at = datetime.now()
                task_status.error = str(e)
            finally:
                self._queue.task_done()

    async def add_task(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> str:
        """Add a task to the queue"""
        task_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        task_status = TaskStatus(
            id=task_id,
            name=name,
            status="pending",
            created_at=datetime.now()
        )
        self._tasks[task_id] = task_status
        await self._queue.put((task_id, func, args, kwargs))
        return task_id

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task"""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[TaskStatus]:
        """Get all tasks"""
        return list(self._tasks.values())

    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up completed tasks older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        for task_id, task in self._tasks.items():
            if task.status in ["completed", "failed"]:
                age = now - task.completed_at
                if age.total_seconds() > max_age_hours * 3600:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self._tasks[task_id]

# Global task queue instance
task_queue = TaskQueue()

def get_task_queue() -> TaskQueue:
    """Get the global task queue instance"""
    return task_queue