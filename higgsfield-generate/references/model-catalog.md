# Model Roles — intent → role → live model

This file maps **intent to a role**. It does not list models, their providers, their
parameters, or their aspect ratios. That is live catalog data and it goes stale between
releases; the CLI is the only source of truth for it.

A **role** is a stable, use-case-named pointer to whatever model currently fills that job
(`role:default-video`, `role:text-render-image`). Roles are published as tags on the live
catalog, so when Higgsfield ships a better video model the role starts resolving to it —
no skill edit, no repo update, no version bump on the user's side.

**Never pass a role name to `higgsfield generate create`.** Resolve the role to a concrete
model id first, then submit that id. Approval prompts, cost estimates, and job history must
name the actual model the user is billed for.

---

## Step 1 — Resolve the role

Try these in order and stop at the first that returns an id.

```bash
# 1. Preferred — CLI resolves the role for you.
higgsfield model recommend --role default-video --json

# 2. Older CLI without --role support. The role TAGS still ship in the catalog,
#    so filter them client-side. This rung works on any CLI with --json.
higgsfield model list --json \
  | jq -r 'map(select((.tags // []) | index("role:default-video"))) | .[0].id // empty'

# 3. Neither returned anything (thin/empty catalog, or role tags not deployed yet)
#    → use the fallback literal from the table below.
```

`higgsfield model roles` lists every role the connected account can see. `higgsfield model
list --role <role>` lists every candidate for a role, best first, when you want to show the
user options rather than pick one.

If rung 1 fails with an unknown-flag error, that is an old CLI — go to rung 2, do not report
a failure to the user. A catalog is per-credential and has been observed returning anywhere
from 6 to 84 entries, so thin results are normal. Degrade quietly; never abort a generation
because role resolution came back empty.

### Fallback literals

Used **only** when rungs 1 and 2 both come back empty. These are the last id known to fill
each role at the time of writing and they may be stale — the role tag always wins.

| role | fallback id |
|---|---|
| `default-image` | `gpt_image_2` |
| `text-render-image` | `gpt_image_2` |
| `character-image` | `text2image_soul_v2` |
| `identity-edit-image` | `seedream_v4_5` |
| `logo-vector-image` | `recraft_v4_1` |
| `marketing-image` | `marketing_studio_image` |
| `default-video` | `seedance_2_0` |
| `fast-video` | `seedance_2_0_mini` |
| `cinematic-video` | `cinematic_studio_3_0` ⚠ unverified |
| `marketing-video` | `marketing_studio_video` |
| `default-audio` | `seed_audio` |
| `voiceover-audio` | `inworld_text_to_speech` |

⚠ **Verify a fallback before submitting it.** A fallback is a guess about the past, so confirm
it still resolves rather than sending a job that errors:

```bash
higgsfield model get <fallback_id> --json >/dev/null || echo "fallback is stale — ask the user"
```

The `cinematic-video` fallback is flagged because it has never been exercised in this repo. If
it does not resolve, prefer `role:default-video` and tell the user the cinema-grade tier is
unavailable on their account — do not silently substitute a look they did not ask for.

This table is the **only** place in this skill that hardcodes a model id. Do not copy these
literals into prose, examples, or other reference files.

## Step 2 — Load the live parameters

Once you have a concrete id, read its real schema before submitting. Never assume an aspect
ratio, duration, or resolution is accepted — the accepted sets differ per model and change
per release.

```bash
higgsfield model get <resolved_id> --json | jq '{aspect_ratios, durations, parameters, medias}'
```

The CLI clamps an out-of-range value to the nearest allowed one and reports an
`adjustments` map (non-fatal). An unknown declared param or an unaccepted media role is a
fatal validation error and is not submitted.

---

## Intent → role

Match by intent, not by surface keyword. When two rows could apply, the higher one wins.

### Image

