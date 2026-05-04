# Higgsfield Skills — Cookbook

Real workflows that combine the three skills end-to-end. Each recipe is what you say to the agent + what the agent runs + tips.

---

## Recipe 1 — Brand Campaign from a Founder Photo

**What it does:** One photo of the founder → trained Soul Character → 5 lifestyle scenes around the brand's product → top 2 animated to short video clips. One headshot in, full content set out.

**Why this is powerful:** Replaces a creative agency's first sprint. The founder appears in every asset, the brand product is consistent, and you go from raw photo to publishable content in one session.

**What you say:**

```
Train my Soul on this headshot, then make 5 lifestyle photos of my product
[bottle.jpg] in scenes I'd post on Instagram, and animate the best 2 into
5-second clips. Save everything to ./campaign/.
```

**What the agent does:**

1. **Soul training** (`higgsfield-soul-id`):

   ```bash
   higgsfield soul-id create --name "founder" --soul-2 \
     --image headshot1.png --image headshot2.png ... \
     --max-train-steps 1000
   ```

   Returns `reference_id`. The agent saves it for the session.

2. **Lifestyle photos** (`higgsfield-product-photoshoot`):

   ```bash
   higgsfield product-photoshoot create \
     --mode lifestyle_scene \
     --prompt "founder using product in 5 distinct IG-feed scenes: morning coffee setup, desk workspace, outdoor café, gym, home office" \
     --image bottle.jpg \
     --count 5 \
     --output-dir ./campaign/photos
   ```

   Backend assembles the prompt, varies preset/lighting/angle/palette across the 5 outputs.

3. **Pick top 2 → animate** (`higgsfield-generate`, image-to-video):

   ```bash
   higgsfield generate create kling3_0 \
     --prompt "subtle product reveal, camera slowly pulls back, ambient motion" \
     --start-image ./campaign/photos/lifestyle-01.jpg \
     --duration 5 \
     --aspect_ratio 1:1 \
     --output-dir ./campaign/videos \
     --wait
   ```

**Tips:**

- Use `--count 5` on photoshoot first — cheaper than 5 separate runs and the backend coordinates the visual system across variants.
- `kling3_0` with `--start-image` gives the cleanest image-to-video. `seedance_2_0` is an alternative for more dramatic motion.
- For the founder's face to stay consistent in animations, use Soul models (`text2image_soul_v2`) for the photoshoot step instead of `gpt_image_2`. Trade-off: less control over background, more on identity.

---

## Recipe 2 — UGC Ad Batch from a Product URL

**What it does:** Paste a Shopify URL → import product automatically → pick a preset avatar → generate 4 different ad styles (UGC, unboxing, product review, TV spot) at 9:16 for paid social. No assets uploaded by you.

**Why this is powerful:** Marketing Studio handles all the heavy lifting — product fetch, avatar matching, mode-specific staging. You go from a URL to 4 publishable ads in one workflow.

**What you say:**

```
Make UGC ads for my product https://shop.example.com/sneakers — try 4 different
angles: organic UGC, unboxing reveal, presenter review, and a TV-spot version.
9:16 for TikTok and Reels. 15 seconds each.
```

**What the agent does:**

1. **Product fetch:**

   ```bash
   higgsfield marketing-studio products fetch \
     --url https://shop.example.com/sneakers \
     --wait
   ```

   Returns `product_id`. URL fetch auto-pulls title, description, hero images.

2. **Pick preset avatar:**

   ```bash
   higgsfield marketing-studio avatars list --json | jq '.[] | select(.tags | contains(["sporty"]))'
   ```

   Picks one matching the brand voice. No user input needed for the typical case.

3. **Generate 4 modes in parallel:**

   ```bash
   for mode in ugc ugc_unboxing product_review tv_spot; do
     higgsfield generate create marketing_studio_video \
       --prompt "<short hook tied to the mode>" \
       --avatars '[{"id":"<avatar_id>","type":"preset"}]' \
       --product_ids '[<product_id>]' \
       --mode $mode \
       --duration 15 \
       --resolution 720p \
       --aspect_ratio 9:16 \
       --output-dir ./ads/$mode \
       --wait &
   done
   wait
   ```

