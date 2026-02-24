from datetime import datetime

from pydantic import BaseModel, Field


class NamespaceUsage(BaseModel):
    namespace: str
    cpu_millicores: float
    memory_bytes: float
    pod_count: int


class ClusterSummary(BaseModel):
    cluster_id: str = "cluster-local"
    generated_at: datetime

    nodes_total: int
    nodes_ready: int

    pods_total: int
    pods_pending: int
    pods_crashloop: int
    pods_oomkilled: int

    cpu_usage_cores: float
    cpu_capacity_cores: float
    memory_usage_bytes: float
    memory_capacity_bytes: float

    alerts_count: int
    risk_score: float = Field(ge=0, le=100)

    top_namespaces: list[NamespaceUsage]
