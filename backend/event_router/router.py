import logging
from typing import Dict, List, Optional
from backend.event_router.models import Event, RoutingRecord

logger = logging.getLogger("orchestrator.event_router.history")

class EventRouterHistory:
    def __init__(self):
        self.events: Dict[str, Event] = {}
        self.records: Dict[str, RoutingRecord] = {}

    def add_event(self, event: Event):
        self.events[event.event_id] = event

    def add_record(self, record: RoutingRecord):
        self.records[record.event_id] = record

    def get_event(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    def get_record(self, event_id: str) -> Optional[RoutingRecord]:
        return self.records.get(event_id)

    def get_all_records(self) -> List[RoutingRecord]:
        return list(self.records.values())

    async def retry_failed_dispatches(self, dispatcher):
        """Scans failed routing logs and re-attempts dispatching up to 3 times."""
        for event_id, record in list(self.records.items()):
            if record.status == "FAILED" and record.retries < 3:
                event = self.events.get(event_id)
                if not event:
                    continue
                
                record.retries += 1
                record.status = "RETRYING"
                record.logs.append(f"Retrying event dispatch (Attempt {record.retries}/3)...")
                logger.info(f"Retrying event dispatch for {event_id} ({event.event_type}). Attempt {record.retries}/3.")
                
                # Re-run dispatch
                await dispatcher.dispatch(event)
