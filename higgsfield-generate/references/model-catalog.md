# Model Catalog

The full lineup of generation models available through Higgsfield. Each entry has its own sweet spot — pick the one that matches your brief. For the actual `--model` ID to pass to `higgsfield generate create`, run `higgsfield model list --json` and look up by display name.

Preferred defaults for examples and quick-start guidance in this repo:
- **Images/design/text:** `gpt_image_2_6` (general/high-fidelity) and `nano_banana_flash` (Nano Banana 2, character/cartoon). The id `nano_banana_2` resolves to Nano Banana Pro.
- **Video:** `seedance_2_5` (SOTA all-purpose video).
- **Character/stylized image work:** `text2image_soul_v2`.
- **Ads/UGC/product demos:** `marketing_studio_video` or `marketing_studio_image`.
- **Audio:** `seed_audio` (general text-to-audio, voice-style, SFX, ambience, and music-like audio).
- **Video analysis:** Virality Predictor (`brain_activity`) for attention, hook, retention, and virality scoring. It may appear under text/analysis because the output is a report, but the input and intent are video analysis.

---

## Image models

| Model | Provider | What it's for |
|---|---|---|
| Nano Banana 2 (`nano_banana_flash`) | Google | **Fast everyday default for character work.** Edits, general generation, character / cartoon / animated-style outputs. The reach-for-this model when the brief calls for character or cartoon-style image generation. |
| Nano Banana 2 Lite | Google | **Lightweight Nano Banana 2.** Fast reference-driven image generation and edits when the brief is simple or cost/speed matters more than Pro-level fidelity. Supports up to 14 image references. |
| Nano Banana Pro (`nano_banana_pro`; alias `nano_banana_2`) | Google | **Top-tier Nano Banana.** Same canvas as Nano Banana 2 with extra fidelity and accuracy on harder briefs. Use when the user names it. |
| Nano Banana | Google | Reliable, budget-friendly entry in the Nano Banana family — picks up the same realistic look at a lighter price point. |
| Higgsfield Soul 2.0 | Higgsfield | **Aesthetic UGC, fashion editorial, character generation.** When the brief leans editorial, lifestyle, or "looks like a magazine cover". Soul-aware (accepts a Soul Character reference). Curated styles: `higgsfield preset list soul-v2`, then `--style_id <id>` (not with an image reference). |
| Soul Cinema (`soul_cinematic`) | Higgsfield | **Cinematic stills, film-grade lighting.** The pick when the user asks for "cinematic" or wants concept-art mood. |
| Soul Cinema Studio (`soul_cinema_studio`) | Higgsfield | Cinematic Soul stills with optional `style_id` presets and `enhance_prompt`. A separate model from `soul_cinematic`, with different params. |
| Soul Cast | Higgsfield | **Distinctive, characterful personas.** Use only when the user names it. Text-only (no reference image), `16:9` only. |
| Soul Location | Higgsfield | **Best-in-class environments and locations.** Unmatched for pure scene and place generation without a person in frame. |
| Seedream 5.0 Pro (`seedream_v5_pro`) | Bytedance | **Faces, character sheets, and complex scene edits with faces.** Up to 10 image references, resolution `1k`/`1.5k`/`2k`. |
| Seedream 4.5 | Bytedance | Earlier face-anchored scene-edit model. Use when the user names it. |
| Seedream 5.0 Lite | Bytedance | Same Seedream lineage as 4.5 with faster turnaround for visual-reasoning and instruction-based edits. |
| Z Image | Tongyi-MAI | **Fastest in the catalog.** Built for speed, drafts, and LoRA-driven stylization. The pick when the brief is "fast and cheap, let me iterate". |
| Flux 2.0 | Black Forest Labs | Precise prompt adherence with multiple variants (pro, flex, max). A strong creative alternative when the user wants a different look from the Banana family. |
| Flux Kontext Max | Black Forest Labs | **Context-aware editing and style transfer.** Strong for anime, stylized looks, typography remix — when defaults feel too generic. |
| Kling O1 Image | Kling | Versatile photorealistic image generation with broad aspect-ratio support. |
| GPT Image 1.5 | OpenAI | Earlier-generation OpenAI image model with editing and text-rendering capabilities. |
| GPT Image 2 | OpenAI | High-fidelity image generation and editing. Used by `higgsfield-product-photoshoot` under the hood. |
| GPT Image 2.6 Sunburst (`gpt_image_2_6`) | OpenAI | **Default high-fidelity image generation.** General images, reference-guided editing, design, typography, native animated GIF and SVG output. Raster formats: PNG/JPEG/WebP. SVG takes no references. |
| GPT Image 2.6 Flare (`gpt_image_2_6_flare`) | OpenAI | Separately selectable Flare model with the same format controls. Use when explicitly requested; do not send a `variant` parameter. |
| GPT Image 2.5 (`gpt_image_2_5`) | OpenAI | Earlier image generation and editing model with Flare/Sunburst variants. Use when the user names it; check its live controls separately. |
| Grok Imagine | xAI | Expressive, high-contrast, bold creative outputs. Worth trying for anime and stylized looks. |
| Recraft V4.1 | Recraft | **Clean graphic and vector-style design assets.** Logos, icons, flat illustrations, brand marks, and controlled-palette visuals. Use `model_type=vector` for vector-like output and `standard` for raster-style graphics. |
| Cinema Studio Image 2.5 | Higgsfield | Cinematic still frames up to 4K, dramatic film look. |
| Marketing Studio Image | Higgsfield | **Branded image ads.** Retrieval-augmented over the user's avatars and products — runs inside the Marketing Studio flow. |
| Auto | Higgsfield | **Smart routing layer.** Picks the best image model from the prompt automatically. Use when the user's intent is open and you don't want to commit to a specific model. |

