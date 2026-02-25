from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ManagedCluster
from app.schemas.cluster import ManagedClusterCreate, ManagedClusterUpdate


class ClusterRepository:
    async def list(self, db: AsyncSession) -> list[ManagedCluster]:
        stmt = select(ManagedCluster).order_by(ManagedCluster.created_at.desc(), ManagedCluster.id.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get(self, db: AsyncSession, cluster_id: int) -> ManagedCluster | None:
        stmt = select(ManagedCluster).where(ManagedCluster.id == cluster_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_cluster_key(self, db: AsyncSession, cluster_key: str) -> ManagedCluster | None:
        stmt = select(ManagedCluster).where(ManagedCluster.cluster_id == cluster_key)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> ManagedCluster | None:
        stmt = select(ManagedCluster).where(ManagedCluster.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, payload: ManagedClusterCreate) -> ManagedCluster:
        row = ManagedCluster(**payload.model_dump())
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def update(self, db: AsyncSession, row: ManagedCluster, payload: ManagedClusterUpdate) -> ManagedCluster:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, key, value)

        await db.commit()
        await db.refresh(row)
        return row

    async def delete(self, db: AsyncSession, row: ManagedCluster) -> None:
        await db.delete(row)
        await db.commit()
