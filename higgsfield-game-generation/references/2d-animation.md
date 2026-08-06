# 2D Sprite Animation (video-to-spritesheet pipeline)

> **Asset reference for game-generation.** Use for ANY animated 2D asset —
> characters, objects, effects — delivered as a spritesheet. The pipeline:
> key-pose image → `higgsfield generate create` (**`seedance1_5`**) → frame extraction
> (ffmpeg) → frame selection → per-frame background removal → spritesheet
> assembly. Style: the key-pose prompt embeds the STYLE FORMULA per
> `stylization.md` — open it first, as for every asset.

Why video instead of generating frames directly: an image model drawing N
frames independently cannot hold the character identical across frames —
limbs, proportions and details drift, and the animation "boils". A video
model animates ONE image, so every frame is the same character by
construction. We then sample the video back into frames. This trades prompt
control for temporal coherence — the right trade for game sprites.

## Native AutoSprite route — preferred

Use `autosprite` when present in the live model catalog. It owns animation, frame
selection, background removal, and sheet assembly:

```bash
higgsfield model get autosprite
higgsfield upload create ./character.png --json
higgsfield generate create autosprite \
  --image_url "<stable URL from upload output>" \
  --kind walk \
  --video_tier turbo \
  --frame_count 12 \
  --frame_size 256 \
  --remove_bg default \
  --with_sound false \
  --is_humanoid true \
  --wait \
  --json
```

Supported standard kinds and isometric directions come from `higgsfield model get
autosprite`. For `kind=custom`, pass both `--prompt` and `--name`; omit both for
standard kinds. Use the manual pipeline below only when AutoSprite is unavailable or
the project requires explicit control over extracted frames.

---

## Pipeline at a glance

| # | Stage | Tool | Output |
|---|---|---|---|
| 1 | Source image | manifest / user / `stylization.md` pipeline | character or object image |
| 2 | Key-pose image | `higgsfield generate create` → `flux_2` | full-body pose at the action's mid/peak phase |
| 3 | Animation video | `higgsfield generate create` → **`seedance1_5`** | 4 s, 720p, AR = key-pose ratio (explicit); loop: start = end frame |
| 4 | Raw frames | ffmpeg | every frame of the video as PNG |
| 5 | Frame selection | local script | `frame_count` frames (2–64, default 25), evenly spaced, first + last always kept |
| 6 | Alpha | `image_background_remover`, per frame | transparent-background PNGs |
| 7 | Spritesheet | local assembly | grid PNG, metadata encoded in the filename |

Hard rules (each one is a known failure when violated):

- **The subject is NEVER cropped.** Full body in frame at every stage, with
  visible empty margin above the head and below the feet. A key pose, a video
  frame, or a sheet cell that clips the subject is a rejected asset —
  regenerate, do not "fix in post".
- **The video model is `seedance1_5` exactly** — a deliberate pin, declared with its
  reason in this skill's `SKILL.md` frontmatter (`models.pinned`). This pipeline is not
  picking "a good video model"; the frame-extraction and spritesheet stages below are
  tuned to this model's motion cadence at 4 s / 720p, so a newer or better general-purpose
  video model produces *worse* sprites here, not better ones. Do NOT resolve a role for
  this stage and do NOT silently substitute. If the call errors, verify availability with
  `higgsfield model list` and stop to ask — swapping the model means re-tuning stages 4–7.
- **start = end only for loops.** Looping actions pass the SAME image as both
  start frame and end frame. One-shot actions (attack, death, hit, cast) pass
  only the start frame — forcing them back to the start pose ruins the action.
- **First and last extracted frames are always kept** in the selection. For
  loops the last frame is then dropped at sheet assembly (see stage 7) —
  kept during selection, excluded from the sheet.
- **Background removal runs on FRAMES, one by one** — never on the video.

---

## Stage 1 — Source image

What goes in: the character/asset image from the manifest (generated per
`stylization.md`, FORMULA embedded) or supplied by the user. Character,
object, or both in one shot — the pipeline does not care what the subject is,
only that it is fully visible.

If the source already crops the subject (feet cut by the canvas, head at the
edge), it cannot enter stage 2 as-is — regenerate or outpaint it to full body
first. A cropped input guarantees a cropped animation.

## Stage 2 — Key-pose generation (`flux_2`)

