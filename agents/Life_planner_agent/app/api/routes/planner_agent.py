import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.planner_extensions import (
    GoalCreate, GoalUpdate, GoalResponse,
    HabitCreate, HabitUpdate, HabitResponse, HabitLogCreate, HabitLogResponse,
    DigitalTwinResponse, DigitalTwinUpdate,
    ReminderCreate, ReminderUpdate, ReminderResponse
)
from app.services.planner_services import (
    GoalService, HabitService, DigitalTwinService, ReminderService,
    ConflictDetectionService, RecommendationService, ScheduleService, PlannerService
)

router = APIRouter(prefix="/planner", tags=["Planner Agent"])

class PlannerAgentRequest(BaseModel):
    message: str
    family_id: str = "default_family"

class PlannerAgentResponse(BaseModel):
    ai_response: str
    action_items: List[str]
    execution_trace: Dict[str, Any]

# Core Agent Query Endpoint
@router.post("/agent", response_model=StandardResponse[PlannerAgentResponse])
def run_planner_agent(req: PlannerAgentRequest, db: Session = Depends(get_db)):
    result = PlannerService.process_agent_query(db, req.message, req.family_id)
    return StandardResponse(
        success=True,
        message="Planner agent analysis completed successfully",
        data=result
    )

# Goals Endpoints
@router.post("/goals", response_model=StandardResponse[GoalResponse], status_code=status.HTTP_201_CREATED)
def create_goal(goal_in: GoalCreate, db: Session = Depends(get_db)):
    goal = GoalService.create_goal(db, goal_in)
    return StandardResponse(
        success=True,
        message="Goal created successfully",
        data=GoalResponse.model_validate(goal)
    )

@router.get("/goals", response_model=StandardResponse[List[GoalResponse]])
def get_goals(family_id: str = "default_family", db: Session = Depends(get_db)):
    goals = GoalService.get_goals(db, family_id)
    return StandardResponse(
        success=True,
        message="Goals retrieved successfully",
        data=[GoalResponse.model_validate(g) for g in goals]
    )

@router.put("/goals/{goal_id}", response_model=StandardResponse[GoalResponse])
def update_goal(goal_id: int, goal_in: GoalUpdate, family_id: str = "default_family", db: Session = Depends(get_db)):
    goal = GoalService.update_goal(db, goal_id, goal_in, family_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return StandardResponse(
        success=True,
        message="Goal updated successfully",
        data=GoalResponse.model_validate(goal)
    )

@router.delete("/goals/{goal_id}", response_model=StandardResponse[dict])
def delete_goal(goal_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    success = GoalService.delete_goal(db, goal_id, family_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return StandardResponse(
        success=True,
        message="Goal deleted successfully",
        data={"goal_id": goal_id}
    )

# Habits Endpoints
@router.post("/habits", response_model=StandardResponse[HabitResponse], status_code=status.HTTP_201_CREATED)
def create_habit(habit_in: HabitCreate, db: Session = Depends(get_db)):
    habit = HabitService.create_habit(db, habit_in)
    return StandardResponse(
        success=True,
        message="Habit created successfully",
        data=HabitResponse.model_validate(habit)
    )

@router.get("/habits", response_model=StandardResponse[List[HabitResponse]])
def get_habits(family_id: str = "default_family", db: Session = Depends(get_db)):
    habits = HabitService.get_habits(db, family_id)
    return StandardResponse(
        success=True,
        message="Habits retrieved successfully",
        data=[HabitResponse.model_validate(h) for h in habits]
    )

@router.put("/habits/{habit_id}", response_model=StandardResponse[HabitResponse])
def update_habit(habit_id: int, habit_in: HabitUpdate, family_id: str = "default_family", db: Session = Depends(get_db)):
    habit = HabitService.update_habit(db, habit_id, habit_in, family_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return StandardResponse(
        success=True,
        message="Habit updated successfully",
        data=HabitResponse.model_validate(habit)
    )

@router.post("/habits/{habit_id}/log", response_model=StandardResponse[HabitLogResponse])
def log_habit(habit_id: int, log_in: HabitLogCreate, family_id: str = "default_family", db: Session = Depends(get_db)):
    log = HabitService.log_habit(db, habit_id, log_in, family_id)
    if not log:
        raise HTTPException(status_code=404, detail="Habit not found")
    return StandardResponse(
        success=True,
        message="Habit log updated successfully",
        data=HabitLogResponse.model_validate(log)
    )

@router.delete("/habits/{habit_id}", response_model=StandardResponse[dict])
def delete_habit(habit_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    success = HabitService.delete_habit(db, habit_id, family_id)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    return StandardResponse(
        success=True,
        message="Habit deleted successfully",
        data={"habit_id": habit_id}
    )

# Digital Twin Endpoints
@router.get("/twin", response_model=StandardResponse[DigitalTwinResponse])
def get_digital_twin(family_id: str = "default_family", db: Session = Depends(get_db)):
    twin = DigitalTwinService.calculate_scores(db, family_id)
    return StandardResponse(
        success=True,
        message="Digital twin fetched successfully",
        data=DigitalTwinResponse.model_validate(twin)
    )

# Timeline & Recommendations
@router.get("/timeline")
def get_timeline(family_id: str = "default_family", db: Session = Depends(get_db)):
    timeline = ScheduleService.get_family_timeline(db, family_id)
    health = ScheduleService.get_schedule_health(db, family_id)
    return StandardResponse(
        success=True,
        message="Consolidated family timeline retrieved",
        data={
            "timeline": timeline,
            "schedule_health": health
        }
    )

@router.get("/recommendations")
def get_recommendations(family_id: str = "default_family", db: Session = Depends(get_db)):
    recs = RecommendationService.generate_recommendations(db, family_id)
    return StandardResponse(
        success=True,
        message="Proactive recommendations generated",
        data=recs
    )
