---
version: 0.12.0
name: higgsfield-generate
description: |
  Generate images/videos/3D assets/audio via Higgsfield AI.
  Picks the model by resolving a live role from the CLI catalog
  (default-image, character-image, default-video, marketing-video,
  default-audio) instead of a hardcoded model name.
  Use when: "generate an image", "make a video", "animate
  this photo", "image-to-video", "edit/stylize/remix this
  image", "reframe this video", "edit this video from a
  sketch", "create a 3D model/GLB", "create a sound effect",
  "make music", "text-to-audio", "create an ad", "make a UGC
  video", "unboxing", "presenter video", "import product from
  URL", or "analyze video virality". Supports generic generation,
  workflows, Marketing Studio, and Virality Predictor.
  Chain with higgsfield-soul-id for face/identity consistency.
  NOT for: Soul training, brand systems/brandbooks (use
  higgsfield-brandkit), photoshoots, cards, YouTube thumbnails
  (use higgsfield-youtube-thumbnail), explainers (use
  higgsfield-video-explainer), playable games/assets (use
  higgsfield-game-generation), or TTS.
argument-hint: "[prompt-or-analysis-request] [--model <name>] [--image|--video <path-or-id>]"
allowed-tools: Bash
models:
  pinned:
    - id: brain_activity
      reason: Virality Predictor is a named product feature with no substitute model
    - id: multi_image_to_3d
      reason: only model that returns a 3D mesh/GLB; no role has a second candidate
    - id: marketing_studio_video
      reason: Marketing Studio's avatars/product_ids/hook_id flag contract is unique to it
    - id: marketing_studio_image
      reason: Marketing Studio's avatars/product_ids flag contract is unique to it
---

# Higgsfield Generate

Submit jobs to any Higgsfield model. Wraps the `higgsfield` CLI. Covers generic image/video/3D/audio generation, Marketing Studio (branded ads, avatars, products, hooks, settings), and, secondarily, Virality Predictor video scoring.

## Step 0 — Bootstrap

Before any other command:

1. If `higgsfield` is not on `$PATH`, install it:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. If `higgsfield account status` fails with `Session expired` / `Not authenticated`, ask the user to run `higgsfield auth login` (interactive) and wait for confirmation.


## UX Rules

1. Be concise. No raw IDs, no JSON dumps in chat. Print the media URL for generated assets, or the text summary for Virality Predictor.
2. No internal jargon. Don't narrate "calling higgsfield cost", "polling job".
3. Detect the user's language from the first message and reply in it. Technical args (`--aspect_ratio 16:9`) stay English.
4. Don't batch-ask. Resolve the default role for the intent and ask one thing at a time only if genuinely missing.
5. Don't pre-estimate cost or optimize for cheaper models unless the user asks. Prefer the quality default first — `fast-video` is opt-in, never an unprompted downgrade.
6. Pass `--wait` to `generate create` so the command blocks until done and prints the result URL itself. Avoid the two-step `create` → `wait` pattern.
7. Name the resolved model, not the role, when you tell the user what ran. Roles are internal plumbing; the user is billed for a specific model.

## Discovery guardrail

When looking for a Higgsfield feature/model, do not rely only on semantic search or CLI `--help`. First run an unfiltered model list, then inspect likely `job_set_type` names. If the user says a model exists but search returns no results, trust that signal and verify with the full model list before answering.

The catalog is per-credential, so "I don't see it" is never proof a model does not exist and a thin catalog is not an error. `higgsfield model roles` lists resolvable roles; `higgsfield model list --role <role>` lists one role's candidates, best first — use it when the user wants to choose rather than have you pick.

Workflows are separate from models. Discover them with `higgsfield workflow list` and inspect params with `higgsfield workflow get <workflow_name>`.

Virality Predictor is exposed as:

- Customer-facing name: Virality Predictor
- Technical `job_set_type`: `brain_activity`
- Category/output: text report. This is video-in/text-out analysis, not a text/chat generation model.
- Input: uploaded video
- Purpose: finished-video hook, attention, retention, and virality analysis

If the user says "analyze this video", "score this ad", "evaluate the hook", or similar, route to `brain_activity` even though it appears under text/analysis models. Classify by task intent and required input, not by output category alone.

## Workflow — generic generation

