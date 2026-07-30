import logging
from backend.auth.dependencies import get_current_user, require_roles, verify_context_scope
from backend.auth.workspace import (
    create_all_tables,
    register_user,
    register_basic_user,
    setup_family_workspace,
    connect_to_family,
    get_user,
    create_workspace,
    join_workspace,
)
from backend.auth.jwt import hash_password

logger = logging.getLogger("orchestrator.auth")

# Auto-create PostgreSQL tables on package load
try:
    create_all_tables()
except Exception as e:
    logger.warning(f"Could not create auth tables: {e}")

# Seed default KinNest family accounts into PostgreSQL if they do not already exist
_DEFAULT_USERS = [
    ("mother",      "motherpass",      "Parent",      "default_family"),
    ("father",      "fatherpass",      "Parent",      "default_family"),
    ("child",       "childpass",       "Child",       "default_family"),
    ("grandparent", "grandparentpass", "Grandparent", "default_family"),
    ("system",      "systempass123",   "Parent",      "default_family"),
]

for _username, _password, _role, _family_id in _DEFAULT_USERS:
    try:
        if not get_user(_username):
            register_user(_username, hash_password(_password), _role, _family_id)
            logger.info(f"Seeded default user: {_username} ({_role})")
    except Exception as e:
        logger.debug(f"Skipping seed for {_username}: {e}")
