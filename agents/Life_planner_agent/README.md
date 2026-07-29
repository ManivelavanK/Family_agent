# KinNest Life Planner Agent Backend

Agentic AI-powered Life Planner backend for Events, Functions, Travel, Guest Visits, Family Routines, and Real Multi-Agent Supervisor Orchestration built with Python, FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic, Pydantic v2, HTTPX, and Groq Llama 3.3.

---

## KinNest Supervisor Architecture (STEP 11)

The **KinNest Supervisor Agent** (`AISupervisorAgent`) operates as the central intelligence orchestrator across all specialized family domain agents (`father`, `mother`, `child`, `grandparent`, `baby`).

```text
                    USER Request
                         │
                         ▼
                AISupervisorAgent
                         │
        Groq Intent & Agent Selection Reasoning
                         │
                         ▼
                AgentRegistry Lookup
                         │
            FamilyContextService (Async Gather)
       ┌───────────┬───────────┬───────────┐
       ▼           ▼           ▼           ▼
    Father       Mother      Child    Grandparent
    (HTTP)       (HTTP)     (HTTP)      (HTTP)
       └───────────┴───────────┴───────────┘
                         │
                         ▼
        Aggregated Context + ContextRetriever
                         │
                         ▼
             Groq Unified Reasoning
                         │
                         ▼
            SupervisorResponse Draft
```

### Core Capabilities
1. **Dynamic AI Selection**: Groq selects relevant agents based on user intent rather than keyword rules.
2. **Resilient Concurrency**: Queries reachable family agents in parallel using `asyncio.gather()`. Timeout or connection errors mark that specific agent as `available: false` while allowing the supervisor to continue without crashing.
3. **Mock vs Real HTTP Switch**: Controlled via `AGENT_COMMUNICATION_MOCK`. Evaluates mock contexts when `true`, and initiates real HTTPX GET requests to `{AGENT_URL}/api/v1/context?family_id={family_id}` when `false`.
4. **Approval Boundary**: Major financial or schedule modifications return `requires_approval: true`. Executions require explicit user approval (`approved: true`).

---

## Supervisor API Endpoints

- `POST /api/v1/ai/supervisor`: Main supervisor natural language endpoint.
- `GET /api/v1/ai/supervisor/agents`: Real-time family agent health status and response times.

---

## Example Request & Response

### Request: `POST /api/v1/ai/supervisor`
```json
{
  "family_id": "default_family",
  "message": "Plan a family trip to Ooty next month under ₹30000."
}
```

### Response:
```json
{
  "success": true,
  "message": "KinNest supervisor analysis completed",
  "data": {
    "request": {
      "family_id": "default_family",
      "message": "Plan a family trip to Ooty next month under ₹30000.",
      "execute": false,
      "approved": false
    },
    "selected_agents": [
      "father",
      "mother",
      "child"
    ],
    "agent_responses": [
      {
        "agent": "father",
        "available": true,
        "response": {
          "available_budget": 35000.0,
          "monthly_savings_goal": 10000.0,
          "financial_notes": "Trip budget ceiling approved up to 35,000 INR."
        },
        "error": null,
        "response_time_ms": 1.5
      },
      {
        "agent": "mother",
        "available": true,
        "response": {
          "food_preferences": ["Vegetarian", "South Indian Buffet"],
          "grocery_budget_limit": 8000.0
        },
        "error": null,
        "response_time_ms": 1.2
      }
    ],
    "available_agents": [
      "father",
      "mother"
    ],
    "unavailable_agents": [],
    "recommendation": {
      "title": "Unified Family Trip to Ooty",
      "summary": "Unified family plan within 30,000 INR ceiling.",
      "financial_impact": "Fits within father's 35,000 INR budget ceiling",
      "action_items": ["Book train tickets 30 days in advance"]
    },
    "confidence": 0.94,
    "requires_approval": true,
    "next_action": "REVIEW_RECOMMENDATION"
  }
}
```

---

## Testing

Run tests with pytest:
```bash
python -m pytest -v
```
Result: **69 passed cleanly** in offline test mode using mocked Groq and HTTPX completions.
