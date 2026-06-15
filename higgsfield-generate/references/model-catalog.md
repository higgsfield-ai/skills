# Model Catalog

The full lineup of generation models available through Higgsfield. Each entry has its own sweet spot — pick the one that matches your brief. For the actual `--model` ID to pass to `higgsfield generate create`, run `higgsfield model list --json` and look up by display name.

Preferred defaults for examples and quick-start guidance in this repo:
- **Images/design/text:** `gpt_image_2` (general/high-fidelity) and `nano_banana_2` (character/cartoon).
- **Video:** `seedance_2_0` (all-purpose serious video).
- **Character/stylized image work:** `text2image_soul_v2`.
- **Ads/UGC/product demos:** `marketing_studio_video` or `marketing_studio_image`.
- **Video analysis:** Virality Predictor (`brain_activity`) for attention, hook, retention, and virality scoring. It may appear under text/analysis because the output is a report, but the input and intent are video analysis.

---

## Image models

| Model | Provider | What it's for |
|---|---|---|
| Nano Banana 2 | Google | **Fast everyday default for character work.** Edits, general generation, character / cartoon / animated-style outputs. The reach-for-this model when the brief calls for character or cartoon-style image generation. |
| Nano Banana Pro | Google | **Top-tier Nano Banana.** Same canvas as Nano Banana 2 with extra fidelity and accuracy on harder briefs. Pick when 2 isn't getting there. |
| Nano Banana | Google | Reliable, budget-friendly entry in the Nano Banana family — picks up the same realistic look at a lighter price point. |
| Higgsfield Soul 2.0 | Higgsfield | **Aesthetic UGC, fashion editorial, character generation.** When the brief leans editorial, lifestyle, or "looks like a magazine cover". Soul-aware (accepts a Soul Character reference). |
| Soul Cinema | Higgsfield | **Cinematic stills, film-grade lighting.** The pick when the user asks for "cinematic" or wants concept-art mood. |
| Soul Cast | Higgsfield | **Distinctive, characterful personas.** When the brief calls for a creative, expressive character rather than photoreal default. Text-only (no reference image). |
| Soul Location | Higgsfield | **Best-in-class environments and locations.** Unmatched for pure scene and place generation without a person in frame. |
| Seedream 4.5 | Bytedance | **Complex scene edits with faces.** When the brief is a face-anchored photo edit into a complex new scene (more than an outfit change), without heavy filters. |
| Seedream 5.0 Lite | Bytedance | Same Seedream lineage as 4.5 with faster turnaround for visual-reasoning and instruction-based edits. |
| Z Image | Tongyi-MAI | **Fastest in the catalog.** Built for speed, drafts, and LoRA-driven stylization. The pick when the brief is "fast and cheap, let me iterate". |
| Flux 2.0 | Black Forest Labs | Precise prompt adherence with multiple variants (pro, flex, max). A strong creative alternative when the user wants a different look from the Banana family. |
| Flux Kontext Max | Black Forest Labs | **Context-aware editing and style transfer.** Strong for anime, stylized looks, typography remix — when defaults feel too generic. |
| Kling O1 Image | Kling | Versatile photorealistic image generation with broad aspect-ratio support. |
| GPT Image 1.5 | OpenAI | Earlier-generation OpenAI image model with editing and text-rendering capabilities. |
| GPT Image 2 | OpenAI | **Default high-fidelity image generation.** Graphic design, UI, banners, typography, and any brief with on-image text. Used by `higgsfield-product-photoshoot` under the hood. |
| Grok Imagine | xAI | Expressive, high-contrast, bold creative outputs. Worth trying for anime and stylized looks. |
| Recraft V4.1 | Recraft | **Clean graphic and vector-style design assets.** Logos, icons, flat illustrations, brand marks, and controlled-palette visuals. Use `model_type=vector` for vector-like output and `standard` for raster-style graphics. |
| Cinema Studio Image 2.5 | Higgsfield | Cinematic still frames up to 4K, dramatic film look. |
| Marketing Studio Image | Higgsfield | **Branded image ads.** Retrieval-augmented over the user's avatars and products — runs inside the Marketing Studio flow. |
| Auto | Higgsfield | **Smart routing layer.** Picks the best image model from the prompt automatically. Use when the user's intent is open and you don't want to commit to a specific model. |

