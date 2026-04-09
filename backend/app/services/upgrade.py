"""Upgrade/Progression logic service."""

import datetime as dt

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.goal import DifficultyLevel, Goal, GoalStatus
from app.models.upgrade import UpgradeHistory, UpgradeStatus
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


def get_previous_difficulty(current: DifficultyLevel) -> DifficultyLevel:
    """Get the previous difficulty level below the current one."""
    idx = DIFFICULTY_ORDER.index(current)
    if idx > 0:
        return DIFFICULTY_ORDER[idx - 1]
    return current  # Already at Easy


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


def rollback_upgrade(db: Session, upgrade_id, notes: str | None = None) -> UpgradeHistory:
    """Rollback an upgrade — revert goal to previous duty and difficulty (UL-02)."""
    upgrade = db.query(UpgradeHistory).filter(UpgradeHistory.id == upgrade_id).first()
    if not upgrade:
        return None

    goal = db.query(Goal).filter(Goal.id == upgrade.goal_id).first()
    if not goal:
        return None

    # Revert the goal to the previous state
    goal.current_duty = upgrade.previous_duty
    goal.difficulty = upgrade.previous_difficulty

    # Mark the upgrade as failed
    upgrade.status = UpgradeStatus.FAILED
    if notes:
        upgrade.notes = (upgrade.notes or "") + f" | Rolled back: {notes}"
    else:
        upgrade.notes = (upgrade.notes or "") + " | Rolled back by user"

    db.commit()
    db.refresh(upgrade)
    return upgrade


def evaluate_post_upgrade_consistency(db: Session) -> list[dict]:
    """Evaluate all upgrades that are 1+ week old but haven't been evaluated yet (Section 5.2 step 5).

    Returns list of upgrades that were evaluated.
    """
    one_week_ago = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)

    # Find upgrades that are older than 1 week but don't have consistency_after set
    pending_upgrades = (
        db.query(UpgradeHistory)
        .filter(
            and_(
                UpgradeHistory.date <= one_week_ago,
                UpgradeHistory.consistency_after.is_(None),
            )
        )
        .all()
    )

    evaluated = []
    today = dt.date.today()
    iso_cal = today.isocalendar()
    year, week = iso_cal[0], iso_cal[1]

    for upgrade in pending_upgrades:
        # Calculate the current weekly consistency for this goal
        pct = get_weekly_consistency_per_goal(db, upgrade.goal_id, year, week)
        upgrade.consistency_after = pct

        # Assign post-upgrade status
        if pct >= 80:
            upgrade.status = UpgradeStatus.GOOD
        elif pct >= 60:
            upgrade.status = UpgradeStatus.WATCH
        else:
            upgrade.status = UpgradeStatus.FAILED

        evaluated.append(
            {
                "upgrade_id": str(upgrade.id),
                "goal_id": str(upgrade.goal_id),
                "consistency_after": pct,
                "status": upgrade.status.value,
            }
        )

    if evaluated:
        db.commit()

    return evaluated


def check_downgrade_suggestions(db: Session) -> list[dict]:
    """Check for goals that should be suggested for downgrade (UL-01).

    If post-upgrade consistency is Failed (< 60%) for 2 consecutive weeks,
    suggest reverting to the previous duty.
    """
    suggestions = []

    # Get recent upgrades that are marked as Failed
    failed_upgrades = (
        db.query(UpgradeHistory)
        .filter(UpgradeHistory.status == UpgradeStatus.FAILED)
        .order_by(UpgradeHistory.date.desc())
        .all()
    )

    today = dt.date.today()
    iso_cal = today.isocalendar()
    year, week = iso_cal[0], iso_cal[1]

    for upgrade in failed_upgrades:
        goal = db.query(Goal).filter(Goal.id == upgrade.goal_id).first()
        if not goal or goal.status != GoalStatus.ACTIVE:
            continue

        # Check if current week is also below 60%
        current_pct = get_weekly_consistency_per_goal(db, goal.id, year, week)

        # Check previous week too
        prev_week = week - 1
        prev_year = year
        if prev_week <= 0:
            prev_year -= 1
            prev_week = 52
        prev_pct = get_weekly_consistency_per_goal(db, goal.id, prev_year, prev_week)

        if current_pct < 60 and prev_pct < 60:
            suggestions.append(
                {
                    "upgrade_id": str(upgrade.id),
                    "goal_id": str(goal.id),
                    "goal_name": goal.name,
                    "current_duty": goal.current_duty,
                    "previous_duty": upgrade.previous_duty,
                    "current_consistency_pct": current_pct,
                    "previous_week_consistency_pct": prev_pct,
                    "suggestion": (
                        f"Consider reverting to '{upgrade.previous_duty}'. "
                        f"Consistency has been below 60% for 2 consecutive weeks "
                        f"({prev_pct}% and {current_pct}%)."
                    ),
                }
            )

    return suggestions


def check_all_upgrade_readiness(db: Session) -> list[dict]:
    """Check upgrade readiness for all active goals."""
    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    results = []
    for goal in active_goals:
        results.append(check_upgrade_readiness(db, goal))
    return results
