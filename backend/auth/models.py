from typing import Optional
from pydantic import BaseModel, Field

# ── Login / Register ─────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field("Parent", description="User Role (Parent, Grandparent, Child, Baby, System).")
    family_id: str = Field("default_family", description="Partition workspace family ID.")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email address.")
    password: str = Field(...)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    family_id: str = ""
    role: str = ""
    username: str = ""

class UserClaims(BaseModel):
    username: str
    role: str
    family_id: str

# ── Workspace Create / Join ──────────────────────────────────────────────────

class CreateWorkspaceRequest(BaseModel):
    family_name: str = Field(..., min_length=2, max_length=100, description="Your family name, e.g. 'The Smiths'.")
    house_address: str = Field(..., min_length=5, description="Home address.")
    admin_username: str = Field(..., min_length=3, max_length=50, description="Admin account username.")
    admin_password: str = Field(..., min_length=6, description="Admin account password.")

class JoinWorkspaceRequest(BaseModel):
    join_code: str = Field(..., description="Family workspace join code, e.g. KIN-ABCDE.")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field("Child", description="Your role in the family.")

class WorkspaceResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    family_id: str
    family_name: str
    join_code: str
    role: str
    username: str
