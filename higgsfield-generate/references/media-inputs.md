# Media Inputs

How to pass reference images, videos, audio, and videos for analysis. Mirrored from MCP server media-handling logic.

## Path or UUID — both work

Each media flag accepts either a local file path or a UUID. The CLI auto-uploads paths before submission and auto-detects whether a UUID is an upload id (from `higgsfield upload create`) or a previous job id.

```bash
# Local path — CLI uploads automatically
higgsfield generate create nano_banana_2 --prompt "stylize in watercolor" --image ./photo.png --wait

# Upload id (from higgsfield upload create)
higgsfield generate create nano_banana_2 --prompt "..." --image <upload_id> --wait

# Job id from a previous generation
higgsfield generate create seedance_2_0 --prompt "anim" --start-image <previous_job_id> --wait

# Video analysis — CLI uploads the file, Virality Predictor returns a text score/report plus an Open report link.
# The output is text, but the task is still video analysis.
higgsfield generate create brain_activity --video ./ad.mp4 --wait
```

Type auto-detected from extension:

- Image: `png`, `jpg`/`jpeg`, `webp`, `gif`
- Video: `mp4`, `mov`, `webm`
- Audio: `mp3`, `wav`, `m4a`, `ogg`

## Roles by model family

Each model declares a closed set of accepted roles or `*_references` params. Pass the right flag; the CLI rejects unknown media locally before submission.

| Model | Accepted roles | Notes |
|---|---|---|
| Most image models (`nano_banana_2`, `flux_2`, `seedream_v4_5`, `gpt_image_2`, …) | `image` | 1+ references, often up to 8. |
| `nano_banana_2_lite` | `image_references` | Up to 14 image references. Use repeated `--image-references` or short alias `--image`; `aspect_ratio=auto` requires at least one reference. |
| `gemini_omni` | `image_references`, `video_references` | Fast reference-to-video. Use repeated `--image-references`/`--video-references` or aliases `--image`/`--video`. Max 1 video reference; max 7 image references, or max 5 when a video reference is included. |
| `seedance_2_0` | `image`, `start_image`, `end_image`, `video`, `audio` | Audio is via `medias` (role `audio`), NOT via `--generate-audio`. |
| `brain_activity` | `video` | Virality Predictor analyzes one uploaded clip and returns a text score report plus an Open report link; no prompt required. Treat "analyze this video" / "score this ad" as this video-analysis flow even though the output is text. Raw `.glb` and `.bin` artifacts stay in JSON/debug output, not normal chat output. |
| `grok_video_v15` | `start_image` | Required single start frame. CLI also accepts `--image` and maps it to `start_image`. |
| `kling3_0` | `start_image`, `end_image` | Image-to-video with optional last-frame transition. |
| `kling3_0_turbo` | `start_image` | Fast text-to-video or single start-frame animation. Max 1 reference; CLI also accepts `--image` and maps it to `start_image`. |
| `kling2_6` | `start_image` | Single frame anchor. |
| `veo3_1` | `start_image` | Max 1 reference. |
| `veo3` | `image` | Single image-to-video. |
| `marketing_studio_video` | `image`, `start_image`, `end_image` | Plus `avatars`, `product_ids`, `assets` as separate fields. |
| `multi_image_to_3d` | `image` | 1–4 object/product reference images. Returns a 3D asset rather than an image/video. |
| `seed_audio` | `audio_references` or `image_references` | Default text-to-audio model. Requires `--prompt`; optional references use repeated `--audio-references`/`--image-references` (short aliases: `--audio`/`--image`). Audio and image references are mutually exclusive. |
| `mirelo_text_to_audio` | (none) | Text-to-audio / SFX generation. Pass `--prompt` and `--duration`; do not pass media inputs. |
| `sonilo_music` | (none) | Text-to-music generation. Pass `--prompt` and `--duration`; do not pass media inputs. |
| `z_image`, `recraft_v4_1`, `soul_cast`, `soul_location` | (none) | Prompt-only. Reject media inputs. |

For simple image-to-video on a video model that only declares `image` (e.g. `veo3`), plain `--image` is auto-remapped to `start_image` by the CLI when unambiguous. When in doubt:

```bash
higgsfield model get <model_id>   # shows the accepted media roles for this model
```

## Multiple images

Most image models accept multiple references — repeat the `--image` flag:

```bash
higgsfield generate create nano_banana_2 --prompt "..." \
  --image ./a.png --image ./b.png --image <upload_id> \
  --wait
```

Single-reference video models (`grok_video_v15`, `veo3`, `veo3_1`, `kling3_0_turbo`, `kling2_6`) reject extra images — the CLI errors locally before submission with `Model accepts only one image reference`.

3D asset generation with `multi_image_to_3d` accepts 1–4 images. Repeat `--image` for front/side/back/detail views:

```bash
higgsfield generate create multi_image_to_3d \
  --image ./front.png --image ./side.png --image ./back.png \
  --should_texture true \
  --wait
```

## Audio reference (Seedance)

`seedance_2_0` is the one model that takes an audio reference for lipsync / soundtrack matching. Pass via `medias` with role `audio`:

```bash
higgsfield generate create seedance_2_0 \
  --prompt "person speaking" \
  --start-image ./headshot.png \
  --audio ./voice.mp3 \
  --duration 8 \
  --wait
```

**Do NOT pass `--generate-audio` to `seedance_2_0`** — the model schema doesn't declare it. Use the audio media role instead.

Seed Audio is the default text-to-audio model. It can run prompt-only, or use optional audio/image references:

```bash
higgsfield generate create seed_audio \
  --prompt "glass breaking in a large hall" \
  --wait

higgsfield generate create seed_audio \
  --prompt "same voice, calmer delivery" \
  --audio-references ./voice.wav \
  --wait
```

Sonilo and Mirelo are specialist/legacy alternatives. Use them only when the user names them or Seed Audio is not appropriate:

```bash
higgsfield generate create sonilo_music \
  --prompt "cinematic synthwave track" \
  --duration 12 \
  --wait

higgsfield generate create mirelo_text_to_audio \
  --prompt "glass breaking in a large hall" \
  --duration 4 \
  --wait
```

## Schema mismatches

The CLI returns specific error messages for known shape mismatches:

- `Model accepts only --image (no roles)` — the model uses the legacy `input_images` shape, not `medias` with roles. Drop role-prefixed flags and use plain `--image`.
- `Model does not accept media inputs` — the model is prompt-only or non-media (`z_image`, `recraft_v4_1`, `mirelo_text_to_audio`, `sonilo_music`, `soul_location`, `soul_cast`, `wan2_6` for some configs). Drop all media flags.
- `Unknown media role "<role>"` — the role isn't in this model's media schema. Run `higgsfield model get <model>` and check accepted media roles or `*_references` params.
- `Missing required params: medias` for `brain_activity` — pass exactly one clip with `--video <path-or-id>`.

## Seeing what a model accepts

```bash
higgsfield model get <model_id> --json | jq '{aspect_ratios, durations, parameters, medias}'
```

Returns the full schema: aspect ratios (closed enum or open), durations (closed list or `min/max` range), parameters (with descriptions and defaults), and media roles per slot.
