import os
import sys
import time
import httpx
import logging
import asyncio
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the Agent Registry and Shared Context components
from backend.registry import registry, registry_heartbeat_loop, Agent
from backend.context import context_manager, context_ttl_cleanup_worker
from backend.context.models import ContextWrapper

# Import the Workflow Engine components
from backend.workflow import workflow_engine, workflow_background_worker
from backend.workflow.registry import registry as workflow_registry
from backend.workflow.models import WorkflowInstance

# Import the Event Router components
from backend.event_router import event_dispatcher, event_history, event_router_background_worker
from backend.event_router.models import Event, RoutingRecord

# Import the Task Scheduler components
from backend.scheduler import scheduler, scheduler_worker
from backend.scheduler.models import ScheduledTask

# Import the Authentication and Workspace Manager components
from backend.auth import get_current_user, require_roles, verify_context_scope, get_user, register_user, create_workspace, join_workspace
from backend.auth.models import RegisterRequest, LoginRequest, TokenResponse, UserClaims, CreateWorkspaceRequest, JoinWorkspaceRequest, WorkspaceResponse
from backend.auth.jwt import create_access_token, verify_password, hash_password, decode_access_token

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] orchestrator: %(message)s"
)
logger = logging.getLogger("orchestrator")

# Agent configs for starting subprocesses
AGENT_STARTUP_CONFIGS = {
    "mother": {"dir": "agents/mother_agent"},
    "father": {"dir": "agents/father_agent/finance-agent"}, # Mocked inside orchestrator if empty
    "children": {"dir": "agents/child_agent"},
    "grandparent": {"dir": "agents/grandparent_agent"},
    "baby": {"dir": "agents/Babychild_agent"},
    "planner": {"dir": "agents/Life_planner_agent"},
}

processes: List[subprocess.Popen] = []

def run_agent_service(name: str, config: dict, port: int):
    """Starts an agent service as a subprocess using its virtualenv if present."""
    agent_dir = os.path.abspath(config["dir"])
    
    # If the directory doesn't exist or is empty (like father agent)
    if not os.path.exists(agent_dir) or not os.listdir(agent_dir):
        if name == "father":
            logger.info(f"Father Agent directory is empty. Running mock Father Agent on port {port} inside orchestrator.")
            return None
        logger.warning(f"Directory for {name} agent does not exist or is empty: {agent_dir}")
        return None

    # Check for virtualenv python
    venv_python = os.path.join(agent_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = os.path.join(agent_dir, "venv", "bin", "python")
        
    python_exec = venv_python if os.path.exists(venv_python) else sys.executable
    
    logger.info(f"Starting {name} agent on port {port} using {python_exec}...")
    
    cmd = [
        python_exec, "-m", "uvicorn", "app.main:app",
        "--host", "127.0.0.1",
        "--port", str(port)
    ]
    
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=agent_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return proc
    except Exception as e:
        logger.error(f"Failed to start {name} agent: {e}")
        return None

# ── Mock Father Agent Server (Port 8002) ────────────────────────────────────
father_mock_app = FastAPI(
    title="KinNest — Father Agent (Mock)",
    description="Mocked Father Agent to answer peer-agent requests.",
    version="1.0.0"
)

class AgentMessageType(str):
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    RESPONSE_APPROVAL = "RESPONSE_APPROVAL"
    NOTIFY_EVENT = "NOTIFY_EVENT"
    QUERY_STATE = "QUERY_STATE"
    STATE_RESPONSE = "STATE_RESPONSE"

class InterAgentMessage(BaseModel):
    protocol: str = "KinNest-Agent-v1"
    message_id: str
    sender_agent: str
    target_agent: str
    message_type: str
    urgency: str = "MEDIUM"
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

@father_mock_app.post("/api/v1/agent-bus/message")
def handle_mock_father_message(msg: InterAgentMessage):
    logger.info(f"[Mock Father] Received message {msg.message_id} from {msg.sender_agent} (Type: {msg.message_type})")
    
    if msg.message_type == AgentMessageType.QUERY_STATE:
        return {
            "success": True,
            "responding_agent": "father_agent",
            "reply_to_id": msg.message_id,
            "data": {
                "status": "active",
                "domain": "finance_decisions",
                "safe_to_spend_balance": 15000.0,
                "pending_approvals": 0
            }
        }
    elif msg.message_type == AgentMessageType.REQUEST_APPROVAL:
        return {
            "success": True,
            "responding_agent": "father_agent",
            "reply_to_id": msg.message_id,
            "data": {
                "approval_status": "APPROVED",
                "notes": "Automatically approved by mock rules engine based on family budget limits."
            }
        }
    else:
        return {
            "success": True,
            "responding_agent": "father_agent",
            "reply_to_id": msg.message_id,
            "data": {"acknowledged": True, "notes": "Processed by Father Agent digital twin."}
        }

@father_mock_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def catch_all_father_mock(path: str, request: Request):
    """Fallback handler for any CRUD queries to the mock father agent."""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": f"Father Agent is running in Mock Mode. Endpoint '{path}' acknowledged.",
            "data": {}
        }
    )

