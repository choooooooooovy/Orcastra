# Task Briefs

Use a repository Task Brief for work that spans sessions, changes architecture
or shared contracts, or benefits from durable review evidence. A concise GitHub
Issue is sufficient for smaller tasks. Do not create a file only to duplicate a
conversation.

Copy the template below to `docs/tasks/ORC-NNNN-short-name.md`.

```markdown
# ORC-NNNN — Task title

Status: Draft | Ready | In progress | Review | Done | Blocked

## Goal

One observable outcome.

## Authoritative context

- User requirement or GitHub Issue
- Relevant Notion section
- Repository documents and contracts

## Scope

- Files/symbols expected to change
- Behavior included in this task

## Confirmed constraints

- Safety, compatibility, and product decisions that cannot change

## Non-goals

- Explicitly excluded work

## Acceptance criteria

- [ ] Observable criterion
- [ ] Regression/safety criterion

## Validation

- Commands and manual checks required

## Known risks or open decisions

- Risks the roles must monitor
- Decisions that require Coordinator/user input

## Role handoffs

### Explorer

Concise file/symbol map, impact, and risks; or `Not needed`.

### Worker

Changed files, behavior, tests, decisions, and gaps.

### Reviewer

Findings, verdict, and verification gaps.

## Completion evidence

- Commit/PR:
- Commands and results:
- Verified behavior:
- Unverified behavior:
- Follow-up:
```
