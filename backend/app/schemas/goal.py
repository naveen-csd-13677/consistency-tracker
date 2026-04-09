"""Pydantic schemas for Goals and Duties."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    purpose: Optional[str] = None
    current_duty: str = Field(..., min_length=1)
    difficulty: str = "Easy"
    priority: str = "Medium"
    status: str = "Active"


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    purpose: Optional[str] = None
    current_duty: Optional[str] = None
    difficulty: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class GoalResponse(BaseModel):
    id: UUID
    name: str
    purpose: Optional[str] = None
    current_duty: str
    difficulty: str
    priority: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DutyCreate(BaseModel):
    goal_id: UUID
    description: str = Field(..., min_length=1)


class DutyUpdate(BaseModel):
    description: Optional[str] = None
    is_current: Optional[bool] = None


class DutyResponse(BaseModel):
    id: UUID
    goal_id: UUID
    description: str
    is_current: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
