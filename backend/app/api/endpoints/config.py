"""Configuration API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.llm_config import LLMConfig
from app.schemas.config import LLMConfigResponse, LLMConfigUpdate

router = APIRouter(prefix="/api/config", tags=["config"])


def _get_or_create_config(db: Session) -> LLMConfig:
    """Get or create the singleton LLM config record."""
    config = db.query(LLMConfig).first()
    if not config:
        config = LLMConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def _redact(key: str) -> str:
    """Redact an API key for display."""
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


@router.get("/", response_model=LLMConfigResponse)
def get_config(db: Session = Depends(get_db)):
    """Get current LLM configuration (keys redacted)."""
    config = _get_or_create_config(db)
    return LLMConfigResponse(
        provider=config.provider or "",
        model=config.model or "",
        openai_api_key=_redact(config.openai_api_key or ""),
        anthropic_api_key=_redact(config.anthropic_api_key or ""),
        google_api_key=_redact(config.google_api_key or ""),
        ollama_base_url=config.ollama_base_url or "http://localhost:11434",
    )


@router.put("/", response_model=LLMConfigResponse)
def update_config(config_in: LLMConfigUpdate, db: Session = Depends(get_db)):
    """Update LLM provider/model settings."""
    config = _get_or_create_config(db)

    update_data = config_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)

    return LLMConfigResponse(
        provider=config.provider or "",
        model=config.model or "",
        openai_api_key=_redact(config.openai_api_key or ""),
        anthropic_api_key=_redact(config.anthropic_api_key or ""),
        google_api_key=_redact(config.google_api_key or ""),
        ollama_base_url=config.ollama_base_url or "http://localhost:11434",
    )
