from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import httpx

from app.core.config import Settings

if TYPE_CHECKING:
    from app.db.models import ManagedCluster


class KubernetesCollector:
    kind_to_resource = {
        "deployment": ("apps/v1", "deployments"),
        "statefulset": ("apps/v1", "statefulsets"),
        "daemonset": ("apps/v1", "daemonsets"),
        "pod": ("v1", "pods"),
        "service": ("v1", "services"),
        "ingress": ("networking.k8s.io/v1", "ingresses"),
    }

    scalable_kinds = {"deployment", "statefulset", "daemonset"}

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: httpx.AsyncClient | None = None
        self._mock_state = self._build_mock_state()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15, verify=self.settings.k8s_verify_ssl)
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def list_nodes(self, cluster: ManagedCluster | None = None) -> list[dict[str, Any]]:
        if self._should_use_mock(cluster):
            return self._mock_state["nodes"]

        payload = await self._request("GET", "/api/v1/nodes", cluster=cluster)
        return payload.get("items", [])

    async def list_pods(
        self,
        namespace: str | None = None,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        if self._should_use_mock(cluster):
            pods: list[dict[str, Any]] = self._mock_state["pods"]
            if namespace:
                return [pod for pod in pods if pod.get("metadata", {}).get("namespace") == namespace]
            return pods

        if namespace:
            payload = await self._request("GET", f"/api/v1/namespaces/{namespace}/pods", cluster=cluster)
        else:
            payload = await self._request("GET", "/api/v1/pods", cluster=cluster)
        return payload.get("items", [])

    async def list_events(
        self,
        namespace: str | None = None,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        if self._should_use_mock(cluster):
            events: list[dict[str, Any]] = self._mock_state["events"]
            if namespace:
                return [
                    event
                    for event in events
                    if event.get("metadata", {}).get("namespace") == namespace
                ]
            return events

        if namespace:
            payload = await self._request("GET", f"/api/v1/namespaces/{namespace}/events", cluster=cluster)
        else:
            payload = await self._request("GET", "/api/v1/events", cluster=cluster)
        return payload.get("items", [])

    async def list_resources(
        self,
        kind: str,
        namespace: str | None = None,
        label_selector: str | None = None,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        if kind not in self.kind_to_resource:
            raise ValueError(f"Unsupported kind: {kind}")

        if self._should_use_mock(cluster):
            items = self._mock_state.get(kind, [])
            if namespace:
                items = [item for item in items if item.get("metadata", {}).get("namespace") == namespace]
            if label_selector:
                key, _, expected = label_selector.partition("=")
                if key and expected:
                    items = [
                        item
                        for item in items
                        if item.get("metadata", {}).get("labels", {}).get(key) == expected
                    ]
            return items

        path = self._list_path(kind=kind, namespace=namespace)
        params = {"labelSelector": label_selector} if label_selector else None
        payload = await self._request("GET", path, params=params, cluster=cluster)
        return payload.get("items", [])

    async def get_resource(
        self,
        kind: str,
        name: str,
        namespace: str,
        cluster: ManagedCluster | None = None,
    ) -> dict[str, Any]:
        if kind not in self.kind_to_resource:
            raise ValueError(f"Unsupported kind: {kind}")

        if self._should_use_mock(cluster):
            for item in self._mock_state.get(kind, []):
                metadata = item.get("metadata", {})
                if metadata.get("name") == name and metadata.get("namespace") == namespace:
                    return item
            raise ValueError("Resource not found")

        path = self._item_path(kind=kind, name=name, namespace=namespace)
        return await self._request("GET", path, cluster=cluster)

    async def get_related_events(
        self,
        kind: str,
        name: str,
        namespace: str,
        cluster: ManagedCluster | None = None,
    ) -> list[dict[str, Any]]:
        events = await self.list_events(namespace=namespace, cluster=cluster)
        expected_kind = {
            "deployment": "Deployment",
            "statefulset": "StatefulSet",
            "daemonset": "DaemonSet",
            "pod": "Pod",
            "service": "Service",
            "ingress": "Ingress",
        }.get(kind, kind)

        related: list[dict[str, Any]] = []
        for event in events:
            involved = event.get("involvedObject", {})
            if (
                involved.get("name") == name
                and involved.get("namespace") == namespace
                and involved.get("kind") == expected_kind
            ):
                related.append(event)
                continue

            # Fallback for incomplete event payloads.
            message = event.get("message", "")
            event_ns = event.get("metadata", {}).get("namespace")
            if event_ns == namespace and name in message:
                related.append(event)

        return related

    async def get_resource_logs(
        self,
        kind: str,
        name: str,
        namespace: str,
        tail_lines: int = 120,
        cluster: ManagedCluster | None = None,
    ) -> list[str]:
        if kind == "pod":
            return await self.get_pod_logs(
                namespace=namespace,
                pod_name=name,
                tail_lines=tail_lines,
                cluster=cluster,
            )

        if self._should_use_mock(cluster):
            pods = await self.list_pods(namespace=namespace, cluster=cluster)
            candidates = [
                pod
                for pod in pods
                if pod.get("metadata", {}).get("labels", {}).get("app") in {name, name.split("-")[0]}
            ]
            if not candidates:
                return [f"No pod logs available for {kind}/{name} in namespace {namespace}."]
            pod_name = candidates[0].get("metadata", {}).get("name", "")
            return await self.get_pod_logs(
                namespace=namespace,
                pod_name=pod_name,
                tail_lines=tail_lines,
                cluster=cluster,
            )

        try:
            resource = await self.get_resource(kind=kind, name=name, namespace=namespace, cluster=cluster)
        except ValueError:
            return []

        match_labels = (
            resource.get("spec", {})
            .get("selector", {})
            .get("matchLabels", {})
        )
        if not match_labels:
            return []

        selector = self._build_label_selector(match_labels)
        pods = await self.list_resources(
            kind="pod",
            namespace=namespace,
            label_selector=selector,
            cluster=cluster,
        )
        if not pods:
            return []

        pod_name = pods[0].get("metadata", {}).get("name")
        if not pod_name:
            return []
        return await self.get_pod_logs(
            namespace=namespace,
            pod_name=pod_name,
            tail_lines=tail_lines,
            cluster=cluster,
        )

    async def get_pod_logs(
        self,
        namespace: str,
        pod_name: str,
        tail_lines: int = 120,
        cluster: ManagedCluster | None = None,
    ) -> list[str]:
        if self._should_use_mock(cluster):
            key = f"{namespace}/{pod_name}"
            lines = self._mock_state.get("pod_logs", {}).get(key)
            if lines:
                return lines[:tail_lines]
            return [f"No mock logs found for pod {pod_name}."]

        k8s_api_url = self._resolve_k8s_api_url(cluster)
        if not k8s_api_url:
            raise ValueError("k8s_api_url is required for real cluster mode")

        headers: dict[str, str] = {}
        k8s_bearer_token = self._resolve_k8s_bearer_token(cluster)
        if k8s_bearer_token:
            headers["Authorization"] = f"Bearer {k8s_bearer_token}"

        endpoint = f"{k8s_api_url.rstrip('/')}/api/v1/namespaces/{namespace}/pods/{pod_name}/log"
        params = {"tailLines": tail_lines}
        client = await self._get_client()
        try:
            response = await client.get(endpoint, params=params, headers=headers)
        except httpx.RequestError as exc:
            return [f"Unable to fetch pod logs: {exc.__class__.__name__}."]

        if response.status_code == 406:
            # Some API gateways reject logs subresource unless Accept is wildcard.
            retry_headers = dict(headers)
            retry_headers["Accept"] = "*/*"
            try:
                response = await client.get(endpoint, params=params, headers=retry_headers)
            except httpx.RequestError as exc:
                return [f"Unable to fetch pod logs after retry: {exc.__class__.__name__}."]

        if response.is_success:
            return [line for line in response.text.splitlines() if line]

        message = self._extract_error_message(response)
        suffix = f" {message}" if message else ""
        return [f"Unable to fetch pod logs (HTTP {response.status_code}).{suffix}"]

    async def scale_workload(
        self,
        kind: str,
        name: str,
        namespace: str,
        replicas: int,
        cluster: ManagedCluster | None = None,
    ) -> dict[str, Any]:
        if kind not in self.scalable_kinds:
            raise ValueError(f"Kind '{kind}' does not support scale")

        if self._should_use_mock(cluster):
            for item in self._mock_state[kind]:
                md = item.get("metadata", {})
                if md.get("name") == name and md.get("namespace") == namespace:
                    item.setdefault("spec", {})["replicas"] = replicas
                    item.setdefault("status", {})["replicas"] = replicas
                    item.setdefault("status", {})["readyReplicas"] = replicas
                    return {"status": "success"}
            raise ValueError("Resource not found")

        api_version, resource = self.kind_to_resource[kind]
        path = f"/apis/{api_version}/namespaces/{namespace}/{resource}/{name}/scale"
        body = {"spec": {"replicas": replicas}}
        return await self._request(
            "PATCH",
            path,
            json=body,
            content_type="application/merge-patch+json",
            cluster=cluster,
        )

    async def rollout_restart(
        self,
        kind: str,
        name: str,
        namespace: str,
        cluster: ManagedCluster | None = None,
    ) -> dict[str, Any]:
        if kind not in self.scalable_kinds:
            raise ValueError(f"Kind '{kind}' does not support rollout restart")

        if self._should_use_mock(cluster):
            now = datetime.now(UTC).isoformat()
            for item in self._mock_state[kind]:
                md = item.get("metadata", {})
                if md.get("name") == name and md.get("namespace") == namespace:
                    annotations = (
                        item.setdefault("spec", {})
                        .setdefault("template", {})
                        .setdefault("metadata", {})
                        .setdefault("annotations", {})
                    )
                    annotations["kubectl.kubernetes.io/restartedAt"] = now
                    return {"status": "success", "restartedAt": now}
            raise ValueError("Resource not found")

        api_version, resource = self.kind_to_resource[kind]
        path = f"/apis/{api_version}/namespaces/{namespace}/{resource}/{name}"
        now = datetime.now(UTC).isoformat()
        patch_payload = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {"kubectl.kubernetes.io/restartedAt": now}
                    }
                }
            }
        }
        return await self._request(
            "PATCH",
            path,
            json=patch_payload,
            content_type="application/strategic-merge-patch+json",
            cluster=cluster,
        )

    def _resolve_k8s_api_url(self, cluster: ManagedCluster | None) -> str | None:
        if cluster and cluster.k8s_api_url:
            return cluster.k8s_api_url
        return self.settings.k8s_api_url

    def _resolve_k8s_bearer_token(self, cluster: ManagedCluster | None) -> str | None:
        if cluster and cluster.k8s_bearer_token:
            return cluster.k8s_bearer_token
        return self.settings.k8s_bearer_token

    def _should_use_mock(self, cluster: ManagedCluster | None) -> bool:
        return self.settings.use_mock_data or not self._resolve_k8s_api_url(cluster)

    def _list_path(self, kind: str, namespace: str | None) -> str:
        api_version, resource = self.kind_to_resource[kind]
        if api_version == "v1":
            base = "/api/v1"
        else:
            base = f"/apis/{api_version}"

        if namespace:
            return f"{base}/namespaces/{namespace}/{resource}"
        return f"{base}/{resource}"

    def _item_path(self, kind: str, name: str, namespace: str) -> str:
        api_version, resource = self.kind_to_resource[kind]
        if api_version == "v1":
            base = "/api/v1"
        else:
            base = f"/apis/{api_version}"
        return f"{base}/namespaces/{namespace}/{resource}/{name}"

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        content_type: str = "application/json",
        cluster: ManagedCluster | None = None,
    ) -> dict[str, Any]:
        k8s_api_url = self._resolve_k8s_api_url(cluster)
        if not k8s_api_url:
            raise ValueError("k8s_api_url is required for real cluster mode")

        headers = {
            "Accept": "application/json",
            "Content-Type": content_type,
        }
        k8s_bearer_token = self._resolve_k8s_bearer_token(cluster)
        if k8s_bearer_token:
            headers["Authorization"] = f"Bearer {k8s_bearer_token}"

        client = await self._get_client()
        response = await client.request(
            method,
            f"{k8s_api_url.rstrip('/')}{path}",
            params=params,
            json=json,
            headers=headers,
        )

        response.raise_for_status()
        if response.content:
            return response.json()
        return {"status": "success"}

    def _build_mock_state(self) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        return {
            "nodes": [
                {
                    "metadata": {"name": "worker-1"},
                    "status": {
                        "capacity": {"cpu": "8", "memory": "32Gi"},
                        "conditions": [{"type": "Ready", "status": "True"}],
                    },
                },
                {
                    "metadata": {"name": "worker-2"},
                    "status": {
                        "capacity": {"cpu": "8", "memory": "32Gi"},
                        "conditions": [{"type": "Ready", "status": "True"}],
                    },
                },
                {
                    "metadata": {"name": "worker-3"},
                    "status": {
                        "capacity": {"cpu": "8", "memory": "32Gi"},
                        "conditions": [{"type": "Ready", "status": "False"}],
                    },
                },
            ],
            "pods": [
                self._mock_pod("web-7b6f", "default", "Running", 0),
                self._mock_pod("api-8d4f", "default", "Running", 1),
                self._mock_pod("worker-559c", "prod", "Pending", 0),
                self._mock_pod("etl-9988", "prod", "Running", 0, crashloop=True),
                self._mock_pod("monitor-776", "monitoring", "Running", 0, oom=True),
            ],
            "events": [
                {
                    "metadata": {"name": "event-1", "namespace": "prod"},
                    "involvedObject": {"kind": "Deployment", "name": "billing", "namespace": "prod"},
                    "type": "Warning",
                    "reason": "BackOff",
                    "message": "Back-off restarting failed container",
                    "lastTimestamp": now,
                },
                {
                    "metadata": {"name": "event-2", "namespace": "monitoring"},
                    "involvedObject": {"kind": "DaemonSet", "name": "node-exporter", "namespace": "monitoring"},
                    "type": "Warning",
                    "reason": "OOMKilled",
                    "message": "Container metrics-agent was OOM killed",
                    "lastTimestamp": now,
                },
                {
                    "metadata": {"name": "event-3", "namespace": "default"},
                    "involvedObject": {"kind": "Deployment", "name": "web", "namespace": "default"},
                    "type": "Normal",
                    "reason": "ScalingReplicaSet",
                    "message": "Scaled up replica set web to 3",
                    "lastTimestamp": now,
                },
            ],
            "deployment": [
                self._mock_workload("web", "default", "deployment", 3, 3),
                self._mock_workload("api", "default", "deployment", 2, 1),
                self._mock_workload("billing", "prod", "deployment", 4, 4),
            ],
            "statefulset": [
                self._mock_workload("redis", "prod", "statefulset", 3, 3),
            ],
            "daemonset": [
                self._mock_workload("node-exporter", "monitoring", "daemonset", 3, 2),
            ],
            "pod": [
                self._mock_workload("web-7b6f", "default", "pod", None, None),
                self._mock_workload("api-8d4f", "default", "pod", None, None),
                self._mock_workload("worker-559c", "prod", "pod", None, None),
            ],
            "service": [
                self._mock_workload("web-svc", "default", "service", None, None),
                self._mock_workload("api-svc", "default", "service", None, None),
            ],
            "ingress": [
                self._mock_workload("main-ingress", "default", "ingress", None, None),
            ],
            "pod_logs": {
                "default/web-7b6f": [
                    "2026-02-24T14:00:11Z INFO web server started on :8080",
                    "2026-02-24T14:02:35Z INFO request_id=1f8a response=200 duration_ms=17",
                    "2026-02-24T14:03:06Z WARN upstream latency high p95=824ms",
                ],
                "default/api-8d4f": [
                    "2026-02-24T14:00:01Z INFO API bootstrap complete",
                    "2026-02-24T14:04:22Z ERROR db timeout after 3 retries",
                ],
                "prod/worker-559c": [
                    "2026-02-24T14:00:00Z INFO worker waiting for queue assignment",
                ],
            },
        }

    @staticmethod
    def _build_label_selector(labels: dict[str, str]) -> str:
        return ",".join(f"{key}={value}" for key, value in labels.items())

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            try:
                payload = response.json()
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                for key in ("message", "detail", "error", "reason"):
                    value = payload.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()

        text = response.text.strip()
        if not text:
            return ""
        first_line = text.splitlines()[0].strip()
        return first_line[:240]

    def _mock_workload(
        self,
        name: str,
        namespace: str,
        kind: str,
        replicas: int | None,
        ready_replicas: int | None,
    ) -> dict[str, Any]:
        spec: dict[str, Any] = {
            "selector": {"matchLabels": {"app": name}},
        }
        status: dict[str, Any] = {"phase": "Running"}
        if replicas is not None:
            spec["replicas"] = replicas
            status["replicas"] = replicas
        if ready_replicas is not None:
            status["readyReplicas"] = ready_replicas

        return {
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": {"app": name, "tier": "backend"},
            },
            "spec": spec,
            "status": status,
            "kind": kind,
        }

    def _mock_pod(
        self,
        name: str,
        namespace: str,
        phase: str,
        restart_count: int,
        crashloop: bool = False,
        oom: bool = False,
    ) -> dict[str, Any]:
        container_status = {
            "name": "main",
            "restartCount": restart_count,
            "ready": phase == "Running",
        }
        if crashloop:
            container_status["state"] = {
                "waiting": {
                    "reason": "CrashLoopBackOff",
                    "message": "Container is restarting",
                }
            }
        if oom:
            container_status["lastState"] = {
                "terminated": {
                    "reason": "OOMKilled",
                    "exitCode": 137,
                }
            }

        return {
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": {"app": name.split("-")[0]},
            },
            "status": {
                "phase": phase,
                "containerStatuses": [container_status],
            },
        }
