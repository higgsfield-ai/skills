# Scenarios

Starter scenarios across the Higgsfield skills. Each is one user request + what the agent should do + how to score it.

These exist to be run by a human (or by another agent acting as the user) in a fresh session with skills installed.

---

## Scenario 1 — Cheap photorealistic image (generate)

**User request:**

> Make me a quick photorealistic image of a fox in a snowy forest.

**Expected behavior:**

- Picks `gpt_image_2_6` (default), or a faster option (`z_image`, `nano_banana_2_lite`) because the user said "quick".
- Does NOT pick a Soul model (no face mentioned).
- Submits via `higgsfield generate create <model> --prompt "..." --wait` (one-shot create+poll, no separate `wait` step).
- Stays silent until done (no "checking status..." spam).
- Delivers ONE URL with a short summary.

**Score:**

- Pass: correct model class, single URL out, no internal narration.
- Partial: correct model but excessive narration ("calling the API now…").
- Fail: wrong model class, multiple jobs submitted, broken URL.

---

## Scenario 2 — Image-to-video animation (generate)

**User request:**

> Animate this photo into a 5-second clip with the camera slowly pulling back.
> [attached: still.jpg]

**Expected behavior:**

- Picks `seedance_2_5` (default for image-to-video) with `--mode omni_reference`.
- Uses `--start-image still.jpg`.
- Uses motion verbs in the prompt ("pulls back", "ambient motion") not redescribed scene.
- `--duration 5`.
- Delivers ONE video URL.

**Score:**

- Pass: correct model, `--start-image` used, prompt focuses on motion.
- Partial: redescribed scene in prompt instead of motion-only.
- Fail: text-only video model picked (ignored the photo), wrong duration, no `--start-image`.

---

## Scenario 3 — Soul training (soul)

**User request:**

> Train my Soul on these 8 photos. Call it "founder".
> [attached: 8 photos]

**Expected behavior:**

- Picks `--soul-2` (default).
- Submits `higgsfield soul-id create --name founder --soul-2 --image ... --image ...`.
- Polls silently. Soul training takes 15–45 min.
- Delivers: "Soul `founder` ready. Use in generate with `--soul-id <id>`."
- Does NOT print the raw `reference_id` in chat (UX rule).

**Score:**

- Pass: correct variant, all 8 photos passed, terminal success message clean.
- Partial: prints raw `reference_id` (against UX rule).
- Fail: wrong variant, fewer photos passed than provided, polling spam.

---

## Scenario 4 — Soul + Generate chain

**User request:**

> Use my Soul "founder" (already trained) to make a cinematic portrait of me on a Tokyo street at night.

**Expected behavior:**

- Looks up the existing Soul reference (asks user for the id, OR detects from a workspace state file if one exists).
- Picks `text2image_soul_v2` or `soul_cinematic` (the cinematic variant fits the "cinematic" word).
- Passes `--soul-id <id>`.
- Does NOT re-train Soul.
- Delivers ONE URL.

**Score:**

- Pass: correct chaining, no re-training, cinematic variant chosen.
- Partial: re-trained Soul unnecessarily.
- Fail: ignored Soul, used a generic photo-real model.

---

## Scenario 5 — Pinterest pin (product-photoshoot)

**User request:**

> Make a Pinterest pin of my candle [attached: candle.jpg]. Cottagecore mood.

**Expected behavior:**

- Picks `--mode moodboard_pin`.
- NOT `lifestyle_scene` or `product_shot`.
- Calls `higgsfield product-photoshoot create --mode moodboard_pin --image candle.jpg --prompt "..."`.
- Does NOT call `higgsfield generate create gpt_image_2 ...` directly (must go through the prompt enhancer).
- Asks ≤4 short questions (count, mood, anything to emphasize). Mode is obvious from the request.
- Delivers ONE URL or a short bulleted list if `--count > 1`.

**Score:**

- Pass: correct mode, routed through `product-photoshoot` (not direct `gpt_image_2`).
- Partial: asks too many interview questions.
- Fail: wrong mode, bypassed the prompt enhancer.

---

## Scenario 6 — Hero banner with use case (product-photoshoot)

**User request:**

> Hero banner for my landing page showing my serum being applied.

**Expected behavior:**

- Picks `--mode hero_banner` (banner format wins over closeup-with-person tie-breaker per SKILL.md).
- Default aspect ratio appropriate for hero banner (16:9 or wider).
- Skips Type-A interview because mode is obvious.

**Score:**

- Pass: `hero_banner` mode, correct aspect ratio.
- Partial: `closeup_product_with_person` (specific genre tie-break that loses to banner format here).
- Fail: random other mode.

---

## Scenario 7 — Marketing Studio UGC video from URL (generate)

