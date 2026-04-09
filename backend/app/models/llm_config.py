"""LLM Configuration database model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class LLMConfig(Base):
    __tablename__ = "llm_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(50), nullable=False, default="")
    model = Column(String(100), nullable=False, default="")
    openai_api_key = Column(Text, nullable=True, default="")
    anthropic_api_key = Column(Text, nullable=True, default="")
    google_api_key = Column(Text, nullable=True, default="")
    ollama_base_url = Column(String(255), nullable=True, default="http://localhost:11434")
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
