# TradingAgents v0.7.0 analysis

Reviewed on 2026-10-24 against upstream tag `v0.7.0`, commit
`e8f5503e9b86d5c2710b0c76b1f686703968c9df`.

Primary sources: [repository](https://github.com/TauricResearch/TradingAgents),
[changelog](https://github.com/TauricResearch/TradingAgents/blob/main/CHANGELOG.md),
and [paper](https://arxiv.org/abs/2412.20138).

## Reuse directly behind an adapter

| Upstream capability | Orcastra use |
| --- | --- |
| Parallel Market, Sentiment, News, Fundamentals analysts | Per-ticker analysis engine |
| Bull/Bear researchers and Research Manager | Preserve structured adversarial debate |
| Trader plus aggressive/neutral/conservative risk debate | Transaction proposal and qualitative risks |
| Portfolio Manager five-tier rating | One input to Orcastra's portfolio decision |
| Pydantic structured manager/trader decisions | Prefer parsed fields over prose scraping |
| `PortfolioContext` | Supply holdings/cash context during the transition |
| Point-in-time vendor routing and dated tools | Historical correctness and backtest foundation |
| SEC EDGAR/Yahoo/Alpha Vantage/FRED/etc. data routing | Initial data collection, with trace wrappers |
| LangGraph checkpointing and streamed subgraph state | Resume and step-level trace capture |
| Backtest and memory log | Reference implementation for later performance evaluation |
| Provider/model configuration and callbacks | Version/cost/latency instrumentation hooks |

## Wrap or extend

- Wrap `TradingAgentsGraph` so Orcastra assigns `run_id`, freezes versions, and
  captures step/tool events before calling it.
- Map upstream reports and final state into `TradingRunTrace`; do not expose the
  LangGraph state as the public API.
- Preserve upstream point-in-time safeguards, then add source IDs, retrieval
  timestamps, hashes, and sanitized tool payloads at the adapter boundary.
- Treat upstream ratings and risk-agent discussion as advisory inputs. Pass the
  resulting portfolio proposal through Orcastra's code-based Risk Guard.
- Pin a tested upstream release instead of tracking `main`; verify mapping tests
  before each upgrade.

## Build in Orcastra

- Market-wide scanner and candidate-ranking policy
- Holdings synchronization and a broker-neutral account snapshot
- Cross-ticker Portfolio Decision Engine for holdings, candidates, and cash
- Deterministic exposure, freshness, buying-power, duplicate-order, and market
  safety rules
- Paper ledger and broker port; Toss read-only adapter first
- Immutable trace storage and independent Evaluation result storage/API
- Evaluation UI, cases, rubrics, judges, and V0/V1 comparisons
- Operational scheduling, reconciliation, alerting, and secret management

## Important upstream limitations for this project

- A normal upstream run is ticker-centric; it does not solve market scanning or
  cross-ticker allocation.
- Its saved state is report-oriented and omits the full normalized source/tool
  provenance required by Orcastra's evaluator.
- Its LLM risk debate is not an enforceable trading constraint.
- Simulated exchange behavior is not a Toss-compatible broker abstraction or a
  persistent portfolio ledger.
- LLM runs are non-deterministic even with stable settings, so exact input,
  version, source, and operational metadata must be retained.

## Integration choice

Use composition, not a source fork: `TradingAgentsAdapter` will own the pinned
dependency and translation. A small maintained patch may be considered only if
upstream callbacks cannot expose a required event; any patch must have an
upstream issue/reference and a contract test.

