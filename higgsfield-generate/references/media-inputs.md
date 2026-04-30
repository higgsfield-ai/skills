# Media Inputs

How to pass reference images, videos, audio.

## Path or UUID — both work

Each media flag accepts either a local file path or a UUID. CLI auto-uploads paths before submission and auto-detects whether a UUID is an upload id or a previous job id.

```bash
# local path — CLI uploads automatically
hf generate create nano_banana_2 --prompt "stylize in watercolor" --image ./photo.png

# upload id (from `hf upload create`)
hf generate create nano_banana_2 --prompt "..." --image <upload_id>

# job id from a previous generation
hf generate create kling3_0 --prompt "anim" --start-image <previous_job_id>
```

Type auto-detected from extension. Supported: png/jpg/jpeg/webp/gif (image), mp4/mov/webm (video), mp3/wav/m4a/ogg (audio).

## Roles for image-to-video

- `--image` — generic image reference (most image models)
- `--start-image` — first frame for video models (kling3_0, seedance, etc.)
- `--end-image` — last frame, for transition models

For simple image-to-video, `--start-image` is what you want. For pure video models, plain `--image` is auto-remapped to `start_image`.

## Multiple images

Most image models accept up to 8 references via repeated `--image`:

```bash
hf generate create nano_banana_2 --prompt "..." --image ./a.png --image ./b.png --image $C_ID
```

Single-image models (`veo3`, `veo3_1`, `kling2_6`) reject multiple — CLI errors locally before submission.

## Schema mismatches

If the CLI says "Model accepts only --image (no roles)" — the model uses `input_images` shape, not `medias`. Drop role-prefixed flags.

If it says "Model does not accept media inputs" — model is text-only (z_image, soul_location, soul_cast, wan2_6).
