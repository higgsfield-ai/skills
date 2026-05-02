---
version: 0.2.0
name: higgsfield-generate
description: |
  Generate images and videos via Higgsfield AI through 35+ models including
  Nano Banana 2, Soul V2, Veo 3.1, Kling 3.0, Seedance 2.0, Flux 2, GPT Image 2,
  plus Marketing Studio for branded ad video/image with curated avatars and
  imported products.
  Use when: "generate an image", "make a picture", "create artwork",
  "make a video", "animate this photo", "image-to-video", "img2vid",
  "edit this image with AI", "stylize a photo", "remix this image",
  "produce a clip", "render a scene", "create an ad", "make a UGC video",
  "generate marketing video", "make a product demo", "create unboxing",
  "TV spot", "virtual try-on", "product showcase", "brand video",
  "presenter video for product", "import product from URL",
  "create avatar for ad".
  Supports text-to-image, image-to-image, image-to-video, reference-based
  generation, and Marketing Studio (avatars + products + ad modes).
  Auto-detects whether passed IDs are uploads or previous jobs.
  Chain with higgsfield-soul when the user wants their face in the output.
  NOT for: training Soul Character (use higgsfield-soul), professional product
  photoshoots with mode-specific prompt enhancement (use
  higgsfield-product-photoshoot), text-only / chat / TTS tasks.
argument-hint: "[prompt] [--model <name>] [--image <path-or-id>]"
allowed-tools: Bash
---

# Higgsfield Generate

Submit jobs to any Higgsfield model. Wraps the `hf` CLI. Covers generic image/video gen and Marketing Studio (branded ads, avatars, products).

## Prerequisites

- `hf` CLI installed: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- Authenticated: `hf auth login`

## UX Rules

1. Be concise. No raw IDs, no JSON dumps in chat. Print result URL when ready.
2. No internal jargon. Don't narrate "calling hf cost", "polling job".
3. Detect the user's language from the first message and reply in it. Technical args (`--aspect_ratio 16:9`) stay English.
4. Don't batch-ask. Pick a sane default model and ask one thing at a time only if genuinely missing.
5. Don't pre-estimate cost. Just submit unless the user asks.
6. Polling is silent. Wait until terminal status, then deliver.

## Workflow — generic generation

1. **Pick a model.** Use the user's intent to choose. If unclear, default:
   - Image, photorealistic → `nano_banana_2`
   - Image, with user's face → `text2image_soul_v2` (needs Soul ref)
   - Image-to-video → `kling3_0`
   - Generic video → `veo3_1`
   - Branded ad video → `marketing_studio_video` (see Marketing Studio below)
   - See `references/model-catalog.md` for the full map.
2. **Pass media inputs straight to flags.** Media flags accept a local file path **or** a UUID. CLI auto-uploads paths and auto-detects job vs upload for UUIDs. No need to pre-upload.
3. **Validate quickly.** If unsure of params, run `hf model get <jst> --json` once and pass only what's needed. Use schema defaults otherwise.
4. **Submit.** `hf generate create <jst> --prompt "..." [media flags] [param flags]`. Capture job id.
5. **Wait.** `hf generate wait <id>` — blocks until terminal, prints result URL on stdout.
6. **Deliver.** Send the URL plus a one-line summary (model, duration if video).

## Media flags

| Flag | Use for |
|---|---|
| `--image <path-or-id>` | reference image |
| `--start-image <path-or-id>` | first frame for image-to-video transitions |
| `--end-image <path-or-id>` | last frame for transitions |
| `--video <path-or-id>` | reference video |
| `--audio <path-or-id>` | reference audio (lipsync) |

Each flag accepts either a local file path (auto-uploaded) or a UUID (upload id from `hf upload create`, or a previous job id).

## Common params

Flags pass through to model schema. Use `hf model get <jst>` to discover.

```bash
hf generate create flux_2 --prompt "neon city at dusk" --aspect_ratio 16:9 --resolution 2k
hf generate create kling3_0 --prompt "camera dollies in" --start-image ./first.png --duration 8
hf generate create text2image_soul_v2 --prompt "..." --custom_reference_id <soul_ref_id>
```

Stdin prompt: `echo "..." | hf generate create z_image`.

## Marketing Studio

Branded image/video gen: avatars + products + ad-style modes. Use models `marketing_studio_video` and `marketing_studio_image`.

### Concepts

- **Avatar** — presenter face. Curated `preset` (browse `hf marketing-studio avatars list`) or `custom` (uploaded photos via `hf marketing-studio avatars create`).
- **Product** — brand item with title + reference images. Imported from URL (`hf marketing-studio products fetch --url ...`) or created from uploaded images (`hf marketing-studio products create`).
- **Webproduct** — App Store / web page version. Auto-routes when fetching App Store URLs.

### UX rules (additional)

- One question per phase. Don't ask product+avatar+mode upfront.

### Workflow — quick ad video

1. **Get product.**
   - URL → `hf marketing-studio products fetch --url <url> --wait` (polls until import done)
   - Local images → `hf upload create <photo>...` then `hf marketing-studio products create --title "..." --image <id>...`
   Capture product id.
2. **Pick avatar.**
   - Default: `hf marketing-studio avatars list` and pick a preset matching the brand voice.
   - Custom: `hf marketing-studio avatars create --name "..." --image <upload_id>`.
3. **Pick mode.** Common: `ugc`, `ugc_unboxing`, `product_showcase`, `tv_spot`. See `references/marketing-modes.md`.
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

### Workflow — marketing image

Same as above but use `marketing_studio_image` model:

```bash
hf generate create marketing_studio_image \
  --prompt "..." \
  --aspect_ratio 1:1 \
  --resolution 2k
```

## Errors

- `Missing required params: prompt` → user gave no prompt; ask for it.
- `Invalid values: aspect_ratio=99:99 (allowed: ...)` → bad enum; pick from allowed.
- `Unknown params: foo` → schema doesn't accept that flag; check `hf model get <jst>`.
- `Session expired` → `hf auth login`.

See `references/troubleshooting.md` for more.

## Reference docs

Load on demand:

- `references/model-catalog.md` — picking the right model for the task
- `references/prompt-engineering.md` — writing prompts that work
- `references/media-inputs.md` — image/video reference flows
- `references/troubleshooting.md` — common errors and fixes
- `references/marketing-avatars.md` — preset vs custom avatars
- `references/marketing-products.md` — URL fetch vs manual product create
- `references/marketing-modes.md` — every Marketing Studio mode
