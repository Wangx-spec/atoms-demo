"""Audit logging helper (scaffolding).

Call from routes/services to record sensitive actions:
    await write_audit_log(db, user_id, "app.publish", target=str(app_id))
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.audit_log import AuditLogORM


async def write_audit_log(
    db: AsyncSession,
    user_id: UUID | None,
    action: str,
    target: str | None = None,
    detail: dict | None = None,
) -> None:
    db.add(
        AuditLogORM(
            user_id=user_id,
            action=action,
            target=target,
            detail=detail or {},
        )
    )
    await db.commit()
