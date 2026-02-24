from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_metrics_service
from app.schemas.metrics import TimeseriesResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    metric: str = Query(default="cpu_usage"),
    range_minutes: int = Query(default=60, ge=5, le=1440),
    step_seconds: int = Query(default=60, ge=15, le=3600),
    namespace: str | None = Query(default=None),
    workload: str | None = Query(default=None),
    _user=Depends(get_current_user),
    service=Depends(get_metrics_service),
) -> TimeseriesResponse:
    return await service.get_timeseries(
        metric=metric,
        range_minutes=range_minutes,
        namespace=namespace,
        workload=workload,
        step_seconds=step_seconds,
    )
