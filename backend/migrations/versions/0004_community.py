"""community fields and tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "generated_apps",
        sa.Column("visibility", sa.String(length=16), server_default="private", nullable=False),
    )
    op.add_column("generated_apps", sa.Column("title", sa.String(length=200), nullable=True))
    op.add_column("generated_apps", sa.Column("tags", sa.String(length=512), nullable=True))
    op.add_column(
        "generated_apps", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "generated_apps",
        sa.Column("view_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "generated_apps",
        sa.Column("like_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "generated_apps",
        sa.Column("comment_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index("ix_generated_apps_visibility", "generated_apps", ["visibility"])

    op.create_table(
        "likes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["app_id"], ["generated_apps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "app_id", name="uq_like_user_app"),
    )
    op.create_index("ix_likes_app_id", "likes", ["app_id"])
    op.create_index("ix_likes_user_id", "likes", ["user_id"])

    op.create_table(
        "gallery_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("app_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["app_id"], ["generated_apps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gallery_comments_app_id", "gallery_comments", ["app_id"])

    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
    op.drop_index("ix_gallery_comments_app_id", table_name="gallery_comments")
    op.drop_table("gallery_comments")
    op.drop_index("ix_likes_user_id", table_name="likes")
    op.drop_index("ix_likes_app_id", table_name="likes")
    op.drop_table("likes")
    op.drop_index("ix_generated_apps_visibility", table_name="generated_apps")
    op.drop_column("generated_apps", "comment_count")
    op.drop_column("generated_apps", "like_count")
    op.drop_column("generated_apps", "view_count")
    op.drop_column("generated_apps", "published_at")
    op.drop_column("generated_apps", "tags")
    op.drop_column("generated_apps", "title")
    op.drop_column("generated_apps", "visibility")
