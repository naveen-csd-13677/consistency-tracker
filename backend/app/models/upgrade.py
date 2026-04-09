"""UpgradeHistory database model."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.goal import DifficultyLevel


class UpgradeStatus(str, enum.Enum):
    GOOD = "Good"
    WATCH = "Watch"
    FAILED = "Failed"


class UpgradeHistory(Base):
    __tablename__ = "upgrade_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False)
    upgrade_number = Column(Integer, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    previous_duty = Column(Text, nullable=False)
    new_duty = Column(Text, nullable=False)
    previous_difficulty = Column(Enum(DifficultyLevel), nullable=False)
    new_difficulty = Column(Enum(DifficultyLevel), nullable=False)
    consistency_before = Column(Float, nullable=True)
    consistency_after = Column(Float, nullable=True)
    status = Column(Enum(UpgradeStatus), nullable=True)
    notes = Column(Text, nullable=True)

    goal = relationship("Goal", back_populates="upgrade_history")
