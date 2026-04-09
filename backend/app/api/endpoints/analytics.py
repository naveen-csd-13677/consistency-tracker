"""Analytics API endpoints — Weekly and Monthly."""

import datetime as dt
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.goal import Goal, GoalStatus
from app.schemas.analytics import (
    MonthlyGoalGrowth,
    MonthlyGrowthResponse,
    WeeklyAnalyticsResponse,
    WeeklyGoalAnalytics,
)
from app.services.consistency import (
    get_consecutive_weeks_at_threshold,
    get_monthly_consistency_per_goal,
    get_status_indicator,
    get_weekly_consistency_per_goal,
)
from app.services.llm_service import generate_suggestion_for_goal, generate_upgrade_proposal

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _parse_iso_week(week_str: str) -> tuple[int, int]:
    """Parse an ISO week string like '2026-W15' into (year, week)."""
    match = re.match(r"(\d{4})-W(\d{1,2})", week_str)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid week format. Use YYYY-WNN")
    return int(match.group(1)), int(match.group(2))


def _parse_month(month_str: str) -> tuple[int, int]:
    """Parse a month string like '2026-04' into (year, month)."""
    match = re.match(r"(\d{4})-(\d{2})", month_str)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
    return int(match.group(1)), int(match.group(2))


@router.get("/weekly", response_model=WeeklyAnalyticsResponse)
def weekly_analytics(
    week: str | None = Query(None, description="ISO week, e.g. 2026-W15"),
    goal_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    """Weekly consistency data per goal with status indicators and AI suggestions."""
    if week:
        year, wk = _parse_iso_week(week)
    else:
        today = dt.date.today()
        iso = today.isocalendar()
        year, wk = iso[0], iso[1]
        week = f"{year}-W{wk:02d}"

    goals_query = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE)
    if goal_id:
        goals_query = goals_query.filter(Goal.id == goal_id)
    goals = goals_query.all()

    goal_analytics = []
    total_pct = 0.0
    for goal in goals:
        pct = get_weekly_consistency_per_goal(db, goal.id, year, wk)
        indicator = get_status_indicator(pct)

        suggestion = None
        if pct < 90:
            suggestion = generate_suggestion_for_goal(
                db, goal.name, goal.purpose or "", goal.current_duty,
                goal.difficulty.value, pct, indicator,
            )

        goal_analytics.append(
            WeeklyGoalAnalytics(
                week=week,
                goal_id=str(goal.id),
                goal_name=goal.name,
                weekly_consistency_pct=pct,
                status_indicator=indicator,
                llm_suggestion=suggestion,
            )
        )
        total_pct += pct

    overall = round(total_pct / len(goals), 2) if goals else 0.0

    return WeeklyAnalyticsResponse(
        week=week, goals=goal_analytics, overall_consistency_pct=overall
    )


@router.get("/monthly", response_model=MonthlyGrowthResponse)
def monthly_analytics(
    month: str | None = Query(None, description="Month, e.g. 2026-04"),
    goal_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    """Monthly growth data with upgrade readiness."""
    if month:
        year, mo = _parse_month(month)
    else:
        today = dt.date.today()
        year, mo = today.year, today.month
        month = f"{year}-{mo:02d}"

    goals_query = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE)
    if goal_id:
        goals_query = goals_query.filter(Goal.id == goal_id)
    goals = goals_query.all()

    goal_growth = []
    for goal in goals:
        monthly_pct = get_monthly_consistency_per_goal(db, goal.id, year, mo)
        weeks_at_95 = get_consecutive_weeks_at_threshold(db, goal.id, 95.0)
        ready = weeks_at_95 >= 4

        proposed_duty = None
        if ready:
            from app.services.upgrade import get_next_difficulty
            next_diff = get_next_difficulty(goal.difficulty)
            proposed_duty = generate_upgrade_proposal(
                db, goal.name, goal.purpose or "", goal.current_duty,
                goal.difficulty.value, next_diff.value,
            )

        goal_growth.append(
            MonthlyGoalGrowth(
                month=month,
                goal_id=str(goal.id),
                goal_name=goal.name,
                previous_duty=goal.current_duty,
                current_consistency_pct=monthly_pct,
                weeks_at_95_pct=weeks_at_95,
                ready_for_upgrade=ready,
                proposed_new_duty=proposed_duty,
            )
        )

    return MonthlyGrowthResponse(month=month, goals=goal_growth)
