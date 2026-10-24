# ORC-0001 — Development harness foundation

Status: Done

## Goal

Establish a minimal Coordinator → Explorer → Worker → Reviewer workflow that
keeps agent contexts bounded and leaves durable, evidence-based handoffs in the
repository without changing Orcastra product behavior.

## Authoritative context

- User request: “Orcastra — Development Harness 구조 개선”, 2026-10-24.
  The user explicitly requested implementation of the minimal harness in this
  task, including role separation, context handoffs, repository workflow files,
  an example Task Brief, and a practical read-only Subagent check. The request
  allowed a Reviewer Custom Agent when useful and required a minimal—not
  maximal—configuration.
- Notion planning page, section 12: Development Harness proposal
- `AGENTS.md`
- `docs/architecture.md`
- `docs/evaluation_contract.md`
- [Official OpenAI Subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## Scope

- Extend `AGENTS.md` with persistent delegation and handoff rules.
- Add the development workflow and reusable Task Brief template.
- Add one project-scoped independent Reviewer agent.
- Demonstrate a read-only Explorer and independent Reviewer on this task.
- Run existing repository checks to prove product behavior is unchanged.

## Confirmed constraints

- Preserve all existing trading, Evaluation, Risk Guard, secret, and contract rules.
- Keep built-in Explorer and Worker; do not duplicate them as Custom Agents.
- Use one writer for shared files.
- Subagent summaries contain only relevant files, evidence, risks, and results.
- Read-only roles inherit parent permissions; instructions do not imply sandbox isolation.

## Non-goals

- TradingAgents Adapter, Trading UI, Evaluation Dashboard, or product feature work.
- Changes to `src/orcastra/contracts.py` or any trading behavior.
- Permanent Planner, Debugger, or Documenter agents.
- Global user Codex configuration changes.
- Automatic commits, PR approval, or deployment.

## Acceptance criteria

- [x] Current Repository, `AGENTS.md`, and latest Notion plan are reviewed.
- [x] An independent read-only Explorer returns a concise bounded handoff.
- [x] Role boundaries, context packets, workflow gates, and cost controls are documented.
- [x] Existing safety invariants remain explicit.
- [x] Built-in roles are reused and only an independent Reviewer is customized.
- [x] Reviewer configuration parses and an independent review completes.
- [x] Existing tests, lint, and mock execution pass without product-code changes.
- [x] Final diff contains only harness documentation/configuration changes.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m orcastra run-mock --ticker AAPL --output artifacts
python -c "import tomllib; tomllib.load(open('.codex/agents/reviewer.toml', 'rb'))"
git diff --check
git status --short
```

## Known risks or open decisions

- Subagents consume additional tokens, so full role separation is reserved for
  non-trivial or safety-sensitive tasks.
- Shared-worktree agents can collide; only one Worker owns a file set.
- This Codex turn can verify generic Subagent delegation directly. Discovery of
  the new project Custom Agent by a fresh client session must be reported
  separately if the current orchestration API cannot select it by name.

## Coordinator decisions

- The current user request approves moving the Repository development workflow
  from the Notion section 12 proposal into active use. This adopts a contributor
  process only; it does not promote any unresolved trading or Evaluation product
  proposal to a confirmed decision.
- Built-in Explorer and Worker are sufficient and are not duplicated. A single
  project Reviewer is added now because independent review is a required gate,
  Codex has no built-in reviewer role, and the configuration is narrow and
  project-scoped. Planner, Debugger, and Documenter remain unconfigured.

## Role handoffs

### Explorer

Inspected the current repository in an independent context. Confirmed the change
can be documentation/configuration-only; identified the one-writer rule,
Reviewer independence, `harness` naming ambiguity, and required repository checks.

### Worker

Coordinator bootstrapped the workflow because it is the first harness task.
Changed only `AGENTS.md`, `README.md`, `.codex/agents/reviewer.toml`,
`docs/development_workflow.md`, and `docs/tasks/*`. No product source, contract,
test, dependency, or global Codex configuration changed. TOML parsing, six unit
tests, Ruff, AAPL mock execution, and `git diff --check` passed before review.

### Reviewer

Independent context reviewed the Task Brief, actual diff and untracked files,
Notion section 12, existing architecture and safety rules, official Subagents
documentation, and test evidence. No actionable findings. Verdict: `PASS`.

Verification gap: automatic discovery/selection of the project-scoped
`reviewer` by a fresh Codex client session was not directly exercised in this
turn. Its required fields and supported feature keys were independently checked,
and the TOML parsed successfully.

## Completion evidence

- Commit/PR: not created in this task
- Commands and results: reviewer TOML parsed; pytest 6 passed; Ruff passed;
  AAPL mock run succeeded; `git diff --check` passed
- Verified behavior: independent Explorer and Reviewer handoffs worked without
  inheriting the main conversation; no product code or contract changed
- Unverified behavior: fresh-session Custom Agent discovery/selection
- Follow-up: apply this workflow to the TradingAgents Adapter or Trading UI task
