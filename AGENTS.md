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

## Development workflow

- Use `docs/development_workflow.md` for work that changes product behavior,
  shared contracts, architecture, or more than one implementation area. Small,
  low-risk documentation or mechanical changes may use the lightweight path.
- Start scoped work from a Task Brief containing the goal, relevant files,
  confirmed constraints, non-goals, acceptance criteria, and validation commands.
- The main agent acts as Coordinator: it owns scope, delegation, decisions,
  integration, and the final evidence-based handoff.
- Use the built-in Explorer for focused read-only code mapping when the change
  path is unclear. Give it only the Task Brief and relevant repository paths;
  require a concise evidence summary rather than raw logs.
- Use one Worker as the sole writer for a shared set of files. Parallel Workers
  are allowed only for disjoint file ownership with an explicit integration plan.
- Have an independent Reviewer assess the Task Brief, actual diff, and test
  evidence. The Reviewer reports findings and a verdict but does not edit files.
- Create a fresh Debugger subagent only after a reproducible failure. Give it the
  failing command, trimmed error output, and related files; keep diagnosis and
  implementation separate unless the fix is trivial and explicitly reassigned.
- Subagents inherit the parent sandbox and permissions. “Read-only” is an
  operating instruction, not a separate security boundary; the Coordinator must
  inspect the final diff and working tree.
- Do not pass full chat histories or unfiltered debug logs between roles. Use the
  handoff fields defined in `docs/development_workflow.md`.
- Record validated implementation evidence in the Task Brief or PR. Do not copy
  speculative discussion into architecture or contract documentation.

## Required checks

Run before handoff:

```bash
python -m pytest
python -m ruff check .
python -m orcastra run-mock --ticker AAPL --output artifacts
```
