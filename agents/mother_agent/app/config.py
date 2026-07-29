import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Validate required config at startup
_missing = [k for k, v in {"DATABASE_URL": DATABASE_URL, "GROQ_API_KEY": GROQ_API_KEY}.items() if not v]
if _missing:
    # Use fallback warning instead of runtime crash to allow running with default DB and warning logs
    logger.warning(f"Missing required environment variables: {', '.join(_missing)}")

# Twilio WhatsApp Config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
DEFAULT_FAMILY_PHONE = os.getenv("DEFAULT_FAMILY_PHONE", "whatsapp:+910000000000")

# Peer Agent Bus endpoints
FATHER_AGENT_URL = os.getenv("FATHER_AGENT_URL", "http://localhost:8002/api/v1/agent-bus/message")
CHILDREN_AGENT_URL = os.getenv("CHILDREN_AGENT_URL", "http://localhost:8003/api/v1/agent-bus/message")
GRANDPARENT_AGENT_URL = os.getenv("GRANDPARENT_AGENT_URL", "http://localhost:8004/api/v1/agent-bus/message")

