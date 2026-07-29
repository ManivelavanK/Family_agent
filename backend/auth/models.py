from typing import Optional
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field("Parent", description="User Role (Parent, Grandparent, Child, Baby, System).")
    family_id: str = Field("default_family", description="Partition workspace family ID.")

class LoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserClaims(BaseModel):
    username: str
    role: str
    family_id: str