## Video models

| Model | Provider | What it's for |
|---|---|---|
| Gemini Omni Flash | Google | **Fast multimodal reference-to-video.** Use for prompt-guided video generation from image references and optionally one video reference, especially when the brief benefits from Google's Gemini/Veo-style understanding without making it the default over Seedance 2.5. |
| Seedance 2.0 | Bytedance | Video generation up to 4K. Use when native 4K output is required. Native audio on by default (`generate_audio`); modes `std`/`fast` (`fast` is 480p/720p only). |
| Seedance 2.5 | Bytedance | **SOTA all-purpose video; the default for serious motion, cinematic and production briefs.** Supports 4–30s output up to 1080p, reference-driven generation, editing and extension. Modes `t2v` / `omni_reference` / `video_edit` / `video_extension`. |
| Kling 3.0 | Kling | **Lower-cost option** for single-plane scenes that don't need heavy motion. Multi-shot, audio sync, motion transfer. |
| Kling 3.0 Turbo | Kling | **Fast Kling option for simple motion.** Text-to-video and single start-frame animation when the user explicitly wants speed, lower cost, or a quick Kling 3.0 variant. |
| Seedance 1.5 Pro | Bytedance | A budget-friendly Seedance for clean single-take shots. |
| Marketing Studio | Higgsfield | **All advertising and commercial video** — UGC, unboxing, TV spot, product showcase. The default whenever the brief is "make an ad". See `marketing-modes.md`. |
| Cinema Studio 4.0 (`cinematic_studio_video_4_0`) | Higgsfield | **Cinema-grade execution** when the user asks for Cinema Studio. Modes `t2v` / `omni_reference` / `video_edit` / `video_extension`, up to 1080p, camera/lens/light/genre controls. |
| Cinema Studio 3.0 (`cinematic_studio_3_0`) | Higgsfield | Previous Cinema Studio release, up to 4K. Use when the user names it or needs 4K. |
| Veo 3.1 Lite | Google | **Fast and cost-effective Veo.** Built for batch and volume work. |
| Google Veo 3.1 | Google | Ultra-realistic, top-tier cinematic quality. Quality tiers basic/high/ultra. Format set is constrained — verify accepted aspect ratio and duration before submitting. |
| Gemini Omni Flash 1.1 (`gemini_omni_flash_1_1`) | Google | Reference-driven video with native audio. Use `reference-to-video` mode and explicit reference flags; inspect the live schema for other modes. |
| Minimax Hailuo | Hailuo | **Cheap with strong physics.** Solid budget pick when natural-physics motion matters; no audio in current variants. |
| Wan 2.7 | Wan | Synchronized audio with character-consistent video. The newer Wan release. |
| Wan 2.6 | Wan | Open-weight, stylized, experimental creative. Cheap option when the brief is intentionally artistic. |
| Kling 2.6 | Kling | Cinematic motion with advanced physics — earlier Kling release alongside 3.0. |
| Grok Video 1.5 | xAI | **Bold image-to-video from a required reference frame.** Use when the user wants stylized, anime-like, high-contrast, or experimental motion from one starting image. Requires one `--start-image` or `--image`; duration 2–15s; resolution `480p`, `720p`, or `1080p` (`1080p` not with reference media). |
| Grok Imagine (video) | xAI | Text and image-to-video with audio support. Worth trying for stylized creative briefs. |
| Cinema Studio Video | Higgsfield | Cinematic compositions with dramatic mood. Use Cinema Studio 4.0 as the modern default. |
| Cinema Studio Video v2 | Higgsfield | Refined cinematic camera and color with genre control. Use Cinema Studio 4.0 as the modern default. |

