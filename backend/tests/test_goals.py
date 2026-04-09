"""Tests for Goals API endpoints."""

import pytest


class TestGoalsCRUD:
    """Test Goals CRUD operations."""

    def test_create_goal(self, client):
        """TS-01: Users can create goals."""
        response = client.post("/api/goals/", json={
            "name": "Get Fit",
            "purpose": "Improve health",
            "current_duty": "Run 5 km",
            "difficulty": "Easy",
            "priority": "High",
            "status": "Active",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Get Fit"
        assert data["purpose"] == "Improve health"
        assert data["current_duty"] == "Run 5 km"
        assert data["difficulty"] == "Easy"
        assert data["priority"] == "High"
        assert data["status"] == "Active"
        assert "id" in data

    def test_list_goals(self, client):
        """TS-01: Users can read (list) goals."""
        client.post("/api/goals/", json={
            "name": "Goal 1", "current_duty": "Duty 1",
        })
        client.post("/api/goals/", json={
            "name": "Goal 2", "current_duty": "Duty 2",
        })
        response = client.get("/api/goals/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_goal(self, client):
        """TS-01: Users can read a single goal."""
        create_resp = client.post("/api/goals/", json={
            "name": "Test Goal", "current_duty": "Test Duty",
        })
        goal_id = create_resp.json()["id"]

        response = client.get(f"/api/goals/{goal_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Goal"

    def test_get_goal_not_found(self, client):
        """404 for nonexistent goal."""
        response = client.get("/api/goals/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_update_goal(self, client):
        """TS-01: Users can update goals."""
        create_resp = client.post("/api/goals/", json={
            "name": "Old Name", "current_duty": "Old Duty",
        })
        goal_id = create_resp.json()["id"]

        response = client.put(f"/api/goals/{goal_id}", json={
            "name": "New Name", "current_duty": "New Duty",
        })
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["current_duty"] == "New Duty"

    def test_delete_goal(self, client):
        """TS-01: Users can delete goals."""
        create_resp = client.post("/api/goals/", json={
            "name": "To Delete", "current_duty": "Duty",
        })
        goal_id = create_resp.json()["id"]

        response = client.delete(f"/api/goals/{goal_id}")
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/goals/{goal_id}")
        assert response.status_code == 404

    def test_filter_by_status(self, client):
        """TS-06: Only active goals appear when filtered."""
        client.post("/api/goals/", json={
            "name": "Active Goal", "current_duty": "D1", "status": "Active",
        })
        client.post("/api/goals/", json={
            "name": "Paused Goal", "current_duty": "D2", "status": "Paused",
        })

        response = client.get("/api/goals/?status=Active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Active Goal"

    def test_difficulty_levels(self, client):
        """TS-03: Difficulty levels."""
        for diff in ["Easy", "Medium", "Hard", "Hard+", "Elite"]:
            resp = client.post("/api/goals/", json={
                "name": f"Goal {diff}", "current_duty": "Duty", "difficulty": diff,
            })
            assert resp.status_code == 201
            assert resp.json()["difficulty"] == diff

    def test_priority_levels(self, client):
        """TS-04: Priority levels."""
        for pri in ["High", "Medium", "Low"]:
            resp = client.post("/api/goals/", json={
                "name": f"Goal {pri}", "current_duty": "Duty", "priority": pri,
            })
            assert resp.status_code == 201
            assert resp.json()["priority"] == pri

    def test_status_values(self, client):
        """TS-05: Status values."""
        for status in ["Active", "Paused", "Completed"]:
            resp = client.post("/api/goals/", json={
                "name": f"Goal {status}", "current_duty": "Duty", "status": status,
            })
            assert resp.status_code == 201
            assert resp.json()["status"] == status
