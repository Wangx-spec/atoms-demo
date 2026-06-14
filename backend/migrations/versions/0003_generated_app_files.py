"""generated app files and runtime

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "generated_apps",
        sa.Column(
            "runtime", sa.String(length=32), server_default="static-html", nullable=False
        ),
    )
    op.create_table(
        "generated_app_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("content", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["app_id"], ["generated_apps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_generated_app_files_app_id", "generated_app_files", ["app_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_generated_app_files_app_id", table_name="generated_app_files")
    op.drop_table("generated_app_files")
    op.drop_column("generated_apps", "runtime")
