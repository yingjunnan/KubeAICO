from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzer.adapters import LLMAdapter
from app.analyzer.rules import RuleEngine
from app.db.session import AsyncSessionLocal
from app.repository.ai_task import AITaskRepository
from app.schemas.ai import AIAnalyzeRequest, AIAnalyzeResult


class AIService:
    def __init__(
        self,
        task_repo: AITaskRepository,
        rule_engine: RuleEngine,
        llm_adapter: LLMAdapter,
        llm_enabled: bool,
    ) -> None:
        self.task_repo = task_repo
        self.rule_engine = rule_engine
        self.llm_adapter = llm_adapter
        self.llm_enabled = llm_enabled

    async def create_task(self, db: AsyncSession, payload: AIAnalyzeRequest) -> int:
        task = await self.task_repo.create(db, request_payload=payload.model_dump(mode="json"))
        return task.id

    async def process_task(self, task_id: int) -> None:
        async with AsyncSessionLocal() as db:
            await self.task_repo.update_status(db, task_id, status="running")
            task = await self.task_repo.get(db, task_id)
            if not task:
                return

            try:
                payload = AIAnalyzeRequest.model_validate(task.request_payload)
                result: AIAnalyzeResult = self.rule_engine.analyze(payload)

                recommendations = list(result.recommendations)
                if self.llm_enabled:
                    recommendations = await self.llm_adapter.enrich_recommendations(
                        recommendations, payload
                    )

                final_result = result.model_copy(update={"recommendations": recommendations})

                await self.task_repo.update_status(
                    db,
                    task_id,
                    status="completed",
                    result_payload=final_result.model_dump(mode="json"),
                )
            except Exception as exc:  # pragma: no cover - defensive path
                await self.task_repo.update_status(
                    db,
                    task_id,
                    status="failed",
                    error=str(exc),
                )

    async def get_task(self, db: AsyncSession, task_id: int):
        return await self.task_repo.get(db, task_id)
