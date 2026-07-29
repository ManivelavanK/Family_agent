from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.context.models import ContextWrapper, AuditEvent

class ContextStoreInterface:
    """Abstract interface defining required store operations for pluggability."""
    async def get_context(self, category: str) -> Optional[ContextWrapper]:
        raise NotImplementedError()

    async def save_context(self, category: str, wrapper: ContextWrapper):
        raise NotImplementedError()

    async def delete_context(self, category: str):
        raise NotImplementedError()

    async def log_event(self, event: AuditEvent):
        raise NotImplementedError()

    async def get_events(self, category: Optional[str] = None, limit: int = 50) -> List[AuditEvent]:
        raise NotImplementedError()

class InMemoryStore(ContextStoreInterface):
    """Memory-cached implementation of the shared context store."""
    def __init__(self):
        self._cache: Dict[str, ContextWrapper] = {}
        self._audit_trail: List[AuditEvent] = []

    async def get_context(self, category: str) -> Optional[ContextWrapper]:
        return self._cache.get(category)

    async def save_context(self, category: str, wrapper: ContextWrapper):
        self._cache[category] = wrapper

    async def delete_context(self, category: str):
        if category in self._cache:
            del self._cache[category]

    async def log_event(self, event: AuditEvent):
        self._audit_trail.append(event)
        # Cap log history for performance (e.g. keep last 500 events)
        if len(self._audit_trail) > 500:
            self._audit_trail = self._audit_trail[-500:]

    async def get_events(self, category: Optional[str] = None, limit: int = 50) -> List[AuditEvent]:
        filtered = self._audit_trail
        if category:
            filtered = [e for e in self._audit_trail if e.category == category]
        # Return descending order (newest first)
        return sorted(filtered, key=lambda e: e.timestamp, reverse=True)[:limit]
