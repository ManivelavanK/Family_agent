import os
import json
import logging
from sqlalchemy.orm import Session
from app.ai.groq_service import _get_groq_client

from app.agents import (
    education_agent,
    routine_agent,
    safety_agent,
    finance_agent,
    wellness_agent,
)

logger = logging.getLogger(__name__)

# Deterministic Keywords Mapping
ROUTING_KEYWORDS = {
    "EDUCATION": ["study", "homework", "exam", "test", "school", "assignment", "subject", "learn", "class", "revision"],
    "FINANCE": ["spend", "spent", "cost", "price", "afford", "buy", "rupees", "pocket money", "allowance", "saving", "expense", "purchase", "₹"],
    "SAFETY": ["going out", "go out", "return at", "return by", "check-in", "check in", "safety", "gps", "location", "arrived"],
    "WELLNESS": ["stressed", "sad", "anxious", "angry", "lonely", "mood", "feel", "happy", "depressed", "wellness"],
    "ROUTINE": ["screen time", "screen", "daily schedule", "routine", "today agenda", "activities", "activity", "tv", "mobile", "gaming"]
}

def route_query_deterministically(query: str) -> str | None:
    """Uses simple rule-based keyword matching to route query to appropriate agent."""
    query_lower = query.lower()
    
    # Track hits for each category
    hits = {category: 0 for category in ROUTING_KEYWORDS}
    for category, keywords in ROUTING_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                hits[category] += 1
                
    # If there is a single category with maximum hits, return it
    sorted_hits = sorted(hits.items(), key=lambda x: x[1], reverse=True)
    if sorted_hits[0][1] > 0:
        return sorted_hits[0][0]
    return None

def route_query_with_llm(query: str) -> str:
    """Uses Groq to classify the user's intent to EDUCATION, FINANCE, SAFETY, WELLNESS, or ROUTINE."""
    client = _get_groq_client()
    if not client:
        return "ROUTINE" # Fallback if no LLM key

    prompt = f"""
    You are an intelligent supervisor agent. Your job is to classify the following user message from a child into one of five categories:
    1. EDUCATION - for queries about study plans, exams, schoolwork, homework, and lessons.
    2. FINANCE - for queries about spending money, allowances, expenses, saving goals, and pricing.
    3. SAFETY - for queries about check-ins, return times, location updates, and emergency status.
    4. WELLNESS - for queries about moods, feelings (stressed, sad, etc.), private diary entries, and relaxation.
    5. ROUTINE - for queries about daily schedule/agenda, non-school activities, and digital wellness/screen time usage.

    User message: "{query}"

    Respond ONLY with a JSON object in this format:
    {{"category": "EDUCATION|FINANCE|SAFETY|WELLNESS|ROUTINE"}}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        parsed = json.loads(response.choices[0].message.content.strip())
        category = parsed.get("category", "ROUTINE").upper()
        if category in ROUTING_KEYWORDS:
            return category
    except Exception as e:
        logger.error(f"Groq routing classification failed: {e}")
    
    return "ROUTINE"

def route_and_execute(db: Session, child_id: int, query: str) -> dict:
    """
    Orchestrates the Children Agent routing flow:
    1. Runs deterministic router first.
    2. Falls back to Groq classification for ambiguous requests.
    3. Calls the selected child agent's handle_query.
    """
    category = route_query_deterministically(query)
    if not category:
        logger.info(f"[SUPERVISOR] Deterministic routing inconclusive. Calling LLM classification for: '{query}'")
        category = route_query_with_llm(query)
    else:
        logger.info(f"[SUPERVISOR] Deterministically routed query to {category}: '{query}'")

    if category == "EDUCATION":
        res = education_agent.handle_query(db, child_id, query)
    elif category == "FINANCE":
        res = finance_agent.handle_query(db, child_id, query)
    elif category == "SAFETY":
        res = safety_agent.handle_query(db, child_id, query)
    elif category == "WELLNESS":
        res = wellness_agent.handle_query(db, child_id, query)
    else:
        res = routine_agent.handle_query(db, child_id, query)

    res["routed_category"] = category
    return res
