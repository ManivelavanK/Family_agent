import time
import logging
from datetime import datetime
from backend.event_router.models import Event, RoutingRecord
from backend.event_router.rules import EVENT_WORKFLOW_MAP, EVENT_CONTEXT_MAP
from backend.context import context_manager
from backend.workflow import workflow_engine

logger = logging.getLogger("orchestrator.event_router.dispatcher")

class EventDispatcher:
    def __init__(self, router_history_store):
        self.history = router_history_store

    async def dispatch(self, event: Event) -> RoutingRecord:
        """Looks up the target workflow, merges relevant shared context, triggers the execution, and logs details."""
        start_time = time.time()
        record = RoutingRecord(
            event_id=event.event_id,
            event_type=event.event_type,
            source_agent=event.source_agent,
            status="PENDING",
            logs=[f"Event routing initialized for {event.event_type}."]
        )
        self.history.add_record(record)
        
        # 1. Map to target workflow blueprint
        workflow_name = EVENT_WORKFLOW_MAP.get(event.event_type)
        if not workflow_name:
            err = f"No workflow definition mapped to event type: '{event.event_type}'."
            record.status = "FAILED"
            record.logs.append(err)
            logger.error(err)
            return record

        record.workflow_name = workflow_name
        
        # 2. Map and read relevant Shared Context Category
        context_category = EVENT_CONTEXT_MAP.get(event.event_type)
        combined_payload = event.payload.copy()
        
        if context_category:
            try:
                # Retrieve from context manager
                wrapper = await context_manager.get_wrapper(context_category)
                # Merge context data under a context_state field
                combined_payload["shared_context_state"] = wrapper.data
                record.logs.append(f"Successfully read and merged Shared Context category '{context_category}' (Version {wrapper.version}).")
            except Exception as e:
                record.logs.append(f"Warning: Failed to retrieve shared context category '{context_category}': {e}")
        
        # 3. Trigger Workflow Engine
        try:
            instance = await workflow_engine.trigger_workflow(workflow_name, combined_payload)
            record.workflow_id = instance.workflow_id
            record.status = "ROUTED"
            record.logs.append(f"Successfully triggered workflow '{workflow_name}' with ID: {instance.workflow_id}.")
        except Exception as e:
            record.status = "FAILED"
            err = f"Failed to trigger workflow '{workflow_name}': {e}"
            record.logs.append(err)
            logger.error(err, exc_info=True)

        record.execution_duration = time.time() - start_time
        return record
