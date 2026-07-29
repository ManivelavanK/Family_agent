import logging
import json
from datetime import date, timedelta
from sqlalchemy.orm import Session
from collections import Counter

from app.models.cognitive import CognitiveLog
from app.schemas.cognitive import CognitiveJournalCreate
from app.ai.llm import call_llm
from app.ai.groq_service import add_journal_entry

logger = logging.getLogger(__name__)


def save_cognitive_journal(db: Session, journal_in: CognitiveJournalCreate) -> CognitiveLog:
    """
    Saves or updates the grandparent's daily reflection log.
    Calculates a detail-oriented Memory Score based on log length and mood positivity.
    """
    today = date.today()
    logger.info("Cognitive Service: Saving daily reflection log for date: %s", today)

    # Calculate dynamic memory score (length-based density check + mood modifier)
    length_points = min(50, len(journal_in.entry) // 4)  # up to 50 points for details
    base_points = 45
    mood_bonus = 5 if journal_in.mood.lower() in ["happy", "cheerful", "excited"] else 0
    memory_score = min(100, base_points + length_points + mood_bonus)

    existing = db.query(CognitiveLog).filter(CognitiveLog.date == today).first()
    if existing:
        existing.journal_entry = journal_in.entry
        existing.mood = journal_in.mood
        existing.memory_score = memory_score
        db_log = existing
    else:
        db_log = CognitiveLog(
            date=today,
            journal_entry=journal_in.entry,
            mood=journal_in.mood,
            memory_score=memory_score
        )
        db.add(db_log)

    db.commit()
    db.refresh(db_log)

    # Populate temporary LLM memory context
    add_journal_entry(journal_in.entry)
    logger.info("Cognitive Service: Reflection saved successfully. Score: %d", memory_score)
    return db_log


def generate_personalized_cognitive_quiz(db: Session) -> dict:
    """
    Retrieves recent logs to feed as context for a custom Groq-generated memory quiz.
    """
    logger.info("Cognitive Service: Preparing personalized memory quiz context...")
    logs = db.query(CognitiveLog).order_by(CognitiveLog.date.desc()).limit(3).all()
    
    context_lines = []
    for log in logs:
        context_lines.append(f"On {log.date.isoformat()}, they logged: '{log.journal_entry}' (Mood: {log.mood})")
        
    context = "\n".join(context_lines) if context_lines else "General details. No recent reflection logs available."

    system_prompt = (
        "You are an expert geriatric cognitive therapist assistant.\n"
        "Generate a simple, engaging memory recollection multiple-choice quiz of 2 questions "
        "specifically testing the grandparent on the facts present in their recent journal reflections.\n"
        "If no recent logs exist, test them on standard general knowledge facts.\n"
        "You must output a valid JSON object matching this schema:\n"
        "{\n"
        "  \"quiz_title\": \"string\",\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"question\": \"string\",\n"
        "      \"options\": [\"string\", \"string\", \"string\", \"string\"],\n"
        "      \"correct_answer\": \"string\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )
    user_prompt = f"Recent reflection logs:\n{context}\n\nGenerate the memory quiz."

    try:
        response_text = call_llm(system_prompt, user_prompt, json_response=True)
        return json.loads(response_text)
    except Exception as e:
        logger.error("Failed to generate personalized cognitive quiz: %s. Using baseline.", e)
        return {
            "quiz_title": "Daily Memory Challenge",
            "questions": [
                {
                    "question": "Which of these is a healthy morning activity?",
                    "options": ["Light walking", "Skipping breakfast", "Staring at screens", "Heavy lifting"],
                    "correct_answer": "Light walking"
                }
            ]
        }


def get_cognitive_report_summary(db: Session) -> dict:
    """
    Compiles Weekly Cognitive Score, mood trends, and queries Groq for custom exercises.
    """
    logger.info("Cognitive Service: Compiling weekly report card...")
    # Fetch last 7 entries
    logs = db.query(CognitiveLog).order_by(CognitiveLog.date.desc()).limit(7).all()

    if not logs:
        return {
            "weekly_cognitive_score": 0.0,
            "mood_trend": "No logs recorded",
            "daily_scores": [],
            "brain_exercises": [
                "Practice reciting the alphabet backwards.",
                "Draw a clock showing the time 10 minutes past 11."
            ]
        }

    # Calculate average score
    weekly_score = sum(log.memory_score for log in logs) / len(logs)

    # Determine mood trend
    moods = [log.mood for log in logs]
    mood_counts = Counter(moods)
    most_common_mood = mood_counts.most_common(1)[0][0]

    # Daily list
    daily_list = [
        {"date": str(log.date), "score": log.memory_score, "mood": log.mood}
        for log in logs
    ]

    # Generate custom exercises via Groq based on last logged context
    last_log = logs[0].journal_entry
    system_prompt = (
        "You are a cognitive therapy coach. Provide exactly 2 custom brain exercises, games, or puzzles "
        "appropriate for an elderly grandparent, utilizing details from their latest reflection entry to trigger mental recall.\n"
        "Output the result as a simple JSON list of strings, for example: [\"exercise 1\", \"exercise 2\"]"
    )
    user_prompt = f"Grandparent's last entry: '{last_log}'"

    try:
        response_text = call_llm(system_prompt, user_prompt, json_response=True)
        exercises = json.loads(response_text)
        if not isinstance(exercises, list):
            exercises = [str(exercises)]
    except Exception as e:
        logger.error("Failed to fetch Groq exercises: %s. Using default.", e)
        exercises = [
            f"Think about your reflection from {logs[0].date.strftime('%A')} and write down 3 nouns mentioned.",
            "Complete a 5-minute crossword or word-puzzle."
        ]

    return {
        "weekly_cognitive_score": round(weekly_score, 2),
        "mood_trend": f"Mainly {most_common_mood}",
        "daily_scores": daily_list,
        "brain_exercises": exercises
    }
