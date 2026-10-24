import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from orcastra.contracts import DecisionAction, EvaluationResult, ExecutionMode, ProposedDecision
from orcastra.risk import evaluate_risk
from orcastra.service import run_mock_analysis
from orcastra.storage import ArtifactAlreadyExistsError, JsonArtifactStore


def test_mock_run_is_paper_only_and_writes_structured_trace(tmp_path) -> None:
    trace, path = run_mock_analysis(
        ticker="aapl",
        output=tmp_path,
        decision_timestamp=datetime(2026, 10, 24, 12, tzinfo=UTC),
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.parent == tmp_path / "traces"
    assert not (tmp_path / "evaluations").exists()
    assert payload["ticker"] == "AAPL"
    assert payload["schema_version"] == "0.1"
    assert payload["execution"]["mode"] == "paper"
    assert payload["execution"]["status"] == "simulated"
    assert payload["risk_guard"]["approved"] is True
    assert len(payload["agent_steps"]) == 4
    assert trace.proposed_decision.evidence_source_ids
    assert trace.latency_ms == 2000
    serialized = path.read_text(encoding="utf-8").lower()
    assert "authorization" not in serialized
    assert "client_secret" not in serialized


def test_evaluation_is_stored_separately_and_is_immutable(tmp_path) -> None:
    run_id = uuid4()
    result = EvaluationResult(
        eval_run_id=uuid4(),
        run_id=run_id,
        evaluator_version="fixture-v1",
        metrics=[],
    )
    store = JsonArtifactStore(tmp_path)
    path = store.save_evaluation(result)
    assert path.parent == tmp_path / "evaluations"
    assert not (tmp_path / "traces").exists()
    with pytest.raises(ArtifactAlreadyExistsError):
        store.save_evaluation(result)


def test_risk_guard_blocks_live_execution() -> None:
    now = datetime(2026, 10, 24, 12, tzinfo=UTC)
    decision = ProposedDecision(
        ticker="AAPL",
        action=DecisionAction.BUY,
        target_weight=0.05,
        rationale="fixture",
        evidence_source_ids=[],
    )
    result = evaluate_risk(
        decision=decision,
        decision_timestamp=now,
        data_as_of=now,
        execution_mode=ExecutionMode.LIVE,
        idempotency_key="live-test",
    )
    assert result.approved is False
    execution_check = next(
        check for check in result.checks if check.check_id == "execution-mode"
    )
    assert execution_check.passed is False