**User request:**

> Make a 15-second UGC ad for https://shop.example.com/sneakers, 9:16.

**Expected behavior:**

- Calls `higgsfield marketing-studio products fetch --url ... --wait` first.
- Then lists/picks an avatar (`higgsfield marketing-studio avatars list`).
- Then `higgsfield generate create marketing_studio_video` with `--mode ugc`, `--duration 15`, `--aspect_ratio 9:16`, `--wait`.
- Asks one question at a time. Does NOT batch-ask (avatar + product + mode + duration upfront).

**Score:**

- Pass: full 3-step Marketing Studio flow, single-question phases.
- Partial: batch-asked questions upfront.
- Fail: tried to use generic `kling3_0` instead of `marketing_studio_video`.

---

## Scenario 8 — Language detection

**User request:** (in Russian)

> Сгенерируй мне фотореалистичную картинку лисы в зимнем лесу.

**Expected behavior:**

- Detects user_language = `ru`.
- Replies in Russian for status, questions, summary.
- Keeps technical flags English (`--model nano_banana_flash`, `--aspect_ratio 16:9`).
- Picks `gpt_image_2_6` (default).

**Score:**

- Pass: Russian for human-facing text, English for flags.
- Partial: half-translated (e.g. translates "16:9" to "16 на 9").
- Fail: replies in English when user wrote Russian.

---

## Scenario 9 — Vague request (product-photoshoot Type F)

**User request:**

> Make me something cool for my brand.

**Expected behavior:**

- Routes to `higgsfield-product-photoshoot` Type F interview.
- Asks 2–3 disambiguating questions (what product, goal, reference image?).
- Does NOT submit a generic image immediately.

**Score:**

- Pass: structured 2–3 labeled questions.
- Partial: too many open-ended questions ("what's your brand about?").
- Fail: submits a generic image without asking.

---

## Scenario 10 — Don't invent model names

**User request:**

> Use Higgsfield's new "supernova_v9" model to make a sci-fi cityscape.

**Expected behavior:**

- Notices the model name is unfamiliar.
- Runs `higgsfield model list` to verify.
- Reports back: "supernova_v9 isn't in the catalog. Suggested alternatives: …".
- Does NOT submit with a fabricated model name.

**Score:**

- Pass: verified before submitting, correct fallback.
- Partial: submitted anyway and surfaced the API error.
- Fail: hallucinated some other model name without verification.

---

## Scenario 11 — Virality Predictor video scoring

**User request:**

> Analyze this ad video and tell me whether the hook is strong enough to hold attention.
> [attached: ad.mp4]

**Expected behavior:**

- Picks Virality Predictor (`brain_activity`).
- Uses `--video ad.mp4`.
- Does NOT ask for a prompt; the video is the input.
- Treats the result as a text score report, not a generated video/image.
- Delivers overall score, peak hook second, sustain score, region highlights, and a business interpretation of attention/virality potential.
- Links the Open report URL for visual inspection.

**Score:**

- Pass: correct model, `--video` used, text metrics summarized with business interpretation, and the Open report URL included.
- Partial: correct model but treats the result URL as the only output.
- Fail: uses a video generation model, asks for a generation prompt, or ignores the uploaded clip.

---

## Scenario 12 — Video explainer preset selection

**User request:**

> Make a one-minute narrated explainer in Russian about how neural networks learn. Show me the available visual styles first.

**Expected behavior:**

- Routes to `higgsfield-faceless-video` (or the compatible explainer entry), not generic video generation.
- Runs `higgsfield preset list video-explainer --json` and shows current preview links.
- Waits for style selection, then resolves its UUID with `higgsfield preset resolve video-explainer`.
- Lets the user choose one voice and creates six Russian `seed_audio` narration jobs first.
- Creates six matching 10-second clips with a supported video model and the chosen style.
- Assembles the ordered pairs with the bundled script and verifies the final MP4.

**Score:**

- Pass: live preset and voice selection, six matched audio/video blocks, final assembled MP4.
- Partial: correct block pipeline but chooses a requested option without showing it or loses a block pairing.
- Fail: embeds a preset list, fabricates an ID, uses a retired server-side assembler, or returns loose clips.

---

## Scenario 13 — Playable browser game

**User request:**

> Build a small mobile-friendly browser game where a fox collects stars, then give me a play link.

**Expected behavior:**

- Routes to `higgsfield-websites` and creates the project with `--type game` and a game-genre `--category`.
- Produces a STYLE FORMULA and `design/assets.csv` before visuals/code.
- Builds responsive touch + keyboard controls and a complete win/lose/restart loop.
- Verifies locally, pushes, and runs `higgsfield website deploy`.
- Does not run `higgsfield website publish` unless publication is requested.

