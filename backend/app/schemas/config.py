"""Pydantic schemas for Configuration and Suggestions."""

from typing import Optional

from pydantic import BaseModel


class LLMConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = None


class LLMConfigResponse(BaseModel):
    provider: str
    model: str
    openai_api_key: str  # redacted
    anthropic_api_key: str  # redacted
    google_api_key: str  # redacted
    ollama_base_url: str

    class Config:
        from_attributes = True


class SuggestionResponse(BaseModel):
    goal_id: str
    goal_name: str
    suggestion: str
    suggestion_type: str  # "improvement", "modification", "upgrade", "motivation"
