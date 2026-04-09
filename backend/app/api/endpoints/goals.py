"""Goals API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import DifficultyLevel, Goal, GoalStatus, PriorityLevel
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("/", response_model=list[GoalResponse])
def list_goals(status: str | None = None, db: Session = Depends(get_db)):
    """List all goals, optionally filtered by status."""
    query = db.query(Goal)
    if status:
        query = query.filter(Goal.status == GoalStatus(status))
    return query.order_by(Goal.created_at.desc()).all()


@router.post("/", response_model=GoalResponse, status_code=201)
def create_goal(goal_in: GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal."""
    goal = Goal(
        name=goal_in.name,
        purpose=goal_in.purpose,
        current_duty=goal_in.current_duty,
        difficulty=DifficultyLevel(goal_in.difficulty),
        priority=PriorityLevel(goal_in.priority),
        status=GoalStatus(goal_in.status),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: UUID, db: Session = Depends(get_db)):
    """Get a single goal by ID."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: UUID, goal_in: GoalUpdate, db: Session = Depends(get_db)):
    """Update a goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    update_data = goal_in.model_dump(exclude_unset=True)
    if "difficulty" in update_data and update_data["difficulty"] is not None:
        update_data["difficulty"] = DifficultyLevel(update_data["difficulty"])
    if "priority" in update_data and update_data["priority"] is not None:
        update_data["priority"] = PriorityLevel(update_data["priority"])
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = GoalStatus(update_data["status"])

    for key, value in update_data.items():
        setattr(goal, key, value)

    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: UUID, db: Session = Depends(get_db)):
    """Delete a goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
