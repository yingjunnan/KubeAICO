from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_cluster_repository,
    get_current_user,
    get_overview_service,
    resolve_cluster_by_id,
)
from app.db.session import get_db
from app.schemas.overview import ClusterSummary

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/summary", response_model=ClusterSummary)
async def summary(
    cluster_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_overview_service),
    cluster_repo=Depends(get_cluster_repository),
) -> ClusterSummary:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=cluster_id,
            cluster_repo=cluster_repo,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    return await service.get_cluster_summary(cluster=cluster)
