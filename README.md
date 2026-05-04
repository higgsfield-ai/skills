# Higgsfield AI Skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](./VERSION)
[![Skills](https://img.shields.io/badge/skills-3-blueviolet.svg)](#skills)
[![Discord](https://img.shields.io/badge/discord-join-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/higgsfield)

AI agent skills for image and video generation via [Higgsfield AI](https://higgsfield.ai).

Works with Claude Code, Cursor, Codex, and other AI coding agents that load Markdown-based skills.

## Install

See [INSTALL.md](./INSTALL.md) for human-facing options. For AI-agent-driven installs, see [INSTALL_FOR_AGENTS.md](./INSTALL_FOR_AGENTS.md).

Quick path (Claude Code):

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
hf auth login
git clone https://github.com/higgsfield-ai/skills.git ~/.claude/skills/higgsfield
```

```text
"Generate a cinematic shot of a fox in a snowy forest, golden hour."
→ picks a photorealistic image model
→ submits via the hf CLI
→ delivers the result URL

"Train my Soul on these 10 photos, then make a 9:16 UGC ad of me holding the product."
→ trains Soul Character (face-faithful identity)
→ chains into Marketing Studio with custom avatar + imported product
→ delivers the share link
```

## Skills

| Skill | Invoke | Description |
|---|---|---|
| [`higgsfield-generate`](./higgsfield-generate) | `/higgsfield:generate` | Image and video generation across 35+ models (Nano Banana 2, Soul V2, Veo 3.1, Kling 3.0, Seedance 2.0, Flux 2, GPT Image 2, …) plus Marketing Studio for branded ads with avatars and imported products. |
| [`higgsfield-soul`](./higgsfield-soul) | `/higgsfield:soul` | Train a Soul Character — a reusable, face-faithful identity model. Returns a `reference_id` consumable by Soul-aware generation. |
| [`higgsfield-product-photoshoot`](./higgsfield-product-photoshoot) | `/higgsfield:product-photoshoot` | Brand-quality product imagery with mode-specific prompt enhancement. 10 modes (studio, lifestyle, Pinterest, hero banner, ad packs, virtual try-on, …) backed by `gpt_image_2`. |

The skills chain: train Soul → use the reference id in `generate` (including Marketing Studio jobs). `product-photoshoot` is self-contained — backend enhances the prompt before submitting to `gpt_image_2`.

### Modes

**`higgsfield-product-photoshoot`** — 10 modes for brand visuals:

| Mode | What it's for |
|---|---|
| `product_shot` | Product on neutral / studio / catalog background |
| `lifestyle_scene` | Product in a real environment — hands, action, atmosphere |
| `closeup_product_with_person` | Tight crop with hands or partial face — beauty, demonstrating |
| `pinterest_pin` | Vertical 2:3 Pinterest-native pin, moodboard feel |
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
| Image with my own face | `higgsfield-soul` then `higgsfield-generate` | One-time training, then `--custom_reference_id` |
| Branded product photo (studio / lifestyle / Pinterest / hero / ad pack) | `higgsfield-product-photoshoot` | Mode-specific prompt enhancer + `gpt_image_2` |
| Branded ad video / UGC / unboxing / TV spot | `higgsfield-generate` | Marketing Studio mode with avatars + products |
| Train a custom face identity | `higgsfield-soul` | 5–20 photos, returns `reference_id` |
| Image-to-video animation | `higgsfield-generate` | Prefer `seedance_2_0` with `--start-image`; use `kling3_0` as lower-cost fallback |

## How it works

The skills are pure Markdown instructions. They drive the [`hf` CLI](https://github.com/higgsfield-ai/cli) to call Higgsfield API endpoints. No MCP server, no extra runtime — just one binary.

Each skill is self-contained: its own `references/` directory bundles deep-dive docs (model catalog, prompt engineering, troubleshooting) loaded on-demand by the agent rather than every turn.

## Repository structure

```
skills/
├── README.md                          # this file
├── INSTALL.md                         # human-facing install (5 options)
├── INSTALL_FOR_AGENTS.md              # agent-driven install runbook
├── CONTRIBUTING.md                    # PR workflow + checklist
├── VERSION                            # 0.3.0
├── LICENSE                            # MIT
├── .claude-plugin/marketplace.json    # Claude Code marketplace
├── .claude-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── .codex-plugin/plugin.json
├── higgsfield-generate/
│   ├── SKILL.md
│   └── references/
│       ├── model-catalog.md
│       ├── prompt-engineering.md
│       ├── media-inputs.md
│       ├── marketing-{avatars,products,modes}.md
│       └── troubleshooting.md
├── higgsfield-soul/
│   ├── SKILL.md
│   └── references/{photo-guide,troubleshooting}.md
└── higgsfield-product-photoshoot/
    └── SKILL.md
```

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for workflow, branch naming, commit style, and the PR checklist.

## License

MIT — see [LICENSE](./LICENSE).
