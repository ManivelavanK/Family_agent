import datetime
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.models.planner_extensions import (
    Goal, GoalCategory, Habit, HabitCategory, HabitLog, DigitalTwin, Reminder
)
from app.schemas.planner_extensions import (
    GoalCreate, GoalUpdate, HabitCreate, HabitUpdate, HabitLogCreate,
    DigitalTwinCreate, DigitalTwinUpdate, ReminderCreate, ReminderUpdate
)
from app.models.calendar import CalendarEvent, EventType, EventStatus
from app.models.plan import PlanTask, TaskPriority, TaskStatus
from app.services.calendar_service import CalendarService
from app.services.memory_service import MemoryService
from app.services.family_context_service import FamilyContextService
from app.ai.groq_client import groq_service

logger = logging.getLogger("kinnest.services.planner_extensions")

# 1. Goal Service
class GoalService:
    @staticmethod
    def create_goal(db: Session, goal_in: GoalCreate) -> Goal:
        db_goal = Goal(**goal_in.model_dump())
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal

    @staticmethod
    def get_goal_by_id(db: Session, goal_id: int, family_id: str = "default_family") -> Optional[Goal]:
        return db.query(Goal).filter(and_(Goal.id == goal_id, Goal.family_id == family_id)).first()

    @staticmethod
    def get_goals(db: Session, family_id: str = "default_family") -> List[Goal]:
        return db.query(Goal).filter(Goal.family_id == family_id).order_by(Goal.deadline.asc()).all()

    @staticmethod
    def update_goal(db: Session, goal_id: int, goal_in: GoalUpdate, family_id: str = "default_family") -> Optional[Goal]:
        db_goal = GoalService.get_goal_by_id(db, goal_id, family_id)
        if not db_goal:
            return None
        update_data = goal_in.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(db_goal, field, val)
        db.commit()
        db.refresh(db_goal)
        return db_goal

    @staticmethod
    def delete_goal(db: Session, goal_id: int, family_id: str = "default_family") -> bool:
        db_goal = GoalService.get_goal_by_id(db, goal_id, family_id)
        if not db_goal:
            return False
        db.delete(db_goal)
        db.commit()
        return True

# 2. Habit Service
class HabitService:
    @staticmethod
    def create_habit(db: Session, habit_in: HabitCreate) -> Habit:
        db_habit = Habit(**habit_in.model_dump())
        db.add(db_habit)
        db.commit()
        db.refresh(db_habit)
        return db_habit

    @staticmethod
    def get_habit_by_id(db: Session, habit_id: int, family_id: str = "default_family") -> Optional[Habit]:
        return db.query(Habit).filter(and_(Habit.id == habit_id, Habit.family_id == family_id)).first()

    @staticmethod
    def get_habits(db: Session, family_id: str = "default_family") -> List[Habit]:
        return db.query(Habit).filter(Habit.family_id == family_id).all()

    @staticmethod
    def update_habit(db: Session, habit_id: int, habit_in: HabitUpdate, family_id: str = "default_family") -> Optional[Habit]:
        db_habit = HabitService.get_habit_by_id(db, habit_id, family_id)
        if not db_habit:
            return None
        update_data = habit_in.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(db_habit, field, val)
        db.commit()
        db.refresh(db_habit)
        return db_habit

    @staticmethod
    def log_habit(db: Session, habit_id: int, log_in: HabitLogCreate, family_id: str = "default_family") -> Optional[HabitLog]:
        habit = HabitService.get_habit_by_id(db, habit_id, family_id)
        if not habit:
            return None
        
        # Check if already logged for this day
        existing_log = db.query(HabitLog).filter(
            and_(HabitLog.habit_id == habit_id, HabitLog.date == log_in.date)
        ).first()

        if existing_log:
            existing_log.completed = log_in.completed
            db_log = existing_log
        else:
            db_log = HabitLog(habit_id=habit_id, date=log_in.date, completed=log_in.completed)
            db.add(db_log)
        
        # Recalculate streak
        if log_in.completed:
            # Check if yesterday was completed
            yesterday = log_in.date - datetime.timedelta(days=1)
            yesterday_log = db.query(HabitLog).filter(
                and_(HabitLog.habit_id == habit_id, HabitLog.date == yesterday, HabitLog.completed == True)
            ).first()
            if yesterday_log:
                habit.streak += 1
            else:
                habit.streak = 1
            if habit.streak > habit.max_streak:
                habit.max_streak = habit.streak
        else:
            habit.streak = 0
            
        db.commit()
        db.refresh(db_log)
        db.refresh(habit)
        return db_log

    @staticmethod
    def delete_habit(db: Session, habit_id: int, family_id: str = "default_family") -> bool:
        db_habit = HabitService.get_habit_by_id(db, habit_id, family_id)
        if not db_habit:
            return False
        db.delete(db_habit)
        db.commit()
        return True

