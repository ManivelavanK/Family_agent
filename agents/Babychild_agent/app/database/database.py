import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # detect stale connections
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,        # recycle connections every 30 min
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
    from app.models.baby import Baby  # noqa: F401
    from app.models.feeding import Feeding  # noqa: F401
    from app.models.sleep import SleepRecord  # noqa: F401
    from app.models.growth import GrowthRecord  # noqa: F401
    from app.models.health import HealthRecord  # noqa: F401
    from app.models.vaccination import VaccinationRecord  # noqa: F401
    
    try:
        # Verify DB connection before creating tables
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection verified.")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error("Failed to verify database connection or create tables: %s", e)
        raise
