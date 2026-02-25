from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.collector.kubernetes import KubernetesCollector
from app.collector.prometheus import PrometheusCollector
from app.db.models import User
from app.repository.audit import AuditRepository
from app.schemas.resource import (
    ResourceDetailResponse,
    ResourceEvent,
    ResourceKind,
    ResourceLogsResponse,
    ResourceMetricPoint,
    ResourceMetricSeries,
    ResourceMetricsPanel,
    WorkloadItem,
    WorkloadListResponse,
)

if TYPE_CHECKING:
    from app.db.models import ManagedCluster


class ResourceService:
    def __init__(
        self,
        k8s_collector: KubernetesCollector,
        prometheus_collector: PrometheusCollector,
        audit_repo: AuditRepository,
    ) -> None:
        self.k8s_collector = k8s_collector
        self.prometheus_collector = prometheus_collector
        self.audit_repo = audit_repo

    async def list_resources(
        self,
        kind: str,
        namespace: str | None,
        label_selector: str | None,
        status: str | None,
        cluster: ManagedCluster | None = None,
    ) -> WorkloadListResponse:
        items = await self.k8s_collector.list_resources(
            kind=kind,
            namespace=namespace,
            label_selector=label_selector,
            cluster=cluster,
        )
        workloads = [self._to_workload_item(kind, item) for item in items]

        if status:
            workloads = [item for item in workloads if item.status.lower() == status.lower()]

        return WorkloadListResponse(kind=kind, total=len(workloads), items=workloads)

    async def get_resource_detail(
        self,
        *,
        kind: str,
        name: str,
        namespace: str,
        range_minutes: int = 10,
        step_seconds: int = 30,
        cluster: ManagedCluster | None = None,
    ) -> ResourceDetailResponse:
        resource = await self.k8s_collector.get_resource(
            kind=kind,
            name=name,
            namespace=namespace,
            cluster=cluster,
        )
        workload = self._to_workload_item(kind, resource)

        events_raw = await self.k8s_collector.get_related_events(
            kind=kind,
            name=name,
            namespace=namespace,
            cluster=cluster,
        )
        events = [
            ResourceEvent(
                type=event.get("type", "Normal"),
                reason=event.get("reason", "Unknown"),
                message=event.get("message", ""),
                timestamp=self._normalize_event_timestamp(event),
            )
            for event in events_raw
        ]

        metrics = await self._build_detail_metrics(
            kind=kind,
            name=name,
            namespace=namespace,
            workload=workload,
            range_minutes=range_minutes,
            step_seconds=step_seconds,
            cluster=cluster,
        )

        return ResourceDetailResponse(
            item=workload,
            manifest=resource,
            events=events,
            metrics=metrics,
        )

    async def get_resource_logs(
        self,
        *,
        kind: ResourceKind,
        name: str,
        namespace: str,
        log_lines: int = 120,
        cluster: ManagedCluster | None = None,
    ) -> ResourceLogsResponse:
        try:
            logs = await self.k8s_collector.get_resource_logs(
                kind=kind,
                name=name,
                namespace=namespace,
                tail_lines=log_lines,
                cluster=cluster,
            )
        except Exception as exc:  # noqa: BLE001 - logs failure should not break detail page
            logs = [f"Unable to load logs: {self._summarize_exception(exc)}."]

        return ResourceLogsResponse(
            kind=kind,
            name=name,
            namespace=namespace,
            logs=logs,
        )

    async def scale_workload(
        self,
        *,
        db: AsyncSession,
        user: User,
        kind: str,
        name: str,
        namespace: str,
        replicas: int,
        cluster: ManagedCluster | None = None,
    ) -> int:
        if replicas > 1000:
            raise ValueError("Scale target is too high; max replicas is 1000 in current policy")

        await self.k8s_collector.scale_workload(
            kind=kind,
            name=name,
            namespace=namespace,
            replicas=replicas,
            cluster=cluster,
        )
        log = await self.audit_repo.create(
            db,
            user_id=user.id,
            action="scale",
            target_kind=kind,
            target_name=name,
            namespace=namespace,
            status="success",
            message=f"Set replicas to {replicas}",
        )
        return log.id

    async def rollout_restart(
        self,
        *,
        db: AsyncSession,
        user: User,
        kind: str,
        name: str,
        namespace: str,
        cluster: ManagedCluster | None = None,
    ) -> int:
        await self.k8s_collector.rollout_restart(
            kind=kind,
            name=name,
            namespace=namespace,
            cluster=cluster,
        )
        log = await self.audit_repo.create(
            db,
            user_id=user.id,
            action="rollout_restart",
            target_kind=kind,
            target_name=name,
            namespace=namespace,
            status="success",
            message="Triggered rollout restart",
        )
        return log.id

    @staticmethod
    def _to_workload_item(kind: str, item: dict) -> WorkloadItem:
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        item_status = item.get("status", {})

        replicas = spec.get("replicas")
        available = item_status.get("readyReplicas")

        ready_ratio = None
        if replicas is not None and replicas > 0:
            ready_ratio = round((available or 0) / replicas, 2)

        restarts = 0
        for container in item_status.get("containerStatuses", []):
            restarts += int(container.get("restartCount", 0))

        if kind == "pod":
            status = item_status.get("phase", "Unknown")
        elif kind in {"service", "ingress"}:
            status = "Active"
        else:
            desired = replicas or 0
            ready = available or 0
            status = "Healthy" if desired == ready else "Degraded"

        return WorkloadItem(
            name=metadata.get("name", "unknown"),
            namespace=metadata.get("namespace", "default"),
            kind=kind,
            status=status,
            replicas=replicas,
            available_replicas=available,
            ready_ratio=ready_ratio,
            restarts=restarts,
            labels=metadata.get("labels") or {},
        )

    @staticmethod
    def _normalize_event_timestamp(event: dict) -> str:
        return (
            event.get("lastTimestamp")
            or event.get("eventTime")
            or event.get("firstTimestamp")
            or ""
        )

    @staticmethod
    def _summarize_exception(exc: Exception) -> str:
        if isinstance(exc, httpx.HTTPStatusError):
            return f"HTTP {exc.response.status_code}"
        if isinstance(exc, httpx.RequestError):
            return exc.__class__.__name__
        return str(exc) or exc.__class__.__name__

    async def _build_detail_metrics(
        self,
        *,
        kind: str,
        name: str,
        namespace: str,
        workload: WorkloadItem,
        range_minutes: int,
        step_seconds: int,
        cluster: ManagedCluster | None = None,
    ) -> ResourceMetricsPanel:
        profile = self._metric_profile(kind=kind)
        workload_filter = (
            self._workload_hint_from_name(name)
            if kind in {"service", "ingress"}
            else name
        )
        series: list[ResourceMetricSeries] = []

        for metric_key, metric_label, unit in profile:
            points = await self._query_metric_series(
                metric_key=metric_key,
                namespace=namespace,
                workload=workload_filter,
                range_minutes=range_minutes,
                step_seconds=step_seconds,
                cluster=cluster,
            )
            series.append(
                ResourceMetricSeries(
                    key=metric_key,
                    label=metric_label,
                    unit=unit,
                    points=points,
                )
            )

        if kind in {"deployment", "statefulset", "daemonset"}:
            desired = float(workload.replicas or 0)
            available = float(workload.available_replicas or 0)
            series.append(
                ResourceMetricSeries(
                    key="desired_replicas",
                    label="Desired Replicas",
                    unit="replicas",
                    points=self._build_constant_series(
                        value=desired,
                        range_minutes=range_minutes,
                        step_seconds=step_seconds,
                    ),
                )
            )
            series.append(
                ResourceMetricSeries(
                    key="available_replicas",
                    label="Available Replicas",
                    unit="replicas",
                    points=self._build_constant_series(
                        value=available,
                        range_minutes=range_minutes,
                        step_seconds=step_seconds,
                    ),
                )
            )

        return ResourceMetricsPanel(
            range_minutes=range_minutes,
            step_seconds=step_seconds,
            series=series,
        )

    def _metric_profile(self, kind: str) -> list[tuple[str, str, str]]:
        if kind == "pod":
            return [
                ("cpu_usage", "CPU Usage", "cores"),
                ("memory_usage", "Memory Usage", "bytes"),
                ("network_rx", "Network RX", "bytes_per_second"),
                ("network_tx", "Network TX", "bytes_per_second"),
            ]
        if kind in {"deployment", "statefulset", "daemonset"}:
            return [
                ("cpu_usage", "CPU Usage", "cores"),
                ("memory_usage", "Memory Usage", "bytes"),
                ("error_rate", "Throttle/Error Rate", "ratio"),
            ]
        if kind in {"service", "ingress"}:
            return [
                ("network_rx", "Ingress Traffic", "bytes_per_second"),
                ("network_tx", "Egress Traffic", "bytes_per_second"),
                ("error_rate", "Throttle/Error Rate", "ratio"),
            ]
        return [
            ("cpu_usage", "CPU Usage", "cores"),
            ("memory_usage", "Memory Usage", "bytes"),
        ]

    async def _query_metric_series(
        self,
        *,
        metric_key: str,
        namespace: str,
        workload: str | None,
        range_minutes: int,
        step_seconds: int,
        cluster: ManagedCluster | None = None,
    ) -> list[ResourceMetricPoint]:
        raw_series = await self.prometheus_collector.get_timeseries(
            metric=metric_key,
            range_minutes=range_minutes,
            namespace=namespace,
            workload=workload,
            step_seconds=step_seconds,
            cluster=cluster,
        )

        merged: dict[int, float] = {}
        for row in raw_series:
            for pair in row.get("values", []):
                ts = int(pair[0])
                value = float(pair[1])
                merged[ts] = merged.get(ts, 0.0) + value

        return [
            ResourceMetricPoint(ts=ts, value=value)
            for ts, value in sorted(merged.items(), key=lambda item: item[0])
        ]

    @staticmethod
    def _build_constant_series(
        *,
        value: float,
        range_minutes: int,
        step_seconds: int,
    ) -> list[ResourceMetricPoint]:
        now = datetime.now(UTC)
        total_points = max(10, int(range_minutes * 60 / step_seconds))
        return [
            ResourceMetricPoint(
                ts=int(
                    (now - timedelta(seconds=(total_points - index) * step_seconds)).timestamp()
                ),
                value=value,
            )
            for index in range(total_points)
        ]

    @staticmethod
    def _workload_hint_from_name(resource_name: str) -> str:
        for suffix in ("-svc", "-service", "-ingress"):
            if resource_name.endswith(suffix):
                return resource_name[: -len(suffix)] or resource_name
        return resource_name
