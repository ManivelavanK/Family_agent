# AI Migration Plan: KinNest Child Agent

## 1. Current Architecture

The **KinNest Child Agent** is a FastAPI-based microservice designed for tracking and supporting children's education, routine, safety, wellness, nutrition, and financial independence.

```
                  +-----------------------------------+
                  |         FastAPI Routers           |
                  | (/api/* endpoints for all domains) |
                  +-----------------+-----------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
+---------v----------+                                     +--v---------------+
| Services & Models  |                                     | Specialized      |
| (CRUD & Analytics) |                                     | Child Agents     |
+---------+----------+                                     +--+---------------+
          |                                                   |
          |           +---------------------------------------+
          |           |
          v           v
+-----------------------------------------------------------------+
|                         Database Layer                          |
|    (SQLAlchemy + SQLite/PostgreSQL Models & Schema Creation)    |
+-----------------------------------------------------------------+
```

### Core Architecture Components:
* **Entrypoint & Routing (`app/main.py`)**: Mounts FastAPI routers for `profile`, `homework`, `study`, `exams`, `attendance`, `screen_time`, `health`, `activities`, `pocket_money`, `safety`, `wellness`, `nutrition`, `schedule`, `prediction`, `recommendation`, `notification`, `cross_agent`, and `dashboard`. Initializes tables safely via `schema.py` and manages background scheduler lifespan.
* **Database & ORM (`app/database/` & `app/models/`)**: SQLAlchemy Base models (`ChildProfile`, `Homework`, `StudySession`, `Exam`, `Attendance`, `ScreenTimeLog`, `HealthLog`, `Activity`, `PocketMoneyAllowance`, `ChildExpense`, `SavingGoal`, `SafetyProfile`, `CheckInLog`, `CallResponseLog`, `DiaryEntry`, `RelaxationLog`, `NutritionLog`, `MotherAgentBridgeEvent`, `ScheduleItem`, `HolidayCalendar`, `NotificationLog`).
* **Services Layer (`app/services/`)**: Contains domain logic for analytics, threshold evaluation, cross-agent summary generation (`cross_agent_service.py`), dashboard aggregation (`dashboard_service.py`), and recommendations (`recommendation_service.py`).
* **Deterministic ML Layer (`app/ml/predictor.py`)**: Uses scikit-learn models (`LinearRegression`, `Ridge`) to predict homework completion time, attendance trends, study performance index, screen time trends, and routine balance score based on historical database entries.
* **Child Agents Orchestration (`app/agents/`)**: Router-supervisor model (`child_supervisor.py`) delegating child natural language queries to specialized sub-agents (`education_agent.py`, `finance_agent.py`, `routine_agent.py`, `safety_agent.py`, `wellness_agent.py`).

---

## 2. Current Rule-Based Decision Logic

Currently, several services rely on explicit hardcoded rules, threshold checks, and keyword regex parsing:

1. **Query Intent Classification (`app/agents/child_supervisor.py`)**:
   * Checks `ROUTING_KEYWORDS` dictionary (e.g., `['study', 'homework']` -> `EDUCATION`, `['spend', 'rupees']` -> `FINANCE`, `['go out', 'check-in']` -> `SAFETY`, `['stressed', 'sad']` -> `WELLNESS`, `['screen time', 'routine']` -> `ROUTINE`).
   * Evaluates hit counts per domain deterministically before invoking fallback logic.

2. **Sub-Agent Query Handling (`app/agents/*_agent.py`)**:
   * `safety_agent.py`: Uses regex `r"(\d+)"` to extract return hours if regex or Groq parsing runs; defaults to 8:00 PM (20:00).
   * `finance_agent.py`: Checks keywords `"afford"`, `"price"`, `"cost"`, `"buy"`, `"course"`. Extracts numeric amounts via regex `r"(?:₹|\$|rs\.?|rupees|)\s*([\d,]+)"` and computes: `(total_allowance + total_saved) >= amount`.
   * `routine_agent.py`: Calculates average screen time over 7 days deterministically or queries today's schedule items.
   * `wellness_agent.py`: Triggers static relaxation suggestion list via `wellness_service.generate_relaxation_suggestions()`.
   * `education_agent.py`: Filters pending homework and exams occurring within 7 days, appending hardcoded Pomodoro study advice.

3. **Age Adaptation Service (`app/services/age_adaptation_service.py`)**:
   * Evaluates `age < 6` -> `EARLY_CHILDHOOD`, `6 <= age <= 12` -> `MIDDLE_CHILDHOOD`, `age > 12` -> `ADOLESCENCE`.
   * Applies hardcoded thresholds for max daily screen time (60 min vs 120 min vs 180 min), min sleep hours (10h vs 9h vs 8h), and pocket money allowance caps.

4. **Safety & Alert Logic (`app/services/safety_service.py`)**:
   * Evaluates check-in status: `EXPECTED`, `CHECKED_IN`, `LATE`, `OVERDUE`, `EMERGENCY`.
   * Evaluates late check-ins by comparing `datetime.now().time()` with `expected_return_time`.