1. **Pick a role, then resolve it to a model.** Never hardcode a model name and never pass a
   role name to `generate create`. The roles, and the intent that selects each, are tabulated
   in `references/model-catalog.md` — read it whenever the intent is not one of these:

   - **image** → `default-image` · `text-render-image` · `character-image` ·
     `identity-edit-image` · `logo-vector-image` · `marketing-image`
   - **video** → `default-video` · `cinematic-video` · `fast-video` · `marketing-video`
   - **audio** → `default-audio` · `voiceover-audio`

   `default-*` is the answer unless a more specific role clearly matches. `fast-video` is
   opt-in only — the user must actually ask for cheaper or faster.

   Resolve live — three rungs, fall through silently, never report a failure:

   ```bash
   ROLE=default-video
   MODEL=$(higgsfield model recommend --role "$ROLE" --json | jq -r '.id // empty')
   # Older CLI without --role: the role tags still ship in the catalog, so filter locally.
   [ -n "$MODEL" ] || MODEL=$(higgsfield model list --json \
     | jq -r --arg r "role:$ROLE" 'map(select((.tags // []) | index($r))) | .[0].id // empty')
   # Still empty → documented fallback from references/model-catalog.md.
   ```

   **`references/model-catalog.md` is the single source of truth** for the full intent→role
   tables, the fallback literals, the capabilities that are not roles, and the specialist
   looks. Read it when the intent is not obvious; do not re-document it here.

   **Route to another skill instead** when the request is: a brand product visual, Pinterest
   pin, lifestyle or hero banner, ad pack, virtual try-on → `higgsfield-product-photoshoot` ·
   a complete brand identity, logo system, palette, brandbook → `higgsfield-brandkit` · a
   YouTube thumbnail, Shorts or Instagram cover → `higgsfield-youtube-thumbnail` · a narrated
   explainer → `higgsfield-video-explainer` · a playable game or game-wide asset system →
   `higgsfield-game-generation`.

   **Named features, not roles** — no substitute exists, so call them by id: Virality Predictor
   (`brain_activity`, video in / text report out) · `multi_image_to_3d` (1–4 reference images →
   mesh/GLB; a merely 3D-*looking* picture is an image job) · `draw_to_video` and `reframe`,
   which are **workflows** rather than models (see `references/workflows.md`).

   When the user names a specific model, use it — verify it resolves first.

2. **Pass media inputs straight to flags.** Media flags accept a local file path **or** a UUID. CLI auto-uploads paths and auto-detects job vs upload for UUIDs. No need to pre-upload. Each model declares accepted media roles or `*_references` params — see `references/media-inputs.md`.
3. **Validate quickly.** If unsure of params, run `higgsfield model get <jst> --json` once and pass only what's needed. Validate the preferred model before falling back to an older one. Use schema defaults otherwise. The server returns `adjustments` for non-fatal coercions (e.g. `aspect_ratio=99:99` → closest match) and a structured error for invalid declared-param values.
4. **Submit and wait in one shot.** `higgsfield generate create <jst> [--prompt "..."] [media flags] [param flags] --wait`. Blocks until terminal status and prints the result on stdout. Tunables: `--wait-timeout 20m` (default 10m), `--wait-interval 5s` (default 3s). Virality Predictor does not need a prompt; pass `--video`.
5. **Deliver.** For generated media and 3D assets, send the primary result URL plus a one-line summary (model, duration if video; GLB/asset URL for 3D). For Virality Predictor, deliver the scores, business interpretation, and the Open report link. Do not surface Virality Predictor `.glb`, `.bin`, or region-table internals in normal chat output.

To inspect or rerun later, `higgsfield generate list --json` and `higgsfield generate get <id> --json` work for retrospection. `higgsfield generate wait <id>` is still available if you ever need to rejoin a job started without `--wait`.

For workflow jobs, use `higgsfield generate workflow <workflow_name> ... --wait`. Cost syntax is `higgsfield generate cost workflow <workflow_name> ...`. See `references/workflows.md`.

## Media flags

| Flag | Media role | Purpose |
|---|---|---|
| `--image <path-or-id>` | `image` | a reference the model looks at — subject, style, or the thing to edit |
| `--start-image <path-or-id>` | `start_image` | first frame of a generated video |
| `--end-image <path-or-id>` | `end_image` | last frame; the model interpolates toward it |
| `--video <path-or-id>` | `video` | a video to reference, or the clip to analyze |
| `--audio <path-or-id>` | `audio` | reference audio for lipsync / soundtrack match |

