# Orcastra initial architecture

Status: architecture baseline for v0.1. Evaluation scoring and portfolio
allocation algorithms are proposals only and are not fixed here.

## Confirmed constraints

- The target universe starts with US stocks and ordinary ETFs at daily/swing to
  medium-term horizons.
- Holdings management and new-candidate discovery converge into one
  portfolio-level decision flow.
- Trading and Evaluation are separate products. Evaluation failure cannot block
  or mutate trading runs; Evaluation has no broker write access.
- The initial broker mode is paper-only. Unattended live execution is outside
  the MVP.
- A deterministic Risk Guard is synchronous and authoritative before execution.
- Raw trading traces and evaluation results are stored separately.

## Component boundaries

```text
Holdings Adapter ----\
Market Scanner -------+--> Candidate Context
Market Data ----------/          |
                                  v
                     TradingAgents Adapter
          analysts -> debate -> trader -> upstream risk opinions
                                  |
                                  v
                    Portfolio Decision Engine
                                  |
                                  v
                     Deterministic Risk Guard
                                  |
                                  v
                        Broker Port
                     /              \
                Paper Broker     Toss Adapter (read-only first)
                     |
                     v
             immutable TradingRunTrace
                     |
                 read-only
                     v
              Evaluation Service ----> separate EvaluationResult
```

The upstream risk-management agents remain useful as qualitative inputs. They
do not replace Orcastra's deterministic Risk Guard.

## Package direction

The initial code keeps dependencies pointing inward:

1. `contracts.py` owns versioned, vendor-neutral records.
2. `risk.py` consumes only contract types and explicit policy.
3. `mock_engine.py` implements the analysis-engine boundary without network.
4. `service.py` coordinates analysis, risk validation, paper execution metadata,
   and trace persistence.
5. `storage.py` owns filesystem persistence. A future database implementation
   must satisfy the same logical separation.

The real `TradingAgentsGraph` will be imported only inside its adapter. This
keeps the core contract and Evaluation reader independent of LangGraph,
LangChain, LLM vendors, and upstream release cadence.

## Runtime flow

1. Assign `run_id` before any external work.
2. Freeze ticker, decision timestamp, market snapshot identity, and versions.
3. Capture each agent step, tool call, timing, usage, error, and source links.
4. Convert the upstream single-ticker output into a portfolio proposal.
5. Run deterministic constraints synchronously.
6. Call only the configured paper broker when all required checks pass.
7. Persist the trace once. Corrections create a new run or an explicit schema
   migration; they do not silently rewrite history.
8. Evaluation reads the trace and writes a separately versioned result linked by
   `run_id`.

## Persistence plan

The foundation uses one JSON document per immutable run:

```text
artifacts/
  traces/<run_id>.json
  evaluations/<eval_run_id>.json
```

This is intentionally simple and inspectable. The next storage step should add
PostgreSQL (JSONB for the original payload plus indexed relational columns) only
when concurrent runs and dashboard queries justify it. Object storage can retain
large raw tool artifacts addressed by content hash.

## Technology choices

- **Python 3.11+** matches TradingAgents and minimizes adapter friction.
- **Pydantic v2** provides executable validation and generated JSON Schema at
  the system boundary.
- **pytest + Ruff** provide a small offline quality gate.
- **Plain JSON artifacts first** avoid choosing a database schema before the
  dashboard query patterns are agreed.
- **No web framework yet** because API routes and Dashboard information
  architecture remain open decisions. FastAPI is a likely proposal, not a
  confirmed choice.

## Safety model

There is no live broker implementation or live CLI flag in v0.1. Adding one
requires an explicit milestone that covers scoped credentials, user approval,
idempotency, duplicate detection, stale-data rejection, reconciliation, kill
switches, and integration-test isolation. Secrets and raw account payloads are
excluded from trace models by design.

The numerical limits in `RiskPolicy` are mock-test defaults only. Production
position, freshness, and account constraints are open product decisions and
must be versioned after approval.
