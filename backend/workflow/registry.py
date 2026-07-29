import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.workflow.models import WorkflowDefinition, StepDefinition, WorkflowInstance
from backend.workflow.state_machine import validate_transition

class WorkflowRegistry:
    def __init__(self):
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self._register_default_definitions()

    def _register_default_definitions(self):
        """Pre-populates definition-driven workflow schemas."""
        
        # 1. LOW_STOCK_WORKFLOW
        self.definitions["LOW_STOCK_WORKFLOW"] = WorkflowDefinition(
            name="LOW_STOCK_WORKFLOW",
            description="Orchestrates grocery stock tracking, budget approval, and shopping tasks.",
            trigger_agent="mother",
            participants=["mother", "father", "planner"],
            steps=[
                StepDefinition(name="log_stock_context", handler_name="low_stock_log_context"),
                StepDefinition(name="request_budget_approval", handler_name="low_stock_request_approval", retryable=True),
                StepDefinition(name="create_shopping_task", handler_name="low_stock_create_task"),
                StepDefinition(name="notify_family", handler_name="notify_family_step")
            ]
        )

        # 2. GRANDPARENT_EMERGENCY_WORKFLOW
        self.definitions["GRANDPARENT_EMERGENCY_WORKFLOW"] = WorkflowDefinition(
            name="GRANDPARENT_EMERGENCY_WORKFLOW",
            description="Broadcasts critical grandparent emergencies to all family members.",
            trigger_agent="grandparent",
            participants=["grandparent", "mother", "father", "children", "baby", "planner"],
            steps=[
                StepDefinition(name="log_emergency_context", handler_name="emergency_log_context"),
                StepDefinition(name="notify_parents", handler_name="emergency_notify_parents", retryable=True),
                StepDefinition(name="notify_children", handler_name="emergency_notify_children"),
                StepDefinition(name="notify_baby_care", handler_name="emergency_notify_baby_care"),
                StepDefinition(name="create_planner_alert", handler_name="emergency_planner_alert")
            ]
        )

        # 3. BABY_VACCINATION_WORKFLOW
        self.definitions["BABY_VACCINATION_WORKFLOW"] = WorkflowDefinition(
            name="BABY_VACCINATION_WORKFLOW",
            description="Coordinates baby vaccinations schedules and parental reminders.",
            trigger_agent="baby",
            participants=["baby", "planner", "father", "mother", "grandparent"],
            steps=[
                StepDefinition(name="log_vaccination_due", handler_name="vaccination_log_context"),
                StepDefinition(name="create_vaccine_appointment", handler_name="vaccination_create_appointment"),
                StepDefinition(name="send_parent_reminders", handler_name="vaccination_notify_parents", retryable=True)
            ]
        )

        # 4. CHILD_EXAM_WORKFLOW
        self.definitions["CHILD_EXAM_WORKFLOW"] = WorkflowDefinition(
            name="CHILD_EXAM_WORKFLOW",
            description="Helps kids prepare for upcoming academic exams with parental check-ins.",
            trigger_agent="children",
            participants=["children", "planner", "father", "mother", "grandparent"],
            steps=[
                StepDefinition(name="log_exam_context", handler_name="exam_log_context"),
                StepDefinition(name="create_study_task", handler_name="exam_create_study_task"),
                StepDefinition(name="alert_family", handler_name="exam_alert_parents", retryable=True)
            ]
        )

        # 5. MONTHLY_GROCERY_WORKFLOW
        self.definitions["MONTHLY_GROCERY_WORKFLOW"] = WorkflowDefinition(
            name="MONTHLY_GROCERY_WORKFLOW",
            description="Automates bulk monthly grocery stock-taking and forecasting.",
            trigger_agent="planner",
            participants=["planner", "mother", "father"],
            steps=[
                StepDefinition(name="query_mother_inventory", handler_name="grocery_query_inventory", retryable=True),
                StepDefinition(name="forecast_consumption", handler_name="grocery_forecast_needs"),
                StepDefinition(name="allocate_father_budget", handler_name="grocery_allocate_budget"),
                StepDefinition(name="publish_shopping_plan", handler_name="grocery_publish_plan")
            ]
        )

    def create_instance(self, name: str, payload: dict) -> WorkflowInstance:
        """Instantiates a workflow blueprint and registers it."""
        definition = self.definitions.get(name)
        if not definition:
            raise ValueError(f"Workflow definition '{name}' not found.")
            
        instance_id = str(uuid.uuid4())
        instance = WorkflowInstance(
            workflow_id=instance_id,
            workflow_name=name,
            trigger_agent=definition.trigger_agent,
            participants=definition.participants,
            status="PENDING",
            context_payload=payload,
            logs=[f"Workflow {name} initialized."]
        )
        
        # Populate initial step states
        for step in definition.steps:
            instance.step_states[step.name] = "PENDING"
            
        self.instances[instance_id] = instance
        return instance

    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        return self.instances.get(instance_id)

    def get_all_instances(self) -> List[WorkflowInstance]:
        return list(self.instances.values())

    def update_status(self, instance_id: str, new_status: str) -> bool:
        """Safely updates an instance's state using state machine validation."""
        instance = self.instances.get(instance_id)
        if not instance:
            return False
            
        if validate_transition(instance.status, new_status):
            old = instance.status
            instance.status = new_status
            instance.updated_time = datetime.utcnow()
            instance.logs.append(f"State transitioned from {old} to {new_status}.")
            return True
        return False

# Global instance of registry
registry = WorkflowRegistry()
