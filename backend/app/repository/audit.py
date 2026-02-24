from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db.models import AuditLog


class AuditRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: int | None,
        action: str,
        target_kind: str,
        target_name: str,
        namespace: str | None,
        status: str,
        message: str | None,
    ) -> AuditLog:
        row = AuditLog(
            user_id=user_id,
            action=action,
            target_kind=target_kind,
            target_name=target_name,
            namespace=namespace,
            status=status,
            message=message,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def list(
        self,
        db: AsyncSession,
        *,
        limit: int,
        offset: int,
        action: str | None = None,
        target_kind: str | None = None,
        namespace: str | None = None,
    ) -> tuple[int, list[AuditLog]]:
        conditions = []
        if action:
            conditions.append(AuditLog.action == action)
        if target_kind:
            conditions.append(AuditLog.target_kind == target_kind)
        if namespace:
            conditions.append(AuditLog.namespace == namespace)

        total_stmt = select(func.count(AuditLog.id))
        list_stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
            .limit(limit)
            .offset(offset)
        )

        if conditions:
            total_stmt = total_stmt.where(*conditions)
            list_stmt = list_stmt.where(*conditions)

        total = int((await db.execute(total_stmt)).scalar() or 0)
        rows = list((await db.execute(list_stmt)).scalars().all())
        return total, rows