**Which flags a given model accepts is live schema data, not a fact to memorize** — read it off
the resolved model with `higgsfield model get <resolved_id> --json | jq '.medias'`.

For reference-array models, the explicit flags are `--image-references`, `--video-references`, and `--audio-references`; `--image`, `--video`, and `--audio` are short aliases when the schema exposes those params.

Each flag accepts either a local file path (auto-uploaded) or a UUID (upload id from `higgsfield upload create`, or a previous job id). See `references/media-inputs.md` for what each role means and how to handle rejections.

## Common params

Param flags pass straight through to the resolved model's schema, so discover them with
`higgsfield model get <resolved_id>` rather than assuming. Every generation is the same two
steps — resolve `$MODEL` (step 1), then submit. Only the role and the flags change:

```bash
higgsfield generate create "$MODEL" --prompt "neon city at dusk" --aspect_ratio 16:9 --wait
```

| Intent | Role | Adds |
|---|---|---|
| General image | `default-image` | — |
| Packaging, banner, UI with readable text | `text-render-image` | — |
| Character / cartoon from a reference | `character-image` | `--image ./ref.png` |
| Stills from a trained Soul Character | `character-image` | `--soul-id <soul_ref_id>` — verify the resolved model is Soul-aware first, see `references/model-catalog.md` row 6b |
| Image-to-video | `default-video` | `--start-image ./first.png` |
| Sound, ambience, music bed | `default-audio` | — |
| Spoken narration | `voiceover-audio` | — |

Named features are called by id, since they have no substitute:

```bash
higgsfield generate create multi_image_to_3d --image ./front.png --image ./side.png --should_texture true --wait
higgsfield generate create brain_activity --video ./ad.mp4 --wait
```

Note that nothing above hardcodes a duration, resolution, or quality tier. Those enums are
per-model and change per release — add them only after reading the resolved model's schema, or
omit them and let the schema defaults apply. When the user asks for a specific duration or
resolution, check it is accepted before submitting; the CLI clamps to the nearest allowed
value and reports an `adjustments` map rather than failing.

For machine-readable output (chained pipelines, agent context), add `--json`. With `--wait --json` you get the final job object array. Without `--wait`, you get the job IDs. Virality Predictor stores raw analysis and render artifacts in the job params, but the default text output should stay to scores plus Open report.

Stdin prompt: `echo "..." | higgsfield generate create "$MODEL" --wait`.

Soul-aware models take `--soul-id <reference_id>` from `higgsfield-soul-id`. Some also expose a
UI-facing `--quality` tier that the backend maps to a resolution and to dimensions derived from
`--aspect_ratio`; others have no quality selector at all. Check `parameters` in
`higgsfield model get` instead of assuming either shape.

## Marketing Studio

Branded image/video gen: avatars + products + optional setup hooks/settings + ad-style modes. Use models `marketing_studio_video` and `marketing_studio_image` — these are what `role:marketing-video` and `role:marketing-image` resolve to, and they are named by id here because this whole section documents their specific flag contract (`--avatars`, `--product_ids`, `--hook_id`), which no other model shares.

### Concepts

- **Avatar** — presenter face. Curated `preset` (browse `higgsfield marketing-studio avatars list`) or `custom` (uploaded photos via `higgsfield marketing-studio avatars create`). For UGC modes, an avatar is optional if the brief clearly mentions a person; the backend can create a Soul Character automatically. Pass an avatar when the user wants a specific presenter.
- **Product** — brand item with title + reference images. Imported from URL (`higgsfield marketing-studio products fetch --url ...`) or created from uploaded images (`higgsfield marketing-studio products create`).
- **Webproduct** — App Store / web page version. Auto-routes when fetching App Store URLs.
- **Hook** — reusable opening angle / ad hook. Browse with `higgsfield marketing-studio hooks list`. Hook text is prepended to the user's prompt; it does not replace `--prompt`.
- **Setting** — reusable environment / scene context. Browse with `higgsfield marketing-studio settings list`.
- **Ad reference** — reusable inspiration video that can be bound to an avatar and/or product. Created from an uploaded video (`--video-input <upload_id>`) or a previous generation job (`--job <job_id>`). Browse with `higgsfield marketing-studio ad-references list`. See `references/marketing-ad-references.md`.
- **Brand kit** — captures a brand's identity (name, logo, hero images, colours, fonts, tone) for reuse across image generations. Created by handing in a website URL (`higgsfield marketing-studio brand-kits fetch --url https://… --wait`). See `references/marketing-brand-kits.md`.
- **Ad format** — presets that drives the visual structure of a generated image (`headline`, `bullet-points`, etc.). Read-only, browse with `higgsfield marketing-studio ad-formats list`. Required input for `dtc-ads generate`.

