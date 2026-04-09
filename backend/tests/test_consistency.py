"""Tests for consistency calculation service."""

import datetime as dt
import uuid

import pytest

from app.models.goal import Goal, DifficultyLevel, PriorityLevel, GoalStatus
from app.models.daily_log import DailyLog
from app.services.consistency import (
    get_daily_consistency,
    get_weekly_consistency_per_goal,
    get_monthly_consistency_per_goal,
    get_status_indicator,
    get_upgrade_status,
    get_perfect_days_count,
)


class TestConsistencyCalculations:
    """Test consistency percentage calculations."""

    def test_daily_consistency_all_done(self, db_session):
        """TS-14: 100% when all goals completed (AC-1)."""
        g1 = Goal(name="G1", current_duty="D1", difficulty=DifficultyLevel.EASY,
                   priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                   created_at=dt.datetime(2026, 1, 1))
        g2 = Goal(name="G2", current_duty="D2", difficulty=DifficultyLevel.EASY,
                   priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                   created_at=dt.datetime(2026, 1, 1))
        db_session.add_all([g1, g2])
        db_session.flush()

        db_session.add(DailyLog(goal_id=g1.id, date=dt.date(2026, 4, 9), completed=True))
        db_session.add(DailyLog(goal_id=g2.id, date=dt.date(2026, 4, 9), completed=True))
        db_session.commit()

        result = get_daily_consistency(db_session, dt.date(2026, 4, 9))
        assert result["percentage"] == 100.0
        assert result["total"] == 2
        assert result["completed"] == 2

    def test_daily_consistency_partial(self, db_session):
        """TS-14: 50% when half done."""
        g1 = Goal(name="G1", current_duty="D1", difficulty=DifficultyLevel.EASY,
                   priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                   created_at=dt.datetime(2026, 1, 1))
        g2 = Goal(name="G2", current_duty="D2", difficulty=DifficultyLevel.EASY,
                   priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                   created_at=dt.datetime(2026, 1, 1))
        db_session.add_all([g1, g2])
        db_session.flush()

        db_session.add(DailyLog(goal_id=g1.id, date=dt.date(2026, 4, 9), completed=True))
        db_session.add(DailyLog(goal_id=g2.id, date=dt.date(2026, 4, 9), completed=False))
        db_session.commit()

        result = get_daily_consistency(db_session, dt.date(2026, 4, 9))
        assert result["percentage"] == 50.0

    def test_daily_consistency_no_goals(self, db_session):
        """0% when no active goals."""
        result = get_daily_consistency(db_session, dt.date(2026, 4, 9))
        assert result["percentage"] == 0.0
        assert result["total"] == 0

    def test_weekly_consistency(self, db_session):
        """TS-15: Weekly consistency = (completed days / 7) × 100."""
        g = Goal(name="G1", current_duty="D1", difficulty=DifficultyLevel.EASY,
                 priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                 created_at=dt.datetime(2026, 1, 1))
        db_session.add(g)
        db_session.flush()

        # Week 15 of 2026 starts Monday April 6
        for day_offset in range(5):  # 5 out of 7 days
            db_session.add(DailyLog(
                goal_id=g.id,
                date=dt.date(2026, 4, 6) + dt.timedelta(days=day_offset),
                completed=True,
            ))
        db_session.commit()

        pct = get_weekly_consistency_per_goal(db_session, g.id, 2026, 15)
        assert pct == round((5 / 7) * 100, 2)

    def test_monthly_consistency(self, db_session):
        """TS-16: Monthly consistency = (completed / days in month) × 100."""
        g = Goal(name="G1", current_duty="D1", difficulty=DifficultyLevel.EASY,
                 priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                 created_at=dt.datetime(2026, 1, 1))
        db_session.add(g)
        db_session.flush()

        # April has 30 days; complete 15
        for day in range(1, 16):
            db_session.add(DailyLog(
                goal_id=g.id,
                date=dt.date(2026, 4, day),
                completed=True,
            ))
        db_session.commit()

        pct = get_monthly_consistency_per_goal(db_session, g.id, 2026, 4)
        assert pct == 50.0

    def test_goals_added_mid_period_no_penalty(self, db_session):
        """AC-3: Goals added mid-week do not penalise earlier days."""
        g = Goal(name="Late Goal", current_duty="D1", difficulty=DifficultyLevel.EASY,
                 priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                 created_at=dt.datetime(2026, 4, 9))  # Created on 9th
        db_session.add(g)
        db_session.flush()

        # Check consistency for April 7 — goal didn't exist yet
        result = get_daily_consistency(db_session, dt.date(2026, 4, 7))
        assert result["total"] == 0  # Goal not counted for earlier date


class TestStatusIndicators:
    """Test status indicator functions."""

    def test_on_track(self):
        """TS ≥ 90%."""
        assert get_status_indicator(90) == "✅"
        assert get_status_indicator(100) == "✅"

    def test_needs_attention(self):
        """70–89%."""
        assert get_status_indicator(70) == "⚠️"
        assert get_status_indicator(89) == "⚠️"

    def test_struggling(self):
        """< 70%."""
        assert get_status_indicator(69) == "❌"
        assert get_status_indicator(0) == "❌"

    def test_upgrade_good(self):
        """Post-upgrade ≥ 80%."""
        assert get_upgrade_status(80) == "Good"
        assert get_upgrade_status(100) == "Good"

    def test_upgrade_watch(self):
        """Post-upgrade 60–79%."""
        assert get_upgrade_status(60) == "Watch"
        assert get_upgrade_status(79) == "Watch"

    def test_upgrade_failed(self):
        """Post-upgrade < 60%."""
        assert get_upgrade_status(59) == "Failed"
        assert get_upgrade_status(0) == "Failed"


class TestPerfectDays:
    """Test perfect days counting."""

    def test_perfect_days_count(self, db_session):
        g1 = Goal(name="G1", current_duty="D1", difficulty=DifficultyLevel.EASY,
                   priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                   created_at=dt.datetime(2026, 1, 1))
        g2 = Goal(name="G2", current_duty="D2", difficulty=DifficultyLevel.EASY,
                   priority=PriorityLevel.MEDIUM, status=GoalStatus.ACTIVE,
                   created_at=dt.datetime(2026, 1, 1))
        db_session.add_all([g1, g2])
        db_session.flush()

        # Day 1: both done (perfect)
        db_session.add(DailyLog(goal_id=g1.id, date=dt.date(2026, 4, 1), completed=True))
        db_session.add(DailyLog(goal_id=g2.id, date=dt.date(2026, 4, 1), completed=True))

        # Day 2: only one done (not perfect)
        db_session.add(DailyLog(goal_id=g1.id, date=dt.date(2026, 4, 2), completed=True))
        db_session.add(DailyLog(goal_id=g2.id, date=dt.date(2026, 4, 2), completed=False))

        # Day 3: both done (perfect)
        db_session.add(DailyLog(goal_id=g1.id, date=dt.date(2026, 4, 3), completed=True))
        db_session.add(DailyLog(goal_id=g2.id, date=dt.date(2026, 4, 3), completed=True))
        db_session.commit()

        count = get_perfect_days_count(db_session, dt.date(2026, 4, 1), dt.date(2026, 4, 3))
        assert count == 2
