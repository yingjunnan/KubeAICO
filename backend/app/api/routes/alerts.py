from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_alert_service,
    get_cluster_repository,
    get_current_user,
    resolve_cluster_by_id,
)
from app.db.session import get_db
from app.schemas.alerts import AlertListResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def alerts(
    namespace: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    cluster_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_alert_service),
    cluster_repo=Depends(get_cluster_repository),
) -> AlertListResponse:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=cluster_id,
            cluster_repo=cluster_repo,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    return await service.get_alerts(namespace=namespace, limit=limit, cluster=cluster)
