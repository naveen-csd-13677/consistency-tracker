"""Pydantic schemas for Analytics."""

from typing import Optional

from pydantic import BaseModel


class WeeklyGoalAnalytics(BaseModel):
    week: str  # e.g., "2026-W15"
    goal_id: str
    goal_name: str
    weekly_consistency_pct: float
    status_indicator: str  # ✅, ⚠️, ❌
    llm_suggestion: Optional[str] = None


class WeeklyAnalyticsResponse(BaseModel):
    week: str
    goals: list[WeeklyGoalAnalytics]
    overall_consistency_pct: float


class MonthlyGoalGrowth(BaseModel):
    month: str  # e.g., "2026-04"
    goal_id: str
    goal_name: str
    previous_duty: str
    current_consistency_pct: float
    weeks_at_95_pct: int
    ready_for_upgrade: bool
    proposed_new_duty: Optional[str] = None


class MonthlyGrowthResponse(BaseModel):
    month: str
    goals: list[MonthlyGoalGrowth]
