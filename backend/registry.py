import time
import httpx
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("orchestrator.registry")

# Static capabilities mapping for each agent
AGENT_METADATA = {
    "mother": {
        "agent_type": "Grocery & Kitchen Assistant",
        "capabilities": ["grocery_inventory", "recipe_generation", "waste_tracking", "meal_planning", "shopping_lists"]
    },
    "father": {
        "agent_type": "Financial Advisor & Twin",
        "capabilities": ["financial_budgeting", "expense_logging", "anomaly_detection", "safe_to_spend", "bills_management"]
    },
    "children": {
        "agent_type": "Academic Guardian",
        "capabilities": ["homework_tracking", "study_planner", "screen_time_management", "wellness_monitoring", "pocket_money"]
    },
    "grandparent": {
        "agent_type": "Elder Care Assistant",
        "capabilities": ["health_vitals_tracking", "medication_reminders", "emergency_alerts", "insurance_management", "appointments"]
    },
    "baby": {
        "agent_type": "Infant Tracker",
        "capabilities": ["feeding_logger", "sleep_tracker", "vaccination_schedule", "growth_monitoring", "diaper_logs"]
    },
    "planner": {
        "agent_type": "Life & Event Planner",
        "capabilities": ["calendar_consolidation", "goal_planning", "habit_tracking", "routine_scheduling", "conflict_resolver"]
    }
}

class Agent(BaseModel):
    name: str
    host: str
    port: int
    status: str = "OFFLINE"  # ONLINE or OFFLINE
    startup_time: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    version: str = "unknown"
    agent_type: str = "Generic Agent"
    capabilities: List[str] = Field(default_factory=list)
    request_count: int = 0

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """Pre-populate the registry with known configurations."""
        port_mappings = {
            "mother": 8001,
            "father": 8002,
            "children": 8003,
            "grandparent": 8004,
            "baby": 8005,
            "planner": 8006
        }
        for name, port in port_mappings.items():
            meta = AGENT_METADATA.get(name, {})
            self.agents[name] = Agent(
                name=name,
                host="127.0.0.1",
                port=port,
                agent_type=meta.get("agent_type", "Generic Agent"),
                capabilities=meta.get("capabilities", [])
            )

    def register_online(self, name: str, version: str):
        """Mark an agent as ONLINE when it responds to heartbeat."""
        agent = self.agents.get(name)
        if agent:
            now = datetime.now(timezone.utc)
            if agent.status == "OFFLINE":
                agent.status = "ONLINE"
                agent.startup_time = now
                logger.info(f"Agent '{name}' status transitioned to ONLINE on port {agent.port}")
            agent.last_heartbeat = now
            agent.version = version

    def register_offline(self, name: str):
        """Mark an agent as OFFLINE when heartbeat fails."""
        agent = self.agents.get(name)
        if agent and agent.status == "ONLINE":
            agent.status = "OFFLINE"
            agent.startup_time = None
            logger.warning(f"Agent '{name}' status transitioned to OFFLINE on port {agent.port}")

    def increment_request(self, name: str):
        """Track metrics by incrementing request count for an agent."""
        agent = self.agents.get(name)
        if agent:
            agent.request_count += 1

    def resolve_url(self, path: str) -> Optional[str]:
        """Resolves target agent URL dynamically by matching path keywords against the registry."""
        path_lower = path.lower()
        
        # 1. Check path prefix first (e.g. /api/v1/mother/voice -> http://localhost:8001/api/v1/voice)
        prefixes = ["mother", "father", "children", "grandparent", "baby", "planner"]
        for prefix in prefixes:
            path_prefix = f"/api/v1/{prefix}"
            if path_lower.startswith(path_prefix):
                agent = self.agents.get(prefix)
                if agent:
                    suffix = path[len(path_prefix):]
                    return f"http://{agent.host}:{agent.port}/api/v1{suffix}"

        # 2. Heuristic Keyword Routing Map
        routing_keywords = {
            "mother": ["inventory", "purchase", "consumption", "analyzer", "expiry", "recipe", "waste", "price", "forecast", "kitchen-assistant", "grocery", "shopping"],
            "father": ["finance", "expense", "income", "budget", "savings", "early-warning", "digital-twin", "anomalies", "bill", "safe-to-spend"],
            "children": ["student", "subject", "assignment", "study", "exam", "progress", "activities", "pocket-money", "nutrition", "screen-time", "safety", "homework", "school", "attendance", "wellness"],
            "grandparent": ["vitals", "medicine", "appointment", "insurance", "grandparent"],
            "baby": ["baby", "feeding", "sleep", "growth", "vaccine", "vaccination", "diaper"],
            "planner": ["planner", "goals", "habits", "twin", "timeline", "recommendations", "plans", "tasks", "itinerary", "calendar", "reflections", "routines"]
        }

        for name, keywords in routing_keywords.items():
            if any(keyword in path_lower for keyword in keywords):
                agent = self.agents.get(name)
                if agent:
                    return f"http://{agent.host}:{agent.port}{path}"

        # Fallback to mother agent
        fallback_agent = self.agents.get("mother")
        if fallback_agent:
            return f"http://{fallback_agent.host}:{fallback_agent.port}{path}"
        return None

    def get_all_agents(self) -> List[Agent]:
        return list(self.agents.values())

    def get_agent(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)

# Global registry instance
registry = AgentRegistry()

async def poll_agent_health(name: str, agent: Agent):
    """Poll `/health` endpoint of a single agent and register status."""
    url = f"http://{agent.host}:{agent.port}/health"
    
    # Special handle for Father Agent Mock (since it runs in the orchestrator)
    if name == "father":
        # The mock is always online
        registry.register_online("father", "1.0.0-mock")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=2.0)
            if response.status_code == 200:
                # Try to fetch version from root `/` or health details
                version = "1.0.0"
                try:
                    # Let's also check root endpoint / for metadata if available
                    root_resp = await client.get(f"http://{agent.host}:{agent.port}/", timeout=1.0)
                    if root_resp.status_code == 200:
                        version = root_resp.json().get("version", "1.0.0")
                except Exception:
                    pass
                registry.register_online(name, version)
            else:
                registry.register_offline(name)
        except Exception:
            registry.register_offline(name)

async def registry_heartbeat_loop():
    """Background task running the health-polling loop for all agents."""
    logger.info("Starting Agent Registry heartbeat polling worker...")
    await asyncio.sleep(2.0)  # Wait for startup
    while True:
        tasks = []
        for name, agent in registry.agents.items():
            tasks.append(poll_agent_health(name, agent))
        await asyncio.gather(*tasks)
        await asyncio.sleep(5.0)
