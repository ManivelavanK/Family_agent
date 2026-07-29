# Children Agent Backend

The **Children Agent** is a modular, standalone agentic AI backend focused on child education, routine, safety, health, personal development, and child finance.

This agent is part of the larger KinNest family platform, which also includes Mother Agent, Father Agent, and Grandparent Agent.

## Technology Stack

- **Core Framework**: Python & FastAPI
- **Database**: SQLAlchemy & SQLite
- **Job Scheduling**: APScheduler
- **Agentic AI & ML**: Groq API, Scikit-learn, Pandas, NumPy
- **Environment Management**: python-dotenv

## Directory Structure

```text
app/
    api/         # API Routes
    models/      # Database models
    schemas/     # Pydantic schemas
    services/    # Business/Service logic (No business logic in routes!)
    database/    # Engine, session, and schema initialization
    scheduler/   # APScheduler setup
    jobs/        # Scheduled background tasks/jobs
    ml/          # Machine learning utilities/models (Scikit-learn)
    ai/          # LLM integrations (Groq API)
    utils/       # Helper functions
    main.py      # Entry point
```

## Setup & Running

1. **Clone/Navigate to the workspace**:
   Ensure you are in `E:\child-agent`.

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in the values:
   ```bash
   cp .env.example .env
   ```

5. **Start the Application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The backend will be running at `http://127.0.0.1:8000`.

## API Endpoints

- **Root info**: `GET /`
- **Health status**: `GET /health`
- **Interactive documentation**: `GET /docs` (Swagger UI) or `GET /redoc`
