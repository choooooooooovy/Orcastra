"""Versioned, vendor-neutral records shared by Trading and Evaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

TRACE_SCHEMA_VERSION = "0.1"
EVALUATION_SCHEMA_VERSION = "0.1"

_SENSITIVE_FIELD_NAMES = {
    "account_id",
    "account_number",
    "access_token",
    "api_key",
    "authorization",
    "client_secret",
    "refresh_token",
    "x_tossinvest_account",
}


def _reject_sensitive_fields(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in _SENSITIVE_FIELD_NAMES or normalized.endswith("_api_key"):
                raise ValueError(f"sensitive field is prohibited in trace data: {path}.{key}")
            _reject_sensitive_fields(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_sensitive_fields(item, f"{path}[{index}]")


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StepStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class DecisionAction(StrEnum):
    BUY = "buy"
    HOLD = "hold"
    REDUCE = "reduce"
    SELL = "sell"


class ExecutionMode(StrEnum):
    PAPER = "paper"
    LIVE = "live"


class ExecutionStatus(StrEnum):
    SIMULATED = "simulated"
    BLOCKED = "blocked"
    NOT_REQUESTED = "not_requested"


class EvaluationOutcome(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class Usage(ContractModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def total_is_consistent(self) -> Usage:
        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError("total_tokens must equal input_tokens + output_tokens")
        return self


class VersionInfo(ContractModel):
    orcastra_version: str
    engine_name: str
    engine_version: str
    model_versions: dict[str, str]
    prompt_version: str
    harness_version: str


class SourceReference(ContractModel):
    source_id: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    uri: str = Field(min_length=1)
    title: str | None = None
    retrieved_at: datetime
    data_as_of: datetime
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ToolCall(ContractModel):
    tool_call_id: str
    tool_name: str
    started_at: datetime
    completed_at: datetime
    status: StepStatus
    sanitized_input: dict[str, Any] = Field(default_factory=dict)
    sanitized_output: dict[str, Any] = Field(default_factory=dict)
    error_type: str | None = None
    error_message: str | None = None

    @model_validator(mode="after")
    def timestamps_are_ordered(self) -> ToolCall:
        if self.completed_at < self.started_at:
            raise ValueError("tool call completed_at cannot precede started_at")
        _reject_sensitive_fields(self.sanitized_input, "sanitized_input")
        _reject_sensitive_fields(self.sanitized_output, "sanitized_output")
        return self


class AgentStep(ContractModel):
    step_id: str
    sequence: int = Field(ge=0)
    role: str
    started_at: datetime
    completed_at: datetime
    status: StepStatus
    model_id: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    source_ids: list[str] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)
    error_type: str | None = None
    error_message: str | None = None

    @model_validator(mode="after")
    def timestamps_are_ordered(self) -> AgentStep:
        if self.completed_at < self.started_at:
            raise ValueError("agent step completed_at cannot precede started_at")
        _reject_sensitive_fields(self.input, "input")
        _reject_sensitive_fields(self.output, "output")
        return self


class DebateTurn(ContractModel):
    speaker: str
    stance: Literal["bull", "bear", "manager"]
    argument: str
    source_ids: list[str] = Field(default_factory=list)


class DebateRecord(ContractModel):
    turns: list[DebateTurn]
    synthesis: str


class ProposedDecision(ContractModel):
    ticker: str = Field(pattern=r"^[A-Z][A-Z0-9.\-]{0,14}$")
    action: DecisionAction
    target_weight: float = Field(ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    rationale: str
    evidence_source_ids: list[str]


class RiskCheck(ContractModel):
    check_id: str
    passed: bool
    observed: str
    limit: str


class RiskGuardResult(ContractModel):
    policy_version: str
    checked_at: datetime
    approved: bool
    checks: list[RiskCheck]

    @model_validator(mode="after")
    def approval_matches_checks(self) -> RiskGuardResult:
        if self.approved != all(check.passed for check in self.checks):
            raise ValueError("approved must equal the conjunction of risk checks")
        return self


class PaperOrder(ContractModel):
    client_order_id: str
    ticker: str
    side: Literal["buy", "sell"]
    quantity: float = Field(gt=0)
    reference_price: float = Field(gt=0)


class ExecutionRecord(ContractModel):
    mode: ExecutionMode
    status: ExecutionStatus
    idempotency_key: str
    orders: list[PaperOrder] = Field(default_factory=list)


class TradingRunTrace(ContractModel):
    schema_version: Literal["0.1"] = TRACE_SCHEMA_VERSION
    run_id: UUID
    scenario_id: str | None = None
    ticker: str
    started_at: datetime
    completed_at: datetime
    decision_timestamp: datetime
    market_snapshot_id: str
    data_as_of: datetime
    versions: VersionInfo
    sources: list[SourceReference]
    agent_steps: list[AgentStep]
    debate: DebateRecord
    proposed_decision: ProposedDecision
    risk_guard: RiskGuardResult
    execution: ExecutionRecord
    usage: Usage
    latency_ms: int = Field(ge=0)
    cost_estimate_usd: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_integrity(self) -> TradingRunTrace:
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot precede started_at")
        if self.data_as_of > self.decision_timestamp:
            raise ValueError("data_as_of cannot be later than decision_timestamp")
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_id values must be unique")
        known = set(source_ids)
        referenced = set(self.proposed_decision.evidence_source_ids)
        for step in self.agent_steps:
            referenced.update(step.source_ids)
        for turn in self.debate.turns:
            referenced.update(turn.source_ids)
        missing = referenced - known
        if missing:
            raise ValueError(f"unknown source references: {sorted(missing)}")
        if self.ticker != self.proposed_decision.ticker:
            raise ValueError("trace ticker and decision ticker must match")
        sequences = [step.sequence for step in self.agent_steps]
        if len(sequences) != len(set(sequences)):
            raise ValueError("agent step sequences must be unique")
        if sequences != sorted(sequences):
            raise ValueError("agent steps must be ordered by sequence")
        for step in self.agent_steps:
            if step.started_at < self.started_at or step.completed_at > self.completed_at:
                raise ValueError("agent step timestamps must fall within the run")
        return self


class MetricResult(ContractModel):
    metric_key: str
    outcome: EvaluationOutcome
    value: bool | int | float | str | None = None
    rationale: str
    evidence_pointers: list[str] = Field(default_factory=list)


class EvaluationResult(ContractModel):
    schema_version: Literal["0.1"] = EVALUATION_SCHEMA_VERSION
    eval_run_id: UUID
    run_id: UUID
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evaluator_version: str
    judge_version: str | None = None
    metrics: list[MetricResult]
    review_notes: str | None = None
