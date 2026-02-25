from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_cluster_repository,
    get_current_user,
    get_resource_service,
    resolve_cluster_by_id,
)
from app.db.models import User
from app.db.session import get_db
from app.schemas.resource import (
    ResourceActionResponse,
    ResourceDetailResponse,
    ResourceKind,
    RestartRequest,
    ScaleRequest,
    WorkloadListResponse,
)

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/{kind}", response_model=WorkloadListResponse)
async def list_resources(
    kind: ResourceKind,
    namespace: str | None = Query(default=None),
    label_selector: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    cluster_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_resource_service),
    cluster_repo=Depends(get_cluster_repository),
) -> WorkloadListResponse:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=cluster_id,
            cluster_repo=cluster_repo,
        )
        return await service.list_resources(
            kind=kind,
            namespace=namespace,
            label_selector=label_selector,
            status=status_filter,
            cluster=cluster,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@router.get("/{kind}/{name}/detail", response_model=ResourceDetailResponse)
async def get_resource_detail(
    kind: ResourceKind,
    name: str,
    namespace: str = Query(...),
    log_lines: int = Query(default=120, ge=10, le=2000),
    range_minutes: int = Query(default=10, ge=5, le=120),
    step_seconds: int = Query(default=30, ge=15, le=300),
    cluster_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_resource_service),
    cluster_repo=Depends(get_cluster_repository),
) -> ResourceDetailResponse:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=cluster_id,
            cluster_repo=cluster_repo,
        )
        return await service.get_resource_detail(
            kind=kind,
            name=name,
            namespace=namespace,
            log_lines=log_lines,
            range_minutes=range_minutes,
            step_seconds=step_seconds,
            cluster=cluster,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@router.post("/{kind}/{name}/scale", response_model=ResourceActionResponse)
async def scale_resource(
    kind: ResourceKind,
    name: str,
    payload: ScaleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    service=Depends(get_resource_service),
    cluster_repo=Depends(get_cluster_repository),
) -> ResourceActionResponse:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=payload.cluster_id,
            cluster_repo=cluster_repo,
        )
        audit_id = await service.scale_workload(
            db=db,
            user=user,
            kind=kind,
            name=name,
            namespace=payload.namespace,
            replicas=payload.replicas,
            cluster=cluster,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    return ResourceActionResponse(
        status="success",
        message=f"{kind}/{name} scaled to {payload.replicas}",
        audit_id=audit_id,
    )


@router.post("/{kind}/{name}/rollout-restart", response_model=ResourceActionResponse)
async def rollout_restart(
    kind: ResourceKind,
    name: str,
    payload: RestartRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    service=Depends(get_resource_service),
    cluster_repo=Depends(get_cluster_repository),
) -> ResourceActionResponse:
    try:
        cluster = await resolve_cluster_by_id(
            db=db,
            cluster_id=payload.cluster_id,
            cluster_repo=cluster_repo,
        )
        audit_id = await service.rollout_restart(
            db=db,
            user=user,
            kind=kind,
            name=name,
            namespace=payload.namespace,
            cluster=cluster,
        )
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc

    return ResourceActionResponse(
        status="success",
        message=f"{kind}/{name} rollout restart triggered",
        audit_id=audit_id,
    )
