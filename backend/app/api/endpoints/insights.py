"""Progression Insights API endpoint."""

import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import Goal, GoalStatus
from app.models.upgrade import UpgradeHistory, UpgradeStatus
from app.services.consistency import (
    get_consecutive_weeks_at_threshold,
    get_weekly_consistency_per_goal,
)
from app.services.llm_service import call_llm
from app.services.upgrade import check_all_upgrade_readiness, DIFFICULTY_ORDER

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/")
def get_progression_insights(db: Session = Depends(get_db)):
    """Get comprehensive progression insights combining historical data and AI."""
    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    all_upgrades = (
        db.query(UpgradeHistory).order_by(UpgradeHistory.date.asc()).all()
    )

    # 1. Upgrade Performance Matrix — success rate per goal, avg consistency drop
    goal_upgrade_stats = {}
    for u in all_upgrades:
        gid = str(u.goal_id)
        if gid not in goal_upgrade_stats:
            goal_upgrade_stats[gid] = {
                "goal_id": gid,
                "total_upgrades": 0,
                "good": 0,
                "watch": 0,
                "failed": 0,
                "consistency_drops": [],
            }
        stats = goal_upgrade_stats[gid]
        stats["total_upgrades"] += 1
        if u.status == UpgradeStatus.GOOD:
            stats["good"] += 1
        elif u.status == UpgradeStatus.WATCH:
            stats["watch"] += 1
        elif u.status == UpgradeStatus.FAILED:
            stats["failed"] += 1

        if u.consistency_before is not None and u.consistency_after is not None:
            stats["consistency_drops"].append(
                u.consistency_before - u.consistency_after
            )

    upgrade_performance_matrix = []
    for gid, stats in goal_upgrade_stats.items():
        goal = db.query(Goal).filter(Goal.id == gid).first()
        drops = stats["consistency_drops"]
        upgrade_performance_matrix.append(
            {
                "goal_id": gid,
                "goal_name": goal.name if goal else "Unknown",
                "total_upgrades": stats["total_upgrades"],
                "success_rate": (
                    round((stats["good"] / stats["total_upgrades"]) * 100, 1)
                    if stats["total_upgrades"] > 0
                    else 0
                ),
                "good": stats["good"],
                "watch": stats["watch"],
                "failed": stats["failed"],
                "avg_consistency_drop": (
                    round(sum(drops) / len(drops), 1) if drops else 0
                ),
            }
        )

    # 2. Difficulty Progression Paths — sequence of difficulty levels per goal
    difficulty_paths = {}
    for u in all_upgrades:
        gid = str(u.goal_id)
        if gid not in difficulty_paths:
            goal = db.query(Goal).filter(Goal.id == gid).first()
            difficulty_paths[gid] = {
                "goal_id": gid,
                "goal_name": goal.name if goal else "Unknown",
                "path": [u.previous_difficulty.value if u.previous_difficulty else "Unknown"],
            }
        difficulty_paths[gid]["path"].append(
            u.new_difficulty.value if u.new_difficulty else "Unknown"
        )

    # 3. Upgrade Safety Indicators — risk assessment for proposed upgrades
    readiness_data = check_all_upgrade_readiness(db)
    safety_indicators = []
    for r in readiness_data:
        gid = r["goal_id"]
        past_upgrades = goal_upgrade_stats.get(gid, {})
        failed_count = past_upgrades.get("failed", 0)
        total = past_upgrades.get("total_upgrades", 0)
        failure_rate = (failed_count / total * 100) if total > 0 else 0

        if failure_rate > 40:
            risk = "high"
        elif failure_rate > 20:
            risk = "medium"
        else:
            risk = "low"

        safety_indicators.append(
            {
                "goal_id": gid,
                "goal_name": r["goal_name"],
                "current_difficulty": r["current_difficulty"],
                "weekly_consistency_pct": r["weekly_consistency_pct"],
                "consecutive_weeks_at_95": r["consecutive_weeks_at_95"],
                "ready_for_upgrade": r["ready_for_upgrade"],
                "past_failure_rate": round(failure_rate, 1),
                "risk_level": risk,
                "recommendation": (
                    "Safe to upgrade — strong track record"
                    if risk == "low" and r["ready_for_upgrade"]
                    else "Proceed with caution — some past upgrades struggled"
                    if risk == "medium"
                    else "Consider waiting longer — high failure rate in past"
                    if risk == "high"
                    else "Not yet ready for upgrade"
                ),
            }
        )

    # 4. Compounding Effect Analysis
    total_upgrades = len(all_upgrades)
    goals_with_upgrades = len(set(str(u.goal_id) for u in all_upgrades))

    highest_difficulty_reached = {}
    for u in all_upgrades:
        gid = str(u.goal_id)
        if u.new_difficulty:
            idx = DIFFICULTY_ORDER.index(u.new_difficulty)
            if gid not in highest_difficulty_reached or idx > highest_difficulty_reached[gid]:
                highest_difficulty_reached[gid] = idx

    compounding_analysis = {
        "total_upgrades_completed": total_upgrades,
        "goals_with_upgrades": goals_with_upgrades,
        "highest_difficulty_achieved": (
            DIFFICULTY_ORDER[max(highest_difficulty_reached.values())].value
            if highest_difficulty_reached
            else "None"
        ),
        "narrative": _get_compounding_narrative(db, total_upgrades, active_goals),
    }

    # 5. Next Upgrade Recommendations — prioritized list
    recommendations = []
    for r in readiness_data:
        if r["ready_for_upgrade"]:
            priority = "high"
        elif r["consecutive_weeks_at_95"] >= 2:
            priority = "medium"
        else:
            priority = "low"

        recommendations.append(
            {
                "goal_id": r["goal_id"],
                "goal_name": r["goal_name"],
                "current_duty": r["current_duty"],
                "current_difficulty": r["current_difficulty"],
                "weekly_consistency_pct": r["weekly_consistency_pct"],
                "consecutive_weeks_at_95": r["consecutive_weeks_at_95"],
                "ready_for_upgrade": r["ready_for_upgrade"],
                "priority": priority,
            }
        )

    # Sort: ready first, then by consecutive weeks desc
    recommendations.sort(
        key=lambda x: (
            0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2,
            -x["consecutive_weeks_at_95"],
        )
    )

    return {
        "upgrade_performance_matrix": upgrade_performance_matrix,
        "difficulty_progression_paths": list(difficulty_paths.values()),
        "upgrade_safety_indicators": safety_indicators,
        "compounding_effect_analysis": compounding_analysis,
        "next_upgrade_recommendations": recommendations,
    }


