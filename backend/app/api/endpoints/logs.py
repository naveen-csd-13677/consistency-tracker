"""Daily Logs API endpoints."""

import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.daily_log import DailyLog
from app.models.goal import Goal, GoalStatus
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse, DailyOverview
from app.services.consistency import get_daily_consistency

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/", response_model=list[DailyLogResponse])
def list_logs(
    date: dt.date | None = None,
    goal_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    """List log entries with optional date and goal_id filters."""
    query = db.query(DailyLog)
    if date:
        query = query.filter(DailyLog.date == date)
    if goal_id:
        query = query.filter(DailyLog.goal_id == goal_id)
    return query.order_by(DailyLog.date.desc()).all()


@router.post("/", response_model=DailyLogResponse, status_code=201)
def upsert_log(log_in: DailyLogCreate, db: Session = Depends(get_db)):
    """Create or update (upsert) a daily log entry. One entry per goal per date."""
    # Verify goal exists
    goal = db.query(Goal).filter(Goal.id == log_in.goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    existing = (
        db.query(DailyLog)
        .filter(
            and_(
                DailyLog.goal_id == log_in.goal_id,
                DailyLog.date == log_in.date,
            )
        )
        .first()
    )

    if existing:
        existing.completed = log_in.completed
        existing.notes = log_in.notes
        db.commit()
        db.refresh(existing)
        return existing

    log_entry = DailyLog(
        goal_id=log_in.goal_id,
        date=log_in.date,
        completed=log_in.completed,
        notes=log_in.notes,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


@router.get("/overview", response_model=DailyOverview)
def get_daily_overview(date: dt.date, db: Session = Depends(get_db)):
    """Get daily overview with all log entries and consistency %."""
    stats = get_daily_consistency(db, date)
    entries = db.query(DailyLog).filter(DailyLog.date == date).all()
    return DailyOverview(
        date=date,
        total_active_goals=stats["total"],
        completed_goals=stats["completed"],
        overall_percentage=stats["percentage"],
        entries=entries,
    )


@router.get("/{log_id}", response_model=DailyLogResponse)
def get_log(log_id: UUID, db: Session = Depends(get_db)):
    """Get a single log entry."""
    log_entry = db.query(DailyLog).filter(DailyLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry


@router.delete("/{log_id}", status_code=204)
def delete_log(log_id: UUID, db: Session = Depends(get_db)):
    """Delete a log entry."""
    log_entry = db.query(DailyLog).filter(DailyLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(log_entry)
    db.commit()