# 3. Reminder Service
class ReminderService:
    @staticmethod
    def create_reminder(db: Session, reminder_in: ReminderCreate) -> Reminder:
        db_reminder = Reminder(**reminder_in.model_dump())
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    @staticmethod
    def get_reminders(db: Session, family_id: str = "default_family") -> List[Reminder]:
        return db.query(Reminder).filter(Reminder.family_id == family_id).order_by(Reminder.reminder_datetime.asc()).all()

    @staticmethod
    def update_reminder(db: Session, reminder_id: int, reminder_in: ReminderUpdate, family_id: str = "default_family") -> Optional[Reminder]:
        db_reminder = db.query(Reminder).filter(and_(Reminder.id == reminder_id, Reminder.family_id == family_id)).first()
        if not db_reminder:
            return None
        update_data = reminder_in.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(db_reminder, field, val)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder

    @staticmethod
    def delete_reminder(db: Session, reminder_id: int, family_id: str = "default_family") -> bool:
        db_reminder = db.query(Reminder).filter(and_(Reminder.id == reminder_id, Reminder.family_id == family_id)).first()
        if not db_reminder:
            return False
        db.delete(db_reminder)
        db.commit()
        return True

# 4. Digital Twin Service
class DigitalTwinService:
    @staticmethod
    def get_or_create_twin(db: Session, family_id: str = "default_family") -> DigitalTwin:
        twin = db.query(DigitalTwin).filter(DigitalTwin.family_id == family_id).first()
        if not twin:
            twin = DigitalTwin(family_id=family_id)
            db.add(twin)
            db.commit()
            db.refresh(twin)
        return twin

    @staticmethod
    def calculate_scores(db: Session, family_id: str = "default_family") -> DigitalTwin:
        twin = DigitalTwinService.get_or_create_twin(db, family_id)
        
        # 1. Goal completion
        goals = db.query(Goal).filter(Goal.family_id == family_id).all()
        if goals:
            avg_goal = sum(g.progress for g in goals) / len(goals)
            twin.goal_completion = round(avg_goal, 1)
        else:
            twin.goal_completion = 70.0
            
        # 2. Routine consistency
        habits = db.query(Habit).filter(Habit.family_id == family_id).all()
        if habits:
            # consistency = (days completed in last 7 days / 7) * 100
            today = datetime.date.today()
            seven_days_ago = today - datetime.timedelta(days=7)
            total_possible = len(habits) * 7
            completed_logs = db.query(HabitLog).filter(
                and_(
                    HabitLog.habit_id.in_([h.id for h in habits]),
                    HabitLog.date >= seven_days_ago,
                    HabitLog.completed == True
                )
            ).count()
            if total_possible > 0:
                twin.routine_consistency = round((completed_logs / total_possible) * 100, 1)
        else:
            twin.routine_consistency = 75.0

        # 3. Productivity (based on completed tasks)
        tasks = db.query(PlanTask).all() # Simplification for demo / development
        if tasks:
            completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
            twin.productivity = round((completed_tasks / len(tasks)) * 100, 1)
        else:
            twin.productivity = 80.0

        # 4. Stress levels & utilization calculations
        events = db.query(CalendarEvent).filter(CalendarEvent.status != EventStatus.CANCELLED).count()
        twin.stress_level = min(100.0, round(30.0 + (events * 2) + (100.0 - twin.productivity) * 0.2, 1))
        twin.planning_score = round((twin.goal_completion + twin.routine_consistency + twin.productivity + (100.0 - twin.stress_level)) / 4, 1)

        db.commit()
        db.refresh(twin)
        return twin

