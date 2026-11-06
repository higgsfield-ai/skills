# Stylization — the style contract for AI-generated game assets

Self-contained specification of the stylization layer for game pipelines.
Owns everything that makes independently generated assets look like ONE game.
Designed to be dropped into any game-generation skill: if your pipeline
generates a single pixel of game art, it consumes this contract.

**Interface in one paragraph:** the pipeline derives ONE text string (the
STYLE FORMULA) per game, gets it user-approved once, then inserts it
byte-identical into every asset-generation prompt of every subsystem
(sprites, animations, tiles, backgrounds, textures, 3D). This file defines
how the formula is built, how prompts are assembled around it, which models
to call with what parameters, and how style consistency is verified.

---

## 1. Why stylization exists

Every asset is produced by an independent model call — the model has no
memory of previous calls. Different subsystems (and different team members'
skills) generate different asset kinds. Without a shared rule the result is
"three different games on one screen": photoreal floor + pixel-art hero +
cartoon background.

The STYLE FORMULA is the glue: the only piece of shared context that travels
into every generation.

## 2. STYLE FORMULA recipe

One English paragraph, **60–90 words**, composed once per game right after
the design brief is parsed, shown to the user for approval, stored in the
pipeline's state (e.g. `gdd.json.style_formula`).

Concatenate five blocks, in order:

| # | Block | Pins down | Example |
|---|---|---|---|
| 1 | Rendering style | what it's "drawn with" | `flat vector cartoon with soft gradients` / `chunky pixel art, 32x32 grid feel` / `soft hand-painted gouache` |
| 2 | Shape & line language | silhouettes and outlines | `rounded blobby shapes with thick dark-plum outlines` |
| 3 | Palette **by role** | readability, not uniformity | `environment in deep violet stone with charcoal shadows, hero in warm coral-cream tones contrasting the surroundings, hazards and pickups marked with acid-green glow` |
| 4 | Light & mood | one clause | `moody but playful underground atmosphere, flat ambient light` |
| 5 | Game-readability | contrast + **perspective word** | `high contrast between game elements and backgrounds, clean readable silhouettes, consistent side-view perspective across all assets` |

Rules:

- **Block 3 is roles, not one global gamma.** Environment gets its base
  colors; the hero gets colors that CONTRAST with that base (the hero must
  pop, never blend); hazards/pickups get one distinct signal hue. A single
  flat color list paints the whole world one gamma and kills element
  readability — style identity lives in blocks 1, 2 and 4, color serves
  readability.
- **The perspective word in block 5 must match the genre**: platformer /
  runner → `side-view`; top-down → `top-down`; puzzle / clicker → `flat
  frontal`. A top-down game with a side-view hero sprite is the most common
  cross-asset failure; the formula is where it is prevented. (3D pipelines:
  see section 8 — the perspective word is replaced, not reused.)
- If the user supplied a style reference image, describe ITS rendering style
  in your own precise words in block 1 — never paste image URLs into the
  formula.
