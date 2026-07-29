import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

# check if it's sqlite to append check_same_thread parameter
connect_args = {}
pool_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    pool_kwargs["pool_pre_ping"] = False
else:
    pool_kwargs["pool_pre_ping"] = True
    pool_kwargs["pool_size"] = 10
    pool_kwargs["max_overflow"] = 20
    pool_kwargs["pool_recycle"] = 1800

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **pool_kwargs
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    # Import all models so Base.metadata knows about them
    from app.models.profile import Profile
    from app.models.vitals import Vitals
    from app.models.medicine import Medicine
    from app.models.activity import Activity
    from app.models.nutrition import Nutrition
    from app.models.appointment import Appointment
    from app.models.insurance import Insurance
    from app.models.daily_summary import DailySummary
    from app.models.emergency import EmergencyIncident
    from app.models.weekly_report import WeeklyReport
    from app.models.cognitive import CognitiveLog

    try:
        # Verify DB connection before creating tables
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection verified.")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created: %s", list(Base.metadata.tables.keys()))
    except Exception as e:
        logger.error("Failed to create tables: %s", e)
        raise