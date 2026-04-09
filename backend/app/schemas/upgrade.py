"""Pydantic schemas for Upgrades."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UpgradeCreate(BaseModel):
    goal_id: UUID
    previous_duty: str
    new_duty: str
    previous_difficulty: str
    new_difficulty: str
    consistency_before: Optional[float] = None
    notes: Optional[str] = None


class UpgradeResponse(BaseModel):
    id: UUID
    goal_id: UUID
    upgrade_number: int
    date: Optional[datetime] = None
    previous_duty: str
    new_duty: str
    previous_difficulty: str
    new_difficulty: str
    consistency_before: Optional[float] = None
    consistency_after: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class UpgradeReadiness(BaseModel):
    goal_id: str
    goal_name: str
    current_duty: str
    current_difficulty: str
    weekly_consistency_pct: float
    consecutive_weeks_at_95: int
    ready_for_upgrade: bool
    proposed_new_duty: Optional[str] = None
    proposed_new_difficulty: Optional[str] = None
