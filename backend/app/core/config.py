# ============================================================
# app/core/config.py — Central Application Configuration
# ============================================================
# PURPOSE: Reads all settings from the .env file.
# Every field here maps directly to a variable in .env.
# This way, you change secrets in ONE place (.env) and the
# whole app picks it up automatically.
# ============================================================

from pydantic_settings import BaseSettings   # Reads .env files automatically
from functools import lru_cache             # Caches result so .env is read only once


class Settings(BaseSettings):
    """
    All application settings loaded from the .env file.
    
    Rules:
    - Field names here are lowercase
    - .env variable names are UPPERCASE
    - pydantic-settings matches them case-insensitively
    
    Example: google_api_key here ↔ GOOGLE_API_KEY in .env
    """

    # ----- Google Gemini AI -----
    # Your Google AI Studio API key (get it from https://aistudio.google.com/app/apikey)
    google_api_key: str = ""

    # ----- OpenAI (kept for future use / embeddings) -----
    openai_api_key: str = "not-needed"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # ----- Database -----
    # Async URL — used by FastAPI for live requests (async = can handle many at once)
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/smartdesk"

    # Sync URL — used by Alembic migrations and tool functions (simpler, blocking)
    sync_database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/smartdesk"

    # ----- JWT Authentication -----
    jwt_secret_key: str = "changethisinproduction"   # Signs and verifies JWT tokens
    jwt_algorithm: str = "HS256"                      # Hashing algorithm
    jwt_access_token_expire_minutes: int = 30          # Token expires after 30 min

    # ----- App Settings -----
    app_name: str = "SmartDesk"
    app_version: str = "1.0.0"
    debug: bool = True

    # Which frontend URL is allowed to call our backend (CORS setting)
    frontend_url: str = "http://localhost:5173"

    # ---- Pydantic Config ----
    model_config = {
        "env_file": ".env",           # Look for .env file in current directory
        "env_file_encoding": "utf-8", # How to read the file
        "case_sensitive": False,       # GOOGLE_API_KEY = google_api_key ✓
        "extra": "ignore"              # Ignore any extra .env variables we don't define here
    }


# ---- Cache the settings ----
# @lru_cache means this function runs ONCE, then returns the same object every time.
# Without this, Python would re-read the .env file on every single API request — slow!
@lru_cache()
def get_settings() -> Settings:
    """Returns the application settings (cached after first call)."""
    return Settings()


# ---- Single shared instance ----
# Other files import this:  from app.core.config import settings
# Then use it:              settings.google_api_key
settings = get_settings()