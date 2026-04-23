import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expense_tracker.db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if DATABASE_URL.startswith("sqlite"):
    logger.warning("DATABASE_URL resolved to SQLite. Persistent production DB may be bypassed.")
if SECRET_KEY == "supersecretkey":
    logger.warning("SECRET_KEY is default value; JWTs may break across environments/redeploys.")