Also available but not profiled here — use them when the user names them, and check params with `higgsfield model get <id>` first:

- **Image:** `grok_image_2_0`, `seedream_5_0_flash`, `openai_hazel`.
- **Video:** `minimax_h3`, `minimax_h3_max`, `wan3_0`, `wan3_0_prime`, `seedance_2_0_mini`, `flux_3_video`, `flux_3_video_edit`, `kling_video_edit`, `happy_horse_video`.
- **Audio (TTS):** `inworld_text_to_speech`, `qwen_audio_tts`, `text2speech_v2`.

---

## 3D models

| Model | Provider | What it's for |
|---|---|---|
| Multi-Image to 3D | Meshy | **Create an actual 3D asset from object/product reference images.** Takes 1–4 images and returns a 3D mesh/GLB-style asset. Use repeated `--image`; add `--should_texture true` when texture matters. |

---

## Audio models

| Model | Provider | What it's for |
|---|---|---|
| Seed Audio 1.0 | Bytedance | **Default audio generation.** Use for text-to-audio, sound effects, ambience, foley, impacts, environmental audio, voice-style generations, and music-like audio. Requires `--prompt`; optional references use `--audio-references`/`--image-references`. |
| Sonilo Music | Sonilo | **Generate music from text.** Use for backing tracks, instrumental beds, jingles, and musical moods. Requires `--prompt` and `--duration`; returns audio and does not take media inputs. |
| Mirelo Text to Audio | Mirelo | **Generate non-speech audio from text.** Use for sound effects, ambience, foley, impacts, transitions, and environmental sounds. Requires `--prompt` and `--duration`; returns audio and does not take media inputs. |

---

## Text / analysis models

| Model | Provider | What it's for |
|---|---|---|
| Virality Predictor (`brain_activity`) | Higgsfield | **Objective attention proxy for video creative testing.** Scores how effectively a clip captures and sustains attention, useful for hook validation, virality potential, ad review, and product/content focus. Takes a video input and returns a text report with overall score, peak second, sustain, and an Open report link. Raw `.glb` / `.bin` render artifacts stay in JSON/debug output. |

---

## Picking flow

Match by intent and requested deliverable. Explicit model choices and specialized workflow pins take priority. Otherwise, a standalone animated GIF or SVG uses `gpt_image_2_6` before the subject/style rules below. Set the output format before submitting; do not start a video or conversion pipeline for a native GIF. When the user names a model, keep it for follow-ups and verify its requested format support. Only the models listed under **Auto-pick** are chosen without being asked; every other model is used only when named or when the user explicitly asks for what it offers.

### Image — auto-pick

