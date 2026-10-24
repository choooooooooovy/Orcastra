"""Application service for one safely simulated analysis run."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from orcastra import __version__
from orcastra.contracts import (
    ExecutionMode,
    ExecutionRecord,
    ExecutionStatus,
    PaperOrder,
    TradingRunTrace,
    Usage,
    VersionInfo,
)
from orcastra.mock_engine import MockTradingAgentsEngine
from orcastra.risk import evaluate_risk
from orcastra.storage import JsonArtifactStore


def run_mock_analysis(
    *,
    ticker: str,
    output: str | Path,
    decision_timestamp: datetime | None = None,
    scenario_id: str | None = "mock-single-ticker",
) -> tuple[TradingRunTrace, Path]:
    now = decision_timestamp or datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("decision_timestamp must include a timezone")
    ticker = ticker.strip().upper()
    engine = MockTradingAgentsEngine()
    bundle = engine.analyze(ticker, now)
    started_at = min(step.started_at for step in bundle.steps)
    run_id = uuid4()
    idempotency_key = f"paper:{run_id}:{ticker}"
    data_as_of = max(source.data_as_of for source in bundle.sources)
    risk_result = evaluate_risk(
        decision=bundle.decision,
        decision_timestamp=now,
        data_as_of=data_as_of,
        execution_mode=ExecutionMode.PAPER,
        idempotency_key=idempotency_key,
    )
    execution = ExecutionRecord(
        mode=ExecutionMode.PAPER,
        status=ExecutionStatus.SIMULATED if risk_result.approved else ExecutionStatus.BLOCKED,
        idempotency_key=idempotency_key,
        orders=(
            [
                PaperOrder(
                    client_order_id=f"mock-{run_id}",
                    ticker=ticker,
                    side="buy",
                    quantity=1,
                    reference_price=189.0,
                )
            ]
            if risk_result.approved
            else []
        ),
    )
    completed_at = now
    trace = TradingRunTrace(
        run_id=run_id,
        scenario_id=scenario_id,
        ticker=ticker,
        started_at=started_at,
        completed_at=completed_at,
        decision_timestamp=now,
        market_snapshot_id=f"mock-snapshot-{ticker}-{now.isoformat()}",
        data_as_of=data_as_of,
        versions=VersionInfo(
            orcastra_version=__version__,
            engine_name=engine.name,
            engine_version=engine.version,
            model_versions={"all_roles": engine.model_id},
            prompt_version="mock-prompts-v1",
            harness_version="mock-harness-v1",
        ),
        sources=bundle.sources,
        agent_steps=bundle.steps,
        debate=bundle.debate,
        proposed_decision=bundle.decision,
        risk_guard=risk_result,
        execution=execution,
        usage=Usage(),
        latency_ms=int((completed_at - started_at).total_seconds() * 1000),
        cost_estimate_usd=0,
    )
    path = JsonArtifactStore(output).save_trace(trace)
    return trace, path
