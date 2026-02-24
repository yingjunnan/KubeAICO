from fastapi import APIRouter, Depends, Query

from app.api.deps import get_alert_service, get_current_user
from app.schemas.alerts import AlertListResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def alerts(
    namespace: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _user=Depends(get_current_user),
    service=Depends(get_alert_service),
) -> AlertListResponse:
    return await service.get_alerts(namespace=namespace, limit=limit)
