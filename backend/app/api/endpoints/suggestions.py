"""AI Suggestions API endpoints."""

import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import Goal, GoalStatus
from app.schemas.config import SuggestionResponse
from app.services.consistency import get_status_indicator, get_weekly_consistency_per_goal
from app.services.llm_service import generate_suggestion_for_goal

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


def _get_suggestions(db: Session, goals: list[Goal]) -> list[SuggestionResponse]:
    """Generate suggestions for a list of goals."""
    today = dt.date.today()
    iso = today.isocalendar()
    year, week = iso[0], iso[1]

    suggestions = []
    for goal in goals:
        pct = get_weekly_consistency_per_goal(db, goal.id, year, week)
        indicator = get_status_indicator(pct)

        if pct < 70:
            stype = "modification"
        elif pct < 90:
            stype = "improvement"
        elif pct >= 95:
            stype = "upgrade"
        else:
            stype = "motivation"

        suggestion_text = generate_suggestion_for_goal(
            db, goal.name, goal.purpose or "", goal.current_duty,
            goal.difficulty.value, pct, indicator,
        )

        suggestions.append(
            SuggestionResponse(
                goal_id=str(goal.id),
                goal_name=goal.name,
                suggestion=suggestion_text,
                suggestion_type=stype,
            )
        )
    return suggestions


@router.get("/", response_model=list[SuggestionResponse])
def list_suggestions(db: Session = Depends(get_db)):
    """Get AI suggestions for all struggling goals (< 90% consistency)."""
    today = dt.date.today()
    iso = today.isocalendar()
    year, week = iso[0], iso[1]

    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    struggling = []
    for goal in active_goals:
        pct = get_weekly_consistency_per_goal(db, goal.id, year, week)
        if pct < 90:
            struggling.append(goal)

    return _get_suggestions(db, struggling)


@router.get("/{goal_id}", response_model=SuggestionResponse)
def get_suggestion(goal_id: UUID, db: Session = Depends(get_db)):
    """Get AI suggestion for a specific goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Goal not found")

    results = _get_suggestions(db, [goal])
    return results[0]


@router.post("/generate", response_model=list[SuggestionResponse])
def generate_suggestions(db: Session = Depends(get_db)):
    """Force-generate fresh suggestions for all active goals."""
    active_goals = db.query(Goal).filter(Goal.status == GoalStatus.ACTIVE).all()
    return _get_suggestions(db, active_goals)
