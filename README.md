# Higgsfield AI Skills

AI agent skills for image and video generation via [Higgsfield AI](https://higgsfield.ai).

Works with Claude Code, Cursor, Codex, and other AI coding agents that load Markdown-based skills.

```
"Generate a cinematic shot of a fox in a snowy forest, golden hour."
→ picks a photorealistic image model
→ submits via the hf CLI
→ delivers the result URL
```

## Skills

- **`higgsfield-generate`** — image and video gen across 35+ models (Nano Banana 2, Soul V2, Veo 3.1, Kling 3.0, Seedance 2.0, Flux 2, GPT Image 2, …) plus Marketing Studio for branded ads (avatars, products, UGC modes)
- **`higgsfield-soul`** — train a Soul Character (reusable face identity)
- **`higgsfield-product-photoshoot`** — brand-quality product imagery with mode-specific prompt enhancement (10 modes: studio, lifestyle, Pinterest, hero banner, ad packs, virtual try-on, …)

They chain: train Soul → use it in generate (including Marketing Studio jobs). Product photoshoot enhances brand-aware prompts before submitting to GPT Image 2.

## Install

See [INSTALL.md](./INSTALL.md).

Quick path (Claude Code):

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
hf auth login
git clone https://github.com/higgsfield-ai/skills.git ~/.claude/skills/higgsfield
```

## How it works

The skills are pure Markdown instructions. They drive the [`hf` CLI](https://github.com/higgsfield-ai/cli) to call Higgsfield API endpoints. No MCP server, no extra runtime — just one binary.

## License

MIT
