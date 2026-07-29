from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.plan import PlanTaskCreate, PlanTaskUpdate, PlanTaskResponse
from app.services.plan_service import TaskService, PlanService

router = APIRouter(tags=["Tasks"])

@router.post("/plans/{plan_id}/tasks", response_model=StandardResponse[PlanTaskResponse], status_code=status.HTTP_201_CREATED)
def create_task(plan_id: int, task_in: PlanTaskCreate, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    task = TaskService.create_task(db, plan_id, task_in)
    return StandardResponse(
        success=True,
        message="Task created successfully",
        data=PlanTaskResponse.model_validate(task)
    )

@router.get("/plans/{plan_id}/tasks", response_model=StandardResponse[List[PlanTaskResponse]])
def get_tasks_by_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    tasks = TaskService.get_tasks_by_plan(db, plan_id)
    return StandardResponse(
        success=True,
        message="Tasks retrieved successfully",
        data=[PlanTaskResponse.model_validate(t) for t in tasks]
    )

@router.put("/tasks/{task_id}", response_model=StandardResponse[PlanTaskResponse])
def update_task(task_id: int, task_in: PlanTaskUpdate, db: Session = Depends(get_db)):
    updated_task = TaskService.update_task(db, task_id, task_in)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Task updated successfully",
        data=PlanTaskResponse.model_validate(updated_task)
    )

@router.delete("/tasks/{task_id}", response_model=StandardResponse[dict])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Task deleted successfully",
        data={"task_id": task_id}
    )
