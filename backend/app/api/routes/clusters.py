from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_cluster_service, get_current_user
from app.db.session import get_db
from app.schemas.cluster import (
    ManagedClusterCreate,
    ManagedClusterListResponse,
    ManagedClusterRead,
    ManagedClusterUpdate,
)

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=ManagedClusterListResponse)
async def list_clusters(
    _user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service=Depends(get_cluster_service),
) -> ManagedClusterListResponse:
    return await service.list_clusters(db)


@router.post("", response_model=ManagedClusterRead, status_code=status.HTTP_201_CREATED)
async def create_cluster(
    payload: ManagedClusterCreate,
    _user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service=Depends(get_cluster_service),
) -> ManagedClusterRead:
    try:
        return await service.create_cluster(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{cluster_pk}", response_model=ManagedClusterRead)
async def update_cluster(
    cluster_pk: int,
    payload: ManagedClusterUpdate,
    _user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service=Depends(get_cluster_service),
) -> ManagedClusterRead:
    try:
        return await service.update_cluster(db, cluster_pk, payload)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.delete("/{cluster_pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cluster(
    cluster_pk: int,
    _user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service=Depends(get_cluster_service),
) -> None:
    try:
        await service.delete_cluster(db, cluster_pk)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
