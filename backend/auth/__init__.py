from backend.auth.dependencies import get_current_user, require_roles, verify_context_scope
from backend.auth.workspace import (
    create_all_tables,
    register_user,
    get_user,
    create_workspace,
    join_workspace,
)
from backend.auth.jwt import hash_password

# Auto-create PostgreSQL tables on package load
try:
    create_all_tables()
except Exception as e:
    import logging
    logging.getLogger("orchestrator.auth").warning(f"Could not create auth tables: {e}")
