import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KinNest Life Planner Agent"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./kinnest_dev.db"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TIMEOUT: float = 30.0
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    
    FATHER_AGENT_URL: str = "http://localhost:8001"
    MOTHER_AGENT_URL: str = "http://localhost:8002"
    CHILD_AGENT_URL: str = "http://localhost:8003"
    GRANDPARENT_AGENT_URL: str = "http://localhost:8004"
    BABY_AGENT_URL: str = "http://localhost:8005"
    AGENT_COMMUNICATION_MOCK: bool = True
    
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "kinnest_secret_key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
