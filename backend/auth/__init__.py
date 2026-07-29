from backend.auth.dependencies import get_current_user, require_roles, verify_context_scope
from backend.auth.workspace import register_user, get_user
from backend.auth.jwt import hash_password

# Seed default mock family partition accounts on package load
try:
    # 1. System Admin Account
    register_user(
        username="system",
        hashed_pw=hash_password("systempass123"),
        role="Parent",
        family_id="default_family"
    )
    # 2. Mother Account
    register_user(
        username="mother",
        hashed_pw=hash_password("motherpass"),
        role="Parent",
        family_id="default_family"
    )
    # 3. Father Account
    register_user(
        username="father",
        hashed_pw=hash_password("fatherpass"),
        role="Parent",
        family_id="default_family"
    )
    # 4. Child Account
    register_user(
        username="child",
        hashed_pw=hash_password("childpass"),
        role="Child",
        family_id="default_family"
    )
    # 5. Grandparent Account
    register_user(
        username="grandparent",
        hashed_pw=hash_password("grandparentpass"),
        role="Grandparent",
        family_id="default_family"
    )
except Exception:
    pass
