from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.collector.kubernetes import KubernetesCollector
from app.collector.prometheus import PrometheusCollector
from app.core.config import Settings
from app.db.models import ManagedCluster
from app.repository.cluster import ClusterRepository
from app.schemas.cluster import (
    ClusterConnectionTestComponent,
    ClusterConnectionTestRequest,
    ClusterConnectionTestResponse,
    ManagedClusterCreate,
    ManagedClusterListResponse,
    ManagedClusterRead,
    ManagedClusterUpdate,
)


@dataclass
class ClusterProbeTarget:
    k8s_api_url: str
    prometheus_url: str | None = None
    k8s_bearer_token: str | None = None


class ClusterService:
    def __init__(
        self,
        repo: ClusterRepository,
        k8s_collector: KubernetesCollector,
        prometheus_collector: PrometheusCollector,
        settings: Settings,
    ) -> None:
        self.repo = repo
        self.k8s_collector = k8s_collector
        self.prometheus_collector = prometheus_collector
        self.settings = settings

    async def list_clusters(self, db: AsyncSession) -> ManagedClusterListResponse:
        rows = await self.repo.list(db)
        return ManagedClusterListResponse(total=len(rows), items=[self._to_read(row) for row in rows])

    async def create_cluster(self, db: AsyncSession, payload: ManagedClusterCreate) -> ManagedClusterRead:
        if await self.repo.get_by_name(db, payload.name):
            raise ValueError(f"name '{payload.name}' already exists")
        if await self.repo.get_by_cluster_key(db, payload.cluster_id):
            raise ValueError(f"cluster_id '{payload.cluster_id}' already exists")

        test_result = await self.test_connection_payload(
            ClusterConnectionTestRequest(
                k8s_api_url=payload.k8s_api_url,
                prometheus_url=payload.prometheus_url,
                k8s_bearer_token=payload.k8s_bearer_token,
            )
        )
        if not test_result.ok:
            raise ValueError(self._build_test_failure_message(test_result))

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

    async def test_connection_payload(
        self,
        payload: ClusterConnectionTestRequest,
    ) -> ClusterConnectionTestResponse:
        target = ClusterProbeTarget(
            k8s_api_url=payload.k8s_api_url.strip(),
            prometheus_url=payload.prometheus_url.strip() if payload.prometheus_url else None,
            k8s_bearer_token=payload.k8s_bearer_token.strip() if payload.k8s_bearer_token else None,
        )
        return await self._run_connection_test(target)

    async def test_cluster_connection(
        self,
        db: AsyncSession,
        cluster_pk: int,
    ) -> ClusterConnectionTestResponse:
        row = await self.repo.get(db, cluster_pk)
        if not row:
            raise ValueError("Cluster not found")
        target = ClusterProbeTarget(
            k8s_api_url=row.k8s_api_url,
            prometheus_url=row.prometheus_url,
            k8s_bearer_token=row.k8s_bearer_token,
        )
        return await self._run_connection_test(target)

    async def _run_connection_test(
        self,
        target: ClusterProbeTarget,
    ) -> ClusterConnectionTestResponse:
        mode = "mock" if self.settings.use_mock_data else "real"

        try:
            nodes = await self.k8s_collector.list_nodes(cluster=target)
            pods = await self.k8s_collector.list_pods(cluster=target)
            events = await self.k8s_collector.list_events(cluster=target)
            k8s_component = ClusterConnectionTestComponent(
                ok=True,
                message=f"Kubernetes API ok (nodes={len(nodes)}, pods={len(pods)}, events={len(events)})",
            )
        except Exception as exc:  # noqa: BLE001 - return actionable diagnostics to UI
            k8s_component = ClusterConnectionTestComponent(
                ok=False,
                message=f"Kubernetes API check failed: {self._summarize_exception(exc)}",
            )

        if target.prometheus_url:
            try:
                vector = await self.prometheus_collector.query_instant("up", cluster=target)
                prometheus_component = ClusterConnectionTestComponent(
                    ok=True,
                    message=f"Prometheus API ok (series={len(vector)})",
                )
            except Exception as exc:  # noqa: BLE001 - return actionable diagnostics to UI
                prometheus_component = ClusterConnectionTestComponent(
                    ok=False,
                    message=f"Prometheus API check failed: {self._summarize_exception(exc)}",
                )
        else:
            prometheus_component = ClusterConnectionTestComponent(
                ok=True,
                message="Prometheus URL is empty, skipped.",
            )

        return ClusterConnectionTestResponse(
            ok=k8s_component.ok and prometheus_component.ok,
            mode=mode,
            kubernetes=k8s_component,
            prometheus=prometheus_component,
            checked_at=datetime.now(UTC),
        )

    @staticmethod
    def _build_test_failure_message(result: ClusterConnectionTestResponse) -> str:
        return (
            "Cluster connection test failed. "
            f"k8s={result.kubernetes.message}; prometheus={result.prometheus.message}"
        )

    @staticmethod
    def _summarize_exception(exc: Exception) -> str:
        if isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code
            request_url = str(exc.request.url)
            return f"HTTP {status_code} from {request_url}"
        if isinstance(exc, httpx.ConnectError):
            return "connection refused or host unreachable"
        if isinstance(exc, httpx.ConnectTimeout):
            return "connection timeout"
        if isinstance(exc, httpx.ReadTimeout):
            return "read timeout"
        return str(exc) or exc.__class__.__name__

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