## Video models

| Model | Provider | What it's for |
|---|---|---|
| Seedance 2.0 | Bytedance | **SOTA all-purpose video.** Crisp, consistent identity, multi-shot capable. The default for any serious motion / cinematic / production brief. |
| Kling 3.0 | Kling | **Cheaper Seedance 2.0 substitute** for single-plane scenes that don't need heavy motion. Multi-shot, audio sync, motion transfer. |
| Seedance 1.5 Pro | Bytedance | A budget-friendly Seedance for clean single-take shots. |
| Marketing Studio | Higgsfield | **All advertising and commercial video** — UGC, unboxing, TV spot, product showcase. The default whenever the brief is "make an ad". See `marketing-modes.md`. |
| Cinema Studio Video 3.0 | Higgsfield | **Top-tier cinema-grade execution.** The pick for film-look briefs at the highest fidelity. |
| Veo 3.1 Lite | Google | **Fast and cost-effective Veo.** Built for batch and volume work. |
| Google Veo 3.1 | Google | Ultra-realistic, top-tier cinematic quality. Quality tiers basic/high/ultra. Format set is constrained — verify accepted aspect ratio and duration before submitting. |
| Google Veo 3 | Google | Reliable cinematic with broad creative range and audio support. |
| Minimax Hailuo | Hailuo | **Cheap with strong physics.** Solid budget pick when natural-physics motion matters; no audio in current variants. |
| Wan 2.7 | Wan | Synchronized audio with character-consistent video. The newer Wan release. |
| Wan 2.6 | Wan | Open-weight, stylized, experimental creative. Cheap option when the brief is intentionally artistic. |
| Kling 2.6 | Kling | Cinematic motion with advanced physics — earlier Kling release alongside 3.0. |
| Grok Video 1.5 | xAI | **Bold image-to-video from a required reference frame.** Use when the user wants stylized, anime-like, high-contrast, or experimental motion from one starting image. Requires one `--start-image` or `--image`; duration 2–15s; resolution `480p` or `720p`. |
| Grok Imagine (video) | xAI | Text and image-to-video with audio support. Worth trying for stylized creative briefs. |
| Cinema Studio Video | Higgsfield | Cinematic compositions with dramatic mood. Use Cinema Studio Video 3.0 as the modern default. |
| Cinema Studio Video v2 | Higgsfield | Refined cinematic camera and color with genre control. Use Cinema Studio Video 3.0 as the modern default. |

---

## 3D models

| Model | Provider | What it's for |
|---|---|---|
| Multi-Image to 3D | Meshy | **Create an actual 3D asset from object/product reference images.** Takes 1–4 images and returns a 3D mesh/GLB-style asset. Use repeated `--image`; add `--should_texture true` when texture matters. |

---

## Audio models

| Model | Provider | What it's for |
|---|---|---|
| Sonilo Music | Sonilo | **Generate music from text.** Use for backing tracks, instrumental beds, jingles, and musical moods. Requires `--prompt` and `--duration`; returns audio and does not take media inputs. |
| Mirelo Text to Audio | Mirelo | **Generate non-speech audio from text.** Use for sound effects, ambience, foley, impacts, transitions, and environmental sounds. Requires `--prompt` and `--duration`; returns audio and does not take media inputs. |

---

## Text / analysis models

| Model | Provider | What it's for |
|---|---|---|
| Virality Predictor (`brain_activity`) | Higgsfield | **Objective attention proxy for video creative testing.** Scores how effectively a clip captures and sustains attention, useful for hook validation, virality potential, ad review, and product/content focus. Takes a video input and returns a text report with overall score, peak second, sustain, and an Open report link. Raw `.glb` / `.bin` render artifacts stay in JSON/debug output. |

---

## Picking flow

Practical defaults from production use. Match by intent, not surface keyword. When two could apply, the higher entry wins.

Core focus first: GPT Image 2 for images/design/text, Seedance 2.0 for video,
Nano Banana 2/Pro for character or reference-driven image work, and Marketing
Studio for ads and brand/product content.

### Image — pick this default

