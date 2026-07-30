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

    join_code           = Column(String(20), primary_key=True, index=True)
    family_name         = Column(String(100), nullable=False)
    house_address       = Column(Text, nullable=True)
    member_count        = Column(String(10), nullable=True)
    children_ages       = Column(Text, nullable=True)        # comma-separated ages
    special_needs       = Column(Text, nullable=True)
    family_password_hash= Column(String(256), nullable=True) # shared family password
    created_at          = Column(DateTime, default=datetime.utcnow)

class WorkspaceUser(Base):
    __tablename__ = "workspace_users"

    username        = Column(String(120), primary_key=True, index=True)  # email used as username
    email           = Column(String(120), nullable=True, index=True)
    hashed_password = Column(String(256), nullable=False)
    role            = Column(String(30), nullable=False, default="Pending")
    family_id       = Column(String(20), nullable=True)      # NULL until connected to a family
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
    },
    "pending": {
        "profile": "NONE", "shopping": "NONE", "budget": "NONE", "health": "NONE",
        "child": "NONE", "baby": "NONE", "planner": "NONE"
    },
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

# ── Basic User Registration (step 1: email + password, no role yet) ──────────

def register_basic_user(email: str, hashed_pw: str) -> dict:
    """Registers a new user with just email + password. No role or family assigned yet."""
    db: Session = SessionLocal()
    try:
        email_lower = email.lower().strip()
        existing = db.query(WorkspaceUser).filter(
            (WorkspaceUser.username == email_lower) | (WorkspaceUser.email == email_lower)
        ).first()
        if existing:
            raise ValueError("An account with this email already exists.")
        user = WorkspaceUser(
            username=email_lower,
            email=email_lower,
            hashed_password=hashed_pw,
            role="Pending",
            family_id=None
        )
        db.add(user)
        db.commit()
        logger.info(f"Registered new user: {email_lower}")
        return {"username": email_lower, "email": email_lower, "role": "Pending", "family_id": None}
    except ValueError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise
    finally:
        db.close()

# ── Family Setup (step 2: creator sets up family + family password) ───────────

def setup_family_workspace(
    creator_email: str,
    role: str,
    family_name: str,
    house_address: str,
    member_count: str,
    children_ages: str,
    special_needs: str,
    family_password_hash: str
) -> dict:
    """Creator sets up a family workspace and is assigned their chosen role."""
    db: Session = SessionLocal()
    try:
        email_lower = creator_email.lower().strip()
        user = db.query(WorkspaceUser).filter(
            (WorkspaceUser.username == email_lower) | (WorkspaceUser.email == email_lower)
        ).first()
        if not user:
            raise ValueError("User account not found. Please register first.")
        if user.family_id:
            raise ValueError("You are already connected to a family workspace.")

        # Generate unique join code
        join_code = _generate_join_code()
        while db.query(FamilyWorkspace).filter_by(join_code=join_code).first():
            join_code = _generate_join_code()

        workspace = FamilyWorkspace(
            join_code=join_code,
            family_name=family_name,
            house_address=house_address,
            member_count=member_count,
            children_ages=children_ages,
            special_needs=special_needs,
            family_password_hash=family_password_hash
        )
        db.add(workspace)

        # Assign role and family to the creator
        user.role = role
        user.family_id = join_code
        db.commit()

        logger.info(f"Family '{family_name}' set up by {email_lower} as {role}. Join code: {join_code}")
        return {
            "username": user.username,
            "email": user.email,
            "role": role,
            "family_id": join_code,
            "family_name": family_name,
            "join_code": join_code
        }
    except ValueError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting up family workspace: {e}")
        raise
    finally:
        db.close()

# ── Family Connect (step 2 alt: member joins using family password + role) ────