| # | Intent | Role |
|---|---|---|
| 1 | Brand product visual (Pinterest pin, lifestyle, hero banner, ad pack, virtual try-on) | → `higgsfield-product-photoshoot` skill, NOT this skill |
| 2 | Complete brand identity, logo system, palette, brandbook, packaging system | → `higgsfield-brandkit` skill, NOT this skill |
| 3 | YouTube thumbnail, Shorts cover, Instagram video cover | → `higgsfield-youtube-thumbnail` skill, NOT this skill |
| 4 | Anything with readable text baked in — packaging, labels, banners, UI, typography, product concept with a brand name | `role:text-render-image` |
| 5 | Branded ad image with presenter avatar + product (Marketing Studio shape, RAG over the user's assets) | `role:marketing-image` |
| 6 | People and characters that must stay identity-consistent — aesthetic UGC, fashion editorial, cartoon/stylized character work | `role:character-image` |
| 6b | Same, but driven by a trained **Soul Character** `reference_id` | `role:character-image`, then **confirm the resolved model is Soul-aware** — see below |
| 7 | Edit an existing photo while preserving the person's identity — face-anchored scene swap, outfit change, retouch | `role:identity-edit-image` |
| 8 | Logo, icon, brand mark, flat illustration, true vector/SVG output | `role:logo-vector-image` |
| 9 | Everything else | `role:default-image` |

### Video

| # | Intent | Role |
|---|---|---|
| 1 | Complete narrated explainer from a topic, story, or document | → `higgsfield-video-explainer` skill, NOT this skill |
| 2 | All advertising / commercial / branded video — UGC, unboxing, TV spot, product showcase, product review | `role:marketing-video`. See `marketing-modes.md`. |
| 3 | Edit an existing video from a sketch/timestamp, or reframe it to another aspect ratio | a **workflow**, not a model. See `workflows.md`. |
| 4 | General-purpose video — motion, multi-shot, image-to-video, identity-consistent production work | `role:default-video` |
| 5 | Premium cinema-grade film look at the highest fidelity | `role:cinematic-video` |
| 6 | Cheap or batch video where cost matters more than motion quality | `role:fast-video` |

Image-to-video is `role:default-video` plus a start frame, not a separate role. Only drop to
`role:fast-video` when the user actually asks for cheaper/faster output — never because the
default model's schema looked harder to satisfy.

#### Soul Character images (row 6b)

`role:character-image` covers both plain character work and Soul-driven work, so when you hold
a `reference_id` from `higgsfield-soul-id` you must check that the resolved model actually
accepts it. Not every character model is Soul-aware:

```bash
MODEL=$(higgsfield model recommend --role character-image --json | jq -r '.id')
higgsfield model get "$MODEL" --json | jq '.parameters | keys'   # look for a soul/reference param
```

If the resolved model has no Soul parameter, ask `higgsfield model list --role character-image
--json` for the other candidates and pick the first Soul-aware one. Never drop `--soul-id`
silently — losing it means the user gets a stranger's face, which looks like a generation
failure rather than a routing bug.

### Audio

| # | Intent | Role |
|---|---|---|
| 1 | Sound effects, ambience, foley, impacts, music beds, general audio from text | `role:default-audio` |
| 2 | Spoken narration / voiceover | `role:voiceover-audio` |
| 3 | Soundtrack on a generated ad video | `role:marketing-video` with `--generate_audio true`, not a separate audio job |

---

## Capabilities that are not roles

These are distinct product features, not interchangeable model choices, so they are named
directly. A role would add nothing — there is no second model that does the same job.

| Capability | How to invoke | Notes |
|---|---|---|
| **Virality Predictor** | `higgsfield generate create brain_activity --video <path-or-id>` | Video in, **text report** out. Needs no prompt. Route "analyze this video" / "score this ad" / "is the hook strong" here even though it is filed under text/analysis. |
| **3D asset from reference images** | `higgsfield generate create multi_image_to_3d --image ... --image ...` | 1–4 object/product images, returns a mesh/GLB. Use `--should_texture true` when texture matters. |
| **Auto image routing** | the `Auto` image model | Picks an image model from the prompt. Use when the user's intent is open and you do not want to commit. There is no video equivalent. |
| **Workflows** | `higgsfield generate workflow <name> ... --wait` | Separate from models; they do not appear in `higgsfield model list`. See `workflows.md`. |

## Specialist looks with no role

Some models exist for a specific aesthetic rather than a job a role can name — anime and
bold stylized output, experimental open-weight looks, physics-forward motion,
fastest-possible drafts, Veo-format-bound work, specialist legacy music/SFX models.

There is deliberately no role for these, because "the anime one" is a taste call the user
makes, not a default. Reach for them **only** when the user names the model or asks for that
specific look. Discover what is actually available by capability tag:

```bash
higgsfield model list --json | jq -r '.[] | "\(.id)\t\(.tags // [] | join(","))"'
```

## Routing rules that survive model churn

These are the judgement calls that stay true no matter which model fills a role.

- **Don't invent model names.** If you did not get an id from role resolution or from
  `higgsfield model list`, you do not have a model. Submitting a guess returns
  `unknown model "..."`.
- **Don't downgrade for schema convenience.** If the role's resolved model fits the intent,
  validate or submit it first. Never switch to a cheaper or older model just because it
  lists a requested duration more explicitly.
- **Don't misroute video analysis because the output is text.** "Analyze this video" is
  video-in/text-out analysis, not text generation.
- **Don't misroute 3D style into 3D asset generation.** "Make a 3D render" is usually an
  image request. `multi_image_to_3d` is for an actual mesh.
- **Don't confuse audio generation with an audio media input.** `role:default-audio` creates
  audio from text. An audio *reference* on a video model is a media role — see
  `media-inputs.md`.
- **Route branded product visuals through `higgsfield-product-photoshoot`** — it adds
  mode-specific prompt templates on top of the image model. Direct generation here is right
  for everything that is not a product photoshoot.
- **Some models reject reference media entirely.** Prompt-only is a per-model fact, so check
  `medias` in `higgsfield model get` rather than assuming. See `media-inputs.md`.
- **When the user names a specific model, use it.** Roles cover the common intents; the rest
  of the catalog exists for users who know what they want. Verify the name resolves before
  submitting.

## Adding a new model

Usually: **do nothing here.** A new model reaches users when fnf tags it into a role — the
catalog is live and this file is already pointing at it.

Edit this file only when the set of *intents* changes (a genuinely new job to be done, or a
new skill takes over a routing row). If you find yourself adding a provider, a parameter, or
an aspect ratio to this file, stop — that belongs in `higgsfield model get`.
