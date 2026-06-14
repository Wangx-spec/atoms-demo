"""add params and result_meta to tasks

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("params", postgresql.JSONB(), server_default="{}", nullable=False),
    )
    op.add_column(
        "tasks",
        sa.Column("result_meta", postgresql.JSONB(), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("tasks", "result_meta")
    op.drop_column("tasks", "params")
