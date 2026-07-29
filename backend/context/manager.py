import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from backend.context.models import ContextWrapper, AuditEvent
from backend.context.store import InMemoryStore

logger = logging.getLogger("orchestrator.context")

# Default values mapping to initialize empty contexts cleanly
DEFAULT_SCHEMAS = {
    "profile": {"family_id": "default_family", "family_name": "KinNest Family", "members": [], "active_admin": "", "family_password_hash": ""},
    "shopping": {"shared_shopping_list": [], "total_estimated_cost": 0.0, "last_updated_by": ""},
    "budget": {"monthly_budget": 0.0, "weekly_budget": 0.0, "current_spending": 0.0, "remaining_budget": 0.0, "pending_purchase_requests": []},
    "health": {"active_emergencies": [], "grandparent_alerts": [], "medicine_reminders": [], "upcoming_appointments": [], "health_summary": ""},
    "child": {"homework_status": {}, "attendance": {}, "exams": [], "study_progress": {}, "parent_notifications": []},
    "baby": {"feeding_schedule": [], "sleep_schedule": [], "vaccinations": [], "growth_milestones": [], "diaper_records": []},
    "planner": {"today_tasks": [], "family_events": [], "upcoming_meetings": [], "shared_calendar": [], "pending_workflows": []}
}

