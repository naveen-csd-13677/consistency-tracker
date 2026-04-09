"""Tests for Daily Logs API endpoints."""

import pytest


class TestDailyLogsCRUD:
    """Test Daily Logs operations."""

    def _create_goal(self, client):
        resp = client.post("/api/goals/", json={
            "name": "Test Goal", "current_duty": "Test Duty",
        })
        return resp.json()["id"]

    def test_create_log(self, client):
        """TS-10: Users log each active goal."""
        goal_id = self._create_goal(client)
        response = client.post("/api/logs/", json={
            "goal_id": goal_id,
            "date": "2026-04-09",
            "completed": True,
            "notes": "Felt great!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["completed"] is True
        assert data["notes"] == "Felt great!"
        assert data["goal_id"] == goal_id

    def test_upsert_log(self, client):
        """TS-12: Only one log entry per goal per date (upsert)."""
        goal_id = self._create_goal(client)

        # First create
        client.post("/api/logs/", json={
            "goal_id": goal_id, "date": "2026-04-09",
            "completed": False, "notes": None,
        })

        # Second create (upsert)
        response = client.post("/api/logs/", json={
            "goal_id": goal_id, "date": "2026-04-09",
            "completed": True, "notes": "Updated!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["completed"] is True
        assert data["notes"] == "Updated!"

        # Verify only one log exists
        logs = client.get(f"/api/logs/?goal_id={goal_id}&date=2026-04-09").json()
        assert len(logs) == 1

    def test_list_logs_by_date(self, client):
        """Logs can be filtered by date."""
        goal_id = self._create_goal(client)
        client.post("/api/logs/", json={
            "goal_id": goal_id, "date": "2026-04-09", "completed": True,
        })
        client.post("/api/logs/", json={
            "goal_id": goal_id, "date": "2026-04-10", "completed": False,
        })

        response = client.get("/api/logs/?date=2026-04-09")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["date"] == "2026-04-09"

    def test_delete_log(self, client):
        """Logs can be deleted."""
        goal_id = self._create_goal(client)
        resp = client.post("/api/logs/", json={
            "goal_id": goal_id, "date": "2026-04-09", "completed": True,
        })
        log_id = resp.json()["id"]

        response = client.delete(f"/api/logs/{log_id}")
        assert response.status_code == 204

    def test_get_daily_overview(self, client):
        """Daily overview returns correct consistency %."""
        g1 = self._create_goal(client)
        g2_resp = client.post("/api/goals/", json={
            "name": "Goal 2", "current_duty": "Duty 2",
        })
        g2 = g2_resp.json()["id"]

        # Mark one done, one not
        client.post("/api/logs/", json={
            "goal_id": g1, "date": "2026-04-09", "completed": True,
        })
        client.post("/api/logs/", json={
            "goal_id": g2, "date": "2026-04-09", "completed": False,
        })

        response = client.get("/api/logs/overview?date=2026-04-09")
        assert response.status_code == 200
        data = response.json()
        assert data["total_active_goals"] == 2
        assert data["completed_goals"] == 1
        assert data["overall_percentage"] == 50.0

    def test_optional_notes(self, client):
        """TS-11: Notes are optional."""
        goal_id = self._create_goal(client)
        response = client.post("/api/logs/", json={
            "goal_id": goal_id, "date": "2026-04-09", "completed": True,
        })
        assert response.status_code == 201
        assert response.json()["notes"] is None

    def test_log_nonexistent_goal(self, client):
        """Cannot log against a nonexistent goal."""
        response = client.post("/api/logs/", json={
            "goal_id": "00000000-0000-0000-0000-000000000000",
            "date": "2026-04-09", "completed": True,
        })
        assert response.status_code == 404
