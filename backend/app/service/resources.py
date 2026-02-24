from sqlalchemy.ext.asyncio import AsyncSession

from app.collector.kubernetes import KubernetesCollector
from app.db.models import User
from app.repository.audit import AuditRepository
from app.schemas.resource import WorkloadItem, WorkloadListResponse


class ResourceService:
    def __init__(self, k8s_collector: KubernetesCollector, audit_repo: AuditRepository) -> None:
        self.k8s_collector = k8s_collector
        self.audit_repo = audit_repo

    async def list_resources(
        self,
        kind: str,
        namespace: str | None,
        label_selector: str | None,
        status: str | None,
    ) -> WorkloadListResponse:
        items = await self.k8s_collector.list_resources(
            kind=kind,
            namespace=namespace,
            label_selector=label_selector,
        )
        workloads = [self._to_workload_item(kind, item) for item in items]

        if status:
            workloads = [item for item in workloads if item.status.lower() == status.lower()]

        return WorkloadListResponse(kind=kind, total=len(workloads), items=workloads)

    async def scale_workload(
        self,
        *,
        db: AsyncSession,
        user: User,
        kind: str,
        name: str,
        namespace: str,
        replicas: int,
    ) -> int:
        await self.k8s_collector.scale_workload(
            kind=kind,
            name=name,
            namespace=namespace,
            replicas=replicas,
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
    ) -> int:
        await self.k8s_collector.rollout_restart(kind=kind, name=name, namespace=namespace)
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
