# Scenarios

Starter scenarios across the Higgsfield skills. Each is one user request + what the agent should do + how to score it.

These exist to be run by a human (or by another agent acting as the user) in a fresh session with skills installed.

## Scoring generation model choice

**Never score on a specific model id.** `higgsfield-generate` resolves a **role** against the
live catalog, so the concrete model a correct run picks changes whenever Higgsfield reships a
role — and a scenario that asserts `seedance_2_0` would start failing correct behavior on the
next catalog deploy. That is exactly the rot this repo moved away from.

Score the **role** and the **resolution mechanism** instead:

- Did the agent pick the right role for the intent?
- Did it resolve that role live (`higgsfield model recommend --role <role>`, or the tag filter
  on an older CLI) rather than typing a model name from memory?
- Did it submit the **resolved concrete id** to `generate create` — never the role name?
- Did it report the actual model to the user, not the role?

Degradation is a pass, not a partial: an older CLI rejecting `--role`, or a thin catalog
returning nothing, should fall through to the tag filter and then to the documented fallback
**silently**. An agent that surfaces "role resolution failed" to the user is a partial.

Skills with **pinned** models (`models.pinned` in their frontmatter — `game-generation`,
`youtube-thumbnail`) are the exception: there, substituting the pinned id IS the failure.

---

## Scenario 1 — Quick photorealistic image (generate)

**User request:**

> Make me a quick photorealistic image of a fox in a snowy forest.

**Expected behavior:**

- Picks `role:default-image`. No text to render, no identity to preserve, no vector output.
- Does NOT pick `role:character-image` (no person or character), and does NOT route to
  `product-photoshoot` or `brandkit`.
- Resolves the role live, then submits the resolved id via
  `higgsfield generate create <resolved_id> --prompt "..." --wait` (one-shot create+poll, no separate `wait` step).
- Does NOT pass `--duration`/`--resolution`/`--quality` values it never verified against the
  resolved model's schema.
- Stays silent until done (no "checking status..." spam).
- Delivers ONE URL with a short summary naming the model that actually ran.

**Score:**

- Pass: correct role, resolved live, single URL out, no internal narration.
- Partial: correct role but excessive narration ("calling the API now…"), or reports the role
  name to the user instead of the resolved model.
- Fail: typed a model name from memory instead of resolving, passed a role name as the model id,
  wrong role, multiple jobs submitted, or broken URL.

---

## Scenario 2 — Image-to-video animation (generate)

**User request:**

> Animate this photo into a 5-second clip with the camera slowly pulling back.
> [attached: still.jpg]

**Expected behavior:**

- Picks `role:default-video`. Image-to-video is the default video role plus a start frame, NOT
  a separate role and NOT `role:fast-video` — the user asked for neither cheap nor fast.
- Resolves the role live and submits the resolved id.
- Uses `--start-image still.jpg`.
- Uses motion verbs in the prompt ("pulls back", "ambient motion") not redescribed scene.
- Confirms `5` is an accepted duration for the resolved model before passing `--duration 5`
  (durations are a per-model closed list or range), or accepts the CLI's `adjustments`
  coercion and discloses it.
- Delivers ONE video URL.

**Score:**

- Pass: `default-video` resolved live, `--start-image` used, duration verified or coercion
  disclosed, prompt focuses on motion.
- Partial: redescribed scene in prompt instead of motion-only, or passed an unverified duration
  and stayed silent about the adjustment.
- Fail: downgraded to `role:fast-video` unprompted, typed a model name from memory, ignored the
  photo (no `--start-image`), or passed a role name as the model id.

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
- Fail: used a generic video role (`default-video` / `fast-video`) instead of
  `role:marketing-video`, losing the avatar/product/hook contract entirely.

---

## Scenario 8 — Language detection

**User request:** (in Russian)

> Сгенерируй мне фотореалистичную картинку лисы в зимнем лесу.

**Expected behavior:**

- Detects user_language = `ru`.
- Replies in Russian for status, questions, summary.
- Keeps technical flags and model ids English (`--aspect_ratio 16:9`); never translates a
  resolved model id or a role name.
- Picks `role:default-image`, same as Scenario 1 — the language of the request must not change
  the routing.

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
- Reports back: "supernova_v9 isn't in the catalog. Suggested alternatives: …", sourcing the
  alternatives from the live catalog (ideally `higgsfield model list --role default-image`), not
  from memory.
- Does NOT claim the model definitively does not exist — the catalog is per-credential, so the
  honest statement is "not available on this account".
- Does NOT submit with a fabricated model name.

**Score:**

- Pass: verified before submitting, alternatives sourced live, scoped the claim to this account.
- Partial: submitted anyway and surfaced the API error, or asserted the model "does not exist".
- Fail: hallucinated some other model name without verification.

---

## Scenario 15 — Role resolution on an older CLI (generate)

Regression guard for the graceful-degradation path. The `--role` flags ship in a separate CLI
release, so every installed CLI older than that must still work.

**Setup:** an installed `higgsfield` CLI that does not support `higgsfield model recommend --role`
(rejects it as an unknown flag).

**User request:**

> Make me a 6-second video of waves hitting rocks at sunset.

**Expected behavior:**

- Picks `role:default-video`, tries `higgsfield model recommend --role default-video` first.
- On the unknown-flag error, falls through to the client-side tag filter over
  `higgsfield model list --json` (role tags ship with the catalog, independently of the CLI).
- If that is also empty, uses the documented fallback literal from
  `higgsfield-generate/references/model-catalog.md`.
- Generates successfully and says nothing to the user about any of this.

**Score:**

- Pass: video delivered; degradation invisible to the user.
- Partial: video delivered but the agent narrated the fallback or apologized for a "failure".
- Fail: aborted the generation, told the user to upgrade the CLI, asked the user which model to
  use, or invented a model id after resolution came back empty.

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

- Routes to `higgsfield-video-explainer`, not generic video generation.
- Runs `higgsfield preset list video-explainer --json` and shows current preview links.
- Waits for style selection, then resolves its UUID with `higgsfield preset resolve video-explainer`.
- Lets the user choose one voice and creates six Russian `seed_audio` narration jobs first.
- Creates six matching 10-second `gemini_omni` clips second, all with the resolved style key.
- Builds ordered `blocks.json` pairs and finishes with one `explainer_video` generation job.

**Score:**

- Pass: live preset and voice selection, six matched audio/video blocks, final assembled MP4.
- Partial: correct block pipeline but chooses a requested option without showing it or loses a block pairing.
- Fail: embeds a preset list, fabricates an ID, uses `video_explainer`, or returns loose clips.

---

## Scenario 13 — Playable browser game

**User request:**

> Build a small mobile-friendly browser game where a fox collects stars, then give me a play link.

**Expected behavior:**

- Routes to `higgsfield-game-generation`.
- Produces a STYLE FORMULA and `design/assets.csv` before visuals/code.
- Builds responsive touch + keyboard controls and a complete win/lose/restart loop.
- Verifies locally, packages the required root layout, and runs `higgsfield game deploy`.
- Does not run `higgsfield game publish` unless marketplace publication is requested.

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

Aggregate: <P pass / Q partial / F fail>
Time-to-result mean: <Ns>
Notable regressions: <list>
```