- Do NOT put into the formula: asset-specific content (that's the per-asset
  description), background/keying instructions (that's the kind suffix),
  pixel dimensions or resolutions.

### STYLE TOKEN (compressed form)

Some downstream fields are length-limited (e.g. Meshy `texture_prompt`
≤800 chars, longer returns `400` — the full formula usually fits; some UI
fields may not). When a consumer cannot take the full formula, it takes the
**STYLE TOKEN**: blocks
1 + 3-condensed + one accent from block 4, ≤120 chars, derived ONCE from the
approved formula and then also frozen byte-identical. Example:
`flat vector cartoon, deep violet dungeon palette, glowing teal accents, warm amber torchlight, thick dark-plum outlines`.
The formula is the source of truth; the token is its compression — never
maintain two competing style strings.

## 3. The byte-identical contract

> The formula is inserted into EVERY generation prompt of EVERY subsystem
> **without changing a single byte**. No paraphrasing, no shortening, no
> "improving". Including single-asset regenerations during iteration.
> Re-deriving the formula mid-game is allowed only when the user explicitly
> asks to change the art style — that re-opens the approval gate and
> invalidates all existing assets.

Consumers and their obligations:

| Consumer | Obligation |
|---|---|
| Static asset generation (sprites, tiles, backgrounds, UI) | formula verbatim in every prompt (assembly in section 4) |
| Character animation (sprite-sheet generation from a base sprite) | formula verbatim in sheet prompts; the animation view parameter MUST match the formula's perspective word (`side-view` → sidescroller view, `top-down` → top-down view) |
| Environment textures | formula verbatim + seamless suffix (section 4) |
| 3D (image-to-3D, e.g. Meshy/Tripo) | formula verbatim in concept/reference image prompts; formula (or token if limited) in `texture_prompt`; style fixes via retexture, not mesh regeneration (section 8) |
| Level/map presentation sheets | formula or token in the sheet prompt so map icons match the asset kit |

## 4. Prompt assembly for 2D assets

Every asset prompt is a concatenation of exactly four parts, in order:

```
<kind template> + <asset description> + <STYLE FORMULA byte-identical> + <kind suffix>
```

The asset description is a stable 3-4 word shorthand from the design doc
(`the round blue slime`), never a character name.

### Kind templates and suffixes

**sprite** (characters, objects — needs transparency)
- template: `game sprite of <description>, single character/object, full body visible, centered,`
- suffix: `, on a solid uniform bright <KEY COLOR> background, no shadows cast on the background, no ground plane, nothing cropped at the edges`

**tile** (repeating surfaces)
- template: `seamless tileable game texture tile of <description>, uniform pattern density,`
- suffix: `, perfectly seamless edges that wrap horizontally and vertically, no border, no vignette, flat even lighting, no single focal object`

**background** (full-frame)
- template: `game background of <description>, wide establishing view,`
- suffix: `, no characters, no UI elements, slightly muted detail so foreground game elements stay readable, soft depth layering`

**texture** (3D surface)
- template: `seamless tileable surface texture of <description>,`
- suffix: `, perfectly seamless edges, flat even lighting, no perspective, no objects, photographed-flat appearance`

**ui** (buttons, icons — needs transparency)
- template: `game UI element: <description>, single element, centered,`
- suffix: `, on a solid uniform bright <KEY COLOR> background, crisp edges, no drop shadow outside the element`

## 5. Key-color selection (the "green screen")

Models cannot output alpha; asking for "transparent background" produces a
fake checkerboard. Transparent assets are generated on a solid key color and
keyed out in post-processing.

**Choosing the key color is a mandatory per-asset step, driven by the
formula's palette:**

1. default: bright magenta `#FF00FF`;
2. if the asset's own colors (its description OR the formula's role palette)
   are anywhere near pink/magenta/purple → bright green `#00FF00`;
3. if both are taken → bright blue `#0000FF`.

The chosen color goes into BOTH the prompt suffix and the keying script.
Real shipped failure: a pink donut generated on magenta — unkeyable, the
donut hole stayed pink in the game. Post-processing must also clear
ENCLOSED key-colored regions (a donut hole is not connected to the image
corners, so corner flood-fill alone misses it).

## 6. Models and volumes

| What | Model | Params | Volume per game |
|---|---|---|---|
| Sprites, tiles, backgrounds, textures | `nano_banana_2` | resolution `1k`; AR `1:1` (sprite/tile/texture/ui), `16:9` (background) | ≤10 assets, `count: 1` each, all submitted in parallel |
| UI elements | `gpt_image_2` | `high` / `1k`, AR `1:1` | 0–1 |
| Character animation sheets | `gpt_image_2` (5×5 grid in one image) | AR `1:1` | 2–3 sheets max, hero only |
| 3D concept/reference images | `gpt_image_2` or `nano_banana_2` | `1k`, AR `1:1` | one per 3D prop |

- One primary generator (`nano_banana_2`) across asset kinds is itself a
  cohesion win — don't spread kinds across models without a reason.
