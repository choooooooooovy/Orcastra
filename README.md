# Orcastra

Orcastra is a personal, US-equity multi-agent trading system built around the
open-source TradingAgents workflow. It is designed to manage existing holdings,
discover new candidates, and make portfolio-level proposals while preserving
enough evidence and execution detail to evaluate *why* a decision was made.

This repository is an initial foundation, not an investment product. It cannot
place live orders. The runnable path is an offline, deterministic paper-trading
mock that writes a versioned trace for one US ticker.

## Current scope

- Versioned trading-run and evaluation-result contracts
- Immutable JSON trace persistence with trading/evaluation separation
- Deterministic risk checks that cannot be overridden by model output
- A mock multi-agent AAPL-style analysis requiring no API keys
- Architecture and upstream-reuse documentation
- Unit tests for contract integrity, isolation, safety, and persistence

Not implemented yet: live market scanning, a real TradingAgents invocation,
Toss account sync, a paper portfolio ledger, live orders, and the Evaluation UI.

The mock's five-percent target, ten-percent cap, 24-hour freshness window, one
share, and reference price are test fixtures—not approved investment policy.

## Quick start

Python 3.11+ is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
python -m orcastra run-mock --ticker AAPL --output artifacts
```

The command prints the trace path. Trading traces are written below
`artifacts/traces/`; evaluation results have a separate
`artifacts/evaluations/` namespace.

To inspect the CLI:

```bash
python -m orcastra --help
```

## Preparing a real TradingAgents run

The upstream run was not attempted in this milestone because no provider login
or API credential was supplied. The next adapter milestone should:

1. Install and pin TradingAgents `v0.7.0` (not floating `main`).
2. Configure a supported LLM provider, or complete the upstream
   `tradingagents login chatgpt` flow locally.
3. Keep market-data/provider credentials in the environment or a secret store.
4. Disable optional update checks for unattended runs with
   `TRADINGAGENTS_NO_UPDATE_CHECK=1`.
5. Run one ticker/date through the adapter and verify every mapped source,
   agent step, tool call, version, and timestamp before enabling scheduled runs.

## Repository map

```text
src/orcastra/contracts.py       executable Trace/Evaluation contract
src/orcastra/mock_engine.py     deterministic multi-agent test engine
src/orcastra/risk.py            synchronous code-based risk guard
src/orcastra/storage.py         separate immutable artifact stores
src/orcastra/service.py         orchestration boundary
docs/architecture.md            components and data flow
docs/development_workflow.md    Coordinator/subagent development harness
docs/evaluation_contract.md     evaluator-facing contract and open questions
docs/tradingagents_analysis.md  upstream v0.7.0 reuse/gap analysis
docs/tasks/                     durable Task Briefs and completion evidence
.codex/agents/reviewer.toml     independent project-scoped review role
```

## Design sources

- [Orcastra planning page](https://app.notion.com/p/40397c872b43810eb217f0d08f1d7f26)
- [TradingAgents repository](https://github.com/TauricResearch/TradingAgents)
- [TradingAgents paper](https://arxiv.org/abs/2412.20138)
- [Toss Securities Open API](https://developers.tossinvest.com/docs)

Confirmed product decisions and still-open proposals are called out separately
in the documents. The detailed evaluation metrics and scoring thresholds remain
deliberately unspecified.
