"""Pydantic schemas for Daily Logs."""

import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DailyLogCreate(BaseModel):
    goal_id: UUID
    date: dt.date
    completed: bool
    notes: Optional[str] = None


class DailyLogResponse(BaseModel):
    id: UUID
    goal_id: UUID
    date: dt.date
    completed: bool
    notes: Optional[str] = None
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True


class DailyOverview(BaseModel):
    date: dt.date
    total_active_goals: int
    completed_goals: int
    overall_percentage: float
    entries: list[DailyLogResponse]
