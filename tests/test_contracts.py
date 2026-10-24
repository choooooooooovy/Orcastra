from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from orcastra.contracts import (
    AgentStep,
    DebateRecord,
    DebateTurn,
    DecisionAction,
    ExecutionMode,
    ExecutionRecord,
    ExecutionStatus,
    ProposedDecision,
    RiskCheck,
    RiskGuardResult,
    SourceReference,
    StepStatus,
    ToolCall,
    TradingRunTrace,
    Usage,
    VersionInfo,
)


def make_trace(source_id: str = "source-1") -> TradingRunTrace:
    now = datetime(2026, 10, 24, 12, tzinfo=UTC)
    decision = ProposedDecision(
        ticker="AAPL",
        action=DecisionAction.HOLD,
        target_weight=0.05,
        rationale="fixture",
        evidence_source_ids=[source_id],
    )
    return TradingRunTrace(
        run_id=uuid4(),
        ticker="AAPL",
        started_at=now,
        completed_at=now,
        decision_timestamp=now,
        market_snapshot_id="snapshot-1",
        data_as_of=now - timedelta(minutes=1),
        versions=VersionInfo(
            orcastra_version="0.1.0",
            engine_name="fixture",
            engine_version="1",
            model_versions={},
            prompt_version="p1",
            harness_version="h1",
        ),
        sources=[
            SourceReference(
                source_id="source-1",
                provider="fixture",
                uri="fixture://source",
                retrieved_at=now,
                data_as_of=now - timedelta(minutes=1),
                content_sha256="a" * 64,
            )
        ],
        agent_steps=[
            AgentStep(
                step_id="step-1",
                sequence=0,
                role="analyst",
                started_at=now,
                completed_at=now,
                status=StepStatus.SUCCEEDED,
                source_ids=[source_id],
            )
        ],
        debate=DebateRecord(
            turns=[DebateTurn(speaker="manager", stance="manager", argument="fixture")],
            synthesis="fixture",
        ),
        proposed_decision=decision,
        risk_guard=RiskGuardResult(
            policy_version="test",
            checked_at=now,
            approved=True,
            checks=[RiskCheck(check_id="test", passed=True, observed="ok", limit="ok")],
        ),
        execution=ExecutionRecord(
            mode=ExecutionMode.PAPER,
            status=ExecutionStatus.NOT_REQUESTED,
            idempotency_key="fixture-key",
        ),
        usage=Usage(),
        latency_ms=0,
        cost_estimate_usd=0,
    )


def test_trace_rejects_unknown_source_reference() -> None:
    with pytest.raises(ValidationError, match="unknown source references"):
        make_trace("missing-source")


def test_risk_approval_must_match_all_checks() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError, match="approved must equal"):
        RiskGuardResult(
            policy_version="test",
            checked_at=now,
            approved=True,
            checks=[RiskCheck(check_id="failed", passed=False, observed="x", limit="y")],
        )


def test_tool_trace_rejects_sensitive_fields() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError, match="sensitive field is prohibited"):
        ToolCall(
            tool_call_id="tool-1",
            tool_name="unsafe",
            started_at=now,
            completed_at=now,
            status=StepStatus.SUCCEEDED,
            sanitized_input={"Authorization": "Bearer secret"},
        )