class SharedContextManager:
    def __init__(self):
        self.store = InMemoryStore()
        # Initialize thread-safe async locks per category namespace
        self._locks: Dict[str, asyncio.Lock] = {
            category: asyncio.Lock() for category in DEFAULT_SCHEMAS.keys()
        }

    def _validate_category(self, category: str):
        if category not in DEFAULT_SCHEMAS:
            raise ValueError(f"Invalid context category: '{category}'")

    async def get_wrapper(self, category: str) -> ContextWrapper:
        """Returns the full metadata wrapper for a category. If none exists, creates a default wrapper."""
        self._validate_category(category)
        
        async with self._locks[category]:
            wrapper = await self.store.get_context(category)
            if not wrapper:
                # Initialize empty default
                wrapper = ContextWrapper(
                    category=category,
                    data=DEFAULT_SCHEMAS[category].copy(),
                    version=1,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    last_updated_by="system"
                )
                await self.store.save_context(category, wrapper)
            return wrapper

    async def update_context(self, category: str, data: Dict[str, Any], updated_by: str, ttl_seconds: Optional[float] = None) -> ContextWrapper:
        """Replaces a category context, increments version, logs action, and updates modification time."""
        self._validate_category(category)
        
        async with self._locks[category]:
            existing = await self.store.get_context(category)
            version = (existing.version + 1) if existing else 1
            created = existing.created_at if existing else datetime.utcnow()
            
            expires = None
            if ttl_seconds is not None:
                expires = datetime.utcnow() + timedelta(seconds=ttl_seconds)

            wrapper = ContextWrapper(
                category=category,
                data=data,
                version=version,
                created_at=created,
                updated_at=datetime.utcnow(),
                expires_at=expires,
                last_updated_by=updated_by
            )
            
            await self.store.save_context(category, wrapper)
            
            # Log action
            logger.info(f"{updated_by.capitalize()} updated {category.capitalize()} Context (Version {version})")
            await self.store.log_event(AuditEvent(
                agent_name=updated_by,
                category=category,
                operation="WRITE",
                details={"version": version, "expires_at": expires.isoformat() if expires else None}
            ))
            return wrapper

    async def patch_context(self, category: str, partial_data: Dict[str, Any], updated_by: str) -> ContextWrapper:
        """Merges changes into category context, increments version, logs action, and updates modification time."""
        self._validate_category(category)
        
        async with self._locks[category]:
            existing = await self.store.get_context(category)
            
            # Load current data or fallback to defaults
            current_data = existing.data.copy() if existing else DEFAULT_SCHEMAS[category].copy()
            version = (existing.version + 1) if existing else 1
            created = existing.created_at if existing else datetime.utcnow()
            expires = existing.expires_at if existing else None
            
            # Merge dictionary fields
            for key, val in partial_data.items():
                if isinstance(val, dict) and isinstance(current_data.get(key), dict):
                    # Shallow dict merge
                    current_data[key].update(val)
                elif isinstance(val, list) and isinstance(current_data.get(key), list):
                    # List extend
                    current_data[key].extend(val)
                else:
                    current_data[key] = val
                    
            wrapper = ContextWrapper(
                category=category,
                data=current_data,
                version=version,
                created_at=created,
                updated_at=datetime.utcnow(),
                expires_at=expires,
                last_updated_by=updated_by
            )
            
            await self.store.save_context(category, wrapper)
            
            # Log action
            logger.info(f"{updated_by.capitalize()} patched {category.capitalize()} Context (Version {version})")
            await self.store.log_event(AuditEvent(
                agent_name=updated_by,
                category=category,
                operation="PATCH",
                details={"version": version}
            ))
            return wrapper

    async def delete_context(self, category: str, deleted_by: str):
        """Clears a context category back to default empty schema and increments version."""
        self._validate_category(category)
        
        async with self._locks[category]:
            existing = await self.store.get_context(category)
            version = (existing.version + 1) if existing else 1
            created = existing.created_at if existing else datetime.utcnow()
            
            wrapper = ContextWrapper(
                category=category,
                data=DEFAULT_SCHEMAS[category].copy(),
                version=version,
                created_at=created,
                updated_at=datetime.utcnow(),
                last_updated_by=deleted_by
            )
            
            await self.store.save_context(category, wrapper)
            
            logger.info(f"{deleted_by.capitalize()} cleared {category.capitalize()} Context")
            await self.store.log_event(AuditEvent(
                agent_name=deleted_by,
                category=category,
                operation="DELETE",
                details={"version": version}
            ))

    async def process_bus_event(self, event_type: str, payload: Dict[str, Any], sender: str):
        """Translates Agent Bus events to automatic shared context updates."""
        try:
            event_upper = event_type.upper()
            
            if event_upper == "LOW_STOCK":
                item_name = payload.get("item_name", "Unknown item")
                quantity = payload.get("quantity", "1")
                # Append to shared shopping list
                item_data = {"name": item_name, "quantity": str(quantity), "status": "PENDING", "requested_by": sender}
                await self.patch_context("shopping", {"shared_shopping_list": [item_data]}, sender)
                
            elif event_upper == "EMERGENCY":
                emergency_id = payload.get("emergency_id", "EMG-911")
                desc = payload.get("description", "Emergency alert triggered")
                sev = payload.get("severity", "HIGH")
                emergency_data = {"emergency_id": emergency_id, "description": desc, "severity": sev, "resolved": False}
                await self.patch_context("health", {"active_emergencies": [emergency_data]}, sender)
                
            elif event_upper == "HOMEWORK_COMPLETED":
                hw_id = payload.get("homework_id")
                student = payload.get("student_name", "student")
                if hw_id:
                    await self.patch_context("child", {"homework_status": {hw_id: "COMPLETED"}, "parent_notifications": [f"{student} completed homework: {hw_id}"]}, sender)
                    
            elif event_upper == "BABY_FEEDING_DONE":
                time_str = payload.get("time", datetime.utcnow().isoformat())
                feed_type = payload.get("feed_type", "milk")
                amount = payload.get("amount", "100ml")
                feeding_data = {"time": time_str, "feed_type": feed_type, "amount": amount, "logged_by": sender}
                await self.patch_context("baby", {"feeding_schedule": [feeding_data]}, sender)
                
            elif event_upper == "BUDGET_UPDATED":
                monthly = payload.get("monthly_budget")
                weekly = payload.get("weekly_budget")
                patch_data = {}
                if monthly is not None:
                    patch_data["monthly_budget"] = float(monthly)
                if weekly is not None:
                    patch_data["weekly_budget"] = float(weekly)
                if patch_data:
                    await self.patch_context("budget", patch_data, sender)
                    
            elif event_upper == "MEDICINE_TAKEN":
                med_name = payload.get("medicine_name")
                dosage = payload.get("dosage", "1 tab")
                if med_name:
                    rem_data = {"medicine_name": med_name, "dosage": dosage, "scheduled_time": datetime.utcnow().isoformat(), "taken": True}
                    await self.patch_context("health", {"medicine_reminders": [rem_data]}, sender)
                    
        except Exception as e:
            logger.error(f"Failed to process bus event '{event_type}' for context syncing: {e}", exc_info=True)

    async def cleanup_expired_contexts(self):
        """Scans context caches and resets expired objects."""
        now = datetime.utcnow()
        for category in list(DEFAULT_SCHEMAS.keys()):
            async with self._locks[category]:
                wrapper = await self.store.get_context(category)
                if wrapper and wrapper.expires_at and wrapper.expires_at < now:
                    logger.info(f"Removing expired Shared Context category: '{category}' (Expired at: {wrapper.expires_at})")
                    # Reset context data to empty default
                    new_wrapper = ContextWrapper(
                        category=category,
                        data=DEFAULT_SCHEMAS[category].copy(),
                        version=wrapper.version + 1,
                        created_at=wrapper.created_at,
                        updated_at=datetime.utcnow(),
                        last_updated_by="system-cleanup"
                    )
                    await self.store.save_context(category, new_wrapper)
                    await self.store.log_event(AuditEvent(
                        agent_name="system-cleanup",
                        category=category,
                        operation="EXPIRE",
                        details={"version": new_wrapper.version}
                    ))
