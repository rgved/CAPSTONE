"""
backend/config.py

Centralised configuration loaded from environment variables.
All modules must import settings from here — not directly from os.environ.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class ConfigurationError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""

# Path to the SQLite database file.
DB_PATH: str = os.getenv("DB_PATH", "./recon.db")

# Path to the ChromaDB persistence directory.
CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_db")

# Logging verbosity: DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Phase 3 Groq provider configuration.
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_PROVIDER_NAME: str = "groq"

# Google OAuth configuration
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")


def validate_groq_config() -> None:
    """Fail fast when Groq configuration is incomplete."""
    if not GROQ_API_KEY:
        raise ConfigurationError("GROQ_API_KEY is not configured")
