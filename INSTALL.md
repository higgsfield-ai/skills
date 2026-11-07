# Install Higgsfield Skills

These skills ship in this repo:

- **`higgsfield-generate`** — image and video generation, 30+ models, plus Marketing Studio (branded ads with avatars, products, hooks, and settings) and Virality Predictor scoring
- **`higgsfield-soul-id`** — train a face-faithful Soul Character
- **`higgsfield-product-photoshoot`** — brand-quality product imagery with mode-specific prompt enhancement
- **`higgsfield-brandkit`** — complete visual identities, editable logo systems, brand applications, and PPTX/PDF brandbooks
- **`higgsfield-marketplace-cards`** — marketplace main, secondary, and A+ style product cards with backend prompt enhancement
- **`higgsfield-websites`** — build, edit, and deploy full-stack websites, apps, and browser games (React 19 + TanStack Start on Cloudflare) via `higgsfield website …`
- **`higgsfield-faceless-video`** — narrated faceless videos with live style-preset selection
- **`higgsfield-video-explainer`** — compatibility entry for explainers
- **`higgsfield-youtube-thumbnail`** — truthful YouTube thumbnails and vertical video covers with controlled variants

They chain: `higgsfield-soul-id` returns a Soul ID consumable by `higgsfield-generate` (Soul models and identity-aware Marketing Studio jobs). `higgsfield-brandkit` coordinates Recraft, Seedream, GPT Image, and local deterministic tools into one approved visual system. `higgsfield-product-photoshoot` is the single entry point for professional brand product visuals; `higgsfield-marketplace-cards` is the marketplace product card pipeline. Both use backend prompt enhancement before submitting image jobs. `higgsfield-websites` chains with `higgsfield-generate` to embed bespoke hero images, video loops, and OG assets in a site.

## Prerequisites

Install Higgsfield CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
higgsfield auth login
```

`higgsfield-websites` additionally uses `git` and [`bun`](https://bun.sh) locally to clone and build the website repo it creates.

`higgsfield-brandkit` checks stage-specific local tools and asks before installing anything. Full exports may require Playwright Chromium, ImageMagick, librsvg, LibreOffice, Poppler, and Fontconfig; FFmpeg is not used. Exact macOS and Ubuntu commands live in `higgsfield-brandkit/references/prerequisites.md`.

## Option 1 — `npx skills` (recommended, cross-agent)

Works with Claude Code, Cursor, Codex, and any agent that picks up `~/.<agent>/skills/<name>/SKILL.md`. Requires Node.js.

```bash
npx skills add higgsfield-ai/skills
```

Installs all eight skills. The `skills` CLI auto-detects the host agent and writes each skill to the right path.

## Option 2 — `gh skill install`

GitHub CLI v2.90+ extension. Same coverage as `npx skills`.

```bash
gh skill install higgsfield-ai/skills
```

Installs all eight skills.

## Option 3 — Claude Code marketplace

Claude Code only. Inside Claude Code:

```
/plugin marketplace add higgsfield-ai/skills
/plugin install higgsfield@higgsfield
```

Pulls the plugin manifest from `.claude-plugin/marketplace.json` and registers all eight skills, including `/higgsfield:higgsfield-brandkit`, `/higgsfield:higgsfield-youtube-thumbnail`, and `/higgsfield:higgsfield-websites`.

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

For a custom skills directory, run `./setup --host codex --target-dir <directory>`. The default Codex destination is `~/.agents/skills`.