1. **Brand product visual (Pinterest pin, lifestyle, hero banner, ad pack, virtual try-on, restyle)** → use `higgsfield-product-photoshoot` instead. NOT this skill.
2. **Generated product concept / packaging / can / bottle with brand name or label text** → GPT Image 2.
3. **Branded ad image with presenter avatar + product (Marketing Studio shape with RAG over user assets)** → Marketing Studio Image.
4. **Aesthetic UGC / fashion editorial / lifestyle character** → Soul 2.0.
5. **Cinematic still frame** → Soul Cinema.
6. **Highly characterful, creative character (text-only, distinctive persona, no reference photo)** → Soul Cast.
7. **Locations / environments / no-people scenes** → Soul Location. Best in class — nothing else matches.
8. **Logo, icon, vector-like illustration, brand mark, controlled-palette graphic** → Recraft V4.1. Use `--model_type vector` for vector-style output.
9. **Face edit + complex scene swap (more than outfit change, no heavy filters)** → Seedream 4.5. Seedream 5.0 Lite for the same niche but faster.
10. **Soul Character (reference id from `higgsfield-soul-id`)** → Soul 2.0 for stills; Soul Cinema for cinematic vibe.
11. **Anime / stylized / non-default look where defaults feel flat** → Flux Kontext Max or Grok Imagine. Worth trying.
12. **Character or cartoon-style work** → Nano Banana 2; step up to Nano Banana Pro on hard cases.
13. **Fast and cheap iteration / drafts / LoRA work** → Z Image.
14. **Default for everything else** → GPT Image 2. High-fidelity general generation, graphic design, UI, banners, anything with on-image text.
15. **Intent-only request, no preference, want auto-routing** → Auto.

### Video — pick this default

1. **All advertising / commercial video (UGC, unboxing, TV spot, product showcase, branded ad)** → Marketing Studio. See `marketing-modes.md`.
2. **Default all-purpose serious video (multi-shot, consistent identity, motion-heavy, production work, image-to-video, 4–15s requests)** → Seedance 2.0. SOTA. Validate this first before falling back.
3. **Single-plane scene without strong dynamics, cheaper** → Kling 3.0. Substitute for Seedance 2.0 when motion isn't critical.
4. **Cheap clean shot without cuts, only when the user asks for budget output** → Seedance 1.5 Pro. Do not pick it over Seedance 2.0 just because duration validation looks simpler.
5. **Image-to-video with explicit first frame** → Kling 3.0 with a start frame, or Seedance 2.0 with a start frame for higher motion.
6. **Cinema-grade execution (highest fidelity, film look)** → Cinema Studio Video 3.0.
7. **Cheap with strong physics, audio not needed** → Minimax Hailuo.
8. **Fast batch / volume** → Veo 3.1 Lite.
9. **Veo-format-bound work (specific aspect / duration set Veo accepts)** → Veo 3.1; Veo 3 is slightly behind.
10. **Stylized / animation-style edit-driven work** → Wan 2.7.
11. **Stylized cheap experimental** → Wan 2.6.
12. **Anime / bold-style image-to-video with a start frame** → Grok Video 1.5 (`grok_video_v15`). Requires one `--start-image` or `--image`, duration 2–15s, resolution `480p` or `720p`.
13. **Anime / bold-style text-to-video or older Grok-style outputs where defaults feel flat** → Grok Imagine (video). Worth trying.

### Video analysis — pick this default

1. **Evaluate a finished clip's hook, virality potential, attention, retention, or distraction risk** → Virality Predictor (`brain_activity`). It takes `--video`, needs no prompt, and returns a text score/report plus an Open report link rather than generated media.

### 3D — pick this default

1. **Create an actual 3D mesh/model/GLB from one or more object/product reference images** → Multi-Image to 3D (`multi_image_to_3d`). Pass 1–4 repeated `--image` flags. Use `--should_texture true` for textured assets; use rigging/animation flags only when the user explicitly wants a rigged or animated asset.
2. **Create a picture that merely looks like a 3D render** → use an image model instead, usually GPT Image 2 or Nano Banana 2 depending on the brief.

### Audio — pick this default

