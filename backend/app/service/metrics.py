from __future__ import annotations

from typing import TYPE_CHECKING

from app.collector.prometheus import PrometheusCollector
from app.schemas.metrics import TimeseriesPoint, TimeseriesResponse, TimeseriesSeries

if TYPE_CHECKING:
    from app.db.models import ManagedCluster


class MetricsService:
    def __init__(self, prometheus_collector: PrometheusCollector) -> None:
        self.prometheus_collector = prometheus_collector

    async def get_timeseries(
        self,
        metric: str,
        range_minutes: int,
        namespace: str | None,
        workload: str | None,
        step_seconds: int,
        cluster: ManagedCluster | None = None,
    ) -> TimeseriesResponse:
        raw_series = await self.prometheus_collector.get_timeseries(
            metric=metric,
            range_minutes=range_minutes,
            namespace=namespace,
            workload=workload,
            step_seconds=step_seconds,
            cluster=cluster,
        )

        series: list[TimeseriesSeries] = []
        for row in raw_series:
            metric_info = row.get("metric", {})
            series_name = metric_info.get("series") or metric_info.get("pod") or "cluster"
            points = [
                TimeseriesPoint(ts=int(item[0]), value=float(item[1]))
                for item in row.get("values", [])
            ]
            series.append(TimeseriesSeries(name=series_name, points=points))

        return TimeseriesResponse(
            metric=metric,
            range_minutes=range_minutes,
            step_seconds=step_seconds,
            series=series,
        )
