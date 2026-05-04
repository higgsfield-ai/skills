## What

<!-- One paragraph: what this PR does. -->

## Why

<!-- One paragraph: why this is needed. Reference issues with `Closes #N`. -->

## Changes

<!-- Bullet list of specific files / behaviors changed. -->

-

## Type

- [ ] `feat:` — new capability
- [ ] `fix:` — bug fix
- [ ] `refactor:` — internal cleanup, no behavior change
- [ ] `docs:` — README / CONTRIBUTING / references-only

## Testing

<!-- How you verified this works. Paste relevant agent output, higgsfield CLI output, or test scenarios. -->

- [ ]
- [ ]

## PR checklist

- [ ] Frontmatter parses; `name` matches the skill directory; `version` set; `description` includes Use-when triggers and a NOT-for boundary.
- [ ] Versions in sync across `VERSION`, all `*/SKILL.md` frontmatters, `marketplace.json`, and the 3 plugin manifests (CI verifies).
- [ ] All `references/X.md` links in `SKILL.md` resolve; no orphan reference files; no `../` parent-dir references.
- [ ] If a skill folder was added or renamed, `marketplace.json` reflects it.
- [ ] If user-facing behavior changed, `SKILL.md` and `README.md` reflect it.
- [ ] Every `higgsfield …` example in the docs is a real, current command.

## Breaking changes

<!-- None / describe what breaks. If yes, this is a `feat!:` (or `fix!:`) commit. -->
