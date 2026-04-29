---
version: 0.1.0
name: higgsfield-generate
description: |
  Generate images and videos via Higgsfield AI through 35+ models including
  Nano Banana 2, Soul V2, Veo 3.1, Kling 3.0, Seedance 2.0, Flux 2, GPT Image 2.
  Use when: "generate an image", "make a picture", "create artwork",
  "make a video", "animate this photo", "image-to-video", "img2vid",
  "edit this image with AI", "stylize a photo", "remix this image",
  "produce a clip", "render a scene".
  Supports text-to-image, image-to-image, image-to-video, and reference-based
  generation. Auto-detects whether passed IDs are uploads or previous jobs.
  Chain with higgsfield-soul when the user wants their face in the output.
  NOT for: training Soul Character (use higgsfield-soul), branded
  marketing ads with avatars/products (use higgsfield-marketing),
  text-only / chat / TTS tasks.
argument-hint: "[prompt] [--model <name>] [--image <path-or-id>]"
allowed-tools: Bash
---

# Higgsfield Generate

Submit jobs to any Higgsfield model. Wraps the `hf` CLI.

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

## Workflow

1. **Pick a model.** Use the user's intent to choose. If unclear, default:
   - Image, photorealistic → `nano_banana_2`
   - Image, with user's face → `text2image_soul_v2` (needs Soul ref)
   - Image-to-video → `kling3_0`
   - Generic video → `veo3_1`
   - See `references/model-catalog.md` for the full map.
2. **Resolve media inputs.** If the user provided a local file path, upload it: `hf upload create <path>`. Stash the returned id. If a job id (UUID) is given, pass it as-is — CLI auto-detects job vs upload.
3. **Validate quickly.** If unsure of params, run `hf model get <jst> --json` once and pass only what's needed. Use schema defaults otherwise.
4. **Submit.** `hf generate create <jst> --prompt "..." [media flags] [param flags]`. Capture job id.
5. **Wait.** `hf generate wait <id>` — blocks until terminal, prints result URL on stdout.
6. **Deliver.** Send the URL plus a one-line summary (model, duration if video).

## Media flags (CLI auto-detects upload vs job)

| Flag | Use for |
|---|---|
| `--image <id>` | reference image |
| `--start-image <id>` | first frame for image-to-video transitions |
| `--end-image <id>` | last frame for transitions |
| `--video <id>` | reference video |
| `--audio <id>` | reference audio (lipsync) |

All flags accept both upload IDs (from `hf upload create`) and job IDs (from previous `hf generate create`).

## Common params

Flags pass through to model schema. Use `hf model get <jst>` to discover.

```bash
hf generate create flux_2 --prompt "neon city at dusk" --aspect_ratio 16:9 --resolution 2k
hf generate create kling3_0 --prompt "camera dollies in" --start-image <id> --duration 8
hf generate create text2image_soul_v2 --prompt "..." --custom_reference_id <soul_ref_id>
```

Stdin prompt: `echo "..." | hf generate create z_image`.

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
