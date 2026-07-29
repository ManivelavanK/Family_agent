from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app.models.wellness import DiaryEntry, RelaxationLog
from app.models.profile import ChildProfile
from app.schemas.wellness import (
    DiaryEntryCreate,
    DiaryEntryUpdate,
    RelaxationResponse,
    RelaxationActivity,
    RelaxationLogCreate,
)
from app.services.age_adaptation_service import classify_age_group

NEGATIVE_MOODS = {"sad", "anxious", "stressed", "angry", "lonely", "overwhelmed", "fearful", "down"}


# --- Diary Entry CRUD ---

def create_diary_entry(db: Session, entry_in: DiaryEntryCreate) -> DiaryEntry:
    db_entry = DiaryEntry(
        child_id=entry_in.child_id,
        date=entry_in.date,
        title=entry_in.title,
        content=entry_in.content,
        mood=entry_in.mood.lower().strip() if entry_in.mood else None,
        tags=entry_in.tags or [],
        share_with_parent=entry_in.share_with_parent or False
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def get_child_diary_entries(db: Session, child_id: int) -> List[DiaryEntry]:
    return db.query(DiaryEntry).filter(
        DiaryEntry.child_id == child_id
    ).order_by(DiaryEntry.date.desc(), DiaryEntry.id.desc()).all()

def get_diary_entry_by_id(db: Session, child_id: int, entry_id: int) -> Optional[DiaryEntry]:
    return db.query(DiaryEntry).filter(
        DiaryEntry.id == entry_id,
        DiaryEntry.child_id == child_id
    ).first()

def update_diary_entry(db: Session, entry_id: int, update_in: DiaryEntryUpdate) -> Optional[DiaryEntry]:
    db_entry = db.query(DiaryEntry).filter(DiaryEntry.id == entry_id).first()
    if not db_entry:
        return None
        
    if update_in.title is not None:
        db_entry.title = update_in.title
    if update_in.content is not None:
        db_entry.content = update_in.content
    if update_in.mood is not None:
        db_entry.mood = update_in.mood.lower().strip()
    if update_in.tags is not None:
        db_entry.tags = update_in.tags
    if update_in.share_with_parent is not None:
        db_entry.share_with_parent = update_in.share_with_parent

    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_diary_entry(db: Session, entry_id: int) -> bool:
    db_entry = db.query(DiaryEntry).filter(DiaryEntry.id == entry_id).first()
    if not db_entry:
        return False
    db.delete(db_entry)
    db.commit()
    return True


# --- Relaxation & Wellbeing Service ---

def generate_relaxation_suggestions(db: Session, child_id: int) -> RelaxationResponse:
    # Fetch child profile to determine age and age group
    profile = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    age = profile.age if profile else 10
    age_group = classify_age_group(age)

    # 9 core relaxation activity types adaptively tailored by age group
    activities = []
    
    if age_group == "EARLY_CHILDHOOD":
        activities = [
            RelaxationActivity(type="breathing", title="Teddy Bear Belly Breathing", description="Lay down with your favorite stuffed animal on your belly and watch it rise and fall as you breathe gently.", suggested_duration_minutes=3, target_age_group=age_group, category="Breathing"),
            RelaxationActivity(type="short walk", title="Nature Scavenger Walk", description="Take a short walk with a parent to spot 3 green leaves and 2 pretty stones.", suggested_duration_minutes=10, target_age_group=age_group, category="Physical Activity"),
            RelaxationActivity(type="music", title="Soft Soft Lullabies", description="Listen to gentle piano melodies or quiet rainfall sounds.", suggested_duration_minutes=10, target_age_group=age_group, category="Audio & Music"),
            RelaxationActivity(type="stretching", title="Animal Yoga Stretches", description="Stretch like a cat, reach high like a giraffe, and curl like a turtle.", suggested_duration_minutes=5, target_age_group=age_group, category="Movement"),
            RelaxationActivity(type="meditation", title="Floating Cloud Story", description="Listen to a calm story about floating peacefully on a soft blue cloud.", suggested_duration_minutes=5, target_age_group=age_group, category="Mindfulness"),
            RelaxationActivity(type="hobby", title="Creative Finger Painting or Blocks", description="Build something fun with blocks or color a bright picture.", suggested_duration_minutes=15, target_age_group=age_group, category="Creative"),
            RelaxationActivity(type="journaling", title="Draw Your Day", description="Draw a picture of the happiest thing that happened to you today.", suggested_duration_minutes=10, target_age_group=age_group, category="Reflection"),
            RelaxationActivity(type="screen break", title="Rest Your Eyes Break", description="Close your eyes for 5 minutes and listen to soft birds singing.", suggested_duration_minutes=5, target_age_group=age_group, category="Screen Wellness"),
            RelaxationActivity(type="social connection", title="Family Hug & Storytime", description="Sit together with family for a cozy story or warm chat.", suggested_duration_minutes=15, target_age_group=age_group, category="Social")
        ]
    elif age_group == "PRIMARY_SCHOOL":
        activities = [
            RelaxationActivity(type="breathing", title="4-4-4 Box Breathing", description="Breathe in for 4 seconds, hold for 4 seconds, and exhale slowly for 4 seconds.", suggested_duration_minutes=5, target_age_group=age_group, category="Breathing"),
            RelaxationActivity(type="short walk", title="Outdoor Refresh Step Walk", description="Take a 10-minute walk outside in fresh air away from indoor noise.", suggested_duration_minutes=10, target_age_group=age_group, category="Physical Activity"),
            RelaxationActivity(type="music", title="Calming Nature & Instrumental Vibes", description="Listen to soothing instrumental tunes or ocean waves.", suggested_duration_minutes=15, target_age_group=age_group, category="Audio & Music"),
            RelaxationActivity(type="stretching", title="Gentle Desk & Back Stretches", description="Stretch arms overhead, twist gently side to side, and roll your shoulders.", suggested_duration_minutes=8, target_age_group=age_group, category="Movement"),
            RelaxationActivity(type="meditation", title="Quiet Mindful Focusing", description="Focus gently on your breath and relax your body from head to toe.", suggested_duration_minutes=8, target_age_group=age_group, category="Mindfulness"),
            RelaxationActivity(type="hobby", title="Lego or Free Coloring Time", description="Spend focused time building or coloring a detailed mandala.", suggested_duration_minutes=15, target_age_group=age_group, category="Creative"),
            RelaxationActivity(type="journaling", title="3 Happy Things Reflection", description="Write down three things that made you smile today in your diary.", suggested_duration_minutes=10, target_age_group=age_group, category="Reflection"),
            RelaxationActivity(type="screen break", title="20-20-20 Eye Wellness Rest", description="Look at something 20 feet away for 20 seconds and sip a glass of water.", suggested_duration_minutes=5, target_age_group=age_group, category="Screen Wellness"),
            RelaxationActivity(type="social connection", title="Board Game or Chat with a Friend", description="Play a quick card game or talk about your favorite cartoon with a buddy.", suggested_duration_minutes=15, target_age_group=age_group, category="Social")
        ]
    else:  # MIDDLE_SCHOOL, HIGH_SCHOOL, COLLEGE
        activities = [
            RelaxationActivity(type="breathing", title="4-7-8 Deep Relaxation Breathing", description="Inhale silently through the nose for 4s, hold for 7s, exhale completely through mouth for 8s.", suggested_duration_minutes=5, target_age_group=age_group, category="Breathing"),
            RelaxationActivity(type="short walk", title="Mindful Park Walk", description="Step outside for a 15-minute walk without checking your phone notifications.", suggested_duration_minutes=15, target_age_group=age_group, category="Physical Activity"),
            RelaxationActivity(type="music", title="Lo-Fi Acoustic & Chill Beats", description="Put on relaxing lo-fi beats, ambient sounds, or soothing acoustic playlists.", suggested_duration_minutes=15, target_age_group=age_group, category="Audio & Music"),
            RelaxationActivity(type="stretching", title="Full Body Muscle De-tensioning", description="Perform neck rolls, shoulder releases, hamstrings stretch, and wrist extensions.", suggested_duration_minutes=10, target_age_group=age_group, category="Movement"),
            RelaxationActivity(type="meditation", title="Mindful Body Scan & Awareness", description="Close your eyes, bring focus to your breathing, and release physical tension.", suggested_duration_minutes=10, target_age_group=age_group, category="Mindfulness"),
            RelaxationActivity(type="hobby", title="Unwind with a Favorite Hobby", description="Spend time sketching, reading a chapter of a book, or playing an instrument.", suggested_duration_minutes=20, target_age_group=age_group, category="Creative"),
            RelaxationActivity(type="journaling", title="Private Reflection & Gratitude", description="Journal your thoughts, goals, or express feelings freely in your private diary.", suggested_duration_minutes=15, target_age_group=age_group, category="Reflection"),
            RelaxationActivity(type="screen break", title="Digital Detox & Hydration Break", description="Step away from all screens, stretch your posture, and drink water.", suggested_duration_minutes=10, target_age_group=age_group, category="Screen Wellness"),
            RelaxationActivity(type="social connection", title="Connect with a Friend or Family", description="Call or chat with a supportive friend or family member for a pleasant catch-up.", suggested_duration_minutes=15, target_age_group=age_group, category="Social")
        ]

    # Mood Trend Evaluation
    entries = db.query(DiaryEntry).filter(DiaryEntry.child_id == child_id).order_by(DiaryEntry.date.desc(), DiaryEntry.id.desc()).limit(10).all()
    negative_count = sum(1 for e in entries if e.mood and e.mood.lower() in NEGATIVE_MOODS)
    
    mood_trend_summary = None
    support_rec = None

    if negative_count >= 3:
        mood_trend_summary = f"Detected {negative_count} recent diary entries with negative or stressed mood logs."
        support_rec = (
            "We notice you've been feeling down or stressed recently. Remember that you're not alone and it can really help "
            "to talk with a trusted parent/guardian, school counselor, or qualified healthcare professional."
        )

    return RelaxationResponse(
        child_id=child_id,
        age=age,
        age_group=age_group,
        suggested_activities=activities,
        mood_trend_summary=mood_trend_summary,
        support_recommendation=support_rec,
        privacy_disclaimer="Diary entries remain strictly private to the child and are kept separate from analytics and automated parent reports unless explicitly enabled.",
        medical_disclaimer="This system provides supportive wellbeing suggestions and does NOT provide medical or mental health diagnoses."
    )


# --- Relaxation Activity Logging ---

def create_relaxation_log(db: Session, log_in: RelaxationLogCreate) -> RelaxationLog:
    db_log = RelaxationLog(
        child_id=log_in.child_id,
        date=log_in.date,
        activity_type=log_in.activity_type.lower().strip(),
        duration_minutes=log_in.duration_minutes,
        mood_before=log_in.mood_before.lower().strip() if log_in.mood_before else None,
        mood_after=log_in.mood_after.lower().strip() if log_in.mood_after else None,
        notes=log_in.notes
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_child_relaxation_logs(db: Session, child_id: int) -> List[RelaxationLog]:
    return db.query(RelaxationLog).filter(
        RelaxationLog.child_id == child_id
    ).order_by(RelaxationLog.date.desc()).all()
