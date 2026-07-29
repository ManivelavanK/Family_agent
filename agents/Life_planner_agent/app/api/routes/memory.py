from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import StandardResponse
from app.schemas.memory import (
    PlannerMemoryCreate, PlannerMemoryUpdate, PlannerMemoryResponse,
    AIMemoryExtractionResponse
)
from app.models.memory import MemoryType
from app.services.memory_service import MemoryService
from app.ai.memory_agent import memory_agent

router = APIRouter(prefix="/memory", tags=["Planner Memory"])

class ExtractMemoryRequest(BaseModel):
    text_content: str = Field(..., min_length=3, description="Text statement or conversation excerpt to analyze")
    family_id: str = Field("default_family", max_length=100)

@router.post("", response_model=StandardResponse[PlannerMemoryResponse], status_code=status.HTTP_201_CREATED)
def create_memory(memory_in: PlannerMemoryCreate, db: Session = Depends(get_db)):
    memory = MemoryService.create_memory(db, memory_in)
    return StandardResponse(
        success=True,
        message="Planner memory created successfully",
        data=PlannerMemoryResponse.model_validate(memory)
    )

@router.get("", response_model=StandardResponse[List[PlannerMemoryResponse]])
def get_memories(
    family_id: str = Query("default_family", description="Family ID filter"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    memories = MemoryService.get_all_memories(db, family_id=family_id, skip=skip, limit=limit)
    return StandardResponse(
        success=True,
        message="Planner memories retrieved successfully",
        data=[PlannerMemoryResponse.model_validate(m) for m in memories]
    )

@router.get("/type/{memory_type}", response_model=StandardResponse[List[PlannerMemoryResponse]])
def get_memories_by_type(
    memory_type: MemoryType,
    family_id: str = Query("default_family", description="Family ID filter"),
    db: Session = Depends(get_db)
):
    memories = MemoryService.get_memories_by_type(db, memory_type=memory_type, family_id=family_id)
    return StandardResponse(
        success=True,
        message=f"Planner memories of type {memory_type.value} retrieved successfully",
        data=[PlannerMemoryResponse.model_validate(m) for m in memories]
    )

@router.post("/extract", response_model=StandardResponse[AIMemoryExtractionResponse])
def extract_memory_ai(req: ExtractMemoryRequest):
    extraction = memory_agent.analyze_for_memories(text_content=req.text_content)
    return StandardResponse(
        success=True,
        message="AI memory extraction analysis completed",
        data=extraction
    )

@router.get("/{memory_id}", response_model=StandardResponse[PlannerMemoryResponse])
def get_memory(
    memory_id: int,
    family_id: str = Query("default_family", description="Family ID filter"),
    db: Session = Depends(get_db)
):
    memory = MemoryService.get_memory_by_id(db, memory_id, family_id=family_id)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planner memory with ID {memory_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Planner memory retrieved successfully",
        data=PlannerMemoryResponse.model_validate(memory)
    )

@router.put("/{memory_id}", response_model=StandardResponse[PlannerMemoryResponse])
def update_memory(
    memory_id: int,
    memory_in: PlannerMemoryUpdate,
    family_id: str = Query("default_family", description="Family ID filter"),
    db: Session = Depends(get_db)
):
    updated_memory = MemoryService.update_memory(db, memory_id, memory_in, family_id=family_id)
    if not updated_memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planner memory with ID {memory_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Planner memory updated successfully",
        data=PlannerMemoryResponse.model_validate(updated_memory)
    )

@router.delete("/{memory_id}", response_model=StandardResponse[dict])
def delete_memory(
    memory_id: int,
    family_id: str = Query("default_family", description="Family ID filter"),
    db: Session = Depends(get_db)
):
    success = MemoryService.delete_memory(db, memory_id, family_id=family_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planner memory with ID {memory_id} not found"
        )
    return StandardResponse(
        success=True,
        message="Planner memory deleted successfully",
        data={"memory_id": memory_id}
    )
