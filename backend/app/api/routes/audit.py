from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_audit_service, get_current_user
from app.db.session import get_db
from app.schemas.audit import AuditLogListResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    action: str | None = Query(default=None),
    kind: str | None = Query(default=None),
    namespace: str | None = Query(default=None),
    _user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service=Depends(get_audit_service),
) -> AuditLogListResponse:
    return await service.list_logs(
        db,
        limit=limit,
        offset=offset,
        action=action,
        target_kind=kind,
        namespace=namespace,
    )
