# Trading–Evaluation data contract

Status: v0.1 draft. The data envelope is implemented; metric definitions,
weights, judges, and thresholds remain open for ChatGPT + user discussion.

The executable source of truth is `src/orcastra/contracts.py`. Models reject
unknown fields so accidental producer/consumer drift fails visibly.

## Separation rule

`TradingRunTrace` is an immutable record of what the trading system observed,
reasoned, proposed, checked, and simulated. `EvaluationResult` is a later,
versioned interpretation. Evaluation never adds scores to or rewrites the trace.

The only required join is:

```text
EvaluationResult.run_id -> TradingRunTrace.run_id
```

## TradingRunTrace v0.1

Top-level groups:

| Group | Required purpose |
| --- | --- |
| Identity | `schema_version`, `run_id`, optional `scenario_id`, ticker |
| Time | start/end, decision timestamp, `data_as_of` |
| Snapshot | stable `market_snapshot_id` and content-addressed sources |
| Versions | Orcastra, engine, model, prompt, and harness versions |
| Steps | ordered agent inputs/outputs, model identity, tool calls, errors, timings |
| Debate | Bull/Bear turns and manager synthesis |
| Decision | action, target weight, rationale, and cited source IDs |
| Risk | policy version and each deterministic check/result |
| Execution | paper/live mode, outcome, idempotency key, simulated orders |
| Operations | aggregate tokens, latency, and estimated cost |

Every cited source ID must exist in the trace source registry. `data_as_of`
cannot be later than the decision timestamp. The trace contains sanitized tool
inputs/outputs only; credentials, auth headers, account identifiers, and raw
sensitive account responses are prohibited.

## EvaluationResult v0.1

An evaluation record contains its own `eval_run_id`, evaluator and optional
judge versions, timestamp, a target `run_id`, metric results, and review notes.
`MetricResult` is intentionally generic:

- `metric_key`: stable identifier chosen by the Evaluation design
- `outcome`: `passed`, `failed`, or `inconclusive`
- optional scalar `value`
- rationale and evidence pointers

This supports the currently discussed dimensions—Evidence Groundedness,
Decision Consistency, Constraint Compliance, and separately reported Trading
Performance—without prematurely fixing formulas or a composite score.

## Compatibility policy

- Add optional fields within `0.1` only when existing readers remain valid.
- Bump the schema version for required-field or semantic changes.
- Producers include all component versions used for a run.
- Evaluators declare the trace schema versions they accept.
- A migration writes a new artifact and provenance record; it does not silently
  alter the original file.

## Queries the contract supports

- Runs list by time, ticker, scenario, model/harness version, result, cost, or latency
- Trace detail ordered by agent and tool call
- Evidence lookup from a claim/decision to its source and valid time
- Proposed decision versus Risk Guard outcome versus paper execution
- V0/V1 evaluation comparison against the same scenario set

## Open decisions for Evaluation design

1. Exact rubrics and evidence-pointer granularity for groundedness.
2. Whether claims need first-class IDs, beyond step-level source references.
3. Human-review workflow and adjudication states.
4. Judge model/version retention and prompt storage policy.
5. Metric value scales and pass thresholds; no aggregate score is assumed.
6. Retention/redaction rules for large tool outputs.
7. Dashboard query/API pagination and comparison semantics.

