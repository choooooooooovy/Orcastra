# Orcastra contributor rules

## Sources of truth

- Product decisions: the Notion planning page linked from `README.md`.
- Implemented behavior and contracts: this repository.
- Keep confirmed decisions separate from proposals. If they conflict, stop and
  document the conflict instead of silently choosing one.

## Safety invariants

- Paper trading is the default and the only executable broker mode until a
  separately reviewed live-trading milestone is approved.
- Evaluation code is read-only with respect to brokers and cannot submit orders.
- Risk checks are deterministic code and must run synchronously before any
  broker call. LLM output never overrides a failed check.
- Never commit credentials, account identifiers, raw authorization headers, or
  unredacted sensitive account payloads. Do not place them in traces.
- Every future order path must be idempotent and must reject duplicate order
  keys. Tests and evaluation runs must use isolated paper adapters.

## Engineering rules

- Support Python 3.11 or newer. Keep the core package small and vendor-neutral.
- Preserve upstream TradingAgents behind an adapter; do not copy or patch its
  internals into Orcastra unless an adapter cannot provide a required hook.
- Treat `src/orcastra/contracts.py` as the executable data contract. Version it
  additively and document incompatible changes before implementation.
- Store immutable trading traces separately from versioned evaluation results.
- Every external fact records its URI/provider, retrieval time, and `data_as_of`.
- Tests must be offline and deterministic by default. Mark external-service
  checks explicitly as integration tests.

## Required checks

Run before handoff:

```bash
python -m pytest
python -m ruff check .
python -m orcastra run-mock --ticker AAPL --output artifacts
```

