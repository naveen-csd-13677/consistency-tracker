"""Tests for miscellaneous API endpoints."""

import pytest


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"


class TestConfigEndpoints:
    def test_get_config(self, client):
        """Get config (should create default)."""
        response = client.get("/api/config/")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "model" in data

    def test_update_config(self, client):
        """Update LLM config."""
        response = client.put("/api/config/", json={
            "provider": "openai",
            "model": "gpt-4",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4"

    def test_api_key_redaction(self, client):
        """API keys should be redacted in response."""
        client.put("/api/config/", json={
            "provider": "openai",
            "openai_api_key": "sk-1234567890abcdef",
        })
        response = client.get("/api/config/")
        data = response.json()
        assert "sk-1234567890abcdef" not in data["openai_api_key"]
        assert "****" in data["openai_api_key"]


class TestExportEndpoints:
    def test_export_json(self, client):
        """Export JSON format."""
        response = client.get("/api/export/?format=json")
        assert response.status_code == 200

    def test_export_csv(self, client):
        """Export CSV format."""
        response = client.get("/api/export/?format=csv")
        assert response.status_code == 200

    def test_export_invalid_format(self, client):
        """Invalid format returns 400."""
        response = client.get("/api/export/?format=xml")
        assert response.status_code == 400


class TestDutiesEndpoints:
    def test_create_duty(self, client):
        """Create a duty for a goal."""
        goal_resp = client.post("/api/goals/", json={
            "name": "Test", "current_duty": "Original Duty",
        })
        goal_id = goal_resp.json()["id"]

        response = client.post("/api/duties/", json={
            "goal_id": goal_id, "description": "New Duty",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "New Duty"
        assert data["is_current"] is True

        # Verify goal's current_duty was updated
        goal = client.get(f"/api/goals/{goal_id}").json()
        assert goal["current_duty"] == "New Duty"

    def test_list_duties(self, client):
        """List duties for a goal."""
        goal_resp = client.post("/api/goals/", json={
            "name": "Test", "current_duty": "D1",
        })
        goal_id = goal_resp.json()["id"]
        client.post("/api/duties/", json={"goal_id": goal_id, "description": "D2"})

        response = client.get(f"/api/duties/?goal_id={goal_id}")
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestDashboardEndpoint:
    def test_dashboard(self, client):
        """Dashboard returns all expected fields."""
        response = client.get("/api/dashboard/")
        assert response.status_code == 200
        data = response.json()
        assert "overall_consistency_pct" in data
        assert "perfect_days" in data
        assert "goals_performance" in data
        assert "weekly_trend" in data
        assert "motivation" in data


class TestInsightsEndpoint:
    def test_insights_empty(self, client):
        """Insights endpoint returns structure even with no data."""
        response = client.get("/api/insights/")
        assert response.status_code == 200
        data = response.json()
        assert "upgrade_performance_matrix" in data
        assert "difficulty_progression_paths" in data
        assert "upgrade_safety_indicators" in data
        assert "compounding_effect_analysis" in data
        assert "next_upgrade_recommendations" in data

    def test_insights_with_goal(self, client):
        """Insights with an active goal returns recommendations."""
        client.post("/api/goals/", json={
            "name": "Test Goal", "current_duty": "Test Duty",
        })
        response = client.get("/api/insights/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["next_upgrade_recommendations"]) >= 1
        assert len(data["upgrade_safety_indicators"]) >= 1


class TestAnalyticsEndpoints:
    def test_weekly_analytics(self, client):
        """Weekly analytics returns data."""
        client.post("/api/goals/", json={
            "name": "Test", "current_duty": "Duty",
        })
        response = client.get("/api/analytics/weekly")
        assert response.status_code == 200
        data = response.json()
        assert "week" in data
        assert "goals" in data
        assert "overall_consistency_pct" in data

    def test_monthly_analytics(self, client):
        """Monthly analytics returns data."""
        client.post("/api/goals/", json={
            "name": "Test", "current_duty": "Duty",
        })
        response = client.get("/api/analytics/monthly")
        assert response.status_code == 200
        data = response.json()
        assert "month" in data
        assert "goals" in data

    def test_weekly_invalid_format(self, client):
        """Invalid week format returns 400."""
        response = client.get("/api/analytics/weekly?week=invalid")
        assert response.status_code == 400

    def test_monthly_invalid_format(self, client):
        """Invalid month format returns 400."""
        response = client.get("/api/analytics/monthly?month=invalid")
        assert response.status_code == 400
