"""Data Export API endpoints."""

import csv
import io
import json
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.daily_log import DailyLog
from app.models.goal import Goal
from app.models.upgrade import UpgradeHistory


router = APIRouter(prefix="/api/export", tags=["export"])


def _serialize(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


@router.get("/")
def export_data(
    format: str = Query("json", description="Export format: json or csv"),
    db: Session = Depends(get_db),
):
    """Export all data as CSV or JSON."""
    goals = db.query(Goal).all()
    logs = db.query(DailyLog).all()
    upgrades = db.query(UpgradeHistory).all()

    if format.lower() == "json":
        data = {
            "goals": [
                {
                    "id": str(g.id),
                    "name": g.name,
                    "purpose": g.purpose,
                    "current_duty": g.current_duty,
                    "difficulty": g.difficulty.value if g.difficulty else None,
                    "priority": g.priority.value if g.priority else None,
                    "status": g.status.value if g.status else None,
                    "created_at": _serialize(g.created_at),
                    "updated_at": _serialize(g.updated_at),
                }
                for g in goals
            ],
            "daily_logs": [
                {
                    "id": str(log.id),
                    "goal_id": str(log.goal_id),
                    "date": _serialize(log.date),
                    "completed": log.completed,
                    "notes": log.notes,
                }
                for log in logs
            ],
            "upgrades": [
                {
                    "id": str(u.id),
                    "goal_id": str(u.goal_id),
                    "upgrade_number": u.upgrade_number,
                    "date": _serialize(u.date),
                    "previous_duty": u.previous_duty,
                    "new_duty": u.new_duty,
                    "previous_difficulty": u.previous_difficulty.value if u.previous_difficulty else None,
                    "new_difficulty": u.new_difficulty.value if u.new_difficulty else None,
                    "consistency_before": u.consistency_before,
                    "consistency_after": u.consistency_after,
                    "status": u.status.value if u.status else None,
                    "notes": u.notes,
                }
                for u in upgrades
            ],
        }
        content = json.dumps(data, indent=2, default=_serialize)
        return StreamingResponse(
            io.StringIO(content),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=consistency_tracker_export.json"},
        )

    elif format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        # Goals section
        writer.writerow(["=== GOALS ==="])
        writer.writerow(["ID", "Name", "Purpose", "Current Duty", "Difficulty", "Priority", "Status", "Created At", "Updated At"])
        for g in goals:
            writer.writerow([
                str(g.id), g.name, g.purpose, g.current_duty,
                g.difficulty.value if g.difficulty else "",
                g.priority.value if g.priority else "",
                g.status.value if g.status else "",
                _serialize(g.created_at), _serialize(g.updated_at),
            ])

        writer.writerow([])
        writer.writerow(["=== DAILY LOGS ==="])
        writer.writerow(["ID", "Goal ID", "Date", "Completed", "Notes"])
        for log in logs:
            writer.writerow([
                str(log.id), str(log.goal_id), _serialize(log.date),
                log.completed, log.notes or "",
            ])

        writer.writerow([])
        writer.writerow(["=== UPGRADES ==="])
        writer.writerow(["ID", "Goal ID", "Upgrade #", "Date", "Previous Duty", "New Duty",
                         "Previous Difficulty", "New Difficulty", "Consistency Before",
                         "Consistency After", "Status", "Notes"])
        for u in upgrades:
            writer.writerow([
                str(u.id), str(u.goal_id), u.upgrade_number, _serialize(u.date),
                u.previous_duty, u.new_duty,
                u.previous_difficulty.value if u.previous_difficulty else "",
                u.new_difficulty.value if u.new_difficulty else "",
                u.consistency_before, u.consistency_after,
                u.status.value if u.status else "", u.notes or "",
            ])

        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=consistency_tracker_export.csv"},
        )

    else:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
