from typing import Optional, List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.ai.schemas import (
    AIPlanningResponse, AICalendarReasoningRequest, AICalendarReasoningResponse,
    AIPlanExecutionRequest, AIPlanExecutionSummary,
    AIPlanRevisionRequest, AIPlanRevisionResponse,
    AIPlanOptimizeRequest, AIPlanOptimizeResponse,
    AIPlanQualityAnalysisResponse,
    AIProactiveAnalysisRequest, AIProactiveAnalysisResponse,
    AIGuestPlanningRequest, AIGuestPlanningResponse,
    AITravelPlan, AITravelPlanningRequest, AITravelPlanningResponse,
    AITravelReviseRequest, AITravelOptimizeRequest,
    AITravelQualityAnalysisResponse,
    AIRoutinePlanningRequest, AIRoutinePlanningResponse
)
from app.communication.supervisor_schemas import (
    SupervisorRequest, SupervisorResponse, AgentHealthStatus
)
from app.ai.planner_agent import planner_agent
from app.ai.calendar_reasoner import calendar_reasoner
from app.ai.executor_agent import executor_agent
from app.ai.proactive_agent import proactive_agent
from app.ai.guest_agent import guest_agent
from app.ai.travel_agent import travel_agent
from app.ai.routine_agent import routine_agent
from app.ai.supervisor_agent import supervisor_agent
from app.services.plan_execution_service import PlanExecutionService

router = APIRouter(prefix="/ai", tags=["AI Planner"])

class AIPlanRequest(BaseModel):
    message: str = Field(..., min_length=3, description="Natural language planning request")
    plan_id: Optional[int] = Field(None, description="Optional existing plan ID to update or attach context to")

@router.post("/plan", response_model=StandardResponse[AIPlanningResponse], status_code=status.HTTP_200_OK)
def analyze_and_plan(request: AIPlanRequest, db: Session = Depends(get_db)):
    ai_result = planner_agent.process_planning_request(
        db=db,
        message=request.message,
        plan_id=request.plan_id
    )
    return StandardResponse(
        success=True,
        message="AI planning analysis completed successfully",
        data=ai_result
    )

@router.post("/plan/execute", response_model=StandardResponse[AIPlanExecutionSummary], status_code=status.HTTP_201_CREATED)
def execute_plan(request: AIPlanExecutionRequest, db: Session = Depends(get_db)):
    execution_result = PlanExecutionService.execute_approved_plan(
        db=db,
        family_id=request.family_id,
        draft_plan=request.draft_plan,
        approved=request.approved
    )
    return StandardResponse(
        success=True,
        message="Approved plan executed successfully",
        data=execution_result
    )

@router.post("/plan/revise", response_model=StandardResponse[AIPlanRevisionResponse], status_code=status.HTTP_200_OK)
def revise_plan(request: AIPlanRevisionRequest, db: Session = Depends(get_db)):
    revision_result = executor_agent.revise_plan(
        db=db,
        plan_id=request.plan_id,
        message=request.message,
        family_id=request.family_id
    )
    return StandardResponse(
        success=True,
        message="AI plan revision completed successfully",
        data=revision_result
    )

@router.post("/plan/optimize", response_model=StandardResponse[AIPlanOptimizeResponse], status_code=status.HTTP_200_OK)
def optimize_plan(request: AIPlanOptimizeRequest, db: Session = Depends(get_db)):
    optimization_result = executor_agent.optimize_plan(
        db=db,
        plan_id=request.plan_id,
        goal=request.optimization_goal,
        family_id=request.family_id
    )
    return StandardResponse(
        success=True,
        message="AI plan optimization completed successfully",
        data=optimization_result
    )

@router.post("/plan/analyze/{plan_id}", response_model=StandardResponse[AIPlanQualityAnalysisResponse], status_code=status.HTTP_200_OK)
def analyze_plan_quality(plan_id: int, family_id: str = "default_family", db: Session = Depends(get_db)):
    analysis_result = executor_agent.analyze_plan_quality(
        db=db,
        plan_id=plan_id,
        family_id=family_id
    )
    return StandardResponse(
        success=True,
        message="AI plan quality analysis completed successfully",
        data=analysis_result
    )

@router.post("/proactive/analyze", response_model=StandardResponse[AIProactiveAnalysisResponse], status_code=status.HTTP_200_OK)
def analyze_proactive(request: AIProactiveAnalysisRequest, db: Session = Depends(get_db)):
    proactive_result = proactive_agent.analyze_proactive_context(
        db=db,
        family_id=request.family_id,
        lookahead_days=request.lookahead_days
    )
    return StandardResponse(
        success=True,
        message="AI proactive analysis completed successfully",
        data=proactive_result
    )

