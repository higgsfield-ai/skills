---
version: 0.1.0
name: higgsfield-marketing
description: |
  Generate branded marketing images and videos with curated avatars and
  imported products via Higgsfield Marketing Studio.
  Use when: "create an ad", "make a UGC video", "generate marketing video",
  "make a product demo", "create unboxing", "TV spot", "virtual try-on",
  "product showcase", "brand video", "presenter video for product",
  "import product from URL", "create avatar for ad".
  Imports products from URL or uploaded images. Curated stock avatars or
  user-created custom avatars. Modes: ugc, ugc_unboxing, product_showcase,
  product_review, tv_spot, virtual_try_on, etc.
  Chain: import product → generate video. Or: create avatar → generate video.
  NOT for: generic image / video gen without product/brand context (use
  higgsfield-generate), training personal Soul Character (use higgsfield-soul).
argument-hint: "[--product-url <url>] [--avatar <id>] [prompt]"
allowed-tools: Bash
---

# Higgsfield Marketing Studio

Branded image and video generation: avatars + products + ad-style modes.

## Prerequisites

- `hf` CLI: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- Authenticated: `hf auth login`

## UX Rules

1. Be concise. Deliver the result URL, not the IDs and metadata dump.
2. Detect language, respond in it. CLI flags English.
3. One question per phase. Don't ask product+avatar+mode upfront.
4. Polling silent.

## Concepts

- **Avatar** — presenter face. Either a curated `preset` (browse `hf marketing-studio avatars list`) or `custom` (uploaded photos via `hf marketing-studio avatars create`).
- **Product** — brand item with title + reference images. Imported from URL (`hf marketing-studio products fetch --url ...`) or created from uploaded images (`hf marketing-studio products create`).
- **Webproduct** — App Store / web page version. Auto-routes when fetching App Store URLs.

## Workflow — quick ad video

1. **Get product.**
   - URL → `hf marketing-studio products fetch --url <url> --wait` (polls until import done)
   - Local images → `hf upload create <photo>...` then `hf marketing-studio products create --title "..." --image <id>...`
   Capture product id.
2. **Pick avatar.**
   - Default: `hf marketing-studio avatars list` and pick a preset matching the brand voice.
   - Custom: `hf marketing-studio avatars create --name "..." --image <upload_id>`.
3. **Pick mode.** Common: `ugc`, `ugc_unboxing`, `product_showcase`, `tv_spot`. See `references/modes.md`.
4. **Generate.**
   ```bash
   hf generate create marketing_studio_video \
     --prompt "..." \
     --avatars '[{"id":"<avatar_id>","type":"preset"}]' \
     --product_ids '[<product_id>]' \
     --mode ugc \
     --duration 15 \
     --resolution 720p \
     --aspect_ratio 9:16
   ```
5. **Wait.** `hf generate wait <id>`.
6. **Deliver.** URL + one-line summary (mode, duration).

## Workflow — marketing image

Same as above but use `marketing_studio_image` model:

```bash
hf generate create marketing_studio_image \
  --prompt "..." \
  --aspect_ratio 1:1 \
  --resolution 2k
```

## Reference docs

- `references/avatars.md` — preset vs custom, when to choose
- `references/products.md` — URL fetch flow vs manual create
- `references/modes.md` — every mode with when to use it
