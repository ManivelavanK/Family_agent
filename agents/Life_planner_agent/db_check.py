from sqlalchemy import create_engine, inspect
from app.config import settings
from app.database.session import Base
import sys

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("Existing tables in DB:")
existing_tables = inspector.get_table_names()
for table_name in existing_tables:
    print(f"- {table_name}")

tables_to_recreate = ["habit_logs", "habits", "goals", "digital_twins", "reminders"]

for table in tables_to_recreate:
    if table in existing_tables:
        print(f"Dropping stale table: {table}")
        # Import models to ensure metadata has table definitions
        import app.models
        Base.metadata.tables[table].drop(engine, checkfirst=True)

print("Recreating tables...")
Base.metadata.create_all(engine)
print("Database schema successfully synchronized!")