4. **Deliver:** four URLs, one per mode, with a one-line summary each.

**Tips:**

- Modes are not interchangeable. `ugc` reads as phone-shot organic content; `tv_spot` reads as broadcast-quality. Don't mix them in the same campaign without intent.
- For a brand where the founder should appear instead of a preset avatar, run `higgsfield-soul-id` first for the founder, then pass `--avatars '[{"id":"<soul_ref_id>","type":"custom"}]'` to Marketing Studio.
- Hooks (the prompt on `--prompt`) matter more than mode for performance. Test 4 hooks × 1 mode before testing 1 hook × 4 modes.

---

## Recipe 3 — Founder Video Update for the Team

**What it does:** Founder records once via Soul → every weekly update gets a fresh on-camera-looking video with their face and voice — without recording.

**Why this is powerful:** Async-first companies lose the high-bandwidth signal of a face on camera. This gives it back at zero recording cost. Once Soul is trained (~30 minutes one-time), every future "team update" is one prompt away.

**What you say (one-time setup):**

```
Train my Soul on these 12 photos. Call it "founder".
```

**What you say (every update afterwards):**

```
Make a 60-second video of me with this script:

  Hey team — this week we shipped X and started Y. Three things to know:
  one, [...]. Two, [...]. Three, [...]. See you Friday.

Landscape, neutral background, conversational tone.
```

**What the agent does (one-time setup):**

```bash
higgsfield soul-id create --name "founder" --soul-2 \
  --image photo01.png --image photo02.png ... \
  --output-dir ./identity
```

Saves `reference_id` to `./identity/training-manifest.json`.

**What the agent does (every update):**

Option A — Marketing Studio with custom avatar (recommended for branded look):

```bash
# One-time: register the Soul as a custom avatar
higgsfield marketing-studio avatars create \
  --name "Founder" \
  --image <upload_id> \
  --image-url <cloudfront_url>
# Returns avatar_id

higgsfield generate create marketing_studio_video \
  --prompt "<full script with scene labels>" \
  --avatars '[{"id":"<avatar_id>","type":"custom"}]' \
  --mode ugc \
  --duration 60 \
  --aspect_ratio 16:9 \
  --wait
```

Option B — direct Soul model (more direct, less branded staging):

```bash
higgsfield generate create soul_cinema_studio \
  --prompt "<full script>" \
  --soul-id <reference_id> \
  --duration 60 \
  --aspect_ratio 16:9 \
  --wait
```

**Tips:**

- For voice consistency, train Soul with `--soul-cinematic` if these will be longer videos (>30s) with talking-head delivery. Default `--soul-2` is fine for shorter clips and image-only work.
- Write scripts for speech, not text: short sentences, natural pauses, ~150 words per minute target. A 60-second video = ~150 words.
- Don't pad scripts to fit duration. The model paces itself; over-stuffed scripts get rushed delivery.
- Save the `reference_id` and `avatar_id` somewhere stable (a `.env` file, a Notion doc) — you'll reuse them weekly forever.

---

## Quick reference — which recipe for what

| Goal | Recipe | Skills used |
|---|---|---|
| Launch a campaign with the founder's face | #1 Brand Campaign | `higgsfield-soul-id` → `higgsfield-product-photoshoot` → `higgsfield-generate` |
| Generate paid-social ads from a URL | #2 UGC Ad Batch | `higgsfield-generate` (Marketing Studio) |
| Async team updates without recording | #3 Founder Video | `higgsfield-soul-id` → `higgsfield-generate` |

## Patterns these recipes share

1. **Train identity once, reuse forever.** Soul training is 15–45 minutes one-time. Every future video that needs the founder's face is one prompt away.
2. **Let the backend assemble the prompt for branded work.** `product-photoshoot` enhances prompts before submitting to `gpt_image_2`. Don't write `gpt_image_2` prompts by hand.
3. **Cheap-first iteration.** Test cheap models (`flux`, `z_image`) for prompt iteration; switch to expensive (`nano_banana_pro`, `gpt_image_2`) only on confirmed direction.
4. **Filenames have timestamps.** Use `yyyy-mm-dd-hh-mm-ss-name.ext` so you can trace which generation came from which session.
