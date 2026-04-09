"""Tests for Upgrade/Progression logic."""

import datetime as dt

import pytest

from app.models.goal import Goal, DifficultyLevel, PriorityLevel, GoalStatus
from app.models.daily_log import DailyLog
from app.services.upgrade import (
    get_next_difficulty,
    get_previous_difficulty,
    DIFFICULTY_ORDER,
)


class TestDifficultyProgression:
    """Test difficulty level transitions."""

    def test_next_difficulty(self):
        """Difficulty advances correctly."""
        assert get_next_difficulty(DifficultyLevel.EASY) == DifficultyLevel.MEDIUM
        assert get_next_difficulty(DifficultyLevel.MEDIUM) == DifficultyLevel.HARD
        assert get_next_difficulty(DifficultyLevel.HARD) == DifficultyLevel.HARD_PLUS
        assert get_next_difficulty(DifficultyLevel.HARD_PLUS) == DifficultyLevel.ELITE
        assert get_next_difficulty(DifficultyLevel.ELITE) == DifficultyLevel.ELITE  # Cap

    def test_previous_difficulty(self):
        """Difficulty decreases correctly."""
        assert get_previous_difficulty(DifficultyLevel.ELITE) == DifficultyLevel.HARD_PLUS
        assert get_previous_difficulty(DifficultyLevel.HARD_PLUS) == DifficultyLevel.HARD
        assert get_previous_difficulty(DifficultyLevel.HARD) == DifficultyLevel.MEDIUM
        assert get_previous_difficulty(DifficultyLevel.MEDIUM) == DifficultyLevel.EASY
        assert get_previous_difficulty(DifficultyLevel.EASY) == DifficultyLevel.EASY  # Floor

    def test_difficulty_order_has_five_levels(self):
        """TS-03: Five difficulty levels."""
        assert len(DIFFICULTY_ORDER) == 5


class TestUpgradeExecution:
    """Test upgrade flow via API."""

    def _create_goal(self, client):
        resp = client.post("/api/goals/", json={
            "name": "Test Goal", "current_duty": "Easy Duty", "difficulty": "Easy",
        })
        return resp.json()

    def test_create_upgrade(self, client):
        """Record a new upgrade event."""
        goal = self._create_goal(client)

        resp = client.post("/api/upgrades/", json={
            "goal_id": goal["id"],
            "previous_duty": "Easy Duty",
            "new_duty": "Medium Duty",
            "previous_difficulty": "Easy",
            "new_difficulty": "Medium",
            "consistency_before": 96.5,
            "notes": "Ready!",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["upgrade_number"] == 1
        assert data["new_duty"] == "Medium Duty"
        assert data["consistency_before"] == 96.5

        # Verify goal was updated
        goal_resp = client.get(f"/api/goals/{goal['id']}")
        assert goal_resp.json()["current_duty"] == "Medium Duty"
        assert goal_resp.json()["difficulty"] == "Medium"

    def test_upgrade_numbering(self, client):
        """Upgrade numbers increment per goal."""
        goal = self._create_goal(client)

        client.post("/api/upgrades/", json={
            "goal_id": goal["id"], "previous_duty": "D1", "new_duty": "D2",
            "previous_difficulty": "Easy", "new_difficulty": "Medium",
        })
        resp2 = client.post("/api/upgrades/", json={
            "goal_id": goal["id"], "previous_duty": "D2", "new_duty": "D3",
            "previous_difficulty": "Medium", "new_difficulty": "Hard",
        })
        assert resp2.json()["upgrade_number"] == 2

    def test_readiness_endpoint(self, client):
        """GET /api/upgrades/readiness returns data."""
        self._create_goal(client)
        resp = client.get("/api/upgrades/readiness")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert "ready_for_upgrade" in data[0]
        assert "consecutive_weeks_at_95" in data[0]

    def test_rollback_upgrade(self, client):
        """UL-02: User can manually revert an upgrade."""
        goal = self._create_goal(client)

        # Execute upgrade
        up_resp = client.post("/api/upgrades/", json={
            "goal_id": goal["id"], "previous_duty": "Easy Duty", "new_duty": "Hard Duty",
            "previous_difficulty": "Easy", "new_difficulty": "Hard",
        })
        upgrade_id = up_resp.json()["id"]

        # Verify goal changed
        goal_resp = client.get(f"/api/goals/{goal['id']}")
        assert goal_resp.json()["current_duty"] == "Hard Duty"

        # Rollback
        rb_resp = client.post(f"/api/upgrades/{upgrade_id}/rollback", json={
            "notes": "Too hard",
        })
        assert rb_resp.status_code == 200
        assert rb_resp.json()["status"] == "Failed"

        # Verify goal reverted
        goal_resp = client.get(f"/api/goals/{goal['id']}")
        assert goal_resp.json()["current_duty"] == "Easy Duty"
        assert goal_resp.json()["difficulty"] == "Easy"


class TestUpgradeReadiness:
    """Test the core upgrade readiness rule."""

    def test_not_ready_without_consistency(self, client):
        """Goal without data is not ready."""
        resp = client.post("/api/goals/", json={
            "name": "New Goal", "current_duty": "Duty",
        })
        goal = resp.json()

        readiness = client.get("/api/upgrades/readiness").json()
        match = next(r for r in readiness if r["goal_id"] == goal["id"])
        assert match["ready_for_upgrade"] is False
        assert match["consecutive_weeks_at_95"] == 0