**Score:**

- Pass: coherent game, manifest-driven assets, local verification, returned deploy URL.
- Partial: playable and deployed but missing one planning artifact or mobile verification.
- Fail: returns only concept art/code, constructs a URL manually, or publishes publicly without consent.

---

## Scenario 14 — Complete visual identity (brandkit)

**User request:**

> Create a visual identity and brandbook for Northline, a calm technical logistics platform. Start from scratch.

**Expected behavior:**

- Routes to `higgsfield-brandkit`, not generic generation or Marketing Studio's URL-import brand kit.
- Asks only for unresolved context/preferences and checks stage-specific local dependencies without installing them silently.
- Creates 2–3 palette boards, shows them, and waits for a selection.
- After palette approval, generates exactly three `recraft_v4_1` vector SVG marks with identical technical parameters and waits for logo selection.
- Proposes typography only after logo selection, persists each approval in project-local `brandkit/state.json`, and builds the canonical PPTX/PDF Brandbook only after all three slots are approved.
- Does not use FFmpeg, self-select a logo, invent brand claims, or replace an approved mark during downstream mockups.

**Score:**

- Pass: correct staged routing, three SVG candidates, explicit approval gates, durable state, and dependency-aware Brandbook output.
- Partial: correct assets but asks a full questionnaire, installs tools without permission, or loses approval state.
- Fail: uses the Marketing Studio metadata kit, self-approves a mark, produces only raster logos, or skips palette/logo/type selection.

---

## Scenario 15 — Native animated GIF

**User request:**

> generate a gif of a cute cat

**Expected behavior:**

- Uses `higgsfield-generate` with `gpt_image_2_6` and `--output_format gif` on the first submission.
- Uses live GIF defaults unless the user specifies size, frame count or frame duration; preserves explicit values.
- Does not submit PNG drafts, use a video model, or create a conversion pipeline.
- Waits for the single job and returns the exact CLI result URL unchanged.

**Score:**

- Pass: one native GIF job, correct format flag, actual result URL.
- Fail: PNG output, video/conversion route, extra unsolicited jobs, or a fabricated URL.

---

## Scenario 16 — Standalone SVG icon

**User request:**

> Generate an SVG icon of a cute cat.

**Expected behavior:**

- Uses `gpt_image_2_6` with `--output_format svg`, before the generic icon/cartoon model rules.
- Sends no `--image` or `--image-references`; SVG takes no references.
- Returns the actual SVG result URL, not a raster preview renamed to `.svg`.
- Keeps complete brand identity work on the existing brandkit workflow (Scenario 14).

**Score:**

- Pass: one native SVG job, no references, exact SVG result URL.
- Fail: wrong format, unsupported references, or an unsolicited brandkit workflow.

---

## Scenario 17 — Explicit GPT Image 2.6 Flare

**User request:**

> Generate an SVG coffee cup icon using GPT Image 2.6 Flare.

**Expected behavior:**

- Uses model `gpt_image_2_6_flare` with `--output_format svg` and no reference images.
- Does not use `--variant flare` on `gpt_image_2_6` or `gpt_image_2_5`.
- Returns the exact CLI result URL.

**Score:**

- Pass: separate Flare model ID and native SVG output.
- Fail: changed model, legacy variant parameter, or raster output.

---

## Scenario 18 — Explicit MP4 remains video

**User request:**

> Generate a four-second MP4 video of a cute cat, not a GIF.

**Expected behavior:**

- Uses the video route with `seedance_2_5` and `--duration 4`.
- Does not substitute a GIF image job because the subject could be animated.

**Score:**

- Pass: one video job with the requested duration.
- Fail: GIF/image route or an unsolicited format change.

---

## Scenario 19 — GIF prompt only

**User request:**

> Write a prompt for a GIF of a cute cat. Do not generate anything.

**Expected behavior:**

- Returns prompt text only.
- Does not submit image/video generation, upload media, or create a conversion pipeline.

**Score:**

- Pass: text only, no generation.
- Fail: any submitted generation job.

---

## Round template (copy when recording results)

```
Round: <N>
Date: <YYYY-MM-DD>
Commit: <sha>
Skills version: <0.x.x>

Scenario 1: pass | partial | fail — <one-line reason>
Scenario 2: ...
...
Scenario 10: ...
Scenario 11: ...
Scenario 12: ...
Scenario 13: ...
Scenario 14: ...
Scenario 15: ...
Scenario 16: ...
Scenario 17: ...
Scenario 18: ...
Scenario 19: ...

Aggregate: <P pass / Q partial / F fail>
Time-to-result mean: <Ns>
Notable regressions: <list>
```
