---
name: New skill request
about: Propose a new top-level skill (not an addition to an existing one)
title: "feat: new skill — "
labels: enhancement, new-skill
assignees: ""
---

## Proposed name

`higgsfield-<name>`

<!-- Lowercase a-z, numbers, and hyphens only. Must match the directory name. -->

## What it does

<!-- One paragraph. -->

## Use-when triggers

<!-- 6–12 phrases the user might say that should activate this skill. These will end up in SKILL.md frontmatter. -->

- "..."
- "..."
- "..."

## Chain rules

<!-- Which existing skills does this work with, and how? Which existing skills does it explicitly NOT replace? -->

- Chain with: ...
- NOT for: ... (use ... instead)

## Why this is a separate skill, not an addition to an existing one

<!-- Critical question. If it can fit inside higgsfield-generate, it should. -->

## Backing API or CLI command

<!-- e.g. `higgsfield <noun> <verb>`. If the CLI command doesn't exist yet, link to the CLI issue/PR. -->

## Sketch of the SKILL.md

```yaml
---
version: 0.3.0
name: higgsfield-<name>
description: |
  ...
  Use when: ...
  Chain with: ...
  NOT for: ...
argument-hint: ""
allowed-tools: Bash
---
```
