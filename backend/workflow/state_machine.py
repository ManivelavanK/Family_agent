from typing import Dict, Set

# Set of allowed target states from each source state
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    "PENDING": {"RUNNING", "CANCELLED"},
    "RUNNING": {"WAITING", "FAILED", "COMPLETED", "CANCELLED"},
    "WAITING": {"RUNNING", "FAILED", "CANCELLED"},
    "FAILED": {"RUNNING", "CANCELLED"},  # FAILED can transition back to RUNNING during background automatic retries
    "COMPLETED": set(),
    "CANCELLED": set()
}

def validate_transition(current_status: str, next_status: str) -> bool:
    """Returns True if the transition is allowed by the state machine; False otherwise."""
    current = current_status.upper()
    nxt = next_status.upper()
    
    if current not in VALID_TRANSITIONS:
        return False
        
    return nxt in VALID_TRANSITIONS[current]
