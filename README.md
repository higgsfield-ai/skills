# Higgsfield AI Skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](./VERSION)
[![Skills](https://img.shields.io/badge/skills-4-blueviolet.svg)](#skills)
[![Discord](https://img.shields.io/badge/discord-join-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/higgsfield)

AI agent skills for image and video generation via [Higgsfield AI](https://higgsfield.ai). Works with Claude Code, Cursor, Codex, and other AI coding agents that load Markdown-based skills.

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
| [`higgsfield-generate`](./higgsfield-generate) | `/higgsfield:generate` | Image and video generation across 30+ models (Nano Banana 2, Soul V2, Veo 3.1, Kling 3.0, Seedance 2.0, Flux 2, GPT Image 2, …) plus Marketing Studio for branded ads with avatars, products, hooks, and settings. |
| [`higgsfield-soul-id`](./higgsfield-soul-id) | `/higgsfield:soul-id` | Train a Soul Character — a reusable, face-faithful identity model. Returns a `reference_id` consumable by Soul-aware generation. |
| [`higgsfield-product-photoshoot`](./higgsfield-product-photoshoot) | `/higgsfield:product-photoshoot` | Brand-quality product imagery with mode-specific prompt enhancement. 10 modes (studio, lifestyle, Pinterest, hero banner, ad packs, virtual try-on, …) backed by `gpt_image_2`. |
| [`higgsfield-marketplace-cards`](./higgsfield-marketplace-cards) | `/higgsfield:marketplace-cards` | Marketplace product cards: compliant main image, secondary product images, and A+ style modules via backend prompt enhancement. |

The skills chain: train Soul → use the reference id in `generate` (including Marketing Studio jobs). `product-photoshoot` and `marketplace-cards` are self-contained — backend enhances prompts before submitting image jobs.

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
| Generate any image / video from a prompt | `higgsfield-generate` | Prefers `gpt_image_2` / `nano_banana_2` for images and `seedance_2_0` for video by default |
| Image with my own face | `higgsfield-soul-id` then `higgsfield-generate` | One-time training, then `--soul-id` |
| Branded product photo (studio / lifestyle / Pinterest / hero / ad pack) | `higgsfield-product-photoshoot` | Mode-specific prompt enhancer + `gpt_image_2` |
| Marketplace product cards / A+ style content | `higgsfield-marketplace-cards` | Main image, secondary images, and A+ style modules with hidden marketplace prompt templates |
| Branded ad video / UGC / unboxing / TV spot | `higgsfield-generate` | Marketing Studio mode with avatars + products + optional hooks/settings |
| Train a custom face identity | `higgsfield-soul-id` | 5–20 photos, returns `reference_id` |
| Image-to-video animation | `higgsfield-generate` | Prefer `seedance_2_0` with `--start-image`; use `kling3_0` as lower-cost fallback |

## License

MIT — see [LICENSE](./LICENSE).