- Pick resolution at generation time; never upscale afterwards.
- **Regeneration budget: 2 attempts per asset** (style drift / keying /
  tiling failures), then take the best attempt and compensate in code
  (tint, scale, 1px overlap). Style drift usually heals with a re-roll of
  the SAME prompt — it's sampling variance, not a prompt error; only edit
  the description when the content itself is wrong.
- The only legitimate full-set regeneration: the user asked to change the
  whole style (new formula → new approval → all assets redone). Never
  regenerate everything in response to point feedback.

## 7. Scale, proportion and coherence checks

- Every object in the design doc carries `relative_scale` — height in
  hero-units (hero = `1.0`, spike trap ≈ `0.6`, doorway ≈ `2.0`). It drives
  in-game sizing and the contact sheet; it is NOT inserted into generation
  prompts.
- **Contact sheet before asset approval:** paste all sprites side by side at
  their relative scales on a strip of the generated tile. Check with eyes
  (the agent reads the image): proportions read right? hero pops against the
  tile or blends? A problem caught here costs one regen; caught after coding
  it costs a debugging session.
- Per-set style checklist: same rendering style on every asset (block 1)?
  outlines consistent (block 2)? palette roles respected — hero contrasts
  environment, signal hue only on hazards/pickups (block 3)? one perspective
  everywhere (block 5)?
- Final in-game sizes (2D): sprite 128px, tile 256px (power-of-two), background
  1280×720. Downscale with NEAREST for pixel-art formulas (LANCZOS smears
  them), LANCZOS otherwise.

## 8. 2D vs 3D stylization — what changes

3D consumes the same formula but through different mechanics:

| Aspect | 2D | 3D (image-to-3D, e.g. Meshy) |
|---|---|---|
| Style carrier | formula in every asset prompt | formula in the CONCEPT IMAGE prompt; formula/token in `texture_prompt` (Meshy texture model `meshy-n1` takes no `texture_prompt` and paints from the concept image, so the image alone carries the style) |
| Background for subject shots | solid key color (magenta/green) for keying | **pure flat white, no shadow, no ground** — shadows and clutter are the top cause of bad mesh reconstruction; keying is irrelevant, the mesh replaces it |
| Perspective word | `side-view` / `top-down` / `flat frontal` everywhere | replaced by `three-quarter isometric view` on concept images (shows top + two sides — maximum shape information for reconstruction); in-game camera is free |
| Style drift fix | regenerate the asset (budget: 2) | **retexture the same mesh** (`retexture` API with the style string) — never regenerate a well-shaped mesh for color reasons |
| Extra style surface | — | engine lighting: light color, fog and ambient intensity must be derived from formula blocks 3-4, or a perfectly styled texture set still reads off-style in-game |
| Geometry style | — | add a geometry clause to 3D concept prompts when the formula implies it (`low-poly faceted`, `smooth rounded blobby`); polycount tiers: ~8000 hero/interactive props, ~3000 for small decoration (Smart Topology `target_polycount`; `model_type: lowpoly` is deprecated) |

**Full style change in 3D** (user asks to restyle the whole game): new
formula → **re-approval gate** (never skip it) → regenerate textures →
**re-derive engine lighting, fog and ambient from the new formula's blocks
3-4** → revisit the geometry clause. New textures on old lighting and old
primitives read as "a picture slapped on the old game" — this exact failure
shipped once (Roblox-style scene "restyled" to Mafia 3 by swapping textures
only).

**Realism ceiling (say it at the gate):** without mesh generation, characters
and props are primitives — a photoreal target style ("like Mafia 3") cannot
be honestly met; textures will look pasted onto blocks. When the requested
style implies realistic/detailed geometry, state the limit at the approval
gate and offer the achievable version (gritty stylized: dark palette, warm
hard light, fog, film grain) — or route through an image-to-3D mesh provider
if the pipeline has one.

Everything else (byte-identical contract, palette roles, regen budget,
checks) applies to 3D unchanged.