1. **Brand product visual (Pinterest pin, lifestyle, hero banner, ad pack, virtual try-on, restyle)** → use `higgsfield-product-photoshoot` instead. NOT this skill.
2. **Branded ad image with presenter avatar + product (Marketing Studio shape with RAG over user assets)** → Marketing Studio Image.
3. **Soul Character (reference id from `higgsfield-soul-id`)** → Soul 2.0 for stills; Soul Cinema (`soul_cinematic`) for cinematic vibe.
4. **New original person — UGC creator, influencer, editorial, fashion** → Soul 2.0.
5. **Cinematic still frame** → Soul Cinema (`soul_cinematic`).
6. **Character sheet, one-shot face from reference photos, or face edit on a real photo** → Seedream 5.0 Pro (`seedream_v5_pro`).
7. **Locations / environments / no-people scenes** → Soul Location.
8. **Logo, icon, vector-like illustration, brand mark, controlled-palette graphic** → Recraft V4.1. Use `--model_type vector` for vector-style output.
9. **Cartoon or illustrated characters, heavily textured photos** → Nano Banana 2 (`nano_banana_flash`).
10. **Default for everything else** → GPT Image 2.6. General generation, editing, design, UI, banners, product concepts, anything with on-image text.

### Image — only when asked

- **Cheaper or faster:** Nano Banana 2 Lite (`nano_banana_2_lite`) for quick reference edits; Z Image for fast drafts.
- **Named by the user:** GPT Image 2.6 Flare, GPT Image 2.5, Nano Banana Pro, Soul Cast, Soul Cinema Studio, Seedream 5.0 Lite, Seedream 4.5, Flux 2, Flux Kontext Max, Kling O1 Image, Grok Image, GPT Image 2, Cinema Studio Image 2.5, Auto, and the unprofiled models listed above.

### GPT Image 2.6 formats

Inspect `higgsfield model get gpt_image_2_6 --json` (or `gpt_image_2_6_flare`) for the current controls. Both models accept `--output_format png|jpeg|webp|gif|svg`; omitting it produces PNG. Select the requested format before the first job. An animation description in `--prompt` alone still produces a PNG.

- **Animated GIF:** `--output_format gif`. Optional `--size`, `--frame_count`, and `--frame_duration_ms` control the animation; defaults are `288x288`, 9 frames and 200 ms per frame. Preserve requested values and validate limits against the live schema. References are allowed.
- **SVG:** `--output_format svg`, with no `--image` or `--image-references`. For editing/vectorizing an existing reference, report this restriction and resolve a compatible workflow instead of silently discarding the reference. Deliver the returned SVG URL unchanged; a raster preview is not the SVG file.
- **Flare:** select `gpt_image_2_6_flare` as the model ID, not `--variant flare` on Sunburst or GPT Image 2.5.

```bash
higgsfield generate create gpt_image_2_6 --prompt "A cute cat blinking in a seamless loop" --output_format gif --size 288x288 --frame_count 9 --frame_duration_ms 200 --wait
higgsfield generate create gpt_image_2_6 --prompt "A simple clean vector cat icon" --output_format svg --wait
higgsfield generate create gpt_image_2_6_flare --prompt "A simple clean vector coffee cup icon" --output_format svg --wait
```

Keep explicit MP4/video requests on the video route. Requests to write a GIF/SVG prompt only return text without starting generation. After a successful submission, wait for that job and use its actual result URL; do not create extra variants merely to repair a reply.

### Video — auto-pick

1. **All advertising / commercial video (UGC, unboxing, TV spot, product showcase, branded ad)** → Marketing Studio. See `marketing-modes.md`.
2. **Everything else** → Seedance 2.5 — multi-shot, consistent identity, motion-heavy, image-to-video (`--mode omni_reference --start-image`), editing, extension, 4–30s. Do not downgrade because another model's schema looks simpler.
3. **The user asks for 4K** → Seedance 2.0 (Seedance 2.5 tops out at 1080p). Say why you switched.

### Video — only when asked

- **Cheaper or faster:** Kling 3.0 Turbo, Veo 3.1 Lite, or Seedance 1.5 Pro.
- **Named by the user:** Cinema Studio 4.0, Cinema Studio 3.0, Kling 3.0, Kling 2.6, Veo 3.1, Veo 3, Minimax Hailuo, Wan 2.7, Wan 2.6, Gemini Omni Flash, Grok Video 1.5, Grok Imagine (video), the earlier Cinema Studio Video variants, and the unprofiled models listed above.

