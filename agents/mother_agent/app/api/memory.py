from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.services.memory_service import add_memory, get_memories, get_item_memory

router = APIRouter(prefix="/api/v1/memory", tags=["Memory Agent"])


@router.post("/add", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(memory: MemoryCreate, db: Session = Depends(get_db)):
    return add_memory(db, memory)


@router.get("/", response_model=list[MemoryResponse])
def read_memories(db: Session = Depends(get_db)):
    return get_memories(db)


@router.get("/{item_name}", response_model=list[MemoryResponse])
def read_item_memory(item_name: str, db: Session = Depends(get_db)):
    memories = get_item_memory(db, item_name)
    if not memories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No memories found for '{item_name}'.")
    return memories
