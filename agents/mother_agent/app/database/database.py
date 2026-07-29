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
    # Import all models so Base.metadata knows about them
    from app.models.grocery_item import GroceryItem       # noqa: F401
    from app.models.purchase import Purchase               # noqa: F401
    from app.models.consumption import Consumption         # noqa: F401
    from app.models.expiry import ExpiryItem               # noqa: F401
    from app.models.price import ProductPrice              # noqa: F401
    from app.models.memory import AgentMemory              # noqa: F401
    from app.models.reflection import Reflection           # noqa: F401
    from app.models.settings import HouseholdSettings      # noqa: F401
    from app.models.alert import KitchenAlert              # noqa: F401
    from app.models.document_vault import DocumentVault    # noqa: F401

    try:
        # Verify DB connection before creating tables
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            # Auto-migrate missing columns for existing tables
            conn.execute(text("ALTER TABLE grocery_items ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE grocery_items ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE consumption_history ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE expiry_items ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE purchase_history ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE user_memory ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE product_prices ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE agent_reflections ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE agent_reflections ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.commit()
        logger.info("Database connection verified and migrations applied.")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created: %s", list(Base.metadata.tables.keys()))
    except Exception as e:
        logger.error("Failed to create tables: %s", e)
        raise