### Video analysis — pick this default

1. **Evaluate a finished clip's hook, virality potential, attention, retention, or distraction risk** → Virality Predictor (`brain_activity`). It takes `--video`, needs no prompt, and returns a text score/report plus an Open report link rather than generated media.

### 3D — pick this default

1. **Create an actual 3D mesh/model/GLB from one or more object/product reference images** → Multi-Image to 3D (`multi_image_to_3d`). Pass 1–4 repeated `--image` flags. Use `--should_texture true` for textured assets; use rigging/animation flags only when the user explicitly wants a rigged or animated asset.
2. **Create a picture that merely looks like a 3D render** → use an image model instead, usually GPT Image 2.6 or Nano Banana 2 (`nano_banana_flash`) depending on the brief.

### Audio — pick this default

1. **Default audio generation (text-to-audio, voice-style, SFX, ambience, foley, impacts, environmental audio, or music-like audio)** → Seed Audio 1.0 (`seed_audio`). Requires `--prompt`; use optional `--audio-references`/`--image-references` only when references are provided.
2. **Create music, backing tracks, jingles, or instrumental beds with the specialist legacy music model** → Sonilo Music (`sonilo_music`) only when the user names Sonilo or Seed Audio is not appropriate. Requires `--prompt` and `--duration`.
3. **Create SFX with the specialist legacy SFX model** → Mirelo Text to Audio (`mirelo_text_to_audio`) only when the user names Mirelo or Seed Audio is not appropriate. Requires `--prompt` and `--duration`.
4. **Add soundtrack/audio to a generated video ad** → use Marketing Studio Video with `--generate_audio true`, not Seed Audio/Sonilo/Mirelo.

### Things to keep in mind

- **Don't invent model names.** Run `higgsfield model list` if you're unsure — submitting an unknown model returns `unknown model "..."`.
- **Don't downgrade for schema convenience.** If Seedance 2.5 fits the intent, validate or submit it first; do not choose Seedance 1.5 only because it lists a requested duration more explicitly.
- **Do not misroute video analysis because the output is text.** A request like "analyze this video" or "score this ad" maps to Virality Predictor (`brain_activity`) when the user provides or references a finished video.
- **Do not misroute 3D style into 3D asset generation.** `multi_image_to_3d` is for actual mesh/GLB-style assets from reference images. A prompt like "make a 3D render" is usually image generation.
- **Do not treat audio generation as an audio media input.** `seed_audio`, `mirelo_text_to_audio`, and `sonilo_music` create audio from text. `--audio` is for reference audio on video models like Seedance 2.0 or an alias for `audio_references` on Seed Audio.
- **Audio on Seedance 2.0**: reference audio comes through the media inputs with role `audio`. Native audio generation is a separate `generate_audio` flag, on by default.
- **Prompt-only models reject reference media.** Z Image, Recraft V4.1, Soul Cast, Soul Location, and some Wan configs are prompt-only; pass no media flags to them. Virality Predictor is different: it returns text but requires a video input.
- **Route branded product visuals through `higgsfield-product-photoshoot`** — its prompt enhancer adds 10 mode-specific templates on top of GPT Image 2. Direct GPT Image 2.6 generation here is the right call for everything that isn't a product photoshoot.
- **Cinema Studio ids** (`cinematic_studio_video_4_0`, `cinematic_studio_3_0`) do not appear in `higgsfield model list`; check them with `higgsfield model get <id>`. Prefer 4.0 when the user asks for Cinema Studio without a version.
- **When the user names a specific model, use it.** The auto-picks cover the common intents — the rest of the catalog exists for users who know what they want.

---

## Media role conventions

Each model accepts a fixed set of media roles or `*_references` params. When unsure, run `higgsfield model get <model>` and inspect the schema.