**What:** produce the subject in the *mid/peak phase* of the requested action.
The video model animates *around* the image it is given; starting from the
action's characteristic phase is what makes 4 seconds of video read as that
action.

- `idle` → slight lean / relaxed breathing stance
- `walk` / `run` → mid-stride, one leg forward
- `attack` → wind-up (weapon raised / fist drawn back)
- `jump` → crouched anticipation
- `cast` / `effect` → energy gathered at the hands / pre-release
- flames, water, props → the shape at its most typical, not its extreme

**How:** `higgsfield generate create` with model `flux_2`, the source image as media
reference, the STYLE FORMULA verbatim in the prompt, plus the pose
instruction. The prompt MUST demand:

- *full body / full object in frame* — head to feet visible;
- *empty margin above and below the subject* — the motion needs headroom and
  footroom (a jump goes up, a stride extends down; without reserve space the
  video model crops);
- a *clean, uniform, uncluttered background* — it is removed per-frame later,
  and a busy background degrades the matte. **The background color must NOT
  appear anywhere on the subject** — pick it by looking at the subject's
  palette first (green character → magenta background, red/pink character →
  green, neutral subject → any saturated key color per `stylization.md`).
  A shared color is how the remover eats holes into the subject or leaves
  background patches stuck to it.

**Why a separate key pose at all:** feeding the neutral source straight into
video gives generic swaying. The key pose is the steering wheel — it is the
single biggest lever on what action the video actually performs.

Gate: subject fully inside the frame with visible margin top and bottom,
nothing clipped, style matches the FORMULA. Cropped or off-style → reroll
(regeneration budget per SKILL.md: 2 attempts, then best-of).

```bash
higgsfield generate create flux_2 \
  --image ./source-character.png \
  --prompt "<STYLE FORMULA>. <single key-pose instruction>. Full body in frame with empty margin above the head and below the feet. Clean uniform <key color> background." \
  --aspect_ratio 1:1 \
  --resolution 1k \
  --wait \
  --json
```

## Stage 3 — Video generation (`seedance1_5`)

**Fixed parameters:**

| Param | Value |
|---|---|
| model | `seedance1_5` |
| duration | 4 s |
| resolution | 720p |
| aspect_ratio | **= the key-pose image's ratio, passed EXPLICITLY on every call** — never omitted |
| start frame | the stage-2 key pose — always |
| end frame | the SAME image — **looping actions only** |

**Aspect ratio is read off the key-pose file and passed explicitly** (a 1:1
pose → `aspect_ratio: "1:1"`, and so on). "Auto" does not exist as a real
parameter value: omitting the parameter does NOT mean "follow the input" —
it silently falls back to the TOOL's default (shipped failure: an unset
ratio on a 1:1 key pose came back as 3:4). A mismatched ratio reframes the
input, eats the top/bottom margins the key pose was built with, and is the
cheapest way to violate the "subject is never cropped" hard rule.

**Why start = end for loops:** the video model is forced to return to the
exact starting pose, so frame 1 and the final frame are identical and the
cycle closes seamlessly. Without it the loop visibly "jumps" at the wrap
point. **Why not for one-shots:** an attack that must end where it began
turns the strike into a rubber-band; one-shot actions get only the start
frame and play once (`once` in the filename, see stage 7).

**Prompt = ONE action + a mandatory negative block.** The positive part
describes the MOTION and nothing else — not the subject (the image already
is the subject), not the mood, not the scene: "smooth idle breathing cycle,
subtle weight shift", "full walk cycle in place", "single sword slash, fast
wind-up, sharp strike, follow-through". Exactly one action per video; any
second verb in the prompt is a defect.

**The negative block is NOT optional and is appended to EVERY animation
prompt**, because the model fills the fixed 4 seconds with improvisation
wherever the prompt leaves freedom — a positive instruction alone only says
what to do and stays silent about everything else. Two parts:

1. *Camera lock (always):* `camera locked, no camera movement, no zoom,
   subject stays fully in frame, plain static background` — camera drift and
   zoom are the top causes of unusable frames.
