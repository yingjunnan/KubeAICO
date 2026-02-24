from datetime import UTC, datetime

from app.collector.kubernetes import KubernetesCollector
from app.collector.prometheus import PrometheusCollector
from app.schemas.overview import ClusterSummary, NamespaceUsage
from app.service.alerts import AlertService


class OverviewService:
    def __init__(
        self,
        k8s_collector: KubernetesCollector,
        prometheus_collector: PrometheusCollector,
        alert_service: AlertService,
    ) -> None:
        self.k8s_collector = k8s_collector
        self.prometheus_collector = prometheus_collector
        self.alert_service = alert_service

    async def get_cluster_summary(self) -> ClusterSummary:
        nodes = await self.k8s_collector.list_nodes()
        pods = await self.k8s_collector.list_pods()
        alerts = await self.alert_service.get_alerts(limit=100)
        usage = await self.prometheus_collector.get_cluster_usage()
        top_ns = await self.prometheus_collector.get_namespace_usage(limit=5)

        nodes_total = len(nodes)
        nodes_ready = sum(1 for node in nodes if self._is_node_ready(node))

        pods_total = len(pods)
        pods_pending = 0
        pods_crashloop = 0
        pods_oomkilled = 0

        for pod in pods:
            phase = pod.get("status", {}).get("phase", "Unknown")
            if phase == "Pending":
                pods_pending += 1

            for status in pod.get("status", {}).get("containerStatuses", []):
                waiting_reason = (
                    status.get("state", {})
                    .get("waiting", {})
                    .get("reason")
                )
                last_reason = (
                    status.get("lastState", {})
                    .get("terminated", {})
                    .get("reason")
                )
                if waiting_reason == "CrashLoopBackOff":
                    pods_crashloop += 1
                if last_reason == "OOMKilled":
                    pods_oomkilled += 1

        risk_score = self._risk_score(
            nodes_total=nodes_total,
            nodes_ready=nodes_ready,
            pods_total=pods_total,
            pods_pending=pods_pending,
            pods_crashloop=pods_crashloop,
            pods_oomkilled=pods_oomkilled,
            alerts_count=alerts.total,
        )

        return ClusterSummary(
            generated_at=datetime.now(UTC),
            nodes_total=nodes_total,
            nodes_ready=nodes_ready,
            pods_total=pods_total,
            pods_pending=pods_pending,
            pods_crashloop=pods_crashloop,
            pods_oomkilled=pods_oomkilled,
            cpu_usage_cores=float(usage.get("cpu_usage_cores", 0)),
            cpu_capacity_cores=float(usage.get("cpu_capacity_cores", 0)),
            memory_usage_bytes=float(usage.get("memory_usage_bytes", 0)),
            memory_capacity_bytes=float(usage.get("memory_capacity_bytes", 0)),
            alerts_count=alerts.total,
            risk_score=risk_score,
            top_namespaces=[
                NamespaceUsage(
                    namespace=item.namespace,
                    cpu_millicores=item.cpu_millicores,
                    memory_bytes=item.memory_bytes,
                    pod_count=item.pod_count,
                )
                for item in top_ns
            ],
        )

    @staticmethod
    def _is_node_ready(node: dict) -> bool:
        conditions = node.get("status", {}).get("conditions", [])
        for cond in conditions:
            if cond.get("type") == "Ready":
                return cond.get("status") == "True"
        return False

    @staticmethod
    def _risk_score(
        *,
        nodes_total: int,
        nodes_ready: int,
        pods_total: int,
        pods_pending: int,
        pods_crashloop: int,
        pods_oomkilled: int,
        alerts_count: int,
    ) -> float:
        score = 0.0
        if nodes_total > 0:
            score += ((nodes_total - nodes_ready) / nodes_total) * 35

        if pods_total > 0:
            score += (pods_pending / pods_total) * 15
            score += ((pods_crashloop + pods_oomkilled) / pods_total) * 35

        score += min(alerts_count * 3, 15)
        return round(min(score, 100), 2)
