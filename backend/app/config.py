"""Application configuration."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@db:5432/dbname",
    )

    # LLM Provider Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Active LLM config
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")  # openai, anthropic, google, ollama
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")

    class Config:
        env_file = ".env"


settings = Settings()