2. *Prop & action inertia (always; expand when the subject holds anything):*
   `the character performs ONLY this action, nothing else happens`. If the
   subject carries a prop with an obvious action of its own (weapon, tool,
   instrument), name the prop and freeze it explicitly: `the <prop> stays
   inert and is never used — no firing, no muzzle flash, no swinging, no
   raising it`. Props carry their own learned scenarios (a raised pistol
   "wants" to fire, a bat "wants" to swing); an unfilled cycle duration plus
   an unconstrained prop is exactly how a run cycle gains a gunshot
   mid-video. Shipped failure: a 4 s "run cycle in place" where the model
   fired the held pistol twice — the negative block above is what prevents
   it.
3. *Facing lock (always):* `the subject keeps facing the SAME direction for
   the entire video — never turns around, never rotates toward or away from
   the camera, no head turns past the shoulder`. Game sprites are generated
   facing ONE direction (the engine mirrors them for the other side); a
   mid-video turn poisons every frame after it — half the selected frames
   face the wrong way and the sheet is garbage. Turning is the model's
   favorite filler for loopable actions (idle "look around", walk "glance
   back"), so the lock is mandatory even when the action seems
direction-neutral. The ONLY exception: the requested action IS a turn —
   then it is a one-shot (start frame only, `once`), never a loop.

Loop example (omit `--end-image` for a one-shot):

```bash
higgsfield generate create seedance1_5 \
  --start-image ./key-pose.png \
  --end-image ./key-pose.png \
  --prompt "<one action>. Camera locked, no camera movement, no zoom, subject stays fully in frame, plain static background. The character performs ONLY this action; nothing else happens. The subject keeps facing the same direction for the entire video." \
  --duration 4 \
  --resolution 720p \
  --aspect_ratio 1:1 \
  --generate_audio false \
  --wait \
  --json
```

Gate before moving on: scrub the video — subject never leaves the frame or
gets clipped, no camera motion, **facing direction is identical in the first
and last frame and never flips in between**, loop wrap is invisible (for
loops). Fail → regenerate the video (adjust the motion prompt) before
burning time on frames.

## Stage 4 — Frame extraction (ffmpeg)

Download the result video into the workspace, then dump every frame:

```bash
ffmpeg -i anim.mp4 -vsync 0 raw/%04d.png
```

4 s at native fps yields ~96–120 PNGs. Extract ALL of them — selection
happens in stage 5 on the full set, never via ffmpeg's own fps filter (it
cannot guarantee the exact first/last frames are kept).

## Stage 5 — Frame selection (`frame_count`)

**What:** pick `frame_count` frames, evenly spaced across the full range,
**always including the first and the last** extracted frame.

```python
import numpy as np
idx = np.unique(np.round(np.linspace(1, total, frame_count)).astype(int))
```

(`linspace` endpoints guarantee first + last; `unique` guards tiny counts.)

**Range:** 2–64. **Default: 25** when nothing in the context says otherwise.

**Choosing by context** — the question is "how much does the silhouette
change per beat of this action":

| Action / context | frame_count |
|---|---|
| idle, breathing, hover, flame flicker | 8–16 |
| walk / run cycle — pixel art | 8–12 |
| walk / run cycle — HD sprites | 16–24 |
| attack, hit, jump, one-shot actions | 10–20 |
| fluid motion: cape, water, fire burst, magic FX (HD) | 24–48 |
| unclear / no signal | 25 |

**Why fewer is often better:** every frame is a sheet cell — memory, texture
size, and background-removal calls all scale linearly with it. A walk cycle
reads perfectly at 8 frames (the entire 8/16-bit era proves it); 60 frames of
walk is waste. Spend frames only where the silhouette genuinely changes fast.

## Stage 6 — Background removal (per frame)

Each selected frame: pass its local path to `image_background_remover`; the CLI
uploads it automatically and the completed job returns the transparent PNG:

```bash
higgsfield generate create image_background_remover \
  --image ./selected/0001.png \
  --wait \
  --json
```

**Why per-frame and not the whole video:** the per-image matte is computed
independently and cleanly per frame; the video path optimizes for temporal
smoothness and smears edges across frames — on sprites that shows up as a
halo that flickers. Frames it is, accepting the N calls.

Submit the frames in parallel, poll all to completion (fire-and-forget does
NOT apply — the sheet needs every frame). Gate: spot-check 3–4 frames at
2× zoom — no leftover background patches, no eaten thin parts (blades, hair,
flame tips). A bad matte on the same spot across frames means the stage-2
background was too busy or **shared a color with the subject** → fix there
(change the key color), not by hand-editing mattes.

