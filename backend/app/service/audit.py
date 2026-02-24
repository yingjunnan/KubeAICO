from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.audit import AuditRepository
from app.schemas.audit import AuditLogItem, AuditLogListResponse


class AuditService:
    def __init__(self, audit_repo: AuditRepository) -> None:
        self.audit_repo = audit_repo

    async def list_logs(
        self,
        db: AsyncSession,
        *,
        limit: int,
        offset: int,
        action: str | None,
        target_kind: str | None,
        namespace: str | None,
    ) -> AuditLogListResponse:
        total, rows = await self.audit_repo.list(
            db,
            limit=limit,
            offset=offset,
            action=action,
            target_kind=target_kind,
            namespace=namespace,
        )

        return AuditLogListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[
                AuditLogItem(
                    id=row.id,
                    user_id=row.user_id,
                    action=row.action,
                    target_kind=row.target_kind,
                    target_name=row.target_name,
                    namespace=row.namespace,
                    status=row.status,
                    message=row.message,
                    created_at=row.created_at,
                )
                for row in rows
            ],
        )
