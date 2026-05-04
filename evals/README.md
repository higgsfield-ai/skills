# Evals

Test scenarios for the three skills. **Dev-only** — not shipped to end users.

## Why

Skill behavior is defined in plain markdown. Plain markdown drifts. Without a fixed set of scenarios + scoring rubric, every refactor is a hope.

Evals exist to:

1. Catch regressions after a `SKILL.md` edit (mode-selection logic, default model, prompt-enhancer routing).
2. Validate empirical decisions before they go into `CLAUDE.md` → "Key Decisions (Do Not Revisit Without Data)".
3. Onboard contributors — reading 10 worked scenarios is faster than reading 666 lines of `SKILL.md`.

## How

There is no automated runner yet. To run a round:

1. Read [`scenarios.md`](./scenarios.md) — 10 user requests + expected agent behavior.
2. Run each scenario in a fresh agent session (Claude Code with skills installed).
3. Score by the rubric in `scenarios.md`. Track in a spreadsheet or Notion.
4. After 3+ rounds with stable results, codify findings as bullets in `CLAUDE.md` → Key Decisions.

## Round vs scenario

- **Round** — a snapshot of the skills at a specific commit, scored against the full scenario set.
- **Scenario** — one user request + expected behavior + scoring rubric.

## When to add new scenarios

Add a scenario when:

- A bug was caught only by a manual test → codify so it's caught next time.
- A new feature ships → write the scenario before the PR merges.
- A user reports unexpected behavior → write the scenario as part of the bug report triage.

Don't add scenarios that test internals (e.g. "did the agent log to stderr"). Test what the user sees.

## Round template

When recording a round, capture:

- Commit SHA being tested.
- Date.
- Score per scenario (pass / fail / partial).
- Failure mode if not passing.
- Time-to-result (seconds from prompt to deliverable).

Compare round-over-round. Regression of >15% on score or >2× on time = revert and investigate.
