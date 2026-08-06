# Media Inputs

How to pass reference images, videos, audio, and videos for analysis.

**Which media a given model accepts is live schema data.** This file explains what each media
role *means* and how to react when one is rejected. It deliberately does not list per-model
role tables — those went stale between every release. Read the truth off the model:

```bash
higgsfield model get <resolved_id> --json | jq '.medias'
```

Do that once after resolving a role (see `model-catalog.md`) and before building the command.

## Path or UUID — both work

Each media flag accepts either a local file path or a UUID. The CLI auto-uploads paths before submission and auto-detects whether a UUID is an upload id (from `higgsfield upload create`) or a previous job id.

```bash
MODEL=$(higgsfield model recommend --role character-image --json | jq -r '.id')

# Local path — CLI uploads automatically
higgsfield generate create "$MODEL" --prompt "stylize in watercolor" --image ./photo.png --wait

# Upload id (from higgsfield upload create)
higgsfield generate create "$MODEL" --prompt "..." --image <upload_id> --wait

# Job id from a previous generation — chain one result into the next
VIDEO=$(higgsfield model recommend --role default-video --json | jq -r '.id')
higgsfield generate create "$VIDEO" --prompt "anim" --start-image <previous_job_id> --wait

# Video analysis — CLI uploads the file, Virality Predictor returns a text score/report plus
# an Open report link. The output is text, but the task is still video analysis.
higgsfield generate create brain_activity --video ./ad.mp4 --wait
```

Type auto-detected from extension:

- Image: `png`, `jpg`/`jpeg`, `webp`, `gif`
- Video: `mp4`, `mov`, `webm`
- Audio: `mp3`, `wav`, `m4a`, `ogg`

## What each media role means

A model declares a closed set of roles. The role says what the model *does* with the file, and
that meaning is stable even as models come and go.

| Role | Flag | What the model does with it |
|---|---|---|
| `image` | `--image` | Looks at it as a subject/style reference, or edits it. On a video model that declares only `image`, the CLI remaps it to `start_image` when unambiguous. |
| `start_image` | `--start-image` | Uses it as the video's **first frame**. This is what you want for ordinary image-to-video. |
| `end_image` | `--end-image` | Uses it as the **last frame** and interpolates toward it. Pair with `start_image` for a controlled transition. |
| `video` | `--video` | Either a motion/style reference for generation, or the clip being analyzed. |
| `audio` | `--audio` | Reference audio to match — lipsync or soundtrack. This is a *reference*, not a request to synthesize audio. |
| `*_references` | `--image-references`, `--video-references`, `--audio-references` | An **array** slot rather than a single fixed role. Repeat the flag. `--image`/`--video`/`--audio` are short aliases when the schema exposes the array param. |

Two distinctions that cause most misroutes:

- **`audio` role ≠ audio generation.** Passing `--audio` supplies a clip for the model to match.
  Creating a sound from a text prompt is `role:default-audio` — a separate job. Some models also
  expose a `--generate-audio` boolean; that is a *parameter*, not a media role, and most models
  do not declare it. Check `parameters` before using it.
- **Single-reference vs array.** A model declaring `start_image` usually takes exactly one; a
  model declaring `image_references` takes many. Passing extras to a single-reference model
  fails locally before submission with `Model accepts only one image reference`.

## Multiple images

Where the schema allows several references, repeat the flag:

```bash
MODEL=$(higgsfield model recommend --role character-image --json | jq -r '.id')
higgsfield generate create "$MODEL" --prompt "..." \
  --image ./a.png --image ./b.png --image <upload_id> \
  --wait
```

How many are accepted is per-model (and per-role — an array cap can shrink when a video
reference is also attached). Read the cap from `.medias` rather than assuming; the CLI enforces
it locally, so an over-cap call fails fast and costs nothing.

3D asset generation with `multi_image_to_3d` accepts 1–4 images. Repeat `--image` for front/side/back/detail views:

```bash
higgsfield generate create multi_image_to_3d \
  --image ./front.png --image ./side.png --image ./back.png \
  --should_texture true \
  --wait
```

## Audio reference on a video model

Some video models accept an audio reference for lipsync / soundtrack matching, via the `audio`
media role. Confirm the role exists on the resolved model first:

```bash
MODEL=$(higgsfield model recommend --role default-video --json | jq -r '.id')
higgsfield model get "$MODEL" --json | jq '.medias'   # look for an "audio" role

higgsfield generate create "$MODEL" \
  --prompt "person speaking" \
  --start-image ./headshot.png \
  --audio ./voice.mp3 \
  --wait
```

If `.medias` has no `audio` role, the model cannot take reference audio at all — generate the
audio separately rather than trying `--generate-audio`, which most video models do not declare.

## Generating audio from text

That is a generation job, not a media input. Resolve the audio role:

```bash
AUDIO=$(higgsfield model recommend --role default-audio --json | jq -r '.id')

higgsfield generate create "$AUDIO" --prompt "glass breaking in a large hall" --wait

# Optional references, when the user supplies them
higgsfield generate create "$AUDIO" --prompt "same voice, calmer delivery" \
  --audio-references ./voice.wav --wait
```

Reference slots on audio models can be mutually exclusive (audio references *or* image
references, not both) and some audio models take no media at all. Check `.medias` first. For
spoken narration use `role:voiceover-audio` instead. Specialist and legacy music/SFX models
exist for users who name them — find them with `higgsfield model list --audio --json`.

## Schema mismatches

The CLI returns specific error messages for known shape mismatches. All four are resolved the
same way: read the live schema, then rebuild the command.

- `Model accepts only --image (no roles)` — the model uses the legacy `input_images` shape, not `medias` with roles. Drop role-prefixed flags and use plain `--image`.
- `Model does not accept media inputs` — the model is prompt-only. Drop all media flags. Prompt-only is a per-model fact and some models are prompt-only in only *some* configurations, so verify with `.medias` rather than memorizing a list.
- `Unknown media role "<role>"` — the role isn't in this model's media schema. Check accepted roles and `*_references` params.
- `Model accepts only one image reference` — single-reference model, caught locally. Pass one.
- `Missing required params: medias` for `brain_activity` — pass exactly one clip with `--video <path-or-id>`.

## Seeing what a model accepts

```bash
higgsfield model get <resolved_id> --json | jq '{aspect_ratios, durations, parameters, medias}'
```

Returns the full schema: aspect ratios (closed enum or open), durations (closed list or `min/max` range), parameters (with descriptions and defaults), and media roles per slot. This one command answers every "does model X take Y?" question in this file.