def _get_compounding_narrative(db: Session, total_upgrades: int, active_goals: list) -> str:
    """Generate a narrative about compounding effects, using LLM if available."""
    if total_upgrades == 0:
        return (
            "Your journey is just beginning! Start by building consistent daily habits. "
            "Even small improvements, maintained consistently, lead to remarkable results over time. "
            "Focus on completing your duties every day, and upgrades will come naturally."
        )

    goal_summaries = []
    for g in active_goals:
        goal_summaries.append(f"{g.name} (difficulty: {g.difficulty.value}, duty: {g.current_duty})")

    prompt = f"""You are a personal consistency coach analyzing compounding progress.

Total upgrades completed: {total_upgrades}
Active goals: {', '.join(goal_summaries) if goal_summaries else 'None'}

Write a 2-3 sentence narrative about how these upgrades demonstrate compounding improvement.
Focus on the positive trajectory and the power of consistent small steps."""

    result = call_llm(db, prompt)
    if result:
        return result

    # Rule-based fallback
    return (
        f"You've completed {total_upgrades} upgrade{'s' if total_upgrades != 1 else ''} "
        f"across your goals. Each upgrade represents sustained excellence — "
        f"maintaining ≥95% consistency for 4+ consecutive weeks before leveling up. "
        f"This compounding effect means your daily capacity is growing steadily over time."
    )
