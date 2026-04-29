# Media Inputs

How to pass reference images, videos, audio.

## Upload first

Local file → `hf upload create <path>` returns an ID. Use that ID with media flags.

```bash
ID=$(hf upload create photo.png)
hf generate create nano_banana_2 --prompt "stylize in watercolor" --image $ID
```

Type auto-detected from extension. Supported: png/jpg/jpeg/webp/gif (image), mp4/mov/webm (video), mp3/wav/m4a/ogg (audio).

## Job IDs work too

The CLI auto-detects whether an ID is an upload or a previous-job result. Pass either:

```bash
hf generate create kling3_0 --prompt "anim" --start-image <upload_id>
hf generate create kling3_0 --prompt "anim" --start-image <previous_job_id>
```

## Roles for image-to-video

- `--image` — generic image reference (most image models)
- `--start-image` — first frame for video models (kling3_0, seedance, etc.)
- `--end-image` — last frame, for transition models

For simple image-to-video, `--start-image` is what you want.

## Multiple images

Most image models accept up to 8 references via repeated `--image`:

```bash
hf generate create nano_banana_2 --prompt "..." --image $A --image $B --image $C
```

Single-image models (`veo3`, `veo3_1`, `kling2_6`) reject multiple — CLI errors locally before submission.

## Schema mismatches

If the CLI says "Model accepts only --image (no roles)" — the model uses `input_images` shape, not `medias`. Drop role-prefixed flags.

If it says "Model does not accept media inputs" — model is text-only (z_image, soul_location, soul_cast, wan2_6).
