from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import math
from typing import TYPE_CHECKING, Any

import httpx

from app.core.config import Settings

if TYPE_CHECKING:
    from app.db.models import ManagedCluster


@dataclass
class NamespaceUsageData:
    namespace: str
    cpu_millicores: float
    memory_bytes: float
    pod_count: int


class PrometheusCollector:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.settings.prometheus_timeout_seconds,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def query_instant(
        self,
        promql: str,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        prometheus_url = self._resolve_prometheus_url(cluster)
        if self._should_use_mock(prometheus_url):
            return []

        client = await self._get_client()
        resp = await client.get(
            f"{prometheus_url.rstrip('/')}/api/v1/query",
            params={"query": promql},
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") != "success":
            return []
        return payload.get("data", {}).get("result", [])

    async def query_range(
        self,
        promql: str,
        start: datetime,
        end: datetime,
        step_seconds: int,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        prometheus_url = self._resolve_prometheus_url(cluster)
        if self._should_use_mock(prometheus_url):
            return []

        client = await self._get_client()
        resp = await client.get(
            f"{prometheus_url.rstrip('/')}/api/v1/query_range",
            params={
                "query": promql,
                "start": int(start.timestamp()),
                "end": int(end.timestamp()),
                "step": step_seconds,
            },
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") != "success":
            return []
        return payload.get("data", {}).get("result", [])

    async def get_cluster_usage(self, cluster: ManagedCluster | None = None) -> dict[str, float]:
        prometheus_url = self._resolve_prometheus_url(cluster)
        if self._should_use_mock(prometheus_url):
            return {
                "cpu_usage_cores": 8.2,
                "cpu_capacity_cores": 16.0,
                "memory_usage_bytes": 22 * 1024**3,
                "memory_capacity_bytes": 48 * 1024**3,
            }

        cpu_usage_res = await self.query_instant(
            'sum(rate(container_cpu_usage_seconds_total{container!=""}[5m]))',
            cluster=cluster,
        )
        cpu_capacity_res = await self.query_instant("sum(machine_cpu_cores)", cluster=cluster)
        mem_usage_res = await self.query_instant(
            'sum(container_memory_working_set_bytes{container!=""})',
            cluster=cluster,
        )
        mem_capacity_res = await self.query_instant("sum(machine_memory_bytes)", cluster=cluster)

        return {
            "cpu_usage_cores": self._extract_scalar(cpu_usage_res),
            "cpu_capacity_cores": self._extract_scalar(cpu_capacity_res),
            "memory_usage_bytes": self._extract_scalar(mem_usage_res),
            "memory_capacity_bytes": self._extract_scalar(mem_capacity_res),
        }

    async def get_namespace_usage(
        self,
        limit: int = 5,
        cluster: ManagedCluster | None = None,
    ) -> list[NamespaceUsageData]:
        prometheus_url = self._resolve_prometheus_url(cluster)
        if self._should_use_mock(prometheus_url):
            return [
                NamespaceUsageData("default", 2100, 5.3 * 1024**3, 28),
                NamespaceUsageData("kube-system", 1200, 3.8 * 1024**3, 22),
                NamespaceUsageData("monitoring", 900, 4.1 * 1024**3, 14),
                NamespaceUsageData("prod", 1800, 6.7 * 1024**3, 31),
                NamespaceUsageData("dev", 600, 2.2 * 1024**3, 16),
            ][:limit]

        cpu_result = await self.query_instant(
            f'topk({limit}, sum(rate(container_cpu_usage_seconds_total{{container!=""}}[5m])) by (namespace))',
            cluster=cluster,
        )
        mem_result = await self.query_instant(
            f'topk({limit}, sum(container_memory_working_set_bytes{{container!=""}}) by (namespace))',
            cluster=cluster,
        )
        pod_result = await self.query_instant(
            f"topk({limit}, count(kube_pod_info) by (namespace))",
            cluster=cluster,
        )

        cpu_map = self._extract_vector_by_namespace(cpu_result, multiply=1000)
        mem_map = self._extract_vector_by_namespace(mem_result)
        pod_map = self._extract_vector_by_namespace(pod_result)

        namespaces = sorted(set(cpu_map) | set(mem_map) | set(pod_map))
        output = [
            NamespaceUsageData(
                namespace=ns,
                cpu_millicores=float(cpu_map.get(ns, 0.0)),
                memory_bytes=float(mem_map.get(ns, 0.0)),
                pod_count=int(pod_map.get(ns, 0)),
            )
            for ns in namespaces
        ]
        output.sort(key=lambda item: item.memory_bytes, reverse=True)
        return output[:limit]

    async def get_firing_alerts(self, cluster: ManagedCluster | None = None) -> list[dict[str, str]]:
        prometheus_url = self._resolve_prometheus_url(cluster)
        if self._should_use_mock(prometheus_url):
            return [
                {
                    "name": "NodeMemoryPressure",
                    "severity": "warning",
                    "summary": "Node worker-1 memory usage is above 85%",
                    "namespace": "kube-system",
                }
            ]

        alert_result = await self.query_instant('ALERTS{alertstate="firing"}', cluster=cluster)
        firing: list[dict[str, str]] = []
        for item in alert_result:
            metric = item.get("metric", {})
            firing.append(
                {
                    "name": metric.get("alertname", "UnknownAlert"),
                    "severity": metric.get("severity", "warning"),
                    "summary": metric.get("summary", "Prometheus firing alert"),
                    "namespace": metric.get("namespace", "default"),
                }
            )
        return firing

    async def get_timeseries(
        self,
        metric: str,
        range_minutes: int,
        namespace: str | None,
        workload: str | None,
        step_seconds: int,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        prometheus_url = self._resolve_prometheus_url(cluster)
        if self._should_use_mock(prometheus_url):
            return self._mock_timeseries(metric=metric, range_minutes=range_minutes, step_seconds=step_seconds)

        end = datetime.now(UTC)
        start = end - timedelta(minutes=range_minutes)

        promql = self._to_promql(metric=metric, namespace=namespace, workload=workload)
        return await self.query_range(
            promql=promql,
            start=start,
            end=end,
            step_seconds=step_seconds,
            cluster=cluster,
        )

    def _resolve_prometheus_url(self, cluster: ManagedCluster | None) -> str | None:
        if cluster and cluster.prometheus_url:
            return cluster.prometheus_url
        return self.settings.prometheus_url

    def _should_use_mock(self, prometheus_url: str | None) -> bool:
        return self.settings.use_mock_data or not prometheus_url

    def _to_promql(self, metric: str, namespace: str | None, workload: str | None) -> str:
        selector_parts: list[str] = ['container!=""']
        if namespace:
            selector_parts.append(f'namespace="{namespace}"')
        if workload:
            selector_parts.append(f'pod=~"{workload}.*"')

        selector = "{" + ",".join(selector_parts) + "}"

        metric_mapping = {
            "cpu_usage": f"sum(rate(container_cpu_usage_seconds_total{selector}[5m]))",
            "memory_usage": f"sum(container_memory_working_set_bytes{selector})",
            "network_rx": f"sum(rate(container_network_receive_bytes_total{selector}[5m]))",
            "network_tx": f"sum(rate(container_network_transmit_bytes_total{selector}[5m]))",
            "error_rate": f"sum(rate(container_cpu_cfs_throttled_seconds_total{selector}[5m]))",
        }
        return metric_mapping.get(metric, metric_mapping["cpu_usage"])

    def _mock_timeseries(self, metric: str, range_minutes: int, step_seconds: int) -> list[dict[str, Any]]:
        now = datetime.now(UTC)
        total_points = max(10, int(range_minutes * 60 / step_seconds))
        result: list[list[float | int]] = []

        base = {
            "cpu_usage": 6.5,
            "memory_usage": 18 * 1024**3,
            "network_rx": 2.3 * 1024**2,
            "network_tx": 1.8 * 1024**2,
            "error_rate": 0.02,
        }.get(metric, 5.0)

        amplitude = base * 0.12

        for index in range(total_points):
            ts = int((now - timedelta(seconds=(total_points - index) * step_seconds)).timestamp())
            value = base + amplitude * math.sin(index / 3.5)
            result.append([ts, max(value, 0)])

        return [
            {
                "metric": {"series": "cluster"},
                "values": result,
            }
        ]

    @staticmethod
    def _extract_scalar(result: list[dict[str, Any]]) -> float:
        if not result:
            return 0.0

        value = result[0].get("value") or [None, 0]
        return float(value[1])

    @staticmethod
    def _extract_vector_by_namespace(
        result: list[dict[str, Any]],
        multiply: float = 1.0,
    ) -> dict[str, float]:
        output: dict[str, float] = {}
        for item in result:
            metric = item.get("metric", {})
            namespace = metric.get("namespace", "default")
            value = item.get("value") or [None, 0]
            output[namespace] = float(value[1]) * multiply
        return output
