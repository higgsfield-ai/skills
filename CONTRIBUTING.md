# Contributing to Higgsfield Skills

Thanks for considering a contribution. This repo follows the [Agent Skills specification](https://agentskills.io/specification.md) — every skill is one folder with a `SKILL.md` plus optional `references/` for on-demand details.

## Git workflow

All changes go through pull requests. No direct pushes to `main`.

```bash
# 1. Create a branch from main
git checkout main && git pull
git checkout -b <type>/<short-description>
# e.g. feat/marketing-studio-presets, fix/soul-timeout, refactor/product-photoshoot

# 2. Make changes, commit with clear messages
git add -A
git commit -m "<type>: short summary of what changed

- Why this change is needed (not just what)
- Reference any test runs or eval results
- Note any breaking changes to the skill interface"

# 3. Push and open a PR
git push -u origin <branch-name>
gh pr create
```

### Branch naming

| Prefix | Use for |
|---|---|
| `feat/` | New capability (new mode, new model mapping, new flag) |
| `fix/` | Bug fix (wrong default, broken reference link, version desync) |
| `refactor/` | Internal cleanup (no user-visible behavior change) |
| `docs/` | README, CONTRIBUTING, references-only updates |

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) so future automation (`release-please`) can read them:

- `feat(generate): add Nano Banana 3 to model catalog`
- `fix(soul): handle 401 on first auth gracefully`
- `docs: clarify Marketing Studio avatar workflow`
- `refactor(product-photoshoot): extract interview flows into references/`

## PR checklist

Before merging, confirm:

1. **Frontmatter is valid.** YAML parses. `name` matches the directory exactly. `version` is set. `description` includes Use-when triggers, Chain rules, and a NOT-for boundary.
2. **Versions are in sync.** `VERSION`, every `*/SKILL.md` `version:` field, `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `.cursor-plugin/plugin.json` all match. Don't bump versions by hand on feature branches — release-please (when enabled) handles it on merge to `main`.
3. **All references resolve.** Every `references/X.md` mentioned in `SKILL.md` exists in the same skill's bundle. No `../` parent-directory references — each skill must be installable standalone via `gh skill install`.
4. **No orphan reference files.** Every file inside `<skill>/references/` is mentioned at least once in that skill's `SKILL.md`. If it isn't reachable, delete it or link it.
5. **`marketplace.json` is up to date.** If you added or renamed a skill folder, update the `skills` array in `.claude-plugin/marketplace.json`.
6. **UX rules unchanged or stricter.** Don't loosen rules like "no raw IDs in chat", "polling is silent", "detect language and respond in it" without an explicit reason in the PR description.
7. **CLI commands are real.** Every `higgsfield …` example in your SKILL.md or references must be a real, current command. Run it locally before merging.
8. **Behavior change → docs change.** If you changed defaults, mode-selection logic, or chain semantics, the affected `SKILL.md` reflects it. An agent reading only `SKILL.md` should be able to execute the skill correctly.

## Adding a new skill

A new skill is a new top-level folder named `higgsfield-<name>/` containing `SKILL.md`. Follow the existing structure:

```yaml
---
version: 0.3.0
name: higgsfield-<name>
description: |
  <One paragraph: what it does and which API surface it wraps>
  Use when: "<trigger phrase>", "<trigger phrase>", ...
  Chain with: <other skill> when ...
  NOT for: <case A> (use <skill A>), <case B> (use <skill B>).
argument-hint: "[primary-arg] [--flag <value>]"
allowed-tools: Bash
---

# <Title>

<One sentence: what this is a wrapper around>

## Prerequisites

## UX Rules
1. Be concise. ...
2. ...

## Workflow
1. ...

## Errors
- ...

## Reference docs
- references/...
```

Then:

1. Add the folder to the `skills` array in `.claude-plugin/marketplace.json`.
2. Update `README.md` with a row in the Skills table and Quick Reference.
3. Add an `INSTALL.md` mention if the skill needs extra setup.
4. Open a `feat/` PR.

## Reference docs

If a section in `SKILL.md` would not break the agent's ability to decide what to do next, move it to `<skill>/references/`. The agent loads references on-demand — `SKILL.md` is injected on every turn, so keep it lean.

Each skill bundles its own references. If two skills happen to share a doc (e.g. both have a `troubleshooting.md`), keep separate copies — drift between skills is acceptable as long as each skill is internally consistent.

## License

By contributing, you agree your contribution is licensed under MIT.
