from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_cluster_repository,
    get_current_user,
    get_metrics_service,
    resolve_cluster_by_id,
)
from app.db.session import get_db
from app.schemas.metrics import TimeseriesResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    metric: str = Query(default="cpu_usage"),
    range_minutes: int = Query(default=60, ge=5, le=1440),
    step_seconds: int = Query(default=60, ge=15, le=3600),
    namespace: str | None = Query(default=None),
    workload: str | None = Query(default=None),
    cluster_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_metrics_service),
    cluster_repo=Depends(get_cluster_repository),
) -> TimeseriesResponse:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=cluster_id,
            cluster_repo=cluster_repo,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    return await service.get_timeseries(
        metric=metric,
        range_minutes=range_minutes,
        namespace=namespace,
        workload=workload,
        step_seconds=step_seconds,
        cluster=cluster,
    )