## Stage 7 — Spritesheet assembly

All transparent frames are composed into ONE grid PNG:

1. **Union bounding box.** Compute the bounding box of non-transparent pixels
   across ALL frames, take the union, crop every frame to that SAME box. This
   anchors the subject identically in every cell — per-frame cropping makes
   the sprite jitter in-game.
2. **Uniform cell.** Pad the union box to a uniform cell size; anchor
   bottom-center (feet stay planted on the ground line across frames).
3. **Loop de-duplication.** For looping animations drop the LAST frame from
   the sheet — it is identical to frame 1 (start = end), and playing both
   makes the loop stall for one beat at the wrap. One-shot animations keep
   every frame.
4. **Grid, not strip.** Lay frames into a near-square grid (24 frames →
   5×5 with the tail row partial). A horizontal strip of 64 cells exceeds
   GPU texture limits. **Total sheet dimension ≤ 4096 px on either side** —
   if it does not fit, downscale the cells, never drop frames.
5. **PNG with alpha**, no compression artifacts.

**Metadata lives in the filename** — no sidecar JSON. The consumer (stage-3
game code) parses everything it needs from the name:

```
{asset}_{action}_f{count}_{cellW}x{cellH}_g{cols}x{rows}_fps{n}_{loop|once}.png

knight_idle_f15_192x256_g4x4_fps12_loop.png
slime_attack_f12_160x160_g4x3_fps14_once.png
torch_flame_f10_96x192_g4x3_fps10_loop.png
```

`f` = frames actually in the sheet (after loop de-dup); `g` = grid; cells
fill left-to-right, top-to-bottom; trailing cells of the last row are empty
and transparent.

**Playback fps** is a recommendation baked into the name: pixel art 8–12,
HD sprites 12–24, **default 12**. Note fps is decoupled from `frame_count` —
15 frames at 12 fps is a 1.25 s loop; pick fps for the feel of the motion,
not to "use up" the frames.

---

## Pixel-art sprites — the quality envelope

Small pixel sprites pass through the same pipeline but only look good
**inside these limits** — choose parameters from them, not from the HD
defaults:

- The video is still generated at 720p from a full-size key pose; the
  pixel-art look is applied at the END — downscale the assembled cells with
  **nearest-neighbor** (no smoothing, no anti-aliasing) to the target size
  from the manifest (e.g. 32/48/64 px).
- **frame_count 8–16, no more.** At small sizes extra frames add shimmer,
  not smoothness — sub-pixel drift between video frames turns into visible
  pixel crawl.
- **Subtle, readable motions** survive the downscale (sway, bob, stride,
  blink). Fine detail motion (fingers, facial expression, thin particles)
  dies below ~64 px — do not request it.
- fps 8–12. Higher framerates at small sizes read as noise.

If the manifest asks for a pixel sprite whose action violates this envelope
(e.g. a 32 px character with a 48-frame cloth simulation), simplify the
action to fit the envelope — that is a planning fix, not a generation fix.

---

## Failure recovery

| Symptom | Cause | Fix |
|---|---|---|
| Subject clipped in the video | key pose lacked top/bottom margin, or camera drifted | back to stage 2: more margin; add "camera locked" to the video prompt |
| Loop visibly jumps at wrap | end frame not passed, or model ignored it | re-check start=end were both set; regenerate video |
| One-shot looks rubber-banded | end frame was passed on a non-loop action | drop the end frame, regenerate |
| Sprite jitters in-game | per-frame cropping instead of union bbox | reassemble the sheet with the union box |
| Flickering halo around edges | busy key-pose background | back to stage 2: flat uniform background |
| Holes in the subject / background patches stuck to it | background color also present on the subject | back to stage 2: pick a key color absent from the subject's palette |
| Subject turns around / changes facing mid-video | facing lock missing from the negative block, or the action invites turning | regenerate with the facing lock; rephrase the action to be direction-neutral ("walk in place" not "walk around") |
| Pixel sprite shimmers | too many frames / AA downscale | cut frame_count to 8–12; nearest-neighbor only |
| Loop stalls one beat at wrap | duplicated last frame left in the sheet | drop the final frame (loops only) |

Regeneration budget per SKILL.md: 2 attempts per stage, then take the best
and compensate downstream.
