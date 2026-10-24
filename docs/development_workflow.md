# Orcastra development workflow

Status: adopted repository workflow, 2026-10-24. This process governs software
development only; it does not change the Trading/Evaluation product architecture
or the trading-agent roles inside Orcastra.

The purpose of this harness is to keep requirements and decisions in the main
context while moving noisy exploration, implementation details, tests, and
debugging into bounded contexts with explicit outputs.

## Minimal agent structure

| Role | Responsibility | Input | Required output |
| --- | --- | --- | --- |
| Coordinator | Scope, Task Brief, delegation, decisions, integration, final report | User request, current Notion decisions, repository rules | Plan, accepted decisions, final evidence and open issues |
| Explorer | Read-only code and dependency mapping | Task Brief plus named paths | Relevant files/symbols, impact, risks, unknowns |
| Worker | Sole scoped writer and test author | Ready Task Brief plus Explorer handoff | Changed files, decisions made, commands and results, remaining risks |
| Reviewer | Independent acceptance and regression review | Task Brief, actual diff, test evidence | Findings by severity, verdict, verification gaps |
| Debugger | On-demand failure diagnosis | Failing command, trimmed log, related paths | Reproduction, root cause, evidence, recommended fix |

Codex provides built-in `explorer` and `worker` agents. Orcastra adds only the
project-scoped `.codex/agents/reviewer.toml`, because independent review is a
repeated project requirement and there is no built-in reviewer role. Coordinator
is the main agent. Debugger is a fresh, task-specific subagent rather than a
permanent configuration.

Custom-agent instructions can request read-only behavior but do not create a
separate sandbox: subagents inherit the parent session's permissions. The
Coordinator therefore verifies the diff and working tree after every delegated
phase. See the [official OpenAI Subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## When to use which path

Use the full workflow when a task changes product behavior, shared contracts,
safety controls, persistence, external integrations, UI/API boundaries, or
multiple implementation areas.

Use a lightweight Coordinator → Worker → checks path for a small, unambiguous,
low-risk change. Add independent review if the change touches a safety invariant
or contract. Do not spawn agents merely to rename a file, fix a typo, or make a
single mechanical edit.

Default operating budget per task:

- zero or one Explorer;
- one Worker for any shared file set;
- one Reviewer after implementation;
- one Debugger only when a failure cannot be explained in the current bounded context.

Parallelize independent read-heavy work only. Parallel Workers must have
disjoint file ownership and an explicit integration order. Never let two agents
edit the same shared worktree files concurrently.

## Context packets

Agents exchange distilled packets, not transcripts.

### Task Brief: Coordinator → roles

- Task ID and status
- Goal
- Authoritative requirements and links
- Relevant files, symbols, and contracts
- Confirmed constraints
- In-scope changes
- Non-goals
- Acceptance criteria
- Validation commands
- Known risks and unresolved decisions
- Expected handoff artifact

### Explorer handoff

- Files and symbols inspected
- Current execution/data path
- Minimal change surface
- Dependencies and affected tests
- Risks, conflicts, and unknowns
- No raw command dump unless it is direct evidence

### Worker handoff

- Files changed
- Behavior implemented
- Decisions made within the brief
- Tests added or changed
- Commands run with summarized results
- Deviations, unverified behavior, and follow-up needs

### Reviewer handoff

- Findings ordered by severity, with file/line evidence
- Violated requirement or acceptance criterion
- Reproduction or verification method
- `PASS`, `CHANGES_REQUIRED`, or `BLOCKED`
- Explicit verification gaps

### Debugger handoff

- Minimal reproduction
- Root cause and supporting evidence
- Ruled-out hypotheses when material
- Smallest recommended correction
- Tests that should fail before and pass after the fix

## Workflow gates

### 1. Requirements and Task Brief

The Coordinator reconciles the request with Notion and repository sources of
truth. Confirmed decisions and proposals remain visibly distinct. A material
conflict or missing product decision stops implementation and is returned to the
user.

Create a Task Brief before delegation. Use a GitHub Issue for short-lived work or
copy the template in `docs/tasks/README.md` when the task spans sessions, changes
architecture/contracts, or needs durable completion evidence.

### 2. Exploration

Use Explorer only when ownership or impact is unclear. Give it named paths and a
bounded question. Explorer must not edit. The Coordinator turns its report into
a Ready Task Brief; the Worker does not receive the Explorer's raw transcript.

### 3. Implementation

Assign one Worker to the declared file set. The Worker may make normal
implementation decisions inside the brief but must stop before changing product
requirements, safety invariants, or public contract semantics. Unexpected scope
is returned to the Coordinator instead of silently expanded.

### 4. Independent review

Reviewer receives the Task Brief, repository diff, and summarized test evidence,
not the implementation conversation. It may inspect code and run safe checks but
does not edit. `CHANGES_REQUIRED` findings go back as a narrow correction brief;
a fresh Debugger is used only for failures needing separate diagnosis.

### 5. Documentation and handoff

After review passes, update only documentation supported by implemented and
verified behavior. The Coordinator records completion evidence in the Task Brief
or PR and reports:

- implementation and changed files;
- tests and results;
- independent review verdict;
- unverified behavior;
- design decisions and rationale;
- next actions or user decisions.

Start the next independent feature from its Task Brief plus current Notion and
repository state. Do not depend on the previous chat transcript.

## Source-of-truth and safety rules

1. Notion owns confirmed product decisions, rationale, and decision history.
2. The repository owns implemented behavior, tests, architecture, and contracts.
3. `AGENTS.md` owns persistent contributor and safety instructions.
4. A Task Brief or GitHub Issue owns one task's scope and completion evidence.
5. Chat transcripts are supporting context only.

All roles preserve Orcastra's existing invariants: paper trading by default,
separate read-only Evaluation, synchronous deterministic Risk Guard, compatible
Trace/Evaluation evolution, secret exclusion, and evidence-backed completion
claims.
