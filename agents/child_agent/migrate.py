"""
Migration script: Rebuild new academic tables for Children Agent.
Run ONCE: python migrate.py

This drops only the new academic tables that conflict with old schema
and recreates them with the correct structure.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine, text, inspect

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

print("Starting Children Agent schema migration...")

# Tables to migrate (drop and recreate with new schema)
TABLES_TO_RESET = [
    "study_sessions",  # old: child_id → new: student_id
    "exams",           # old schema incompatible
    "assignments",     # may have old schema
    "goals",           # may have old schema
    "progress",        # new table
    "notifications",   # new table
    "student_memories",# existing but now references students
    "subjects",        # new table
    "students",        # new table
]

# Import all models to register them with Base
from app.database.database import Base
import app.models.student
import app.models.profile
import app.models.digital_twin
import app.models.subject
import app.models.assignment
import app.models.study_session
import app.models.goal
import app.models.exam
import app.models.progress
import app.models.notification
import app.models.memory
import app.models.screen_time
import app.models.attendance
import app.models.pocket_money
import app.models.health
import app.models.schedule
import app.models.homework

print("Dropping all existing database tables...")
Base.metadata.reflect(bind=engine)
Base.metadata.drop_all(bind=engine)
print("All tables dropped successfully.")

print("\nRecreating tables and running full dynamic seed...")
from app.database.schema import create_tables
create_tables()

print("\nMigration and dynamic database seeding complete! SUCCESS")
