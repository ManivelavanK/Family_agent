from typing import Dict

# Map incoming Event Type to Target Workflow Name
EVENT_WORKFLOW_MAP: Dict[str, str] = {
    "LOW_STOCK": "LOW_STOCK_WORKFLOW",
    "GRANDPARENT_EMERGENCY": "GRANDPARENT_EMERGENCY_WORKFLOW",
    "BABY_VACCINE_DUE": "BABY_VACCINATION_WORKFLOW",
    "CHILD_EXAM_CREATED": "CHILD_EXAM_WORKFLOW",
    "MONTH_END": "MONTHLY_GROCERY_WORKFLOW"
}

# Map incoming Event Type to associated Shared Context category
EVENT_CONTEXT_MAP: Dict[str, str] = {
    "LOW_STOCK": "shopping",
    "GRANDPARENT_EMERGENCY": "health",
    "BABY_VACCINE_DUE": "baby",
    "CHILD_EXAM_CREATED": "child",
    "MONTH_END": "planner"
}