5. **Recommendation Fallback Engine (`app/ai/groq_service.py` -> `generate_fallback_recommendations`)**:
   * Produces static string arrays for 10 core domains if Groq API key is absent or fails.

---

## 3. Existing AI / Groq Integration

The codebase already possesses initial Groq integration located in `app/ai/groq_service.py` using `Groq` SDK with model `llama-3.3-70b-versatile`:

* **`generate_ai_recommendations(context)`**: Receives full structured child context (profile, homework summary, health summary, screen time summary, safety status, ML predictions) and prompts Groq to generate advice across 10 required domains adhering strictly to JSON format.
* **`route_query_with_llm(query)`**: `child_supervisor.py` calls Groq to classify intent into `EDUCATION`, `FINANCE`, `SAFETY`, `WELLNESS`, or `ROUTINE` when keyword matching is inconclusive.
* **`safety_agent.py` & `finance_agent.py`**: Perform structured entity extraction (extracting return time/location or amount/category/description) via raw JSON completion requests.

### Limitations of Current AI Integration:
* Calls are direct point-to-point completions without agentic memory, tool calling, or multi-step reasoning.
* LLMs are used as passive string formatters or fallback entity parsers rather than autonomous decision-making agents with tool-access capabilities.

---

## 4. Components to Become AI-Powered

The following components will be upgraded to full Agentic AI functionality:

1. **Unified Child Intelligence Agent (`app/ai/child_ai_agent.py`)**:
   * Transform from single completion calls to a dynamic ReAct / Tool-calling agent capable of accessing child database tools (retrieving real-time schedule, checking pending homework, checking savings progress) and synthesizing holistic answers.
2. **Intent Routing & Context-Aware Dispatcher (`app/agents/child_supervisor.py`)**:
   * Upgrade supervisor to an Agentic Supervisor that evaluates intent, mood, urgency, and multi-intent queries (e.g., "I spent 500 on books and I'm feeling stressed about my exam tomorrow").
3. **Conversational Wellness & Emotional Support (`app/agents/wellness_agent.py`)**:
   * Dynamic empathetic child support agent providing age-adapted guidance, mood reflection, and coping strategies based on child diary logs and recent stress triggers.
4. **Intelligent Financial Advisor (`app/agents/finance_agent.py`)**:
   * AI reasoning agent that evaluates child savings goals, trade-offs, interest calculation scenarios, and generates age-appropriate financial literacy tips.
5. **Adaptive Study Planner (`app/agents/education_agent.py`)**:
   * Autonomous study schedule generator that analyzes upcoming exams, subject difficulty, past study focus scores, and homework estimates to propose personalized daily timetables.

---

## 5. Components to Remain Deterministic / Rule-Based for Safety

For safety, auditability, data integrity, and strict legal compliance, the following components **MUST remain 100% deterministic and rule-based**:

1. **Safety & Emergency Alert Engine (`app/services/safety_service.py`, `app/models/safety.py`)**:
   * Check-in time comparison (`expected_return_time < current_time` => `OVERDUE`).
   * Emergency trigger creation, guardian emergency notification dispatch, and SOS status transitions.
2. **Financial Balances & Ledger Calculations (`app/services/pocket_money_service.py`, `app/models/pocket_money.py`)**:
   * Pocket money balance calculation (`total_allowance + total_saved - total_expenses`).
   * Education expense authorization bridge events sent to Father/Mother agents.
3. **Database CRUD & Schema Integrity (`app/database/`, `app/models/`, `app/schemas/`)**:
   * All SQLAlchemy models, Pydantic schemas, database migrations, and raw table operations.
4. **Machine Learning Quantitative Predictors (`app/ml/predictor.py`)**:
   * Statistical regression models for numeric numerical estimations (actual minutes prediction, attendance percentage forecast, focus index).
5. **Age Limit Hard Rules (`app/services/age_adaptation_service.py`)**:
   * Strict legal and parental boundary caps (e.g. maximum permitted screen time thresholds, absolute curfew limits).

---

## 6. Proposed Agent Architecture

```
                                  +---------------------------------------+
                                  |         Child Natural Language        |
                                  |            Query / Request            |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Child Supervisor Agent          |
                                  |   (Hybrid: Deterministic Guardrails   |
                                  |        + LLM Router Dispatcher)       |
                                  +-------------------+-------------------+
                                                      |
         +--------------------+-----------------------+-----------------------+--------------------+
         |                    |                       |                       |                    |
         v                    v                       v                       v                    v
+-----------------+  +------------------+   +-------------------+   +--------------------+  +-------------------+
| Education Agent |  |  Finance Agent   |   |   Safety Agent    |   |   Wellness Agent   |  |   Routine Agent   |
| (Study & Exams) |  | (Allowance/Save) |   | (Check-ins/Alert) |   | (Empathy/Diary Log)|  | (Screen/Schedule) |
+--------+--------+  +--------+---------+   +---------+---------+   +---------+----------+  +---------+---------+
         |                    |                       |                       |                    |
         +--------------------+-----------------------+-----------------------+--------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     Tool Execution & Guardrails       |
                                  |  - Database Services & Read/Writes    |
                                  |  - ML Predictor Models Integration    |
                                  |  - Safety Threshold Guardrail Checks  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |      Structured JSON / Natural        |
                                  |      Language Safe Response           |
                                  +---------------------------------------+
```

