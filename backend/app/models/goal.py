"""Goal and Duty database models."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DifficultyLevel(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    HARD_PLUS = "Hard+"
    ELITE = "Elite"


class PriorityLevel(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class GoalStatus(str, enum.Enum):
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=True)
    current_duty = Column(Text, nullable=False)
    difficulty = Column(
        Enum(DifficultyLevel), nullable=False, default=DifficultyLevel.EASY
    )
    priority = Column(
        Enum(PriorityLevel), nullable=False, default=PriorityLevel.MEDIUM
    )
    status = Column(Enum(GoalStatus), nullable=False, default=GoalStatus.ACTIVE)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    duties = relationship("Duty", back_populates="goal", cascade="all, delete-orphan")
    daily_logs = relationship(
        "DailyLog", back_populates="goal", cascade="all, delete-orphan"
    )
    upgrade_history = relationship(
        "UpgradeHistory", back_populates="goal", cascade="all, delete-orphan"
    )


class Duty(Base):
    __tablename__ = "duties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False)
    description = Column(Text, nullable=False)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    goal = relationship("Goal", back_populates="duties")
