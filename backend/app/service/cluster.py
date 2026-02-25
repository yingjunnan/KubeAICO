from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ManagedCluster
from app.repository.cluster import ClusterRepository
from app.schemas.cluster import (
    ManagedClusterCreate,
    ManagedClusterListResponse,
    ManagedClusterRead,
    ManagedClusterUpdate,
)


class ClusterService:
    def __init__(self, repo: ClusterRepository) -> None:
        self.repo = repo

    async def list_clusters(self, db: AsyncSession) -> ManagedClusterListResponse:
        rows = await self.repo.list(db)
        return ManagedClusterListResponse(total=len(rows), items=[self._to_read(row) for row in rows])

    async def create_cluster(self, db: AsyncSession, payload: ManagedClusterCreate) -> ManagedClusterRead:
        if await self.repo.get_by_name(db, payload.name):
            raise ValueError(f"name '{payload.name}' already exists")
        if await self.repo.get_by_cluster_key(db, payload.cluster_id):
            raise ValueError(f"cluster_id '{payload.cluster_id}' already exists")

        row = await self.repo.create(db, payload)
        return self._to_read(row)

    async def update_cluster(
        self,
        db: AsyncSession,
        cluster_pk: int,
        payload: ManagedClusterUpdate,
    ) -> ManagedClusterRead:
        row = await self.repo.get(db, cluster_pk)
        if not row:
            raise ValueError("Cluster not found")

        if payload.cluster_id and payload.cluster_id != row.cluster_id:
            existing = await self.repo.get_by_cluster_key(db, payload.cluster_id)
            if existing and existing.id != row.id:
                raise ValueError(f"cluster_id '{payload.cluster_id}' already exists")

        if payload.name and payload.name != row.name:
            existing_by_name = await self.repo.get_by_name(db, payload.name)
            if existing_by_name and existing_by_name.id != row.id:
                raise ValueError(f"name '{payload.name}' already exists")

        row = await self.repo.update(db, row, payload)
        return self._to_read(row)

    async def delete_cluster(self, db: AsyncSession, cluster_pk: int) -> None:
        row = await self.repo.get(db, cluster_pk)
        if not row:
            raise ValueError("Cluster not found")
        await self.repo.delete(db, row)

    @staticmethod
    def _mask_token(token: str | None) -> str | None:
        if not token:
            return None
        if len(token) <= 8:
            return '*' * len(token)
        return f"{token[:4]}...{token[-4:]}"

    def _to_read(self, row: ManagedCluster) -> ManagedClusterRead:
        return ManagedClusterRead(
            id=row.id,
            name=row.name,
            cluster_id=row.cluster_id,
            k8s_api_url=row.k8s_api_url,
            prometheus_url=row.prometheus_url,
            k8s_bearer_token_masked=self._mask_token(row.k8s_bearer_token),
            is_active=row.is_active,
            description=row.description,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
