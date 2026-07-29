import logging
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.models import UserClaims
from backend.auth.jwt import decode_access_token
from backend.auth.workspace import has_context_permission

logger = logging.getLogger("orchestrator.auth.dependencies")

# Bearer token HTTP scheme dependency
security = HTTPBearer(auto_error=False)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> UserClaims:
    """FastAPI Dependency: extracts claims from the Bearer token, verifying validity and parsing identity."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Bearer header token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    username = payload.get("sub")
    role = payload.get("role")
    family_id = payload.get("family_id")
    
    if not username or not role or not family_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incomplete authentication token claims.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return UserClaims(username=username, role=role, family_id=family_id)

def require_roles(allowed_roles: List[str]):
    """FastAPI Dependency Factory: restricts access to specific designated user roles."""
    def dependency(current_user: UserClaims = Depends(get_current_user)) -> UserClaims:
        # Match case-insensitive
        role_normalized = current_user.role.lower()
        allowed_normalized = [r.lower() for r in allowed_roles]
        
        if role_normalized not in allowed_normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{current_user.role}' lacks permission for this action."
            )
        return current_user
    return dependency

def verify_context_scope(category: str, action: str):
    """FastAPI Dependency Factory: enforces role-based boundaries on Shared Context categories."""
    def dependency(current_user: UserClaims = Depends(get_current_user)) -> UserClaims:
        if not has_context_permission(current_user.role, category, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: role '{current_user.role}' cannot {action.upper()} shared context category '{category}'."
            )
        return current_user
    return dependency
