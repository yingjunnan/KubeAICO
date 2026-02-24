from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import Settings


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

    async def list_nodes(self) -> list[dict[str, Any]]:
        if self._use_mock:
            return self._mock_state["nodes"]

        payload = await self._request("GET", "/api/v1/nodes")
        return payload.get("items", [])

    async def list_pods(self, namespace: str | None = None) -> list[dict[str, Any]]:
        if self._use_mock:
            pods: list[dict[str, Any]] = self._mock_state["pods"]
            if namespace:
                return [pod for pod in pods if pod.get("metadata", {}).get("namespace") == namespace]
            return pods

        if namespace:
            payload = await self._request("GET", f"/api/v1/namespaces/{namespace}/pods")
        else:
            payload = await self._request("GET", "/api/v1/pods")
        return payload.get("items", [])

    async def list_events(self, namespace: str | None = None) -> list[dict[str, Any]]:
        if self._use_mock:
            events: list[dict[str, Any]] = self._mock_state["events"]
            if namespace:
                return [
                    event
                    for event in events
                    if event.get("metadata", {}).get("namespace") == namespace
                ]
            return events

        if namespace:
            payload = await self._request("GET", f"/api/v1/namespaces/{namespace}/events")
        else:
            payload = await self._request("GET", "/api/v1/events")
        return payload.get("items", [])

    async def list_resources(
        self,
        kind: str,
        namespace: str | None = None,
        label_selector: str | None = None,
    ) -> list[dict[str, Any]]:
        if kind not in self.kind_to_resource:
            raise ValueError(f"Unsupported kind: {kind}")

        if self._use_mock:
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
        payload = await self._request("GET", path, params=params)
        return payload.get("items", [])

    async def scale_workload(
        self,
        kind: str,
        name: str,
        namespace: str,
        replicas: int,
    ) -> dict[str, Any]:
        if kind not in self.scalable_kinds:
            raise ValueError(f"Kind '{kind}' does not support scale")

        if self._use_mock:
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
        return await self._request("PATCH", path, json=body, content_type="application/merge-patch+json")

    async def rollout_restart(self, kind: str, name: str, namespace: str) -> dict[str, Any]:
        if kind not in self.scalable_kinds:
            raise ValueError(f"Kind '{kind}' does not support rollout restart")

        if self._use_mock:
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
        )

    @property
    def _use_mock(self) -> bool:
        return self.settings.use_mock_data or not self.settings.k8s_api_url

    def _list_path(self, kind: str, namespace: str | None) -> str:
        api_version, resource = self.kind_to_resource[kind]
        if api_version == "v1":
            base = "/api/v1"
        else:
            base = f"/apis/{api_version}"

        if namespace:
            return f"{base}/namespaces/{namespace}/{resource}"
        return f"{base}/{resource}"

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        if not self.settings.k8s_api_url:
            raise ValueError("k8s_api_url is required for real cluster mode")

        headers = {
            "Accept": "application/json",
            "Content-Type": content_type,
        }
        if self.settings.k8s_bearer_token:
            headers["Authorization"] = f"Bearer {self.settings.k8s_bearer_token}"

        client = await self._get_client()
        response = await client.request(
            method,
            f"{self.settings.k8s_api_url.rstrip('/')}{path}",
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
                    "type": "Warning",
                    "reason": "BackOff",
                    "message": "Back-off restarting failed container",
                    "lastTimestamp": now,
                },
                {
                    "metadata": {"name": "event-2", "namespace": "monitoring"},
                    "type": "Warning",
                    "reason": "OOMKilled",
                    "message": "Container metrics-agent was OOM killed",
                    "lastTimestamp": now,
                },
                {
                    "metadata": {"name": "event-3", "namespace": "default"},
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
        }

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
