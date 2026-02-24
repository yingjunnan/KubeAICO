from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AITask


class AITaskRepository:
    async def create(self, db: AsyncSession, request_payload: dict) -> AITask:
        task = AITask(status="pending", request_payload=request_payload)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def get(self, db: AsyncSession, task_id: int) -> AITask | None:
        stmt = select(AITask).where(AITask.id == task_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        db: AsyncSession,
        task_id: int,
        status: str,
        result_payload: dict | None = None,
        error: str | None = None,
    ) -> AITask | None:
        task = await self.get(db, task_id)
        if not task:
            return None

        task.status = status
        task.result_payload = result_payload
        task.error = error
        task.updated_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(task)
        return task
