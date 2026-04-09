"""Duties API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import Duty, Goal
from app.schemas.goal import DutyCreate, DutyResponse, DutyUpdate

router = APIRouter(prefix="/api/duties", tags=["duties"])


@router.get("/", response_model=list[DutyResponse])
def list_duties(goal_id: UUID | None = None, db: Session = Depends(get_db)):
    """List all duties (current and archived)."""
    query = db.query(Duty)
    if goal_id:
        query = query.filter(Duty.goal_id == goal_id)
    return query.order_by(Duty.created_at.desc()).all()


@router.post("/", response_model=DutyResponse, status_code=201)
def create_duty(duty_in: DutyCreate, db: Session = Depends(get_db)):
    """Create / assign a new duty to a goal."""
    goal = db.query(Goal).filter(Goal.id == duty_in.goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Mark existing current duties as not current
    db.query(Duty).filter(
        Duty.goal_id == duty_in.goal_id, Duty.is_current.is_(True)
    ).update({"is_current": False})

    duty = Duty(
        goal_id=duty_in.goal_id,
        description=duty_in.description,
        is_current=True,
    )
    db.add(duty)

    # Update the goal's current_duty field
    goal.current_duty = duty_in.description

    db.commit()
    db.refresh(duty)
    return duty


@router.get("/{duty_id}", response_model=DutyResponse)
def get_duty(duty_id: UUID, db: Session = Depends(get_db)):
    """Get a single duty."""
    duty = db.query(Duty).filter(Duty.id == duty_id).first()
    if not duty:
        raise HTTPException(status_code=404, detail="Duty not found")
    return duty


@router.put("/{duty_id}", response_model=DutyResponse)
def update_duty(duty_id: UUID, duty_in: DutyUpdate, db: Session = Depends(get_db)):
    """Update a duty."""
    duty = db.query(Duty).filter(Duty.id == duty_id).first()
    if not duty:
        raise HTTPException(status_code=404, detail="Duty not found")

    update_data = duty_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(duty, key, value)

    db.commit()
    db.refresh(duty)
    return duty


@router.delete("/{duty_id}", status_code=204)
def delete_duty(duty_id: UUID, db: Session = Depends(get_db)):
    """Delete a duty."""
    duty = db.query(Duty).filter(Duty.id == duty_id).first()
    if not duty:
        raise HTTPException(status_code=404, detail="Duty not found")
    db.delete(duty)
    db.commit()