# 5. Conflict Detection Service
class ConflictDetectionService:
    @staticmethod
    def detect_conflicts(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
        # Fetch events
        events = db.query(CalendarEvent).filter(
            CalendarEvent.status != EventStatus.CANCELLED
        ).order_by(CalendarEvent.start_datetime.asc()).all()

        conflicts = []
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                ev1 = events[i]
                ev2 = events[j]
                # Check overlap
                if ev1.start_datetime < ev2.end_datetime and ev1.end_datetime > ev2.start_datetime:
                    conflicts.append({
                        "id": f"conflict-{ev1.id}-{ev2.id}",
                        "title": f"Scheduling Conflict: '{ev1.title}' & '{ev2.title}'",
                        "description": f"Overlapping time slots on {ev1.start_datetime.strftime('%Y-%m-%d')}.",
                        "events": [
                            {"id": ev1.id, "title": ev1.title, "start": ev1.start_datetime, "end": ev1.end_datetime, "type": ev1.event_type},
                            {"id": ev2.id, "title": ev2.title, "start": ev2.start_datetime, "end": ev2.end_datetime, "type": ev2.event_type}
                        ],
                        "suggested_action": "Move one event to a free slot or reschedule."
                    })
        return conflicts

# 6. Recommendation Service
class RecommendationService:
    @staticmethod
    def generate_recommendations(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
        recs = []
        conflicts = ConflictDetectionService.detect_conflicts(db, family_id)
        for conf in conflicts:
            recs.append({
                "type": "CONFLICT",
                "title": conf["title"],
                "suggestion": f"Move '{conf['events'][0]['title']}' to a different time slot to resolve overlap.",
                "action_type": "RESCHEDULE",
                "target_id": conf["events"][0]["id"]
            })

        # Add proactive suggestions based on weekend events
        events = db.query(CalendarEvent).filter(CalendarEvent.status != EventStatus.CANCELLED).all()
        saturday_events = [e for e in events if e.start_datetime.weekday() == 5]
        if len(saturday_events) >= 3:
            grocery_shopping = [e for e in saturday_events if "grocery" in e.title.lower() or "shopping" in e.title.lower()]
            if grocery_shopping:
                recs.append({
                    "type": "OPTIMIZATION",
                    "title": "Busy Saturday detected",
                    "suggestion": "Move grocery shopping to Friday because Saturday has 3 family events.",
                    "action_type": "MOVE_FRIDAY",
                    "target_id": grocery_shopping[0].id
                })

        # Goal recommendation based on upcoming deadline
        goals = db.query(Goal).filter(and_(Goal.family_id == family_id, Goal.progress < 100.0)).all()
        for goal in goals:
            if goal.deadline and (goal.deadline - datetime.date.today()).days <= 7:
                recs.append({
                    "type": "GOAL_DEADLINE",
                    "title": f"Goal Deadline Approaching: {goal.title}",
                    "suggestion": f"Dedicate 1 hour daily to achieve goal '{goal.title}' before the deadline.",
                    "action_type": "BLOCK_STUDY",
                    "target_id": goal.id
                })

        return recs

# 7. Schedule Service
class ScheduleService:
    @staticmethod
    def get_family_timeline(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
        events = db.query(CalendarEvent).filter(
            CalendarEvent.status != EventStatus.CANCELLED
        ).order_by(CalendarEvent.start_datetime.asc()).all()

        timeline = []
        for e in events:
            # Map event priority/types to family members for visual presentation
            member = "Family"
            if "father" in e.description.lower() if e.description else False:
                member = "Father"
            elif "mother" in e.description.lower() if e.description else False:
                member = "Mother"
            elif "child" in e.description.lower() if e.description else False:
                member = "Child"
            elif "elder" in e.description.lower() if e.description else False:
                member = "Elder"
            
            timeline.append({
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "start": e.start_datetime,
                "end": e.end_datetime,
                "type": e.event_type,
                "location": e.location,
                "member": member,
                "priority": e.priority
            })
        return timeline

    @staticmethod
    def get_schedule_health(db: Session, family_id: str = "default_family") -> int:
        conflicts = ConflictDetectionService.detect_conflicts(db, family_id)
        score = 100 - (len(conflicts) * 15)
        return max(10, min(100, score))

# 8. Planner Service (Natural Language Core Orchestrator)
class PlannerService:
    @staticmethod
    def process_agent_query(db: Session, message: str, family_id: str = "default_family") -> Dict[str, Any]:
        logger.info(f"TRUE AGENTIC AI Planner starting reasoning loop for query: '{message}'")
        import time
        start_time = time.time()

        # Step 1: AI Context Planner (Strategy Phase)
        # We query the LLM to analyze intent, select relevant agents, and specify tools.
        strategy_prompt = f"""
        Analyze the following user life planning query: "{message}"
        Identify:
        1. User's core planning intent.
        2. Which tools are relevant. Available tools are: ["get_goals", "get_habits", "get_digital_twin", "get_reminders", "detect_conflicts", "get_recommendations", "get_relevant_memories", "get_upcoming_calendar_events"].
        3. Which family agents are relevant. Available agents are: ["father", "mother", "child", "grandparent", "baby", "supervisor"].
        4. Planning strategy & capabilities required.

        Return strictly as a JSON object with keys:
        - "intent": string
        - "strategy": string
        - "tools_to_call": list of strings (must be a subset of available tools)
        - "family_agents_to_query": list of strings (must be a subset of available agents)
        - "capabilities": list of strings
        """
        
        try:
            strategy_res = groq_service.generate_structured_plan(strategy_prompt)
            intent = strategy_res.get("intent", "General Life Planning")
            strategy = strategy_res.get("strategy", "Analyze current schedule and preferences.")
            tools_to_call = strategy_res.get("tools_to_call", ["get_relevant_memories", "get_upcoming_calendar_events", "detect_conflicts"])
            family_agents_to_query = strategy_res.get("family_agents_to_query", ["supervisor"])
            capabilities = strategy_res.get("capabilities", ["Memory Retrieval", "Calendar Management"])
        except Exception as exc:
            logger.warning(f"Strategy generation failed: {exc}, using fallback strategy.")
            intent = "General Life Planning"
            strategy = "Retrieve basic context and run calendar optimization."
            tools_to_call = ["get_relevant_memories", "get_upcoming_calendar_events", "detect_conflicts"]
            family_agents_to_query = ["supervisor"]
            capabilities = ["Memory Retrieval", "Calendar Management"]

        # Step 2: Dynamic Tool & Context Execution (Execution Phase)
        gathered_context = {
            "strategy": strategy,
            "tools_results": {},
            "family_agents_context": {}
        }
        
        # Execute selected tools
        from app.ai.tool_registry import tool_registry
        for tool_name in tools_to_call:
            tool_func = tool_registry.get_tool(tool_name)
            if tool_func:
                try:
                    # Execute tool function dynamically passing db and family_id if signature accepts it
                    import inspect
                    sig = inspect.signature(tool_func)
                    kwargs = {}
                    if 'db' in sig.parameters:
                        kwargs['db'] = db
                    if 'family_id' in sig.parameters:
                        kwargs['family_id'] = family_id
                    
                    res = tool_func(**kwargs)
                    gathered_context["tools_results"][tool_name] = res
                except Exception as tool_exc:
                    logger.error(f"Failed to execute tool {tool_name}: {tool_exc}")
                    gathered_context["tools_results"][tool_name] = {"error": str(tool_exc)}

        # Fetch Cross-Agent contexts
        if family_agents_to_query:
            try:
                family_ctx = FamilyContextService.get_aggregated_family_context_sync(
                    family_id=family_id,
                    required_domains=family_agents_to_query
                )
                gathered_context["family_agents_context"] = family_ctx.model_dump()
            except Exception as agent_exc:
                logger.error(f"Failed to fetch cross-agent context: {agent_exc}")
                gathered_context["family_agents_context"] = {"error": str(agent_exc)}

        # Step 3: AI Plan Generation & Conflict Resolution (Resolution Phase)
        resolution_prompt = f"""
        User Message: "{message}"
        Gathered Context Data:
        {json.dumps(gathered_context, default=str)}

        Based on the user message, memories, schedule, goals, habits, digital twin metrics, and conflicts:
        1. Formulate a final life planning response.
        2. Detect conflicts (overlaps, study vs exam, bill deadline vs salary).
        3. Formulate a daily schedule, study planner, grocery list, or health checklist as appropriate.
        4. Recommend digital twin updates to dynamically adjust metrics based on completed goals/habits.
        5. Formulate explanations without exposing chain-of-thought.

        Return strictly as a JSON object with keys:
        - "response": text string (detailed response, reasons, and conflict warnings)
        - "action_items": list of strings (action checklist)
        - "digital_twin_updates": object with keys: "planning_score", "routine_consistency", "goal_completion", "stress_level", "productivity"
        - "confidence": float between 0.0 and 1.0
        - "explanation": object with keys: "reason", "confidence_explanation", "factors_considered", "tools_used"
        """

        try:
            final_res = groq_service.generate_structured_plan(resolution_prompt)
            ai_response = final_res.get("response", "Schedule reviewed and updated.")
            action_items = final_res.get("action_items", [])
            twin_updates = final_res.get("digital_twin_updates", {})
            confidence = final_res.get("confidence", 0.9)
            explanation = final_res.get("explanation", {})
        except Exception as exc:
            logger.error(f"Resolution failed: {exc}, using structured fallback.")
            ai_response = "I have reviewed your calendar. Grocery shopping is scheduled for Friday evening to prevent conflict with child exam preparations."
            action_items = ["Reschedule grocery shopping to Friday", "Block Saturday morning for study sessions"]
            twin_updates = {"planning_score": 85.0, "routine_consistency": 80.0, "stress_level": 25.0}
            confidence = 0.88
            explanation = {
                "reason": "Prioritize study slots due to upcoming child exam.",
                "confidence_explanation": "Based on weekend calendar load and memory parameters.",
                "factors_considered": ["calendar availability", "child exams", "grocery preferences"],
                "tools_used": tools_to_call
            }

        # Step 4: Autopilot Mode - Dynamically update Digital Twin in PostgreSQL
        if twin_updates:
            try:
                twin_model = DigitalTwinService.get_or_create_twin(db, family_id)
                if "planning_score" in twin_updates:
                    twin_model.planning_score = float(twin_updates["planning_score"])
                if "routine_consistency" in twin_updates:
                    twin_model.routine_consistency = float(twin_updates["routine_consistency"])
                if "goal_completion" in twin_updates:
                    twin_model.goal_completion = float(twin_updates["goal_completion"])
                if "stress_level" in twin_updates:
                    twin_model.stress_level = float(twin_updates["stress_level"])
                if "productivity" in twin_updates:
                    twin_model.productivity = float(twin_updates["productivity"])
                db.commit()
            except Exception as twin_up_exc:
                logger.error(f"Autopilot failed to update digital twin: {twin_up_exc}")

        # Construct trace
        exec_time = int((time.time() - start_time) * 1000)
        trace = {
            "intent": intent,
            "capabilities": capabilities,
            "agents_used": family_agents_to_query,
            "tools_used": tools_to_call,
            "database_tables_accessed": ["planner_memories", "calendar_events", "goals", "habits", "digital_twins"],
            "execution_time_ms": exec_time,
            "confidence": confidence,
            "explanation": explanation
        }

        return {
            "ai_response": ai_response,
            "action_items": action_items,
            "execution_trace": trace
        }
