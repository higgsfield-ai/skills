# Model Catalog

Live catalog: `hf model list` for the actual list. This file is intent → model mapping for picking the right one.

## By intent

### Photorealistic image, single shot
- `nano_banana_2` — Nano Banana Pro. Strong default. Accepts `--image` for ref.
- `nano_banana_flash` — faster, cheaper, slightly lower fidelity.
- `flux_2` — Flux 2 (pro/flex/max). Strong adherence to prompt.
- `seedream_v4_5` — Seedream 4.5. Photorealistic, multiple aspect ratios.
- `gpt_image_2` / `imagegen_2_0` — GPT Image 2. High fidelity, slow, expensive.
- `openai_hazel` — OpenAI Hazel. Quality knob low/medium/high.
- `grok_image` — Grok Image, std/pro modes.

### Image with user's face
- `text2image_soul_v2` — Soul V2. Requires `--custom_reference_id` from a trained Soul.
- `soul_cinematic` — Soul Cinematic, more dramatic look.

### Identity / scene
- `soul_location` — generate Soul Locations (no face, only env).
- `image_auto` — Higgsfield's auto-routed image gen.

### Video, generic
- `veo3_1` — Google Veo 3.1, with quality tiers basic/high/ultra.
- `veo3_1_lite` — lite variant.
- `veo3` — Veo 3.0. Requires `--input_image`.
- `kling3_0` — Kling 3.0, std/pro mode. Strong image-to-video.
- `kling2_6` — Kling 2.6. Lipsync support.
- `seedance_2_0` — Seedance 2.0. Genre tags (action/horror/comedy/...).
- `seedance1_5` — Seedance 1.5 Pro.
- `wan2_6` — Wan 2.6.
- `wan2_7` — Wan 2.7.
- `grok_video` — Grok Video.
- `minimax_hailuo` — Minimax Hailuo. Multiple model variants.

### Cinematic
- `cinematic_studio_3_0` — Cinematic Studio 3.0.
- `cinematic_studio_video` / `cinematic_studio_video_v2` — earlier variants.
- `cinematic_studio_2_5` — Cinematic Studio 2.5 (image).

### Marketing-only (use higgsfield-marketing skill)
- `marketing_studio_image`
- `marketing_studio_video`

### Special
- `soul_cast` — multi-character cast assembly.
- `z_image` — text-only image gen, no inputs.

## Picking flow

1. Image or video? → narrow.
2. User's face? → Soul models or `--image` ref.
3. Quality vs speed? → flash/lite vs pro/ultra.
4. Specific brand requested? → match name.

When in doubt: image → `nano_banana_2`, video → `kling3_0` (with `--start-image`) or `veo3_1`.
