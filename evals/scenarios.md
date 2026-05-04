# Scenarios

10 starter scenarios across the 3 skills. Each is one user request + what the agent should do + how to score it.

These exist to be run by a human (or by another agent acting as the user) in a fresh session with skills installed.

---

## Scenario 1 — Cheap photorealistic image (generate)

**User request:**

> Make me a quick photorealistic image of a fox in a snowy forest.

**Expected behavior:**

- Picks `nano_banana_2`, `flux_2`, or another photorealistic-default model.
- Does NOT pick a Soul model (no face mentioned).
- Does NOT pick `gpt_image_2` (overkill for "quick").
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

- Picks `kling3_0` (default for image-to-video) or `seedance_2_0`.
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
- Picks `text2image_soul_v2` or `soul_cinema_studio` (the cinematic variant fits the "cinematic" word).
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

- Picks `--mode pinterest_pin`.
- NOT `lifestyle_scene` or `product_shot`.
- Calls `higgsfield product-photoshoot create --mode pinterest_pin --image candle.jpg --prompt "..."`.
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
- Keeps technical flags English (`--model nano_banana_2`, `--aspect_ratio 16:9`).
- Picks `nano_banana_2` or `flux_2`.

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

Aggregate: <P pass / Q partial / F fail>
Time-to-result mean: <Ns>
Notable regressions: <list>
```