def connect_to_family(email: str, role: str, family_password: str) -> dict:
    """Connects an existing user to a family workspace using the shared family password."""
    db: Session = SessionLocal()
    try:
        from backend.auth.jwt import verify_password as vp
        email_lower = email.lower().strip()
        user = db.query(WorkspaceUser).filter(
            (WorkspaceUser.username == email_lower) | (WorkspaceUser.email == email_lower)
        ).first()
        if not user:
            raise ValueError("User account not found. Please register first.")
        if user.family_id:
            raise ValueError("You are already connected to a family workspace.")

        # Find the workspace matching the family password
        workspaces = db.query(FamilyWorkspace).all()
        matched_workspace = None
        for ws in workspaces:
            if ws.family_password_hash and vp(family_password, ws.family_password_hash):
                matched_workspace = ws
                break

        if not matched_workspace:
            raise ValueError("Incorrect family password. Ask your family admin for the correct password.")

        # Assign role and family
        user.role = role
        user.family_id = matched_workspace.join_code
        db.commit()

        logger.info(f"User {email_lower} connected to family '{matched_workspace.family_name}' as {role}.")
        return {
            "username": user.username,
            "email": user.email,
            "role": role,
            "family_id": matched_workspace.join_code,
            "family_name": matched_workspace.family_name,
            "join_code": matched_workspace.join_code
        }
    except ValueError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error connecting to family: {e}")
        raise
    finally:
        db.close()

# ── Legacy Workspace Operations (kept for backward compatibility) ─────────────

def create_workspace(family_name: str, house_address: str, admin_username: str, hashed_pw: str) -> dict:
    """Legacy: Creates a new family workspace and registers creator as Parent admin."""
    db: Session = SessionLocal()
    try:
        join_code = _generate_join_code()
        while db.query(FamilyWorkspace).filter_by(join_code=join_code).first():
            join_code = _generate_join_code()
        workspace = FamilyWorkspace(join_code=join_code, family_name=family_name, house_address=house_address)
        db.add(workspace)
        user = WorkspaceUser(username=admin_username, hashed_password=hashed_pw, role="Parent", family_id=join_code)
        db.add(user)
        db.commit()
        return {"join_code": join_code, "family_name": family_name, "username": admin_username, "role": "Parent", "family_id": join_code}
    except Exception as e:
        db.rollback(); raise
    finally:
        db.close()

def join_workspace(join_code: str, username: str, hashed_pw: str, role: str) -> dict:
    """Legacy: Joins existing workspace via join code."""
    db: Session = SessionLocal()
    try:
        workspace = db.query(FamilyWorkspace).filter_by(join_code=join_code.upper()).first()
        if not workspace:
            raise ValueError(f"No workspace found with join code '{join_code}'.")
        existing = db.query(WorkspaceUser).filter_by(username=username).first()
        if existing:
            raise ValueError(f"Username '{username}' is already registered.")
        user = WorkspaceUser(username=username, hashed_password=hashed_pw, role=role, family_id=join_code.upper())
        db.add(user)
        db.commit()
        return {"join_code": join_code.upper(), "family_name": workspace.family_name, "username": username, "role": role, "family_id": join_code.upper()}
    except ValueError:
        raise
    except Exception as e:
        db.rollback(); raise
    finally:
        db.close()

def register_user(username: str, hashed_pw: str, role: str, family_id: str) -> dict:
    """Legacy: Saves a user directly to PostgreSQL with known role and family_id."""
    db: Session = SessionLocal()
    try:
        existing = db.query(WorkspaceUser).filter_by(username=username).first()
        if existing:
            raise ValueError(f"Username '{username}' is already registered.")
        user = WorkspaceUser(username=username, hashed_password=hashed_pw, role=role, family_id=family_id)
        db.add(user)
        db.commit()
        return {"username": username, "role": role, "family_id": family_id}
    except ValueError:
        raise
    except Exception as e:
        db.rollback(); raise
    finally:
        db.close()

def get_user(identifier: str) -> Optional[dict]:
    """Lookup by username OR email (case-insensitive)."""
    db: Session = SessionLocal()
    try:
        identifier_lower = identifier.lower().strip()
        user = db.query(WorkspaceUser).filter(WorkspaceUser.username == identifier_lower).first()
        if not user and "@" in identifier_lower:
            username_part = identifier_lower.split("@")[0]
            user = db.query(WorkspaceUser).filter(WorkspaceUser.username == username_part).first()
        if not user:
            user = db.query(WorkspaceUser).filter(WorkspaceUser.email == identifier_lower).first()
        if user:
            return {
                "username": user.username,
                "email": user.email,
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