# ── App factory and Lifespan ────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start all agent subprocesses using ports defined in registry
    for name, agent in registry.agents.items():
        config = AGENT_STARTUP_CONFIGS.get(name)
        if config:
            proc = run_agent_service(name, config, agent.port)
            if proc:
                processes.append(proc)
            
    # Start the Father Agent mock server in the background using uvicorn
    import uvicorn
    father_config = uvicorn.Config(father_mock_app, host="127.0.0.1", port=8002, log_level="warning")
    father_server = uvicorn.Server(father_config)
    asyncio.create_task(father_server.serve())
    logger.info("Mock Father Agent started on port 8002.")
    
    # Start the Agent Registry health poller loop
    asyncio.create_task(registry_heartbeat_loop())
    
    # Start the Context Manager TTL cleanup loop
    asyncio.create_task(context_ttl_cleanup_worker())
    
    # Start the Workflow Engine periodic worker loop
    asyncio.create_task(workflow_background_worker())
    
    # Start the Event Router background worker loop
    asyncio.create_task(event_router_background_worker())
    
    # Start the Task Scheduler queue worker loop
    asyncio.create_task(scheduler_worker.start())
    
    yield
    
    # Shutdown: Stop all processes
    logger.info("Stopping all agent processes...")
    for proc in processes:
        proc.terminate()
        try:
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.kill()
    logger.info("All agent processes terminated.")

