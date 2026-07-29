import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.memory import AgentMemory
from app.models.reflection import Reflection
from app.services.ai_service import call_groq

logger = logging.getLogger(__name__)


def generate_reflection(db: Session, item_name: str) -> dict | Reflection:
    memories = (
        db.query(AgentMemory)
        .filter(func.lower(AgentMemory.item_name) == item_name.lower())
        .all()
    )

    if not memories:
        return {"message": f"No memories found for '{item_name}'."}

    consumption_values = [
        m.memory_value
        for m in memories
        if "consumption" in m.memory_type
    ]

    if not consumption_values:
        return {"message": f"No consumption pattern available for '{item_name}'."}

    # Use LLM to generate a meaningful insight from memory
    memory_summary = "\n".join(consumption_values[-5:])  # last 5 entries
    prompt = f"""You are a family grocery analyst.

Based on these consumption memory records for '{item_name}':
{memory_summary}

Generate:
1. A one-sentence insight about consumption pattern
2. A one-sentence recommendation for the family

Return only plain text, 2 lines."""

    try:
        ai_response = call_groq(prompt, temperature=0.4, max_tokens=150)
        lines = [line.strip() for line in ai_response.strip().splitlines() if line.strip()]
        insight = lines[0] if lines else f"Family has {len(consumption_values)} consumption records for {item_name}."
        recommendation = lines[1] if len(lines) > 1 else f"Monitor {item_name} usage regularly."
    except Exception as e:
        logger.error("Reflection AI call failed for '%s': %s", item_name, e)
        insight = f"Family has recorded {len(consumption_values)} consumption patterns for {item_name}."
        recommendation = f"Maintain regular monitoring of {item_name}."

    existing = (
        db.query(Reflection)
        .filter(func.lower(Reflection.item_name) == item_name.lower())
        .first()
    )

    if existing:
        existing.insight = insight
        existing.recommendation = recommendation
        db.commit()
        db.refresh(existing)
        return existing

    reflection = Reflection(
        item_name=item_name,
        insight=insight,
        recommendation=recommendation,
    )
    db.add(reflection)
    db.commit()
    db.refresh(reflection)
    logger.info("Reflection created for '%s'.", item_name)
    return reflection


def get_reflections(db: Session) -> list[Reflection]:
    return db.query(Reflection).order_by(Reflection.created_at.desc()).all()
