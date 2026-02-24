from datetime import UTC, datetime

from app.analyzer.rules import RuleEngine
from app.schemas.ai import AIAnalyzeRequest, EventSnapshot, MetricSnapshot


def test_rules_engine_high_risk() -> None:
    engine = RuleEngine()
    payload = AIAnalyzeRequest(
        metrics=[
            MetricSnapshot(name="cpu_utilization", value=91),
            MetricSnapshot(name="memory_utilization", value=88),
            MetricSnapshot(name="restart_rate", value=0.2),
        ],
        events=[
            EventSnapshot(
                type="k8s-event",
                message="Back-off restarting container",
                severity="warning",
                timestamp=datetime.now(UTC),
            )
        ],
    )

    result = engine.analyze(payload)

    assert result.risk_level == "high"
    assert len(result.root_causes) >= 1
    assert len(result.recommendations) >= 1
