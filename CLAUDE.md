
# Higgsfield AI — Image & Video Generation

Skill for generating images and videos through the Higgsfield API, training personalized models (Soul Character), and inspecting the user's account (balance, history, uploads).

## Auth

When the user asks to login or authenticate:
```bash
python3 login.py
```

Opens browser, polls until approved, saves token. All subsequent requests use `Authorization: Bearer $(python3 get_token.py)`.

## Output rules (apply to every command)

- **Never dump raw JSON.** Pipe `curl` through `jq` so that the bash stdout IS the final markdown the user sees.
- **Do not restate bash output.** After a command whose `jq` output is user-ready markdown, your assistant text must NOT contain any of the listed items. Allowed follow-ups: a single-line question ("Switch to another?"), a single-line action note ("Selected."), or no text at all. Never re-enumerate the results.
- **Hide internal identifiers.** Workspace `id` and model `job_set_type` are for API calls only — show `name`, `display_name`, and other user-facing fields.
- **Use column-aligned tables for multi-attribute items** (workspaces, transactions, jobs, uploads, soul characters). In jq emit pipe-separated lines, then pipe through `column -t -s '|'` for aligned monospace columns. Do NOT use markdown pipe syntax (`| col | col |`) — it renders as raw text in bash stdout. Use bulleted lists only for single-attribute lists like model names; group by category when relevant (e.g. Image / Video models).
- **Result URLs are clickable.** Don't download files unless the user explicitly asks.
- **Enhance short prompts** into detailed visual descriptions (lighting, composition, style, mood) while keeping the user's intent intact.
- **Use defaults from each model's `params` schema.** Only ask about params the user explicitly mentioned.

## Workspace selection

On first use, list workspaces and ask which to use, then persist the choice via `/workspaces/select`. Once selected, every workspace-scoped endpoint (balance, transactions, generate, custom-references, uploads) uses the stored workspace. Details: `docs/workspaces.md`.

## Topics

Read the relevant doc before running commands for that area:

- **Workspaces** (list, select, unselect) → `docs/workspaces.md`
- **Models** (what's available, params schema) → `docs/models.md`
- **Generate** (image/video, cost, media inputs) → `docs/generate.md`
- **Jobs** (poll status, list completed) → `docs/jobs.md`
- **Balance & Transactions** → `docs/balance.md`
- **Uploads** (image, video, audio) → `docs/uploads.md`
- **Soul Character** (train personalized model & use) → `docs/soul.md`

## Common failures

- `Session expired` / `401 Unauthorized` — run `python3 login.py`
- `API error 400/422` — check models list and the model's params schema
- `Soul Character not found` — check reference id and status
- `Minimum Basic plan required` — Soul Character training requires a paid plan
