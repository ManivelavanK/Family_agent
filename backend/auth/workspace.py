import random
import string
import logging
from typing import Optional, Dict
from datetime import datetime

from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger("orchestrator.auth.workspace")

# ── Database Connection ──────────────────────────────────────────────────────

DATABASE_URL = "postgresql://postgres:Mani%402006@localhost:5432/kinnest_auth"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── SQLAlchemy Models ────────────────────────────────────────────────────────

class FamilyWorkspace(Base):
    __tablename__ = "family_workspaces"

    join_code   = Column(String(20), primary_key=True, index=True)
    family_name = Column(String(100), nullable=False)
    house_address = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

class WorkspaceUser(Base):
    __tablename__ = "workspace_users"

    username        = Column(String(50), primary_key=True, index=True)
    email           = Column(String(120), nullable=True, index=True)
    hashed_password = Column(String(256), nullable=False)
    role            = Column(String(30), nullable=False, default="Parent")
    family_id       = Column(String(20), nullable=False)   # References join_code
    created_at      = Column(DateTime, default=datetime.utcnow)

def create_all_tables():
    """Creates all auth tables in the kinnest_auth PostgreSQL database if not exists."""
    Base.metadata.create_all(bind=engine)
    logger.info("KinNest auth tables verified / created in PostgreSQL.")

# ── RBAC Access Matrix ───────────────────────────────────────────────────────

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
    "baby caregiver": {
        "profile": "READ", "shopping": "WRITE", "budget": "NONE", "health": "READ",
        "child": "NONE", "baby": "WRITE", "planner": "NONE"
    },
    "baby": {
        "profile": "READ", "shopping": "NONE", "budget": "NONE", "health": "READ",
        "child": "NONE", "baby": "READ", "planner": "NONE"
    }
}

def has_context_permission(role: str, category: str, action: str) -> bool:
    """Checks the Access Matrix to verify if a user role is permitted READ/WRITE on a category."""
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

# ── Join Code Generator ──────────────────────────────────────────────────────

def _generate_join_code() -> str:
    """Generates a unique 5-character alphanumeric family workspace join code."""
    chars = string.ascii_uppercase + string.digits
    code = "KIN-" + "".join(random.choices(chars, k=5))
    return code

# ── Workspace Operations ─────────────────────────────────────────────────────

def create_workspace(family_name: str, house_address: str, admin_username: str, hashed_pw: str) -> dict:
    """Creates a new family workspace and registers the creator as a Parent (admin)."""
    db: Session = SessionLocal()
    try:
        # Generate a unique join code
        join_code = _generate_join_code()
        while db.query(FamilyWorkspace).filter_by(join_code=join_code).first():
            join_code = _generate_join_code()

        workspace = FamilyWorkspace(
            join_code=join_code,
            family_name=family_name,
            house_address=house_address
        )
        db.add(workspace)

        user = WorkspaceUser(
            username=admin_username,
            hashed_password=hashed_pw,
            role="Parent",
            family_id=join_code
        )
        db.add(user)
        db.commit()

        logger.info(f"Created workspace '{family_name}' with join code {join_code}.")
        return {
            "join_code": join_code,
            "family_name": family_name,
            "username": admin_username,
            "role": "Parent",
            "family_id": join_code
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating workspace: {e}")
        raise
    finally:
        db.close()

def join_workspace(join_code: str, username: str, hashed_pw: str, role: str) -> dict:
    """Joins an existing family workspace using the join code. Validates the workspace exists."""
    db: Session = SessionLocal()
    try:
        workspace = db.query(FamilyWorkspace).filter_by(join_code=join_code.upper()).first()
        if not workspace:
            raise ValueError(f"No workspace found with join code '{join_code}'. Please check the code.")

        existing = db.query(WorkspaceUser).filter_by(username=username).first()
        if existing:
            raise ValueError(f"Username '{username}' is already registered.")

        user = WorkspaceUser(
            username=username,
            hashed_password=hashed_pw,
            role=role,
            family_id=join_code.upper()
        )
        db.add(user)
        db.commit()

        logger.info(f"User '{username}' joined workspace '{workspace.family_name}' as {role}.")
        return {
            "join_code": join_code.upper(),
            "family_name": workspace.family_name,
            "username": username,
            "role": role,
            "family_id": join_code.upper()
        }
    except ValueError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error joining workspace: {e}")
        raise
    finally:
        db.close()

def register_user(username: str, hashed_pw: str, role: str, family_id: str) -> dict:
    """Backward compatible registration that saves directly to PostgreSQL."""
    db: Session = SessionLocal()
    try:
        existing = db.query(WorkspaceUser).filter_by(username=username).first()
        if existing:
            raise ValueError(f"Username '{username}' is already registered.")

        user = WorkspaceUser(
            username=username,
            hashed_password=hashed_pw,
            role=role,
            family_id=family_id
        )
        db.add(user)
        db.commit()
        return {"username": username, "role": role, "family_id": family_id}
    except ValueError:
        raise
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def get_user(identifier: str) -> Optional[dict]:
    """Lookup by username OR email (case-insensitive) to support both login forms."""
    db: Session = SessionLocal()
    try:
        identifier_lower = identifier.lower()
        # Try username first
        user = db.query(WorkspaceUser).filter(
            WorkspaceUser.username == identifier_lower
        ).first()
        # If not found, try stripping email domain (e.g. 'mother@family.com' → 'mother')
        if not user and "@" in identifier_lower:
            username_part = identifier_lower.split("@")[0]
            user = db.query(WorkspaceUser).filter(
                WorkspaceUser.username == username_part
            ).first()
        # Also try email column match
        if not user:
            user = db.query(WorkspaceUser).filter(
                WorkspaceUser.email == identifier_lower
            ).first()
        if user:
            return {
                "username": user.username,
                "hashed_password": user.hashed_password,
                "role": user.role,
                "family_id": user.family_id
            }
        return None
    finally:
        db.close()

def get_workspace(join_code: str) -> Optional[dict]:
    """Fetch workspace details by join code."""
    db: Session = SessionLocal()
    try:
        ws = db.query(FamilyWorkspace).filter_by(join_code=join_code.upper()).first()
        if ws:
            return {"join_code": ws.join_code, "family_name": ws.family_name, "house_address": ws.house_address}
        return None
    finally:
        db.close()
