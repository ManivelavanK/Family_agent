import os
import json
import logging
import re
from datetime import date, time, datetime
from sqlalchemy.orm import Session
from app.models.safety import CheckInLog
from app.models.profile import ChildProfile
from app.ai.groq_service import _get_groq_client
from app.services.cross_agent_service import create_or_update_check_in
from app.schemas.cross_agent import ChildCheckInCreate

logger = logging.getLogger(__name__)

def handle_query(db: Session, child_id: int, query: str) -> dict:
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    child_name = child.name if child else "Child"

    # Default check-in parameters
    expected_time = time(20, 0) # default 8 PM
    location = "Outside"
    
    # Try parsing query using Groq if available
    client = _get_groq_client()
    if client:
        try:
            prompt = f"""
            Analyze this message from a child: "{query}"
            Extract check-in information:
            1. expected_return_time: string in HH:MM:SS format (24 hour) or null
            2. location_note: string describing destination or null
            
            Return ONLY a raw JSON object:
            {{
              "expected_return_time": "20:00:00",
              "location_note": "Outside"
            }}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            parsed = json.loads(response.choices[0].message.content.strip())
            t_str = parsed.get("expected_return_time")
            if t_str:
                expected_time = datetime.strptime(t_str, "%H:%M:%S").time()
            location = parsed.get("location_note") or "Outside"
        except Exception as e:
            logger.error(f"Groq parsing failed in safety agent: {e}")
            # fallback to simple regex
            match = re.search(r"(\d+)\s*(?:pm|am|o'clock|)?", query.lower())
            if match:
                hour = int(match.group(1))
                if "pm" in query.lower() or (hour < 12 and "pm" not in query.lower() and hour >= 1 and hour <= 8):
                    hour += 12
                expected_time = time(hour % 24, 0)
    else:
        # regex parser fallback
        match = re.search(r"(\d+)", query)
        if match:
            val = int(match.group(1))
            if val <= 12:
                # assume PM if afternoon/evening statement
                expected_time = time((val + 12) % 24, 0)
            else:
                expected_time = time(val % 24, 0)

    # Save to database using check-in creation service
    check_in_data = ChildCheckInCreate(
        child_id=child_id,
        date=date.today(),
        expected_return_time=expected_time,
        location_note=location,
        status="EXPECTED"
    )
    
    db_log = create_or_update_check_in(db=db, check_in_in=check_in_data)

    return {
        "agent": "Safety Agent",
        "reply": f"Ok {child_name}, I've registered your check-in. Expected return at {db_log.expected_return_time.strftime('%I:%M %p')}. Stay safe!",
        "actions": {
            "check_in_id": db_log.id,
            "expected_return_time": db_log.expected_return_time.isoformat(),
            "status": db_log.status
        }
    }
