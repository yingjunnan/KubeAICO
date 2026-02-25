from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.collector.kubernetes import KubernetesCollector
from app.collector.prometheus import PrometheusCollector
from app.schemas.alerts import AlertItem, AlertListResponse, AlertSeverity

if TYPE_CHECKING:
    from app.db.models import ManagedCluster


class AlertService:
    def __init__(
        self,
        k8s_collector: KubernetesCollector,
        prometheus_collector: PrometheusCollector,
    ) -> None:
        self.k8s_collector = k8s_collector
        self.prometheus_collector = prometheus_collector

    async def get_alerts(
        self,
        namespace: str | None = None,
        limit: int = 50,
        cluster: ManagedCluster | None = None,
    ) -> AlertListResponse:
        events = await self.k8s_collector.list_events(namespace=namespace, cluster=cluster)
        prom_alerts = await self.prometheus_collector.get_firing_alerts(cluster=cluster)

        items: list[AlertItem] = []

        for event in events:
            event_type = event.get("type", "Normal")
            if event_type == "Normal":
                continue

            reason = event.get("reason", "Unknown")
            severity = self._severity_from_reason(reason)

            event_ts = event.get("lastTimestamp") or event.get("eventTime")
            if event_ts:
                try:
                    start_time = datetime.fromisoformat(event_ts.replace("Z", "+00:00"))
                except ValueError:
                    start_time = datetime.now(UTC)
            else:
                start_time = datetime.now(UTC)

            items.append(
                AlertItem(
                    id=f"k8s-{event.get('metadata', {}).get('name', 'unknown')}",
                    severity=severity,
                    source="k8s-event",
                    title=reason,
                    message=event.get("message", "Kubernetes warning event"),
                    namespace=event.get("metadata", {}).get("namespace"),
                    start_time=start_time,
                    recommendation=self._recommendation_for_reason(reason),
                )
            )

        for idx, alert in enumerate(prom_alerts, start=1):
            sev = alert.get("severity", "warning").lower()
            mapped = AlertSeverity.p2 if sev in {"warning", "medium"} else AlertSeverity.p1

            items.append(
                AlertItem(
                    id=f"prom-{idx}",
                    severity=mapped,
                    source="prometheus",
                    title=alert.get("name", "PrometheusAlert"),
                    message=alert.get("summary", "Prometheus alert is firing"),
                    namespace=alert.get("namespace"),
                    start_time=datetime.now(UTC),
                    recommendation="Review firing alert labels and correlate with recent deployments.",
                )
            )

        items.sort(key=lambda item: item.start_time, reverse=True)
        return AlertListResponse(total=min(len(items), limit), items=items[:limit])

    @staticmethod
    def _severity_from_reason(reason: str) -> AlertSeverity:
        reason_low = reason.lower()
        if reason_low in {"oomkilled", "failed", "failedmount", "failedscheduling"}:
            return AlertSeverity.p1
        if reason_low in {"backoff", "unhealthy", "nodepressure"}:
            return AlertSeverity.p2
        return AlertSeverity.p3

    @staticmethod
    def _recommendation_for_reason(reason: str) -> str:
        reason_low = reason.lower()
        if reason_low == "oomkilled":
            return "Increase memory limits or optimize workload memory consumption."
        if reason_low == "backoff":
            return "Check container logs and startup probes for repeated crashes."
        if reason_low == "failedscheduling":
            return "Inspect node allocatable resources and affinity/toleration constraints."
        return "Inspect workload events and recent deployment/config changes."
