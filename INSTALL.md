# Install Higgsfield Skills

Three skills ship in this repo:

- **`higgsfield-generate`** — image and video generation, 35+ models, plus Marketing Studio (branded ads with avatars and imported products)
- **`higgsfield-soul`** — train a face-faithful Soul Character
- **`higgsfield-product-photoshoot`** — brand-quality product imagery with mode-specific prompt enhancement

They chain: `higgsfield-soul` returns a reference id consumable by `higgsfield-generate` (Soul models and identity-aware Marketing Studio jobs). `higgsfield-product-photoshoot` is the single entry point for any professional product visual; backend enhances the prompt before submitting to `gpt_image_2`.

## Prerequisites

Install the `hf` CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
hf auth login
```

## Option 1 — Claude Code

```bash
git clone https://github.com/higgsfield-ai/skills.git ~/.claude/skills/higgsfield
```

All three skills are auto-discovered.

## Option 2 — Cursor

Add via Cursor's plugin marketplace (search "Higgsfield"), or:

```bash
git clone https://github.com/higgsfield-ai/skills.git ~/.cursor/plugins/higgsfield
```

## Option 3 — Codex

```bash
git clone https://github.com/higgsfield-ai/skills.git ~/.codex/plugins/higgsfield
```

## Option 4 — `gh skill install`

If you have GitHub CLI v2.90+:

```bash
gh skill install higgsfield-ai/skills higgsfield-generate
gh skill install higgsfield-ai/skills higgsfield-soul
gh skill install higgsfield-ai/skills higgsfield-product-photoshoot
```

## Option 5 — manual git clone

For any agent with a skills directory (`~/.<agent>/skills/`):

```bash
git clone https://github.com/higgsfield-ai/skills.git ~/.<agent>/skills/higgsfield
```

## Verify

In your agent, ask:

> "Generate a minimal test image with Higgsfield."

The agent should invoke `higgsfield-generate`, run `hf generate create z_image --prompt "test"`, and deliver a URL.

## Updating

```bash
cd ~/.<agent>/skills/higgsfield
git pull
```
