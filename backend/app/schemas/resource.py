from typing import Literal

from pydantic import BaseModel, Field

ResourceKind = Literal[
    "deployment",
    "statefulset",
    "daemonset",
    "pod",
    "service",
    "ingress",
]


class WorkloadItem(BaseModel):
    name: str
    namespace: str
    kind: ResourceKind
    status: str
    replicas: int | None = None
    available_replicas: int | None = None
    ready_ratio: float | None = None
    restarts: int = 0
    labels: dict[str, str] = Field(default_factory=dict)


class WorkloadListResponse(BaseModel):
    kind: ResourceKind
    total: int
    items: list[WorkloadItem]


class ScaleRequest(BaseModel):
    namespace: str
    replicas: int = Field(ge=0)


class RestartRequest(BaseModel):
    namespace: str


class ResourceActionResponse(BaseModel):
    status: str
    message: str
    audit_id: int | None = None


class ResourceEvent(BaseModel):
    type: str
    reason: str
    message: str
    timestamp: str


class ResourceDetailResponse(BaseModel):
    item: WorkloadItem
    events: list[ResourceEvent] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)
