from pydantic import BaseModel


class MemoryCreate(BaseModel):

    user_role: str = "family"

    memory_type: str

    item_name: str | None = None

    memory_value: str



class MemoryResponse(BaseModel):

    id: int

    user_role: str

    memory_type: str

    item_name: str | None

    memory_value: str


    class Config:
        from_attributes = True