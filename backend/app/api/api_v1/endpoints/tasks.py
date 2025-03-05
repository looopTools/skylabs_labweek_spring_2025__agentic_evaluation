from typing import List
from fastapi import APIRouter, HTTPException
from app.core.tasks import get_task_queue, TaskStatus

router = APIRouter()

@router.get("/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str) -> TaskStatus:
    """Get the status of a task"""
    task_queue = get_task_queue()
    task_status = task_queue.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    return task_status

@router.get("/", response_model=List[TaskStatus])
async def list_tasks() -> List[TaskStatus]:
    """List all tasks"""
    task_queue = get_task_queue()
    return task_queue.get_all_tasks()