app = FastAPI(
    title="KinNest — Multi-Agent Orchestrator Gateway",
    description="Central gateway routing, Dynamic Agent Registry, Shared Context, Workflow Engine, Event Router, Priority Task Scheduler, and Family Workspace Manager for KinNest family agents.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Authentication & Registration Endpoints ─────────────────────────────────

@app.post("/orchestrator/auth/register", response_model=TokenResponse, tags=["Family Workspace Auth"])
def register_workspace_user(req: RegisterRequest):
    """Backward-compatible registration: binds a user to a family partition workspace and returns a JWT token."""
    existing = get_user(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered.")
    try:
        hashed = hash_password(req.password)
        user = register_user(req.username, hashed, req.role, req.family_id)
        token = create_access_token({"sub": user["username"], "role": user["role"], "family_id": user["family_id"]})
        return {"access_token": token, "token_type": "bearer", "family_id": user["family_id"], "role": user["role"], "username": user["username"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orchestrator/auth/login", response_model=TokenResponse, tags=["Family Workspace Auth"])
def login_workspace_user(req: LoginRequest):
    """Authenticates credentials (username OR email) and returns a JWT access token with family claims."""
    user = get_user(req.username)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token({"sub": user["username"], "role": user["role"], "family_id": user["family_id"]})
    return {"access_token": token, "token_type": "bearer", "family_id": user["family_id"], "role": user["role"], "username": user["username"]}

@app.post("/orchestrator/auth/workspace/create", response_model=WorkspaceResponse, tags=["Family Workspace Auth"])
def create_family_workspace(req: CreateWorkspaceRequest):
    """Creates a new family workspace with a unique join code and registers the creator as a Parent admin."""
    existing = get_user(req.admin_username)
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{req.admin_username}' is already taken.")
    try:
        hashed = hash_password(req.admin_password)
        result = create_workspace(
            family_name=req.family_name,
            house_address=req.house_address,
            admin_username=req.admin_username,
            hashed_pw=hashed
        )
        token = create_access_token({"sub": result["username"], "role": result["role"], "family_id": result["family_id"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "family_id": result["family_id"],
            "family_name": result["family_name"],
            "join_code": result["join_code"],
            "role": result["role"],
            "username": result["username"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orchestrator/auth/workspace/join", response_model=WorkspaceResponse, tags=["Family Workspace Auth"])
def join_family_workspace(req: JoinWorkspaceRequest):
    """Joins an existing family workspace using the join code, registering as a new member with specified role."""
    try:
        hashed = hash_password(req.password)
        result = join_workspace(
            join_code=req.join_code,
            username=req.username,
            hashed_pw=hashed,
            role=req.role
        )
        token = create_access_token({"sub": result["username"], "role": result["role"], "family_id": result["family_id"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "family_id": result["family_id"],
            "family_name": result["family_name"],
            "join_code": result["join_code"],
            "role": result["role"],
            "username": result["username"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ── Registry API Endpoints ──────────────────────────────────────────────────

@app.get("/orchestrator/agents", response_model=List[Agent], tags=["Orchestrator Registry"])
def get_agents(current_user: UserClaims = Depends(get_current_user)):
    """Retrieve all registered agents and their current statuses/metadata."""
    return registry.get_all_agents()

@app.get("/orchestrator/agents/{agent_name}", response_model=Agent, tags=["Orchestrator Registry"])
def get_agent_details(agent_name: str, current_user: UserClaims = Depends(get_current_user)):
    """Retrieve detailed metadata, capabilities, and health status for a specific agent."""
    agent = registry.get_agent(agent_name.lower())
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found in registry.")
    return agent

@app.get("/orchestrator/status", tags=["Orchestrator Registry"])
def get_orchestrator_status(current_user: UserClaims = Depends(get_current_user)):
    """Overall status of the orchestrator gateway, summary of online agents, and metrics."""
    agents = registry.get_all_agents()
    online_count = sum(1 for a in agents if a.status == "ONLINE")
    total_requests = sum(a.request_count for a in agents)
    
    return {
        "status": "ONLINE",
        "total_agents": len(agents),
        "online_agents": online_count,
        "offline_agents": len(agents) - online_count,
        "total_proxied_requests": total_requests,
        "system_time": datetime.now(timezone.utc).isoformat()
    }

# ── Shared Context Manager API Endpoints ────────────────────────────────────

@app.get("/orchestrator/context", tags=["Shared Context"])
async def get_complete_context(current_user: UserClaims = Depends(get_current_user)):
    """Returns the complete shared context containing all categories and metadata."""
    categories = ["profile", "shopping", "budget", "health", "child", "baby", "planner"]
    complete_context = {}
    for cat in categories:
        wrapper = await context_manager.get_wrapper(cat)
        complete_context[cat] = wrapper.model_dump()
    return complete_context

@app.get("/orchestrator/context/{category}", tags=["Shared Context"])
async def get_category_context(category: str, metadata: bool = False, current_user: UserClaims = Depends(get_current_user)):
    """Returns the context data for a category. Enforces Role-Based Access Control (RBAC)."""
    # Enforce RBAC Dependency
    from backend.auth.workspace import has_context_permission
    if not has_context_permission(current_user.role, category, "READ"):
        raise HTTPException(status_code=403, detail=f"Forbidden: role '{current_user.role}' cannot READ category '{category}'.")
        
    try:
        wrapper = await context_manager.get_wrapper(category.lower())
        if metadata:
            return wrapper
        return wrapper.data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orchestrator/context/{category}", tags=["Shared Context"])
async def replace_category_context(category: str, request: Request, ttl_seconds: Optional[float] = None, current_user: UserClaims = Depends(get_current_user)):
    """Create or fully replace one category context. Enforces RBAC boundary guards."""
    from backend.auth.workspace import has_context_permission
    if not has_context_permission(current_user.role, category, "WRITE"):
        raise HTTPException(status_code=403, detail=f"Forbidden: role '{current_user.role}' cannot WRITE category '{category}'.")
        
    try:
        body = await request.json()
        wrapper = await context_manager.update_context(
            category=category.lower(),
            data=body,
            updated_by=current_user.username,
            ttl_seconds=ttl_seconds
        )
        return {"success": True, "wrapper": wrapper}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replace context: {e}")

@app.patch("/orchestrator/context/{category}", tags=["Shared Context"])
async def patch_category_context(category: str, request: Request, current_user: UserClaims = Depends(get_current_user)):
    """Partially update fields in a category context. Enforces RBAC boundary guards."""
    from backend.auth.workspace import has_context_permission
    if not has_context_permission(current_user.role, category, "WRITE"):
        raise HTTPException(status_code=403, detail=f"Forbidden: role '{current_user.role}' cannot WRITE category '{category}'.")
        
    try:
        body = await request.json()
        wrapper = await context_manager.patch_context(
            category=category.lower(),
            partial_data=body,
            updated_by=current_user.username
        )
        return {"success": True, "wrapper": wrapper}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to patch context: {e}")

@app.delete("/orchestrator/context/{category}", tags=["Shared Context"])
async def clear_category_context(category: str, current_user: UserClaims = Depends(get_current_user)):
    """Reset a category context back to its empty default schema. Enforces RBAC write guards."""
    from backend.auth.workspace import has_context_permission
    if not has_context_permission(current_user.role, category, "WRITE"):
        raise HTTPException(status_code=403, detail=f"Forbidden: role '{current_user.role}' cannot WRITE category '{category}'.")
        
    try:
        await context_manager.delete_context(category.lower(), current_user.username)
        return {"success": True, "message": f"Category '{category}' context cleared."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ── Workflow Engine API Endpoints ───────────────────────────────────────────

class TriggerWorkflowRequest(BaseModel):
    name: str = Field(..., description="The name of the workflow definition (blueprint) to trigger.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Custom input data passed to the workflow context.")

@app.get("/orchestrator/workflows", response_model=List[WorkflowInstance], tags=["Workflow Engine"])
def get_workflows(current_user: UserClaims = Depends(get_current_user)):
    """Retrieve all running, completed, or failed workflow instances."""
    return workflow_registry.get_all_instances()

@app.get("/orchestrator/workflows/{workflow_id}", response_model=WorkflowInstance, tags=["Workflow Engine"])
def get_workflow_details(workflow_id: str, current_user: UserClaims = Depends(get_current_user)):
    """Retrieve execution states, variables, and sequential audit logs for one workflow instance."""
    instance = workflow_registry.get_instance(workflow_id)
    if not instance:
        raise HTTPException(status_code=404, detail=f"Workflow instance '{workflow_id}' not found.")
    return instance

@app.post("/orchestrator/workflows", response_model=WorkflowInstance, tags=["Workflow Engine"])
async def trigger_workflow(req: TriggerWorkflowRequest, current_user: UserClaims = Depends(get_current_user)):
    """Trigger a new definition-driven business workflow instance asynchronously."""
    try:
        # Inject family_id claim in payload partition context
        payload = req.payload.copy()
        payload["family_id"] = current_user.family_id
        payload["priority"] = payload.get("priority", "NORMAL")
        
        instance = await workflow_engine.trigger_workflow(req.name, payload)
        return instance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger workflow: {e}")

@app.delete("/orchestrator/workflows/{workflow_id}", tags=["Workflow Engine"])
def cancel_workflow(workflow_id: str, current_user: UserClaims = Depends(require_roles(["Parent", "System"]))):
    """Force transition a running workflow instance to CANCELLED state. Restrict to Admin roles."""
    success = workflow_registry.update_status(workflow_id, "CANCELLED")
    if not success:
        raise HTTPException(status_code=400, detail=f"Cannot cancel workflow '{workflow_id}' in its current state.")
    return {"success": True, "message": f"Workflow '{workflow_id}' was successfully cancelled."}

# ── Event Router API Endpoints ──────────────────────────────────────────────

class TriggerEventRequest(BaseModel):
    event_type: str = Field(..., description="Event Type string, e.g., LOW_STOCK, GRANDPARENT_EMERGENCY.")
    source_agent: str = Field(..., description="Sender agent initiating the event.")
    priority: str = Field("MEDIUM", description="Optional priority field.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Payload data carried in the event.")

@app.post("/orchestrator/events", tags=["Event Router"])
async def receive_event(req: TriggerEventRequest, current_user: UserClaims = Depends(get_current_user)):
    """Receive an incoming event, resolve matching rules, merge context state, and launch the corresponding workflow."""
    payload = req.payload.copy()
    payload["family_id"] = current_user.family_id
    
    event = Event(
        event_type=req.event_type,
        source_agent=req.source_agent,
        priority=req.priority,
        payload=payload
    )
    event_history.add_event(event)
    
    record = await event_dispatcher.dispatch(event)
    if record.status == "FAILED":
        err_msg = record.logs[-1] if record.logs else "Event dispatching failed."
        raise HTTPException(status_code=400, detail=err_msg)
        
    return {
        "workflow_id": record.workflow_id,
        "workflow_name": record.workflow_name,
        "status": "STARTED"
    }

@app.get("/orchestrator/events", response_model=List[RoutingRecord], tags=["Event Router"])
def get_events_history(current_user: UserClaims = Depends(get_current_user)):
    """Retrieve history of all dispatched events, selected workflows, duration, and outcomes."""
    return event_history.get_all_records()

@app.get("/orchestrator/events/{event_id}", response_model=RoutingRecord, tags=["Event Router"])
def get_event_routing_info(event_id: str, current_user: UserClaims = Depends(get_current_user)):
    """Retrieve detailed routing history, context state integration, and errors for one event."""
    record = event_history.get_record(event_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Routing record for Event '{event_id}' not found.")
    return record

# ── Task Scheduler API Endpoints ───────────────────────────────────────────

class CreateManualTaskRequest(BaseModel):
    priority: str = Field("NORMAL", description="Task Priority (CRITICAL, HIGH, NORMAL, LOW).")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task payload parameters.")
    delay_seconds: float = Field(0.0, description="Execute task after a specific delay in seconds.")

@app.get("/orchestrator/tasks", response_model=List[ScheduledTask], tags=["Task Scheduler"])
async def get_all_scheduled_tasks(current_user: UserClaims = Depends(get_current_user)):
    """Retrieve all queued, running, waiting, completed, or failed priority queue tasks."""
    return await scheduler.get_all_tasks()

@app.get("/orchestrator/tasks/{task_id}", response_model=ScheduledTask, tags=["Task Scheduler"])
async def get_scheduled_task_details(task_id: str, current_user: UserClaims = Depends(get_current_user)):
    """Retrieve detailed execution logs, status, and variables for one task."""
    task = await scheduler.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found in scheduler.")
    return task

@app.post("/orchestrator/tasks", response_model=ScheduledTask, tags=["Task Scheduler"])
async def create_manual_task(req: CreateManualTaskRequest, current_user: UserClaims = Depends(get_current_user)):
    """Manually insert a priority task with custom payload and optional delayed execution timestamp."""
    run_at = datetime.utcnow() + timedelta(seconds=req.delay_seconds)
    payload = req.payload.copy()
    payload["family_id"] = current_user.family_id
    
    task = ScheduledTask(
        priority=req.priority,
        payload=payload,
        scheduled_time=run_at
    )
    await scheduler.schedule_task(task)
    return task

@app.delete("/orchestrator/tasks/{task_id}", tags=["Task Scheduler"])
async def cancel_scheduled_task(task_id: str, current_user: UserClaims = Depends(require_roles(["Parent", "System"]))):
    """Cancel a queued, pending, or waiting task before execution. Restricted to Parent roles."""
    success = await scheduler.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Cannot cancel task '{task_id}'. Already running or finished.")
    return {"success": True, "message": f"Task '{task_id}' was successfully cancelled."}

@app.post("/orchestrator/tasks/{task_id}/retry", tags=["Task Scheduler"])
async def retry_failed_task(task_id: str, current_user: UserClaims = Depends(require_roles(["Parent", "System"]))):
    """Force re-queue and reset retry metrics for a failed or cancelled task. Restricted to Parent roles."""
    success = await scheduler.retry_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Cannot retry task '{task_id}'. Must be in FAILED or CANCELLED status.")
    return {"success": True, "message": f"Task '{task_id}' was successfully scheduled for immediate retry."}

# ── Dynamic Reverse Proxy Gateway ───────────────────────────────────────────

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def gateway_proxy(path: str, request: Request):
    """Transparently proxies incoming HTTP traffic, parsing JWT identity and back-injecting partition headers."""
    
    # Skip routing for orchestrator endpoints
    if path.startswith("orchestrator/"):
        return JSONResponse(status_code=404, content={"error": "Not Found"})

    query_params = request.url.query
    
    # Extract identity from authorization bearer token if present
    user_id = "anonymous"
    user_role = "member"
    family_id = "default_family"
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        claims = decode_access_token(token)
        if claims:
            user_id = claims.get("sub", user_id)
            user_role = claims.get("role", user_role)
            family_id = claims.get("family_id", family_id)
            
    # 1. Resolve agent bus target specifically using target_agent if available
    target_agent_name = None
    if "/api/v1/agent-bus/message" in request.url.path:
        try:
            body = await request.json()
            target_agent_field = body.get("target_agent", "")
            message_type = body.get("message_type", "")
            payload = body.get("payload", {})
            sender_agent = body.get("sender_agent", "")
            
            # Hook: Intercept agent bus event notifications to update Shared Context automatically
            if message_type and payload:
                asyncio.create_task(context_manager.process_bus_event(message_type, payload, sender_agent))

            # Map target agent field to registry name
            mapping = {
                "mother_agent": "mother",
                "father_agent": "father",
                "children_agent": "children",
                "child_agent": "children",
                "grandparent_agent": "grandparent",
                "baby_agent": "baby",
                "planner_agent": "planner"
            }
            resolved_name = mapping.get(target_agent_field)
            if resolved_name:
                target_agent_name = resolved_name
        except Exception:
            pass

    # 2. Resolve URL
    if target_agent_name:
        agent = registry.get_agent(target_agent_name)
        target_url = f"http://{agent.host}:{agent.port}/api/v1/agent-bus/message" if agent else None
    else:
        target_url = registry.resolve_url(request.url.path)
        
    if not target_url:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"success": False, "error": f"Unable to route request path: {request.url.path}"}
        )
        
    if query_params:
        target_url = f"{target_url}?{query_params}"

    logger.info(f"Proxying request: {request.method} {request.url.path} -> {target_url}")

    # Track metrics by finding target agent from resolved URL port
    try:
        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        for a_name, agent in registry.agents.items():
            if agent.port == parsed.port:
                registry.increment_request(a_name)
                break
    except Exception:
        pass

    async with httpx.AsyncClient() as client:
        # Reconstruct headers without host header
        headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
        
        # Inject tenant identity headers for downstream agent consumption
        headers["X-User-ID"] = user_id
        headers["X-User-Role"] = user_role
        headers["X-Family-ID"] = family_id
        
        try:
            req_content = await request.body()
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=req_content,
                timeout=15.0
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers)
            )
        except httpx.RequestError as exc:
            logger.error(f"Failed connection to {target_url}: {exc}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"success": False, "error": f"Service offline at {target_url}"}
            )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting KinNest Orchestrator Gateway...")
    uvicorn.run("orchestrator:app", host="0.0.0.0", port=8000, reload=False)
