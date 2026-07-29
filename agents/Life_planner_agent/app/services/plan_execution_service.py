import datetime
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.plan import Plan, PlanTask, BudgetItem, ItineraryItem, Participant, PlanStatus
from app.models.calendar import CalendarEvent, EventType, EventStatus
from app.ai.schemas import AIPlanDraft, AIPlanExecutionSummary

logger = logging.getLogger("kinnest.services.plan_execution")

class PlanExecutionService:
    @staticmethod
    def execute_approved_plan(
        db: Session,
        family_id: str,
        draft_plan: AIPlanDraft,
        approved: bool = True
    ) -> AIPlanExecutionSummary:
        if not approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan execution rejected. Explicit approval (approved=True) is required."
            )

        try:
            logger.info(f"Starting atomic plan execution for '{draft_plan.title}' (family_id: {family_id})")

            # 1. Create main Plan record
            db_plan = Plan(
                plan_type=draft_plan.plan_type,
                title=draft_plan.title,
                description=draft_plan.description,
                start_date=draft_plan.start_date,
                end_date=draft_plan.end_date,
                number_of_people=draft_plan.number_of_people,
                budget=draft_plan.budget,
                status=PlanStatus.APPROVED,
                location=draft_plan.location
            )
            db.add(db_plan)
            db.flush()  # get db_plan.id

            created_counts = {
                "tasks": 0,
                "budget_items": 0,
                "itinerary_items": 0,
                "participants": 0,
                "calendar_events": 0
            }

            # 2. Create Tasks
            for t_draft in draft_plan.tasks:
                db_task = PlanTask(
                    plan_id=db_plan.id,
                    title=t_draft.title,
                    description=t_draft.description,
                    due_date=t_draft.due_date,
                    priority=t_draft.priority,
                    estimated_cost=t_draft.estimated_cost
                )
                db.add(db_task)
                created_counts["tasks"] += 1

            # 3. Create Budget Items
            for b_draft in draft_plan.budget_breakdown:
                db_budget = BudgetItem(
                    plan_id=db_plan.id,
                    category=b_draft.category,
                    description=b_draft.description,
                    estimated_amount=b_draft.estimated_amount,
                    status=b_draft.status
                )
                db.add(db_budget)
                created_counts["budget_items"] += 1

            # 4. Create Itinerary Items
            for i_draft in draft_plan.itinerary:
                db_itin = ItineraryItem(
                    plan_id=db_plan.id,
                    date=i_draft.date,
                    start_time=i_draft.start_time,
                    end_time=i_draft.end_time,
                    activity=i_draft.activity,
                    location=i_draft.location,
                    estimated_cost=i_draft.estimated_cost,
                    notes=i_draft.notes
                )
                db.add(db_itin)
                created_counts["itinerary_items"] += 1

            # 5. Create Participants
            for p_draft in draft_plan.participants:
                db_part = Participant(
                    plan_id=db_plan.id,
                    name=p_draft.name,
                    age=p_draft.age,
                    relationship=p_draft.relationship,
                    special_requirements=p_draft.special_requirements
                )
                db.add(db_part)
                created_counts["participants"] += 1

            # 6. Create Calendar Events for Itinerary Items or Plan bounds
            if draft_plan.itinerary:
                for i_draft in draft_plan.itinerary:
                    s_time = i_draft.start_time or datetime.time(9, 0)
                    e_time = i_draft.end_time or datetime.time(17, 0)
                    start_dt = datetime.datetime.combine(i_draft.date, s_time, tzinfo=datetime.timezone.utc)
                    end_dt = datetime.datetime.combine(i_draft.date, e_time, tzinfo=datetime.timezone.utc)

                    cal_event = CalendarEvent(
                        title=f"{draft_plan.title}: {i_draft.activity}",
                        description=i_draft.notes or f"Activity for plan #{db_plan.id}",
                        event_type=EventType(draft_plan.plan_type.value) if draft_plan.plan_type.value in EventType.__members__ else EventType.OTHER,
                        start_datetime=start_dt,
                        end_datetime=end_dt,
                        location=i_draft.location or draft_plan.location,
                        status=EventStatus.SCHEDULED,
                        plan_id=db_plan.id,
                        source="AI_PLAN_EXECUTION"
                    )
                    db.add(cal_event)
                    created_counts["calendar_events"] += 1
            elif draft_plan.start_date:
                start_dt = datetime.datetime.combine(draft_plan.start_date, datetime.time(9, 0), tzinfo=datetime.timezone.utc)
                end_dt = datetime.datetime.combine(draft_plan.end_date or draft_plan.start_date, datetime.time(18, 0), tzinfo=datetime.timezone.utc)
                cal_event = CalendarEvent(
                    title=draft_plan.title,
                    description=draft_plan.description,
                    event_type=EventType(draft_plan.plan_type.value) if draft_plan.plan_type.value in EventType.__members__ else EventType.OTHER,
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    location=draft_plan.location,
                    status=EventStatus.SCHEDULED,
                    plan_id=db_plan.id,
                    source="AI_PLAN_EXECUTION"
                )
                db.add(cal_event)
                created_counts["calendar_events"] += 1

            # Single atomic transaction commit
            db.commit()
            db.refresh(db_plan)

            logger.info(f"Successfully executed approved plan #{db_plan.id} with {created_counts}")

            return AIPlanExecutionSummary(
                plan_id=db_plan.id,
                created=created_counts,
                message=f"Approved plan '{db_plan.title}' executed successfully."
            )

        except Exception as exc:
            db.rollback()
            logger.error(f"Plan execution failed and was rolled back: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute plan: {str(exc)}"
            )
