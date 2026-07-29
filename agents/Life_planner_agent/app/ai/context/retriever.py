import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.services.plan_service import PlanService
from app.services.calendar_service import CalendarService
from app.services.memory_service import MemoryService
from app.services.routine_service import RoutineService

class ContextRetriever:
    @staticmethod
    def get_planning_context(
        db: Session,
        plan_id: Optional[int] = None,
        family_id: str = "default_family",
        query_date: Optional[datetime.date] = None,
        family_agent_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        target_date = query_date or datetime.date.today()

        context: Dict[str, Any] = {
            "current_date": str(target_date),
            "existing_plans_count": db.query(Plan).count(),
            "recent_plans": [],
            "upcoming_calendar_events": [],
            "family_memories": [],
            "family_routines": [],
            "cross_agent_family_context": family_agent_context or {}
        }

        if plan_id:
            plan = PlanService.get_plan_by_id(db, plan_id)
            if plan:
                context["current_plan"] = {
                    "id": plan.id,
                    "title": plan.title,
                    "plan_type": plan.plan_type.value,
                    "budget": plan.budget,
                    "number_of_people": plan.number_of_people,
                    "tasks_count": len(plan.tasks),
                    "budget_items_count": len(plan.budget_items),
                    "participants_count": len(plan.participants)
                }

        recent_plans = db.query(Plan).order_by(Plan.created_at.desc()).limit(5).all()
        for p in recent_plans:
            context["recent_plans"].append({
                "id": p.id,
                "title": p.title,
                "plan_type": p.plan_type.value,
                "status": p.status.value,
                "budget": p.budget
            })

        upcoming_events = CalendarService.get_upcoming_events(db, limit=5)
        context["upcoming_calendar_events"] = [
            {
                "id": e.id,
                "title": e.title,
                "event_type": e.event_type.value,
                "start": str(e.start_datetime),
                "end": str(e.end_datetime)
            } for e in upcoming_events
        ]

        family_memories = MemoryService.get_relevant_memories(db, family_id=family_id, limit=10)
        context["family_memories"] = [
            {
                "id": m.id,
                "memory_type": m.memory_type.value,
                "title": m.title,
                "content": m.content,
                "importance": m.importance
            } for m in family_memories
        ]

        from app.services.routine_service import RoutineService
        routines = RoutineService.get_all_routines(db, family_id=family_id, limit=20)
        context["family_routines"] = [r.to_dict() for r in routines]

        return context
