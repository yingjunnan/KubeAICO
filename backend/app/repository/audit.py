from sqlalchemy.ext.asyncio import AsyncSession

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