### Discovery commands

Use these exact list commands when the user asks what already exists:

```bash
higgsfield marketing-studio avatars list --json
higgsfield marketing-studio products list --json
higgsfield marketing-studio hooks list --json
higgsfield marketing-studio settings list --json
higgsfield marketing-studio ad-references list --json
higgsfield marketing-studio brand-kits list --json
higgsfield marketing-studio ad-formats list --json
```

`--hook_id` and `--setting_id` are supported by `marketing_studio_video` only; do not pass them to `marketing_studio_image`.

### UX rules (additional)

- One question per phase. Don't ask product+avatar+mode upfront.
- **Two ad approaches are mutually exclusive.** Either the user gives an ad reference video (reference-driven) **or** picks hook/setting blocks (composed-from-blocks) — never both. If the user has an ad reference selected, do not offer hook/setting; if hook/setting are picked, do not offer to attach an ad reference.
- **Ad reference source.** The only valid inputs are a local video file (uploaded via `higgsfield upload create ... --video`) or a prior video job. If the user provides anything else, ask for a local file.
- **`dtc-ads` ad format is mandatory.** Always ask the user to pick from `ad-formats list`. There is no auto-default — both the CLI and server reject calls without `--format-id`.
- **`dtc-ads` optional inputs.** Suggest avatars, products, and reference media when the brief calls for them; only attach what the user picks.

### Workflow — quick ad video

1. **Get product.**
   - Existing product → `higgsfield marketing-studio products list --json`
   - URL → `higgsfield marketing-studio products fetch --url <url> --wait` (polls until import done)
   - Local images → `higgsfield upload create <photo>...` then `higgsfield marketing-studio products create --title "..." --image <id>...`
   Capture product id. When using `--hook_id`, strongly prefer passing `--product_ids`; hooks are designed to pivot into a product and work poorly without product context.
2. **Pick avatar if needed.**
   - Default: `higgsfield marketing-studio avatars list` and pick a preset matching the brand voice.
   - Custom: `higgsfield marketing-studio avatars create --name "..." --image <upload_id>`.
   For UGC modes, you may omit `--avatars` when no specific presenter is required and the brief mentions a person; the backend can synthesize a Soul Character.
3. **Optionally pick setup items.**
   - Hook: `higgsfield marketing-studio hooks list --json`
   - Setting: `higgsfield marketing-studio settings list --json`
   Pass selected IDs as `--hook_id <hook_id>` and `--setting_id <setting_id>` for `marketing_studio_video` only. Do not copy the hook's prompt into `--prompt` unless the user explicitly wants to reinforce the same wording.
4. **Pick mode if needed.** Default is `ugc`; `--mode` is not required just because `--hook_id` is present. Other current slugs: `ugc_how_to`, `ugc_unboxing`, `product_showcase`, `product_review`, `tv_spot`, `wild_card`, `ugc_virtual_try_on`, `virtual_try_on`. **Hook/setting are valid only for `ugc`, `ugc_how_to`, `ugc_unboxing`, `product_review`, `ugc_virtual_try_on`** — do not pass `--hook_id` / `--setting_id` with the other modes. See `references/marketing-modes.md`.
5. **Generate (one-shot).**
   ```bash
   PRODUCT_IDS_JSON=$(mktemp)
   AVATARS_JSON=$(mktemp)
   printf '["<product_id>"]' > "$PRODUCT_IDS_JSON"
   printf '[{"id":"<avatar_id>","type":"preset"}]' > "$AVATARS_JSON"

   higgsfield generate create marketing_studio_video \
     --prompt "..." \
     --avatars @"$AVATARS_JSON" \
     --product_ids @"$PRODUCT_IDS_JSON" \
     --mode ugc \
     --duration 15 \
     --resolution 720p \
     --aspect_ratio 9:16 \
     --wait
   ```
   Add `--hook_id <hook_id>` and/or `--setting_id <setting_id>` when a setup hook/setting was selected.
   `product_ids` and `avatars` are JSON arrays; pass them via `@/path/to/file.json`. Do not pass a bare UUID to `--product_ids`.
   Read the accepted `resolution` and `aspect_ratio` sets off `higgsfield model get marketing_studio_video --json` rather than assuming them. `--generate-audio true` is supported here; on plain video models audio is a media *reference* role instead, so check `medias` before reaching for the flag. `--wait` blocks until done; bump `--wait-timeout 30m` for longer ad runs.
