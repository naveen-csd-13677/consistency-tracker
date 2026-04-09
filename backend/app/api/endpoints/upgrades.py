"""Upgrades API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import DifficultyLevel, Goal
from app.models.upgrade import UpgradeHistory
from app.schemas.upgrade import UpgradeCreate, UpgradeReadiness, UpgradeResponse
from app.services.upgrade import (
    check_all_upgrade_readiness,
    check_downgrade_suggestions,
    evaluate_post_upgrade_consistency,
    execute_upgrade,
    rollback_upgrade,
)

router = APIRouter(prefix="/api/upgrades", tags=["upgrades"])


class RollbackRequest(BaseModel):
    notes: Optional[str] = None


@router.get("/", response_model=list[UpgradeResponse])
def list_upgrades(goal_id: UUID | None = None, db: Session = Depends(get_db)):
    """List all upgrade history records."""
    query = db.query(UpgradeHistory)
    if goal_id:
        query = query.filter(UpgradeHistory.goal_id == goal_id)
    return query.order_by(UpgradeHistory.date.desc()).all()


@router.post("/", response_model=UpgradeResponse, status_code=201)
def create_upgrade(upgrade_in: UpgradeCreate, db: Session = Depends(get_db)):
    """Record a new upgrade event."""
    goal = db.query(Goal).filter(Goal.id == upgrade_in.goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    upgrade = execute_upgrade(
        db=db,
        goal=goal,
        new_duty=upgrade_in.new_duty,
        new_difficulty=DifficultyLevel(upgrade_in.new_difficulty),
        consistency_before=upgrade_in.consistency_before,
        notes=upgrade_in.notes,
    )
    return upgrade


@router.get("/readiness", response_model=list[UpgradeReadiness])
def get_readiness(db: Session = Depends(get_db)):
    """Get current upgrade readiness status for all active goals."""
    return check_all_upgrade_readiness(db)


@router.get("/downgrade-suggestions")
def get_downgrade_suggestions(db: Session = Depends(get_db)):
    """Check for goals that should be suggested for downgrade (UL-01).

    Returns goals where post-upgrade consistency < 60% for 2 consecutive weeks.
    """
    return check_downgrade_suggestions(db)


@router.post("/evaluate")
def evaluate_upgrades(db: Session = Depends(get_db)):
    """Evaluate post-upgrade consistency for upgrades older than 1 week.

    This calculates consistency_after and assigns status (Good/Watch/Failed).
    """
    return evaluate_post_upgrade_consistency(db)


@router.post("/{upgrade_id}/rollback", response_model=UpgradeResponse)
def rollback(
    upgrade_id: UUID,
    body: RollbackRequest | None = None,
    db: Session = Depends(get_db),
):
    """Rollback an upgrade — revert goal to previous duty and difficulty (UL-02)."""
    result = rollback_upgrade(db, upgrade_id, notes=body.notes if body else None)
    if not result:
        raise HTTPException(status_code=404, detail="Upgrade not found")
    return result


@router.get("/{upgrade_id}", response_model=UpgradeResponse)
def get_upgrade(upgrade_id: UUID, db: Session = Depends(get_db)):
    """Get a single upgrade record."""
    upgrade = db.query(UpgradeHistory).filter(UpgradeHistory.id == upgrade_id).first()
    if not upgrade:
        raise HTTPException(status_code=404, detail="Upgrade not found")
    return upgrade
