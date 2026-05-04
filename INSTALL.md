# Install Higgsfield Skills

Three skills ship in this repo:

- **`higgsfield-generate`** — image and video generation, 30+ models, plus Marketing Studio (branded ads with avatars and imported products)
- **`higgsfield-soul-id`** — train a face-faithful Soul Character
- **`higgsfield-product-photoshoot`** — brand-quality product imagery with mode-specific prompt enhancement

They chain: `higgsfield-soul-id` returns a Soul ID consumable by `higgsfield-generate` (Soul models and identity-aware Marketing Studio jobs). `higgsfield-product-photoshoot` is the single entry point for any professional product visual; backend enhances the prompt before submitting to `gpt_image_2`.

## Prerequisites

Install Higgsfield CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
higgsfield auth login
```

## Option 1 — `npx skills` (recommended, cross-agent)

Works with Claude Code, Cursor, Codex, and any agent that picks up `~/.<agent>/skills/<name>/SKILL.md`. Requires Node.js.

```bash
npx skills add higgsfield-ai/skills
```

Installs all three skills. The `skills` CLI auto-detects the host agent and writes each skill to the right path.

## Option 2 — `gh skill install`

GitHub CLI v2.90+ extension. Same coverage as `npx skills`.

```bash
gh skill install higgsfield-ai/skills
```

Installs all three skills.

## Option 3 — Claude Code marketplace

Claude Code only. Inside Claude Code:

```
/plugin marketplace add higgsfield-ai/skills
/plugin install higgsfield@higgsfield
```

Pulls the plugin manifest from `.claude-plugin/marketplace.json` and registers all three skills as `/higgsfield:generate`, `/higgsfield:soul-id`, `/higgsfield:product-photoshoot`.

## Option 4 — Setup script

Universal fallback. Clones the repo locally and symlinks each skill into the agent's expected directory.

```bash
git clone --depth 1 https://github.com/higgsfield-ai/skills.git
cd skills
./setup
```

The script auto-detects Claude Code / Cursor / Codex (override with `--host <agent>`), installs the CLI if missing, checks auth, and symlinks each skill subdirectory into place. Idempotent.

## Verify

In your agent, ask:

> "Generate a minimal test image with Higgsfield."

The agent should invoke `higgsfield-generate`, run `higgsfield generate create z_image --prompt "test" --wait`, and deliver the URL printed on stdout.

## Updating

| Method | Update command |
|---|---|
| `npx skills` | re-run the `npx skills add ...` commands |
| `gh skill install` | `gh skill update higgsfield-ai/skills` |
| Claude Code marketplace | `/plugin update higgsfield@higgsfield` |
| Setup script | `cd skills && git pull && ./setup` |