1. **Create non-speech sound effects, foley, ambience, impacts, or environmental audio from text** → Mirelo Text to Audio (`mirelo_text_to_audio`). Requires `--prompt` and `--duration`. Do not pass media inputs.
2. **Create music, backing tracks, jingles, or instrumental beds from text** → Sonilo Music (`sonilo_music`). Requires `--prompt` and `--duration`. Do not pass media inputs.
3. **Add soundtrack/audio to a generated video ad** → use Marketing Studio Video with `--generate_audio true`, not Mirelo/Sonilo.

### Things to keep in mind

- **Don't invent model names.** Run `higgsfield model list` if you're unsure — submitting an unknown model returns `unknown model "..."`.
- **Don't downgrade for schema convenience.** If Seedance 2.0 fits the intent, validate or submit it first; do not choose Seedance 1.5 only because it lists a requested duration more explicitly.
- **Do not misroute video analysis because the output is text.** A request like "analyze this video" or "score this ad" maps to Virality Predictor (`brain_activity`) when the user provides or references a finished video.
- **Do not misroute 3D style into 3D asset generation.** `multi_image_to_3d` is for actual mesh/GLB-style assets from reference images. A prompt like "make a 3D render" is usually image generation.
- **Do not treat audio generation as an audio media input.** `mirelo_text_to_audio` and `sonilo_music` create audio from text. `--audio` is for reference audio on video models like Seedance 2.0.
- **Audio reference for Seedance 2.0** comes through the media inputs with role `audio`, not via a separate `generate_audio` flag.
- **Prompt-only models reject reference media.** Z Image, Recraft V4.1, Soul Cast, Soul Location, and some Wan configs are prompt-only; pass no media flags to them. Virality Predictor is different: it returns text but requires a video input.
- **Route branded product visuals through `higgsfield-product-photoshoot`** — its prompt enhancer adds 10 mode-specific templates on top of GPT Image 2. Direct GPT Image 2 generation here is the right call for everything that isn't a product photoshoot.
- **For cinema video, prefer Cinema Studio Video 3.0** as the modern default; reach for the earlier Cinema Studio Video variants only when the user names them.
- **When the user names a specific model, use it.** The defaults above cover the common intents — the rest of the catalog exists for users who know what they want.

---

## Media role conventions

Each model accepts a fixed set of media roles. When unsure, run `higgsfield model get <model>` and inspect the `medias[].roles` field.

| Model | Accepted media roles |
|---|---|
| Seedance 2.0 | `image`, `start_image`, `end_image`, `video`, `audio` |
| Kling 3.0 | `start_image`, `end_image` |
| Kling 2.6 | `start_image` |
| Grok Video 1.5 | `start_image` (required max 1; CLI also accepts `--image`) |
| Veo 3.1 | `start_image` (max 1) |
| Veo 3 | `image` (max 1) |
| Marketing Studio (video) | `image`, `start_image`, `end_image` |
| Virality Predictor (`brain_activity`) | `video` |
| Multi-Image to 3D | `image` (1–4) |
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

- **Seedance 2.0** image: `auto`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`. Duration 4–15s. Optional `--bitrate_mode standard|high`, default `standard`.
- **Kling 3.0**: `16:9`, `9:16`, `1:1`. Duration 3–15s. Modes `pro`/`std`. Sound `on`/`off`.
- **Soul 2.0**: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`. Quality `1.5k` or `2k` maps to backend `720p`/`1080p`.
- **Soul Cinema**: same as Soul 2.0 plus `21:9`. Quality `1.5k` or `2k`.
- **Soul Location**: `1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `3:2`, `2:3`, `21:9`, `9:21`. No quality/resolution selector; dimensions are fixed by aspect ratio.
- **Veo 3.1**: `16:9` or `9:16`. Duration `4`, `6`, or `8` only. Quality `basic`/`high`/`ultra`.
- **Marketing Studio (video)**: `auto`/`21:9`/`16:9`/`4:3`/`1:1`/`3:4`/`9:16`. Resolution `480p` or `720p`.

## When you submit an unknown value

The CLI reports two kinds of feedback:

- **Adjustments** — a non-fatal coercion. E.g. you passed `aspect_ratio=99:99` and the model accepts a closed set; the CLI picks the closest match and continues. The adjustments map is included in the response.
- **Validation error** — a fatal mismatch. E.g. an unknown declared parameter, or a media role the model doesn't accept. The CLI returns an error and does not submit.
