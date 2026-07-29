import datetime
import logging
from typing import Dict, Any, Callable, List
from sqlalchemy.orm import Session
from app.services.plan_service import PlanService, TaskService, BudgetService, ParticipantService

logger = logging.getLogger("kinnest.ai.tools")

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def register_tool(self, name: str, func: Callable):
        self._tools[name] = func
        logger.info(f"Registered AI tool: {name}")

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def _register_default_tools(self):
        def get_upcoming_plans(db: Session) -> List[Dict[str, Any]]:
            plans = PlanService.get_all_plans(db, limit=10)
            return [{"id": p.id, "title": p.title, "type": p.plan_type.value, "status": p.status.value} for p in plans]

        def get_plan_details(db: Session, plan_id: int) -> Dict[str, Any]:
            plan = PlanService.get_plan_by_id(db, plan_id)
            if not plan:
                return {"error": "Plan not found"}
            return {
                "id": plan.id,
                "title": plan.title,
                "budget": plan.budget,
                "tasks": [t.title for t in plan.tasks],
                "participants": [p.name for p in plan.participants]
            }

        def estimate_plan_cost(people: int, duration_days: int = 1, category: str = "TRAVEL") -> float:
            base_rate = 1500.0 if category == "TRAVEL" else 800.0
            return float(people * duration_days * base_rate)

        def get_upcoming_calendar_events(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
            from app.services.calendar_service import CalendarService
            events = CalendarService.get_upcoming_events(db, limit=limit)
            return [
                {
                    "id": e.id,
                    "title": e.title,
                    "event_type": e.event_type.value,
                    "start": str(e.start_datetime),
                    "end": str(e.end_datetime)
                } for e in events
            ]

        def get_calendar_events_for_date(db: Session, date_str: str) -> List[Dict[str, Any]]:
            from app.services.calendar_service import CalendarService
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            events = CalendarService.get_events_by_date(db, target_date)
            return [
                {
                    "id": e.id,
                    "title": e.title,
                    "event_type": e.event_type.value,
                    "start": str(e.start_datetime),
                    "end": str(e.end_datetime)
                } for e in events
            ]

        def get_calendar_events_in_range(db: Session, start_date_str: str, end_date_str: str) -> List[Dict[str, Any]]:
            from app.services.calendar_service import CalendarService
            s_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            events = CalendarService.get_events_in_range(db, s_date, e_date)
            return [
                {
                    "id": e.id,
                    "title": e.title,
                    "event_type": e.event_type.value,
                    "start": str(e.start_datetime),
                    "end": str(e.end_datetime)
                } for e in events
            ]

        def check_calendar_conflicts(db: Session, start_iso: str, end_iso: str) -> Dict[str, Any]:
            from app.services.calendar_service import CalendarService
            s_dt = datetime.datetime.fromisoformat(start_iso)
            e_dt = datetime.datetime.fromisoformat(end_iso)
            res = CalendarService.check_conflicts(db, s_dt, e_dt)
            return res.model_dump(mode="json")

        def get_available_time_slots(db: Session, date_str: str, duration_minutes: int = 60) -> List[Dict[str, Any]]:
            from app.services.calendar_service import CalendarService
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            existing_events = CalendarService.get_events_by_date(db, target_date)
            
            # Simple factual scanner for free windows between 08:00 and 20:00
            day_start = datetime.datetime.combine(target_date, datetime.time(8, 0), tzinfo=datetime.timezone.utc)
            day_end = datetime.datetime.combine(target_date, datetime.time(20, 0), tzinfo=datetime.timezone.utc)
            
            current = day_start
            free_slots = []
            dur = datetime.timedelta(minutes=duration_minutes)
            
            while current + dur <= day_end:
                slot_end = current + dur
                # Check factual conflict with existing events
                conflict_res = CalendarService.check_conflicts(db, current, slot_end)
                if not conflict_res.has_conflict:
                    free_slots.append({
                        "start": current.isoformat(),
                        "end": slot_end.isoformat(),
                        "duration_minutes": duration_minutes
                    })
                current += datetime.timedelta(minutes=60)
            return free_slots

        def get_relevant_memories(db: Session, family_id: str = "default_family", limit: int = 10) -> List[Dict[str, Any]]:
            from app.services.memory_service import MemoryService
            memories = MemoryService.get_relevant_memories(db, family_id=family_id, limit=limit)
            return [
                {
                    "id": m.id,
                    "type": m.memory_type.value,
                    "title": m.title,
                    "content": m.content,
                    "importance": m.importance
                } for m in memories
            ]

        def get_memories_by_type(db: Session, memory_type_str: str, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.memory_service import MemoryService
            from app.models.memory import MemoryType
            try:
                m_type = MemoryType(memory_type_str)
                memories = MemoryService.get_memories_by_type(db, memory_type=m_type, family_id=family_id)
                return [{"id": m.id, "title": m.title, "content": m.content} for m in memories]
            except ValueError:
                return []

        def get_plan_reflections(db: Session, plan_id: int) -> List[Dict[str, Any]]:
            from app.services.reflection_service import ReflectionService
            reflections = ReflectionService.get_reflections_by_plan(db, plan_id)
            return [
                {
                    "id": r.id,
                    "rating": r.rating,
                    "what_went_well": r.what_went_well,
                    "what_went_wrong": r.what_went_wrong,
                    "feedback": r.feedback,
                    "future_suggestions": r.future_suggestions
                } for r in reflections
            ]

        def get_family_context(family_id: str = "default_family") -> Dict[str, Any]:
            from app.services.family_context_service import FamilyContextService
            return FamilyContextService.get_aggregated_family_context_sync(family_id).model_dump()

        def get_proactive_planning_context(db: Session, family_id: str = "default_family", lookahead_days: int = 30) -> Dict[str, Any]:
            from app.ai.context.retriever import ContextRetriever
            return ContextRetriever.get_planning_context(db, family_id=family_id)

        def get_guest_details(db: Session, guest_id: int, family_id: str = "default_family") -> Dict[str, Any]:
            from app.services.guest_service import GuestService
            guest = GuestService.get_guest_by_id(db, guest_id, family_id)
            return guest.to_dict() if guest else {"error": "Guest not found"}

        def get_upcoming_guest_visits(db: Session, family_id: str = "default_family", limit: int = 10) -> List[Dict[str, Any]]:
            from app.services.guest_service import GuestService
            guests = GuestService.get_all_guests(db, family_id, limit)
            return [g.to_dict() for g in guests]

        def get_guest_visit_calendar_context(db: Session, start_date_str: str, end_date_str: str) -> List[Dict[str, Any]]:
            from app.services.calendar_service import CalendarService
            s_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            events = CalendarService.get_events_in_range(db, s_date, e_date)
            return [e.to_dict() for e in events]

        def get_family_routines(db: Session, family_id: str = "default_family", limit: int = 50) -> List[Dict[str, Any]]:
            from app.services.routine_service import RoutineService
            routines = RoutineService.get_all_routines(db, family_id, limit)
            return [r.to_dict() for r in routines]

        def get_family_routines_for_date(db: Session, target_date_str: str, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.routine_service import RoutineService
            t_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            routines = RoutineService.get_routines_for_date(db, t_date, family_id)
            return [r.to_dict() for r in routines]

        def get_family_routines_in_range(db: Session, start_date_str: str, end_date_str: str, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.routine_service import RoutineService
            s_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            e_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            routines = RoutineService.get_routines_in_range(db, s_date, e_date, family_id)
            return [r.to_dict() for r in routines]

        def check_routine_conflicts(db: Session, member_name: str, start_dt_str: str, end_dt_str: str, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.routine_service import RoutineService
            s_dt = datetime.datetime.fromisoformat(start_dt_str)
            e_dt = datetime.datetime.fromisoformat(end_dt_str)
            conflicts = RoutineService.check_routine_conflicts(db, member_name, s_dt, e_dt, family_id)
            return [c.to_dict() for c in conflicts]

        def get_goals_tool(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.planner_services import GoalService
            goals = GoalService.get_goals(db, family_id)
            return [
                {
                    "id": g.id,
                    "title": g.title,
                    "description": g.description,
                    "category": g.category.value,
                    "progress": g.progress,
                    "deadline": str(g.deadline) if g.deadline else None,
                    "ai_recommendation": g.ai_recommendation
                } for g in goals
            ]

        def get_habits_tool(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.planner_services import HabitService
            habits = HabitService.get_habits(db, family_id)
            return [
                {
                    "id": h.id,
                    "title": h.title,
                    "category": h.category.value,
                    "streak": h.streak,
                    "max_streak": h.max_streak
                } for h in habits
            ]

        def get_digital_twin_tool(db: Session, family_id: str = "default_family") -> Dict[str, Any]:
            from app.services.planner_services import DigitalTwinService
            twin = DigitalTwinService.get_or_create_twin(db, family_id)
            return {
                "planning_score": twin.planning_score,
                "routine_consistency": twin.routine_consistency,
                "goal_completion": twin.goal_completion,
                "time_utilization": twin.time_utilization,
                "stress_level": twin.stress_level,
                "productivity": twin.productivity
            }

        def get_reminders_tool(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.planner_services import ReminderService
            reminders = ReminderService.get_reminders(db, family_id)
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "datetime": str(r.reminder_datetime),
                    "is_sent": r.is_sent
                } for r in reminders
            ]

        def detect_conflicts_tool(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.planner_services import ConflictDetectionService
            return ConflictDetectionService.detect_conflicts(db, family_id)

        def get_recommendations_tool(db: Session, family_id: str = "default_family") -> List[Dict[str, Any]]:
            from app.services.planner_services import RecommendationService
            return RecommendationService.generate_recommendations(db, family_id)

        self.register_tool("get_upcoming_plans", get_upcoming_plans)
        self.register_tool("get_plan_details", get_plan_details)
        self.register_tool("estimate_plan_cost", estimate_plan_cost)
        self.register_tool("get_upcoming_calendar_events", get_upcoming_calendar_events)
        self.register_tool("get_calendar_events_for_date", get_calendar_events_for_date)
        self.register_tool("get_calendar_events_in_range", get_calendar_events_in_range)
        self.register_tool("check_calendar_conflicts", check_calendar_conflicts)
        self.register_tool("get_available_time_slots", get_available_time_slots)
        self.register_tool("get_relevant_memories", get_relevant_memories)
        self.register_tool("get_memories_by_type", get_memories_by_type)
        self.register_tool("get_plan_reflections", get_plan_reflections)
        self.register_tool("get_family_context", get_family_context)
        self.register_tool("get_proactive_planning_context", get_proactive_planning_context)
        self.register_tool("get_guest_details", get_guest_details)
        self.register_tool("get_upcoming_guest_visits", get_upcoming_guest_visits)
        self.register_tool("get_guest_visit_calendar_context", get_guest_visit_calendar_context)
        self.register_tool("get_family_routines", get_family_routines)
        self.register_tool("get_family_routines_for_date", get_family_routines_for_date)
        self.register_tool("get_family_routines_in_range", get_family_routines_in_range)
        self.register_tool("check_routine_conflicts", check_routine_conflicts)
        self.register_tool("get_goals", get_goals_tool)
        self.register_tool("get_habits", get_habits_tool)
        self.register_tool("get_digital_twin", get_digital_twin_tool)
        self.register_tool("get_reminders", get_reminders_tool)
        self.register_tool("detect_conflicts", detect_conflicts_tool)
        self.register_tool("get_recommendations", get_recommendations_tool)

tool_registry = ToolRegistry()
