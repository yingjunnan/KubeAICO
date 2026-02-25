from datetime import datetime

from pydantic import BaseModel, Field


class ManagedClusterBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    cluster_id: str = Field(min_length=1, max_length=64)
    k8s_api_url: str = Field(min_length=1, max_length=300)
    prometheus_url: str | None = Field(default=None, max_length=300)
    k8s_bearer_token: str | None = Field(default=None, max_length=4096)
    is_active: bool = True
    description: str | None = Field(default=None, max_length=500)


class ManagedClusterCreate(ManagedClusterBase):
    pass


class ManagedClusterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    cluster_id: str | None = Field(default=None, min_length=1, max_length=64)
    k8s_api_url: str | None = Field(default=None, min_length=1, max_length=300)
    prometheus_url: str | None = Field(default=None, max_length=300)
    k8s_bearer_token: str | None = Field(default=None, max_length=4096)
    is_active: bool | None = None
    description: str | None = Field(default=None, max_length=500)


class ManagedClusterRead(BaseModel):
    id: int
    name: str
    cluster_id: str
    k8s_api_url: str
    prometheus_url: str | None = None
    k8s_bearer_token_masked: str | None = None
    is_active: bool
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ManagedClusterListResponse(BaseModel):
    total: int
    items: list[ManagedClusterRead]


class ClusterConnectionTestRequest(BaseModel):
    k8s_api_url: str = Field(min_length=1, max_length=300)
    prometheus_url: str | None = Field(default=None, max_length=300)
    k8s_bearer_token: str | None = Field(default=None, max_length=4096)


class ClusterConnectionTestComponent(BaseModel):
    ok: bool
    message: str


class ClusterConnectionTestResponse(BaseModel):
    ok: bool
    mode: str
    kubernetes: ClusterConnectionTestComponent
    prometheus: ClusterConnectionTestComponent
    checked_at: datetime
