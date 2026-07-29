from sqlalchemy.orm import Session
from app.models.profile import ChildProfile
from app.services.wellness_service import generate_relaxation_suggestions

def handle_query(db: Session, child_id: int, query: str) -> dict:
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    child_name = child.name if child else "Child"

    # Get relaxation suggestions
    relax_res = generate_relaxation_suggestions(db=db, child_id=child_id)
    
    # Extract the first few suggested activities
    act_summaries = []
    for act in relax_res.suggested_activities[:2]:
        act_summaries.append(f"'{act.title}' ({act.description})")

    reply = f"Hi {child_name}, I'm sorry to hear that you might be feeling stressed or down. "
    reply += "Here are a couple of relaxing activities you can try right now: "
    reply += " and ".join(act_summaries) + ". "

    if relax_res.support_recommendation:
        reply += relax_res.support_recommendation

    return {
        "agent": "Wellness Agent",
        "reply": reply,
        "actions": {
            "suggested_activities_count": len(relax_res.suggested_activities),
            "mood_trend_summary": relax_res.mood_trend_summary
        }
    }