### Architecture Highlights:
* **Hybrid Supervisor Pattern**: Fast deterministic keyword checks first for standard commands; ReAct routing via Groq for ambiguous/multi-turn messages.
* **Domain Tool Binding**: Each specialized agent is granted explicit read/write python functions as executable tools (e.g. `get_homework_list`, `log_child_expense`, `create_check_in`).
* **Strict Safety Guardrail Wrapper**: AI outputs containing actions or alerts pass through deterministic verification before mutating database states or firing parent notifications.

---

## 7. Required Environment Variables

Ensure `.env` and `.env.example` contain:

```env
# Server & Database Configuration
DATABASE_URL=sqlite:///./child_agent.db
ENVIRONMENT=development
LOG_LEVEL=INFO

# AI Agent Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
AI_TEMPERATURE=0.6
AI_MAX_TOKENS=1500
ENABLE_AI_AGENT=true

# Safety & Notification Settings
EMERGENCY_OVERDUE_MINUTES=30
```

---

## 8. New Files to be Created

| New File Path | Description / Purpose |
|---|---|
| `app/ai/agent_tools.py` | Defines reusable, typed tool definitions for agents (e.g., query homework, query savings, check safety status). |
| `app/ai/agent_prompts.py` | System prompts, persona definitions, and age-adapted conversation templates for all child agents. |
| `app/ai/agent_memory.py` | Short-term conversation history buffer management for multi-turn child dialogue. |
| `tests/test_ai_agent.py` | Unit and integration tests for AI agent execution, tool calls, and fallback mechanisms. |
| `AI_MIGRATION_PLAN.md` | Comprehensive architectural migration plan (this document). |

---

## 9. Existing Files to be Modified

| Existing File Path | Planned Modification Scope | Preservation & Compatibility Guarantee |
|---|---|---|
| `app/ai/groq_service.py` | Add structured tool-calling handlers and enhanced exception fallback mechanisms. | Existing `generate_ai_recommendations` and `generate_fallback_recommendations` signatures remain unchanged. |
| `app/agents/child_supervisor.py` | Enhance routing logic with multi-intent classification and tools invocation dispatcher. | Standard `route_and_execute(db, child_id, query)` function signature and dict output format preserved. |
| `app/agents/education_agent.py` | Integrate tool execution and adaptive study plan generation. | `handle_query(db, child_id, query)` return schema (`agent`, `reply`, `actions`) strictly maintained. |
| `app/agents/finance_agent.py` | Implement LLM-backed expense categorization and savings reasoning while keeping calculations deterministic. | Exact expense logging and education bridge event creation unchanged. |
| `app/agents/safety_agent.py` | Enhance check-in location parsing while enforcing deterministic safety logging via `cross_agent_service`. | All database check-in records and safety log outputs preserved. |
| `app/agents/wellness_agent.py` | Integrate empathetic text generation with relaxation suggestions. | Preserves output structure and integration with `wellness_service`. |
| `app/agents/routine_agent.py` | Enhance schedule interpretation and screen time balance recommendations. | Preserves output schema and weekly average computations. |
| `.env.example` | Document new optional AI configuration variables. | All existing environment settings retained. |

---

## 10. Testing Strategy

To ensure zero regressions and 100% backward compatibility:

1. **Automated Regression Test Suite**:
   * Run all 22 existing test suites in `tests/` (`test_activities.py`, `test_attendance.py`, `test_child_supervisor.py`, `test_cross_agent.py`, `test_dashboard.py`, `test_exams.py`, `test_health.py`, `test_homework.py`, `test_nutrition.py`, `test_pocket_money.py`, `test_prediction.py`, `test_profile.py`, `test_recommendation.py`, `test_safety.py`, `test_schedule.py`, `test_screen_time.py`, `test_study.py`, `test_wellness.py`, etc.).
   * Ensure 100% passing rate before and after migration.

2. **Deterministic Fallback Verification**:
   * Test all agent endpoints with `GROQ_API_KEY=""` (un-set or invalid) to ensure 100% fallback to deterministic rule engines without raising uncaught exceptions.

3. **Tool Calling & Execution Safety Tests**:
   * Validate that LLM tool invocations execute correct database services and return identical response structures as original agents.

4. **API Endpoint Contract Testing**:
   * Verify FastAPI HTTP responses for `/api/recommendation`, `/api/cross-agent`, `/api/dashboard`, and agent query endpoints match exact expected schema contracts.
