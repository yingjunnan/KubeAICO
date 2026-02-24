from datetime import UTC, datetime

from app.schemas.ai import AIAnalyzeRequest, AIAnalyzeResult, RootCauseCandidate


class RuleEngine:
    def analyze(self, payload: AIAnalyzeRequest) -> AIAnalyzeResult:
        risk_score = 0
        recommendations: list[str] = []
        root_causes: list[RootCauseCandidate] = []

        metrics_map = {item.name: item.value for item in payload.metrics}
        event_count = len(payload.events)

        cpu = metrics_map.get("cpu_utilization", metrics_map.get("cpu_usage_percent", 0))
        memory = metrics_map.get("memory_utilization", metrics_map.get("memory_usage_percent", 0))
        restart_rate = metrics_map.get("restart_rate", 0)
        error_rate = metrics_map.get("error_rate", 0)

        if cpu >= 80:
            risk_score += 30
            root_causes.append(
                RootCauseCandidate(
                    cause="Cluster CPU pressure is high",
                    confidence=0.82,
                    evidence=[f"cpu_utilization={cpu}"],
                )
            )
            recommendations.append("Scale out affected workloads or increase CPU limits for hot services.")

        if memory >= 85:
            risk_score += 30
            root_causes.append(
                RootCauseCandidate(
                    cause="Memory pressure likely to trigger eviction/OOM",
                    confidence=0.79,
                    evidence=[f"memory_utilization={memory}"],
                )
            )
            recommendations.append(
                "Inspect top memory consumers and adjust requests/limits to reduce OOM risk."
            )

        if restart_rate > 0.1:
            risk_score += 20
            root_causes.append(
                RootCauseCandidate(
                    cause="Abnormal restart rate detected",
                    confidence=0.75,
                    evidence=[f"restart_rate={restart_rate}"],
                )
            )
            recommendations.append("Prioritize workloads with frequent restarts and inspect recent rollouts.")

        if error_rate > 0.05:
            risk_score += 10
            recommendations.append("Error rate is elevated; correlate logs with recent config or image changes.")

        warning_events = [event for event in payload.events if event.severity.lower() in {"warning", "error"}]
        if warning_events:
            risk_score += min(20, len(warning_events) * 4)
            root_causes.append(
                RootCauseCandidate(
                    cause="Warning/error events are concentrated in the selected time window",
                    confidence=0.72,
                    evidence=[event.message for event in warning_events[:3]],
                )
            )

        if event_count == 0 and not payload.metrics:
            recommendations.append("No metrics or events provided; collect a baseline snapshot before diagnosis.")

        risk_score = min(100, risk_score)

        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        if not root_causes:
            root_causes.append(
                RootCauseCandidate(
                    cause="No dominant fault pattern detected by current rules",
                    confidence=0.45,
                    evidence=["Rule engine did not match major thresholds"],
                )
            )

        if not recommendations:
            recommendations.append("Cluster looks stable. Keep monitoring trend changes.")

        return AIAnalyzeResult(
            summary=f"Rule-based analysis completed with {risk_level} operational risk.",
            recommendations=recommendations,
            root_causes=root_causes,
            risk_level=risk_level,
            generated_at=datetime.now(UTC),
        )