| Model | Accepted media roles |
|---|---|
| Gemini Omni Flash | `image_references` (0–7) and `video_references` (0–1); with a video reference, max 5 image references |
| Nano Banana 2 Lite | `image_references` (0–14); `aspect_ratio=auto` requires at least one image reference |
| Seedance 2.0 | `image`, `start_image`, `end_image`, `video`, `audio` |
| Seedance 2.5 | `start_image`, `end_image`, `image_references`, `video_references`, `audio_references`; use `omni_reference` for reference generation |
| Kling 3.0 | `start_image`, `end_image` |
| Cinema Studio 4.0 | `start_image`, `end_image` (`omni_reference` only), `image_references`, `video_references`, `audio_references`; up to 30 images |
| Kling 3.0 Turbo | `start_image` (max 1; CLI also accepts `--image`) |
| Kling 2.6 | `start_image` |
| Grok Video 1.5 | `start_image` (max 1) or `image_references`, not both; `audio_references` need an image reference |
| Veo 3.1 | `start_image` (max 1) |
| Veo 3 | `image` (max 1) |
| Marketing Studio (video) | `image`, `start_image`, `end_image` |
| Virality Predictor (`brain_activity`) | `video` |
| Multi-Image to 3D | `image` (1–4) |
| Seed Audio 1.0 | `audio_references` or `image_references` (optional; mutually exclusive) |
| Mirelo Text to Audio | (no media — pass `--prompt`) |
| Sonilo Music | (no media — pass `--prompt` and `--duration`) |
| Most image models | `image` (1+) |
| Z Image, Recraft V4.1, Soul Cast, Soul Location | (no media — prompt-only) |

For simple image-to-video, the `start_image` role is what you want. For pure video models that only declare `image`, the `image` flag is auto-remapped to `start_image` by the CLI.

## Aspect ratios and durations

These are model-specific. The CLI clamps unsupported values to the nearest allowed one (with a `Note: adjustments applied` warning) when the model declares a closed set. When in doubt:

```bash
higgsfield model get <model>
```

Common patterns:

- **Seedance 2.5**: duration 4–30s; resolution `480p`, `720p`, or `1080p`. Use `t2v` for prompt-only generation and `omni_reference` for reference inputs. Use Seedance 2.0 when native 4K is required.
- **Seedance 2.0** image: `auto`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`. Duration 4–15s. Resolution `480p`, `720p`, `1080p`, or `4k`. Optional `--bitrate_mode standard|high`, default `standard`.
- **Kling 3.0**: `16:9`, `9:16`, `1:1`. Duration 3–15s. Modes `std`/`pro`/`4k`. Sound `on`/`off`.
- **Kling 3.0 Turbo**: `16:9`, `9:16`, `1:1`. Duration 3–15s. Resolution `720p` or `1080p`. Optional single `start_image` only.
- **Soul 2.0**: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`. Quality `1.5k` or `2k` maps to backend `720p`/`1080p`.
- **Soul Cinema** (`soul_cinematic`, `soul_cinema_studio`): same as Soul 2.0 plus `21:9`. Quality `1.5k` or `2k`. `style_id` is accepted only by `soul_cinema_studio`.
- **Soul Location**: `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `3:2`, `2:3`, `21:9`, `9:21`. No quality/resolution selector; dimensions are fixed by aspect ratio.
- **Veo 3.1**: `16:9` or `9:16`. Duration `4`, `6`, or `8` only. Quality `basic`/`high`/`ultra`.
- **Marketing Studio (video)**: `auto`/`21:9`/`16:9`/`4:3`/`1:1`/`3:4`/`9:16`. Resolution `480p`, `720p`, or `1080p`.
- **Cinema Studio 4.0**: `auto`/`21:9`/`16:9`/`4:3`/`1:1`/`3:4`/`9:16`. Resolution `480p`, `720p`, or `1080p`. Native audio on by default.

## When you submit an unknown value

The CLI reports two kinds of feedback:

- **Adjustments** — a non-fatal coercion. E.g. you passed `aspect_ratio=99:99` and the model accepts a closed set; the CLI picks the closest match and continues. The adjustments map is included in the response.
- **Validation error** — a fatal mismatch. E.g. an unknown declared parameter, or a media role the model doesn't accept. The CLI returns an error and does not submit.
