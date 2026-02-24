from datetime import datetime

from pydantic import BaseModel, Field


class MetricSnapshot(BaseModel):
    name: str
    value: float
    trend: str | None = None


class EventSnapshot(BaseModel):
    type: str
    message: str
    severity: str
    timestamp: datetime


class AIAnalyzeRequest(BaseModel):
    cluster_id: str = "cluster-local"
    time_window_minutes: int = Field(default=30, ge=5, le=1440)
    namespace: str | None = None
    workload: str | None = None
    metrics: list[MetricSnapshot] = Field(default_factory=list)
    events: list[EventSnapshot] = Field(default_factory=list)
    extra_context: dict[str, str] = Field(default_factory=dict)


class RootCauseCandidate(BaseModel):
    cause: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)


class AIAnalyzeResult(BaseModel):
    summary: str
    recommendations: list[str]
    root_causes: list[RootCauseCandidate]
    risk_level: str
    generated_at: datetime


class AIAnalyzeTaskResponse(BaseModel):
    task_id: int
    status: str


class AIAnalyzeTaskRead(BaseModel):
    task_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    result: AIAnalyzeResult | None = None
    error: str | None = None
