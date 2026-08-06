# Higgsfield AI Skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-0.12.0-green.svg)](./VERSION)
[![Skills](https://img.shields.io/badge/skills-9-blueviolet.svg)](#skills)
[![Discord](https://img.shields.io/badge/discord-join-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/higgsfield)

AI agent skills for image/video generation and complete visual brand systems via [Higgsfield AI](https://higgsfield.ai), including Marketing Studio and Virality Predictor video scoring. Works with Claude Code, Cursor, Codex, and other AI coding agents that load Markdown-based skills.

## Install

Pick one. Each method handles the Higgsfield CLI install and auth as part of skill setup.

### `npx skills` — recommended, cross-agent

```bash
npx skills add higgsfield-ai/skills
```

### `gh skill install`

GitHub CLI v2.90+:

```bash
gh skill install higgsfield-ai/skills
```

### Claude Code marketplace

Inside Claude Code:

```
/plugin marketplace add higgsfield-ai/skills
/plugin install higgsfield@higgsfield
```

### Setup script

Universal fallback:

```bash
git clone --depth 1 https://github.com/higgsfield-ai/skills.git
cd skills
./setup
```

More options in [INSTALL.md](./INSTALL.md). Agent-driven install (paste into your agent): [INSTALL_FOR_AGENTS.md](./INSTALL_FOR_AGENTS.md).

## Skills

| Skill | Invoke | Description |
|---|---|---|
| [`higgsfield-generate`](./higgsfield-generate) | `/higgsfield:generate` | Image, video, 3D, and audio generation across 30+ models, selected by resolving a **role** (`default-video`, `text-render-image`, `character-image`, …) against the live catalog rather than a hardcoded name — so a new model reaches you without a skill update. Plus Marketing Studio for branded ads with avatars/products/hooks/settings and Virality Predictor scoring for finished videos. |
| [`higgsfield-soul-id`](./higgsfield-soul-id) | `/higgsfield:soul-id` | Train a Soul Character — a reusable, face-faithful identity model. Returns a `reference_id` consumable by Soul-aware generation. |
| [`higgsfield-product-photoshoot`](./higgsfield-product-photoshoot) | `/higgsfield:product-photoshoot` | Brand-quality product imagery with mode-specific prompt enhancement. 10 modes (studio, lifestyle, Pinterest, hero banner, ad packs, virtual try-on, …) backed by `gpt_image_2`. |
| [`higgsfield-brandkit`](./higgsfield-brandkit) | `/higgsfield:brandkit` | Create or extend a complete visual identity: palettes, editable SVG logo marks, typography, mockups, social graphics, packaging, signage, merchandise, decks, and canonical PPTX/PDF brandbooks. |
| [`higgsfield-marketplace-cards`](./higgsfield-marketplace-cards) | `/higgsfield:marketplace-cards` | Marketplace product cards: compliant main image, secondary product images, and A+ style modules via backend prompt enhancement. |
| [`higgsfield-websites`](./higgsfield-websites) | `/higgsfield:websites` | Build, edit, and deploy full-stack websites — React 19 + TanStack Start, server-rendered as one Cloudflare Worker with D1 / R2 / KV / Durable Objects / Containers. Create → get git repo access → edit locally → push → deploy preview/production, all via `higgsfield website …`. |
| [`higgsfield-video-explainer`](./higgsfield-video-explainer) | `/higgsfield:video-explainer` | Create a narrated non-photoreal explainer as matched Seed Audio + Gemini Omni blocks, then assemble the final MP4 with `explainer_video`. |
| [`higgsfield-youtube-thumbnail`](./higgsfield-youtube-thumbnail) | `/higgsfield:youtube-thumbnail` | Create truthful, high-impact YouTube thumbnails and vertical video covers with identity-preserving references, controlled variants, focused edits, and optional text-overlay guidance. |
| [`higgsfield-game-generation`](./higgsfield-game-generation) | `/higgsfield:game-generation` | Plan, build, verify, and deploy playable browser games, or generate game-specific sprites, textures, rigged 3D assets, and audio. |

The skills chain: train Soul → use the reference id in `generate` (including Marketing Studio jobs). `brandkit` chains Recraft, Seedream, GPT Image, and deterministic local tooling into one approval-aware identity system. `product-photoshoot` and `marketplace-cards` are self-contained — backend enhances prompts before submitting image jobs. `youtube-thumbnail` can follow any video workflow once its truthful topic and visual direction are known. `websites` chains with `generate` to embed bespoke hero images, video loops, and OG assets in the site.

### Modes

**`higgsfield-product-photoshoot`** — 10 modes for brand visuals:

| Mode | What it's for |
|---|---|
| `product_shot` | Product on neutral / studio / catalog background |
| `lifestyle_scene` | Product in a real environment — hands, action, atmosphere |
| `closeup_product_with_person` | Tight crop with hands or partial face — beauty, demonstrating |
| `moodboard_pin` | Vertical 2:3 Pinterest-native pin, moodboard feel |
| `hero_banner` | Wide-format website / email / campaign header |
| `social_carousel` | 3–10 connected slides for IG / LinkedIn / Facebook |
| `ad_creative_pack` | Coordinated pack of static ad variants for Meta / TikTok / Pinterest / Google |
| `virtual_model_tryout` | Product worn or used by an AI-rendered model |
| `conceptual_product` | Surreal / CGI-style / levitating / splash / sculptural product |
| `restyle` | Transform an existing image's aesthetic, mood, or seasonal context |

**`higgsfield-generate` Marketing Studio** — 9 modes for branded ad video:

| Mode | What it's for |
|---|---|
| `ugc` | Default. Casual, organic-feel content from a presenter |
| `ugc_how_to` | Tutorial / explainer |
| `ugc_unboxing` | Unboxing reveal |
| `product_showcase` | Clean product highlight, polished |
| `product_review` | Presenter giving an opinion |
| `tv_spot` | Broadcast-style commercial |
| `wild_card` | Experimental, model picks the vibe |
| `ugc_virtual_try_on` | Trying on clothing — UGC vibe |
| `virtual_try_on` | Trying on clothing — polished, model-driven |

## Quick Reference

| What you want | Skill | Note |
|---|---|---|
| Generate any image / video from a prompt | `higgsfield-generate` | Resolves a live role (`default-image`, `default-video`, …) from the CLI catalog — no model name is baked into the skill |
| Generate audio from a prompt | `higgsfield-generate` | Resolves `role:default-audio`, or `role:voiceover-audio` for narration |
| Image with my own face | `higgsfield-soul-id` then `higgsfield-generate` | One-time training, then `--soul-id` |
| Branded product photo (studio / lifestyle / Pinterest / hero / ad pack) | `higgsfield-product-photoshoot` | Mode-specific prompt enhancer + `gpt_image_2` |
| Create or extend a logo, visual identity, brand asset system, or Brandbook | `higgsfield-brandkit` | Recraft SVG marks + approved palette/type + local editable exports and dependency-aware revisions |
| Marketplace product cards / A+ style content | `higgsfield-marketplace-cards` | Main image, secondary images, and A+ style modules with hidden marketplace prompt templates |
| Branded ad video / UGC / unboxing / TV spot | `higgsfield-generate` | Marketing Studio mode with avatars + products + optional hooks/settings |
| Analyze a video's hook / attention / virality potential | `higgsfield-generate` | Uses Virality Predictor (`brain_activity`) with `--video`; returns score metrics plus an Open report link |
| Train a custom face identity | `higgsfield-soul-id` | 5–20 photos, returns `reference_id` |
| Image-to-video animation | `higgsfield-generate` | `role:default-video` with `--start-image`; `role:fast-video` only when you ask for cheaper output |
| Build / edit / deploy a website, web app, landing page, or dashboard | `higgsfield-websites` | Full-stack React 19 + TanStack Start on Cloudflare; `higgsfield website create/repo-access/deploy` |
| Create a narrated explainer from a topic or document | `higgsfield-video-explainer` | Resolves a live style, generates audio then video per block, and assembles with `explainer_video` |
| Create a YouTube thumbnail or Shorts/Instagram video cover | `higgsfield-youtube-thumbnail` | Pinned 4K main render, optional face/logo references, controlled variants, and identity-preserving tweaks |
| Build and deploy a playable browser game | `higgsfield-game-generation` | Owns game design, assets, implementation, QA, deploy, and optional marketplace publish |

## License

MIT — see [LICENSE](./LICENSE).
