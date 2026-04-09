"""Upgrade/Progression logic service."""

import datetime as dt

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.goal import DifficultyLevel, Goal, GoalStatus
from app.models.upgrade import UpgradeHistory
from app.services.consistency import (
    get_consecutive_weeks_at_threshold,
    get_weekly_consistency_per_goal,
)


DIFFICULTY_ORDER = [
    DifficultyLevel.EASY,
    DifficultyLevel.MEDIUM,
    DifficultyLevel.HARD,
    DifficultyLevel.HARD_PLUS,
    DifficultyLevel.ELITE,
]


def get_next_difficulty(current: DifficultyLevel) -> DifficultyLevel:
    """Get the next difficulty level above the current one."""
    idx = DIFFICULTY_ORDER.index(current)
    if idx < len(DIFFICULTY_ORDER) - 1:
        return DIFFICULTY_ORDER[idx + 1]
    return current  # Already at Elite


def check_upgrade_readiness(db: Session, goal: Goal) -> dict:
    """Check if a goal is ready for an upgrade based on core rules."""
    today = dt.date.today()
    iso_cal = today.isocalendar()
    year, week = iso_cal[0], iso_cal[1]

    current_weekly_pct = get_weekly_consistency_per_goal(db, goal.id, year, week)
    consecutive_weeks = get_consecutive_weeks_at_threshold(db, goal.id, 95.0)
    ready = consecutive_weeks >= 4

    next_diff = get_next_difficulty(goal.difficulty)

    return {
        "goal_id": str(goal.id),
        "goal_name": goal.name,
        "current_duty": goal.current_duty,
        "current_difficulty": goal.difficulty.value,
        "weekly_consistency_pct": current_weekly_pct,
        "consecutive_weeks_at_95": consecutive_weeks,
        "ready_for_upgrade": ready,
        "proposed_new_difficulty": next_diff.value if ready else None,
        "proposed_new_duty": None,  # Will be filled by LLM
    }


def execute_upgrade(
    db: Session,
    goal: Goal,
    new_duty: str,
    new_difficulty: DifficultyLevel,
    consistency_before: float,
    notes: str | None = None,
) -> UpgradeHistory:
    """Execute an upgrade for a goal."""
    # Get the next upgrade number for this goal
    max_num = (
        db.query(func.max(UpgradeHistory.upgrade_number))
        .filter(UpgradeHistory.goal_id == goal.id)
        .scalar()
    )
    next_num = (max_num or 0) + 1

    upgrade = UpgradeHistory(
        goal_id=goal.id,
        upgrade_number=next_num,
        previous_duty=goal.current_duty,
        new_duty=new_duty,
        previous_difficulty=goal.difficulty,
        new_difficulty=new_difficulty,
        consistency_before=consistency_before,
        notes=notes,
    )

    # Update the goal
    goal.current_duty = new_duty
    goal.difficulty = new_difficulty

    db.add(upgrade)
    db.commit()
    db.refresh(upgrade)
    return upgrade


def check_all_upgrade_readiness(db: Session) -> list[dict]:
    """Check upgrade readiness for all active goals."""
    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    results = []
    for goal in active_goals:
        results.append(check_upgrade_readiness(db, goal))
    return results