6. **Deliver.** URL + one-line summary (mode, duration).

### Click-to-Ad shortcut (URL-driven)

When the user gives a product URL and wants a marketing video in one go:

```bash
# 1. Trigger fetch (returns the product id, import runs in the background)
higgsfield marketing-studio products fetch --url https://shop.example.com/sneakers --wait

# 2. Generate the marketing video against the same URL — backend reuses the entity
higgsfield generate create marketing_studio_video \
  --url https://shop.example.com/sneakers \
  --mode ugc \
  --duration 15 \
  --aspect_ratio 9:16 \
  --wait
```

Backend dedupes by URL, so repeated runs reuse the existing entity instead of re-fetching.

### Workflow — marketing image

Same as above but use `marketing_studio_image` model:

```bash
higgsfield generate create marketing_studio_image \
  --prompt "..." \
  --aspect_ratio 1:1 \
  --resolution 2k \
  --wait
```

## Virality Predictor video scoring

Use Virality Predictor (`brain_activity`) when the user wants to evaluate a finished video as a business creative: hook strength, virality potential, attention, retention, or how well the content/product holds focus and minimizes distraction. Treat "Virality Predictor" as the customer-facing feature name; `brain_activity` is only the CLI/job_set_type.

```bash
higgsfield generate create brain_activity --video ./creative.mp4 --wait
```

The result is text, not a generated image/video. Report the overall score, peak hook second, sustain score, strongest/weakest regions, and report URL if present. Interpret it as an objective attention proxy for creative testing: higher Visual/Auditory/Language/Attention scores suggest stronger stimulus and focus; lower Default Mode is better because it suggests less mind-wandering.

The CLI prints an Open report URL like `https://<app-domain>/apps/virality-predictor?resultJobId=<job_id>`. Send that URL for the visual report. Raw artifact URLs such as `brain_example_url`, `vertexMapBinaryUrl`, and `vertexMapUrl` are implementation details; mention them only when the user asks for raw data or implementation details.

Good final shape:

```text
Overall score: 44/100
Peak hook: 49% at 1s
Sustain: 89%
Strongest region: Visual Cortex
Risk: Default Mode is high, which can indicate mind-wandering.

Open report: <report_url>
```

## Errors

- `Missing required params: prompt` → user gave no prompt; ask for it.
- `Missing required params: medias` on `brain_activity` / Virality Predictor → pass exactly one video via `--video <path-or-id>`.
- `Invalid values: aspect_ratio=99:99 (allowed: ...)` → bad enum; pick from allowed.
- `Unknown params: foo` → schema doesn't accept that flag; check `higgsfield model get <jst>`. If this happens for `hook_id` or `setting_id`, the selected model/job_set_type does not support Marketing Studio setup items.
- `Session expired` → `higgsfield auth login`.

See `references/troubleshooting.md` for more.

## Reference docs

Load on demand:

- `references/model-catalog.md` — **the single source of truth for model choice**: intent→role tables, how to resolve a role live, and the one fallback table
- `references/workflows.md` — `draw_to_video` and `reframe` workflow generation
- `references/prompt-engineering.md` — writing prompts that work
- `references/media-inputs.md` — image/video/audio reference flows and Virality Predictor video analysis
- `references/troubleshooting.md` — common errors and fixes
- `references/marketing-avatars.md` — preset vs custom avatars
- `references/marketing-products.md` — URL fetch vs manual product create
- `references/marketing-setup-items.md` — hooks/settings discovery and usage
- `references/marketing-ad-references.md` — ad reference videos (create/list/get)
- `references/marketing-brand-kits.md` — brand kits (fetch from URL, list, get)
- `references/marketing-dtc-ads.md` — DTC Ads Engine (`dtc-ads generate`)
- `references/marketing-modes.md` — every Marketing Studio mode
