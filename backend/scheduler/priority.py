from typing import Dict

# Map priority categories to numerical values (higher = executes first)
PRIORITY_VALUES: Dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "NORMAL": 2,
    "LOW": 1
}

def get_priority_weight(priority: str) -> int:
    """Returns sorting weight for a priority level, defaulting to NORMAL (2)."""
    return PRIORITY_VALUES.get(priority.upper(), 2)
