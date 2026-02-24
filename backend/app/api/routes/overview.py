from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_overview_service
from app.schemas.overview import ClusterSummary

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/summary", response_model=ClusterSummary)
async def summary(
    _user=Depends(get_current_user),
    service=Depends(get_overview_service),
) -> ClusterSummary:
    return await service.get_cluster_summary()
