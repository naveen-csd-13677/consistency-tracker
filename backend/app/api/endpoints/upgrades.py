"""Upgrades API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.goal import DifficultyLevel, Goal
from app.models.upgrade import UpgradeHistory
from app.schemas.upgrade import UpgradeCreate, UpgradeReadiness, UpgradeResponse
from app.services.upgrade import check_all_upgrade_readiness, execute_upgrade

router = APIRouter(prefix="/api/upgrades", tags=["upgrades"])


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


@router.get("/{upgrade_id}", response_model=UpgradeResponse)
def get_upgrade(upgrade_id: UUID, db: Session = Depends(get_db)):
    """Get a single upgrade record."""
    upgrade = db.query(UpgradeHistory).filter(UpgradeHistory.id == upgrade_id).first()
    if not upgrade:
        raise HTTPException(status_code=404, detail="Upgrade not found")
    return upgrade
