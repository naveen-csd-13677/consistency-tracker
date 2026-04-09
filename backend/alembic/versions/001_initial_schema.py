"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("purpose", sa.Text, nullable=True),
        sa.Column("current_duty", sa.Text, nullable=False),
        sa.Column(
            "difficulty",
            sa.Enum("Easy", "Medium", "Hard", "Hard+", "Elite", name="difficultylevel"),
            nullable=False,
            server_default="Easy",
        ),
        sa.Column(
            "priority",
            sa.Enum("High", "Medium", "Low", name="prioritylevel"),
            nullable=False,
            server_default="Medium",
        ),
        sa.Column(
            "status",
            sa.Enum("Active", "Paused", "Completed", name="goalstatus"),
            nullable=False,
            server_default="Active",
        ),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "duties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "goal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("goals.id"),
            nullable=False,
        ),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("is_current", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "daily_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "goal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("goals.id"),
            nullable=False,
        ),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
        sa.UniqueConstraint("goal_id", "date", name="uq_goal_date"),
    )

    op.create_table(
        "upgrade_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "goal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("goals.id"),
            nullable=False,
        ),
        sa.Column("upgrade_number", sa.Integer, nullable=False),
        sa.Column("date", sa.DateTime, nullable=True),
        sa.Column("previous_duty", sa.Text, nullable=False),
        sa.Column("new_duty", sa.Text, nullable=False),
        sa.Column(
            "previous_difficulty",
            sa.Enum("Easy", "Medium", "Hard", "Hard+", "Elite", name="difficultylevel"),
            nullable=False,
        ),
        sa.Column(
            "new_difficulty",
            sa.Enum("Easy", "Medium", "Hard", "Hard+", "Elite", name="difficultylevel"),
            nullable=False,
        ),
        sa.Column("consistency_before", sa.Float, nullable=True),
        sa.Column("consistency_after", sa.Float, nullable=True),
        sa.Column(
            "status",
            sa.Enum("Good", "Watch", "Failed", name="upgradestatus"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text, nullable=True),
    )

    op.create_table(
        "llm_config",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False, server_default=""),
        sa.Column("model", sa.String(100), nullable=False, server_default=""),
        sa.Column("openai_api_key", sa.Text, nullable=True),
        sa.Column("anthropic_api_key", sa.Text, nullable=True),
        sa.Column("google_api_key", sa.Text, nullable=True),
        sa.Column(
            "ollama_base_url",
            sa.String(255),
            nullable=True,
            server_default="http://localhost:11434",
        ),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("llm_config")
    op.drop_table("upgrade_history")
    op.drop_table("daily_logs")
    op.drop_table("duties")
    op.drop_table("goals")
    op.execute("DROP TYPE IF EXISTS upgradestatus")
    op.execute("DROP TYPE IF EXISTS goalstatus")
    op.execute("DROP TYPE IF EXISTS prioritylevel")
    op.execute("DROP TYPE IF EXISTS difficultylevel")
