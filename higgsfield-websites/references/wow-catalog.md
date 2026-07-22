# wow-catalog — Tier-1 experience techniques (pick in Phase 0, build in Phase 4)

The Tier-1 mechanic is the thing a visitor remembers. One per page, chosen in
the design brief, fully executed — and chosen from THIS catalog, not from the
first idea that comes to mind. Every technique here leans on Higgsfield
generation: the wow is bespoke media responding to input, not a CSS trick.

**The default is the animated website (A4).** Every `--type website` build is
an **animated website** — the seam-locked scroll-scrub camera journey (A4) — and
you do NOT open this menu unless the user EXPLICITLY asked for a different
treatment. Skip straight to `references/scroll-scrub.md`. The rules below apply
only on that explicit-alternative path.

**Selection rules (mechanical):**

1. Pick the technique that pays off the CONCEPT SPINE — the mechanic should
   enact the site's idea (a "calibration" spine wants focus/precision physics;
   an "ascent" spine wants climbing/parallax depth; an "archive" spine wants
   leafing/stacking). Write one sentence in the brief defending the pairing.
2. **Never reuse the previous build's technique** (see the anti-convergence
   ledger below). If the spine genuinely demands a repeat, change its
   expression (different subject, different axis, different payoff).
3. Cinema tier: one Tier-1 from the catalog + motivated reveals. Spectacle:
   one Tier-1 PLUS a second beat mid-page (different technique family) +
   custom cursor.
4. Every technique must be screenshot-safe (initial state fully rendered) and
   reduced-motion-safe (static composed fallback).

## The catalog

### A. Film scrub family (scroll plays generated video)

- **A1 — Single-shot hero scrub.** One ~5s seedance clip from the approved
  hero still (push-in, rack focus, subject turn, light sweep; start ≠ end).
  ffmpeg → ~100 frames → canvas bound to pin progress. The proven baseline.
- **A2 — Long-form chaptered scrub.** The upgrade: 2-4 clips (same grade,
  different beats — e.g. wide establishing → detail macro → reveal) played
  across a LONG pin (300-500vh). Between chapters, pinned text cards, layered
  cutouts, or metric readouts hand off. Many moving parts choreographed on one
  timeline: frames scrub, headline stages swap per chapter, a progress rail /
  readout tracks the journey. This is the awwwards centerpiece — budget it
  only when the page has few other heavy beats.
- **A3 — Product turntable.** Multi-angle generated shots of the SAME product
  (reference-driven so identity holds) or a short orbit clip → frame scrub =
  the user rotates the product by scrolling. For physical-product briefs.
- **A4 — Seam-locked scroll scrub (the "animated website" — DEFAULT for every
  website).** A full-site camera journey through 4–7 generated scenes. Chain
  each leg from the previous rendered leg's ACTUAL boundary frame (grounded
  continuous-forward architecture), or join miniature/isometric dives with
  start/end-frame-locked aerial connectors. Scrub optimized MP4 segments
  directly while semantic chapter copy remains in normal document flow. This is
  what "animated website" means and it is the default experience — reach for
  another technique here ONLY when the user explicitly asked for one. This is a
  specialized pipeline: read and follow **`references/scroll-scrub.md`** before
  boards/assets/code.

### B. Layered depth family (one image becomes a 3D-feeling scene)

- **B1 — Cutout parallax rig.** Take the hero image, cut out the subject
  (`image_background_remover`), generate/outpaint a clean background plate
  behind it (+ optionally
  a mid layer: fog, foliage, particles as transparent PNGs). Stack 3-5 layers
  moving at different rates on scroll AND subtly on cursor. The hero feels
  volumetric. Cheap, robust, dramatic.
- **B2 — Grade-shift interaction pair.** Two renders of the SAME composition
  (image-edit re-grade: dark/dormant vs. lit/alive). Crossfade by cursor
  spotlight (mask follows pointer) or by scroll. The "the site notices you"
  effect.
- **B3 — 3D subject scene.** Approved hero image → `multi_image_to_3d` GLB →
  R3F scene with scroll-driven camera orbit + cursor tilt. Spectacle tier.

### C. Canvas/pixel family (the image itself is alive)

- **C1 — Displacement/liquid hover.** Hero image on a WebGL plane; cursor
  ripples/distorts it (three.js displacement or OGL). Editorial-compatible
  when subtle.
- **C2 — Particle dissolve.** Hero image sampled into canvas particles that
  assemble on load and scatter/reform with scroll or cursor. Good for
  data/tech/AI spines.
- **C3 — Scroll-driven mask reveal.** The page opens inside giant display
  type or a shape; scrolling expands the mask until the media goes full-bleed
  (clip-path or canvas). Strong opener for editorial+cinema hybrids.

### D. Spatial layout family (the page itself moves unusually)

- **D1 — Horizontal cinema rail.** A pinned section pans horizontally through
  a WIDE generated panorama (outpaint the hero sideways) or a sequence of
  scene plates; content cards ride the rail. The scroll axis rotation itself
  is the surprise.
- **D2 — Sticky-stack chapters.** Full-bleed chapters stack/peel over each
  other, each carrying its own plate/loop; type pinned per chapter. Reliable,
  editorial-friendly.
- **D3 — Kinetic type opener.** Massive display type choreographed on scroll
  (per-char stagger, weight/width axis animation on a variable font, lines
  sliding on different tracks) over a generated plate. When the brand voice
  IS typography.

**Banned as Tier-1:** autoplay ambient loop alone (passive), generic fade-in
reveals, particles-behind-text with no interaction, marquee strips, tilt-on-
hover cards. These may exist as seasoning, never as the answer to "what's the
wow."

## Implementation contracts (all families)

- Initial paint is complete: frame 1 / layer stack / unmasked state renders
  before any JS-driven interaction (headless full-page shot shows a finished
  hero).
- Input → response latency feels physical: scrub via ScrollTrigger progress
  (scrub: 0.5-1), cursor via `useMotionValue` + springs. Never `useState` per
  frame, never animating layout properties.
- Reduced motion: the composed final state, static, no pin.
- Mobile: the technique must degrade deliberately (shorter pin, cursor
  effects replaced by scroll equivalents, turntable becomes a swipeable
  sequence) — declare the degradation in the brief.

## Anti-convergence ledger (mechanical, checked in the gate)

The skill must not produce siblings. Before Phase 0 locks, list what the
PREVIOUS build in this chat used (if any) for the six identity axes — then
differ on AT LEAST four:

1. **Palette family** (already a hard ban on repeat)
2. **Type pairing** (no repeat of the exact display face two builds running)
3. **Hero architecture** (image-as-canvas / split / masked / rail…)
4. **Tier-1 technique** (this catalog — no repeat, per selection rule 2).
   EXCEPTION: the animated website (A4) is the default and repeats build-to-
   build by design — it is exempt from this no-repeat axis. When two consecutive
   builds are both animated websites, differ instead on the world/subject,
   journey shape, and the remaining axes.
5. **CTA garment set** (see garment catalog in `image-to-code.md` — zero
   garment overlap with the previous build)
6. **Corner/border language** (sharp vs. soft vs. pill vs. hairline-ruled)

First build in a chat: derive all six from the brief's material world (the
nouns the business actually touches — steel, paper, steam, moss, vinyl) and
say so in the brief. When there is no previous build to differ from, the enemy
is the model's own statistical default — if an axis choice would look at home
in a generic template, re-roll that choice.
