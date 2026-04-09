"""Dashboard API endpoint."""

import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import Goal, GoalStatus
from app.models.upgrade import UpgradeHistory
from app.services.consistency import (
    get_daily_consistency,
    get_overall_consistency,
    get_perfect_days_count,
    get_weekly_consistency_per_goal,
)
from app.services.llm_service import generate_motivation
from app.services.upgrade import check_all_upgrade_readiness

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    """Get at-a-glance dashboard data."""
    today = dt.date.today()
    iso = today.isocalendar()
    year, week = iso[0], iso[1]

    # Period: last 30 days
    period_start = today - dt.timedelta(days=30)

    overall_pct = get_overall_consistency(db, period_start, today)
    perfect_days = get_perfect_days_count(db, period_start, today)

    # Active goals with weekly consistency
    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    goals_performance = []
    for goal in active_goals:
        weekly_pct = get_weekly_consistency_per_goal(db, goal.id, year, week)
        goals_performance.append({
            "goal_id": str(goal.id),
            "goal_name": goal.name,
            "current_duty": goal.current_duty,
            "weekly_consistency_pct": weekly_pct,
        })

    # Last 4 weeks trend
    weekly_trend = []
    for i in range(4):
        w = week - i
        y = year
        if w <= 0:
            y -= 1
            w += 52
        week_label = f"{y}-W{w:02d}"

        monday = dt.date.fromisocalendar(y, w, 1)
        sunday = monday + dt.timedelta(days=6)
        week_pct = get_overall_consistency(db, monday, sunday)
        weekly_trend.append({"week": week_label, "consistency_pct": week_pct})

    weekly_trend.reverse()

    # Upgrade readiness
    readiness = check_all_upgrade_readiness(db)
    approaching = [r for r in readiness if r["consecutive_weeks_at_95"] >= 2]

    # Recent upgrades (progression journey)
    recent_upgrades = (
        db.query(UpgradeHistory)
        .order_by(UpgradeHistory.date.desc())
        .limit(10)
        .all()
    )
    progression = [
        {
            "date": u.date.isoformat() if u.date else None,
            "goal_id": str(u.goal_id),
            "previous_duty": u.previous_duty,
            "new_duty": u.new_duty,
            "previous_difficulty": u.previous_difficulty.value if u.previous_difficulty else None,
            "new_difficulty": u.new_difficulty.value if u.new_difficulty else None,
        }
        for u in recent_upgrades
    ]

    # Motivational message
    motivation = generate_motivation(db, overall_pct, perfect_days)

    return {
        "overall_consistency_pct": overall_pct,
        "perfect_days": perfect_days,
        "goals_performance": goals_performance,
        "weekly_trend": weekly_trend,
        "upgrade_readiness": approaching,
        "progression_journey": progression,
        "motivation": motivation,
    }
