"""Deterministic risk policy. No LLM output can bypass these checks."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from orcastra.contracts import (
    ExecutionMode,
    ProposedDecision,
    RiskCheck,
    RiskGuardResult,
)


@dataclass(frozen=True)
class RiskPolicy:
    """Mock defaults only; production limits require a separately approved policy."""

    version: str = "mock-risk-v0.1"
    max_target_weight: float = 0.10
    max_data_age: timedelta = timedelta(hours=24)
    allow_live_execution: bool = False


DEFAULT_RISK_POLICY = RiskPolicy()


def evaluate_risk(
    *,
    decision: ProposedDecision,
    decision_timestamp: datetime,
    data_as_of: datetime,
    execution_mode: ExecutionMode,
    idempotency_key: str,
    policy: RiskPolicy = DEFAULT_RISK_POLICY,
) -> RiskGuardResult:
    age = decision_timestamp - data_as_of
    checks = [
        RiskCheck(
            check_id="execution-mode",
            passed=execution_mode == ExecutionMode.PAPER or policy.allow_live_execution,
            observed=execution_mode.value,
            limit="paper-only",
        ),
        RiskCheck(
            check_id="target-weight",
            passed=decision.target_weight <= policy.max_target_weight,
            observed=f"{decision.target_weight:.4f}",
            limit=f"<= {policy.max_target_weight:.4f}",
        ),
        RiskCheck(
            check_id="data-freshness",
            passed=timedelta(0) <= age <= policy.max_data_age,
            observed=f"{age.total_seconds():.0f}s",
            limit=f"0s..{policy.max_data_age.total_seconds():.0f}s",
        ),
        RiskCheck(
            check_id="idempotency-key",
            passed=bool(idempotency_key.strip()),
            observed="present" if idempotency_key.strip() else "missing",
            limit="required",
        ),
    ]
    return RiskGuardResult(
        policy_version=policy.version,
        checked_at=decision_timestamp,
        approved=all(check.passed for check in checks),
        checks=checks,
    )
