import logging
from typing import Dict, Optional

logger = logging.getLogger("orchestrator.auth.workspace")

# In-memory mock database of registered users: username -> user details dict
users_db: Dict[str, dict] = {}

# Access Matrix map (Role -> Category -> Permission)
ROLE_CONTEXT_ACCESS: Dict[str, Dict[str, str]] = {
    "parent": {
        "profile": "WRITE", "shopping": "WRITE", "budget": "WRITE", "health": "WRITE",
        "child": "WRITE", "baby": "WRITE", "planner": "WRITE"
    },
    "system": {
        "profile": "WRITE", "shopping": "WRITE", "budget": "WRITE", "health": "WRITE",
        "child": "WRITE", "baby": "WRITE", "planner": "WRITE"
    },
    "grandparent": {
        "profile": "READ", "shopping": "WRITE", "budget": "NONE", "health": "WRITE",
        "child": "READ", "baby": "WRITE", "planner": "WRITE"
    },
    "child": {
        "profile": "READ", "shopping": "WRITE", "budget": "NONE", "health": "READ",
        "child": "WRITE", "baby": "READ", "planner": "WRITE"
    },
    "baby": {
        "profile": "READ", "shopping": "NONE", "budget": "NONE", "health": "READ",
        "child": "NONE", "baby": "READ", "planner": "NONE"
    }
}

def has_context_permission(role: str, category: str, action: str) -> bool:
    """Checks the Access Matrix to verify if a user role is permitted to perform READ or WRITE on a category."""
    role_lower = role.lower()
    cat_lower = category.lower()
    action_upper = action.upper()

    role_permissions = ROLE_CONTEXT_ACCESS.get(role_lower)
    if not role_permissions:
        return False
        
    permission = role_permissions.get(cat_lower, "NONE")
    
    if action_upper == "READ":
        return permission in ["READ", "WRITE"]
    elif action_upper == "WRITE":
        return permission == "WRITE"
        
    return False

def register_user(username: str, hashed_pw: str, role: str, family_id: str) -> dict:
    """Saves user data in-memory."""
    user = {
        "username": username,
        "hashed_password": hashed_pw,
        "role": role,
        "family_id": family_id
    }
    users_db[username] = user
    return user

def get_user(username: str) -> Optional[dict]:
    return users_db.get(username)
