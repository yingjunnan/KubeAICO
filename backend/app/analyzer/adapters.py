from app.schemas.ai import AIAnalyzeRequest


class LLMAdapter:
    async def enrich_recommendations(
        self,
        recommendations: list[str],
        payload: AIAnalyzeRequest,
    ) -> list[str]:
        raise NotImplementedError


class NoopLLMAdapter(LLMAdapter):
    async def enrich_recommendations(
        self,
        recommendations: list[str],
        payload: AIAnalyzeRequest,
    ) -> list[str]:
        _ = payload
        extra = "LLM adapter placeholder: connect provider to generate context-aware runbooks."
        return [*recommendations, extra]
