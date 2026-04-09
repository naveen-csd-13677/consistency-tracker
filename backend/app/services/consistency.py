"""Consistency calculation service."""

import datetime as dt
from collections import defaultdict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.daily_log import DailyLog
from app.models.goal import Goal, GoalStatus


def get_daily_consistency(db: Session, date: dt.date) -> dict:
    """Calculate daily consistency % = (goals completed / total active goals) × 100."""
    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    if not active_goals:
        return {"date": date, "total": 0, "completed": 0, "percentage": 0.0}

    # Only count goals that were created on or before this date
    eligible_goals = [g for g in active_goals if g.created_at.date() <= date]
    if not eligible_goals:
        return {"date": date, "total": 0, "completed": 0, "percentage": 0.0}

    goal_ids = [g.id for g in eligible_goals]
    completed_count = (
        db.query(func.count(DailyLog.id))
        .filter(
            and_(
                DailyLog.date == date,
                DailyLog.completed.is_(True),
                DailyLog.goal_id.in_(goal_ids),
            )
        )
        .scalar()
    )

    total = len(eligible_goals)
    pct = (completed_count / total) * 100 if total > 0 else 0.0
    return {
        "date": date,
        "total": total,
        "completed": completed_count,
        "percentage": round(pct, 2),
    }


def get_weekly_consistency_per_goal(
    db: Session, goal_id, year: int, week: int
) -> float:
    """Weekly consistency % per goal = (days completed / 7) × 100 for an ISO week."""
    # Calculate the Monday of the given ISO week
    monday = dt.date.fromisocalendar(year, week, 1)
    sunday = monday + dt.timedelta(days=6)

    completed_days = (
        db.query(func.count(DailyLog.id))
        .filter(
            and_(
                DailyLog.goal_id == goal_id,
                DailyLog.date >= monday,
                DailyLog.date <= sunday,
                DailyLog.completed.is_(True),
            )
        )
        .scalar()
    )

    return round((completed_days / 7) * 100, 2)


def get_monthly_consistency_per_goal(
    db: Session, goal_id, year: int, month: int
) -> float:
    """Monthly consistency % per goal = (days completed / days in month) × 100."""
    import calendar

    days_in_month = calendar.monthrange(year, month)[1]
    start_date = dt.date(year, month, 1)
    end_date = dt.date(year, month, days_in_month)

    completed_days = (
        db.query(func.count(DailyLog.id))
        .filter(
            and_(
                DailyLog.goal_id == goal_id,
                DailyLog.date >= start_date,
                DailyLog.date <= end_date,
                DailyLog.completed.is_(True),
            )
        )
        .scalar()
    )

    return round((completed_days / days_in_month) * 100, 2)


def get_consecutive_weeks_at_threshold(
    db: Session, goal_id, threshold: float = 95.0
) -> int:
    """Count consecutive weeks (going back from current) where goal had >= threshold%."""
    today = dt.date.today()
    iso_cal = today.isocalendar()
    year, week = iso_cal[0], iso_cal[1]

    consecutive = 0
    for i in range(52):  # Check up to 52 weeks back
        w = week - i
        y = year
        if w <= 0:
            y -= 1
            w += 52

        pct = get_weekly_consistency_per_goal(db, goal_id, y, w)
        if pct >= threshold:
            consecutive += 1
        else:
            break

    return consecutive


def get_status_indicator(pct: float) -> str:
    """Return status indicator based on weekly consistency."""
    if pct >= 90:
        return "✅"
    elif pct >= 70:
        return "⚠️"
    else:
        return "❌"


def get_upgrade_status(pct: float) -> str:
    """Return post-upgrade status."""
    if pct >= 80:
        return "Good"
    elif pct >= 60:
        return "Watch"
    else:
        return "Failed"


def get_overall_consistency(db: Session, start_date: dt.date, end_date: dt.date) -> float:
    """Overall consistency % = average of daily consistency across the selected period."""
    current = start_date
    daily_pcts = []
    while current <= end_date:
        result = get_daily_consistency(db, current)
        if result["total"] > 0:
            daily_pcts.append(result["percentage"])
        current += dt.timedelta(days=1)

    if not daily_pcts:
        return 0.0
    return round(sum(daily_pcts) / len(daily_pcts), 2)


def get_perfect_days_count(db: Session, start_date: dt.date, end_date: dt.date) -> int:
    """Count days where all active goals were completed."""
    current = start_date
    perfect = 0
    while current <= end_date:
        result = get_daily_consistency(db, current)
        if result["total"] > 0 and result["percentage"] == 100.0:
            perfect += 1
        current += dt.timedelta(days=1)
    return perfect