@router.post("/guest/plan", response_model=StandardResponse[AIGuestPlanningResponse], status_code=status.HTTP_200_OK)
def plan_guest_visit(request: AIGuestPlanningRequest, db: Session = Depends(get_db)):
    guest_result = guest_agent.plan_guest_visit(
        db=db,
        message=request.message,
        family_id=request.family_id,
        guest_id=request.guest_id
    )
    return StandardResponse(
        success=True,
        message="AI guest visit planning completed successfully",
        data=guest_result
    )

@router.post("/travel/plan", response_model=StandardResponse[AITravelPlanningResponse], status_code=status.HTTP_200_OK)
def plan_travel_trip(request: AITravelPlanningRequest, db: Session = Depends(get_db)):
    travel_result = travel_agent.plan_travel_visit(
        db=db,
        message=request.message,
        family_id=request.family_id,
        start_date=request.start_date,
        end_date=request.end_date
    )
    return StandardResponse(
        success=True,
        message="AI travel planning completed successfully",
        data=travel_result
    )

@router.post("/travel/revise", response_model=StandardResponse[AITravelPlanningResponse], status_code=status.HTTP_200_OK)
def revise_travel_trip(request: AITravelReviseRequest, db: Session = Depends(get_db)):
    revised_result = travel_agent.revise_travel_plan(
        db=db,
        message=request.message,
        current_travel_plan=request.current_travel_plan,
        family_id=request.family_id
    )
    return StandardResponse(
        success=True,
        message="AI travel plan revision completed successfully",
        data=revised_result
    )

@router.post("/travel/optimize", response_model=StandardResponse[AITravelPlanningResponse], status_code=status.HTTP_200_OK)
def optimize_travel_trip(request: AITravelOptimizeRequest, db: Session = Depends(get_db)):
    optimized_result = travel_agent.optimize_travel_plan(
        db=db,
        message=request.message,
        current_travel_plan=request.current_travel_plan,
        family_id=request.family_id
    )
    return StandardResponse(
        success=True,
        message="AI travel plan optimization completed successfully",
        data=optimized_result
    )

@router.post("/travel/analyze", response_model=StandardResponse[AITravelQualityAnalysisResponse], status_code=status.HTTP_200_OK)
def analyze_travel_trip(travel_plan: AITravelPlan, family_id: str = "default_family", db: Session = Depends(get_db)):
    analysis_result = travel_agent.analyze_travel_quality(
        db=db,
        current_travel_plan=travel_plan,
        family_id=family_id
    )
    return StandardResponse(
        success=True,
        message="AI travel quality analysis completed successfully",
        data=analysis_result
    )

@router.post("/routine/plan", response_model=StandardResponse[AIRoutinePlanningResponse], status_code=status.HTTP_200_OK)
def plan_daily_routine(request: AIRoutinePlanningRequest, db: Session = Depends(get_db)):
    routine_result = routine_agent.plan_routine(
        db=db,
        message=request.message,
        family_id=request.family_id,
        target_date=request.target_date
    )
    return StandardResponse(
        success=True,
        message="AI family routine planning completed successfully",
        data=routine_result
    )

@router.post("/supervisor", response_model=StandardResponse[SupervisorResponse], status_code=status.HTTP_200_OK)
async def supervisor_process(request: SupervisorRequest, db: Session = Depends(get_db)):
    response = await supervisor_agent.process_request_async(db=db, request=request)
    return StandardResponse(
        success=True,
        message="KinNest supervisor analysis completed",
        data=response
    )

@router.get("/supervisor/agents", response_model=StandardResponse[List[AgentHealthStatus]], status_code=status.HTTP_200_OK)
async def supervisor_agents_health(family_id: str = "default_family"):
    health_list = await supervisor_agent.get_agents_health_async(family_id=family_id)
    return StandardResponse(
        success=True,
        message="Retrieved family agent status successfully",
        data=health_list
    )

@router.post("/calendar/reason", response_model=StandardResponse[AICalendarReasoningResponse], status_code=status.HTTP_200_OK)
def reason_calendar(request: AICalendarReasoningRequest, db: Session = Depends(get_db)):
    reasoning_result = calendar_reasoner.reason_schedule(
        db=db,
        req=request
    )
    return StandardResponse(
        success=True,
        message="AI calendar reasoning completed successfully",
        data=reasoning_result
    )
