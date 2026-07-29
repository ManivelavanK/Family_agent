from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.reflection import PlanReflectionCreate, PlanReflectionResponse
from app.schemas.memory import PlannerMemoryCreate
from app.services.reflection_service import ReflectionService
from app.services.plan_service import PlanService
from app.services.memory_service import MemoryService
from app.ai.memory_agent import memory_agent

router = APIRouter(prefix="/reflections", tags=["Reflections"])

@router.post("", response_model=StandardResponse[PlanReflectionResponse], status_code=status.HTTP_201_CREATED)
def create_reflection(reflection_in: PlanReflectionCreate, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, reflection_in.plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {reflection_in.plan_id} not found"
        )
    reflection = ReflectionService.create_reflection(db, reflection_in)

    # Automatically analyze post-event reflection with AI Memory Agent to store lessons learned
    reflection_text = f"Plan: {plan.title}\nRating: {reflection.rating}\nWhat went well: {reflection.what_went_well}\nWhat went wrong: {reflection.what_went_wrong}\nFeedback: {reflection.feedback}\nFuture suggestions: {reflection.future_suggestions}"
    
    try:
        ai_extraction = memory_agent.analyze_for_memories(
            text_content=reflection_text,
            context_type="PLAN_REFLECTION",
            context_id=plan.id
        )
        if ai_extraction.should_remember:
            for mem_candidate in ai_extraction.memories:
                MemoryService.create_memory(db, PlannerMemoryCreate(
                    family_id="default_family",
                    memory_type=mem_candidate.memory_type,
                    title=mem_candidate.title,
                    content=mem_candidate.content,
                    source_type="PLAN_REFLECTION",
                    source_id=plan.id,
                    importance=mem_candidate.importance
                ))
    except Exception:
        # Non-blocking AI memory extraction fallback
        pass

    return StandardResponse(
        success=True,
        message="Plan reflection saved successfully",
        data=PlanReflectionResponse.model_validate(reflection)
    )

@router.get("/{plan_id}", response_model=StandardResponse[List[PlanReflectionResponse]])
def get_reflections_by_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    reflections = ReflectionService.get_reflections_by_plan(db, plan_id)
    return StandardResponse(
        success=True,
        message="Plan reflections retrieved successfully",
        data=[PlanReflectionResponse.model_validate(r) for r in reflections]
    )
