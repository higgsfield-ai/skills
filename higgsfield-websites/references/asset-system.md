# asset-system — the Higgsfield-generated visual system (Phase 2)

The whole point of this skill: sites built here look expensive because **as
much of the visual layer as possible is bespoke-generated on Higgsfield** — not
stock, not icon fonts, not CSS approximations. One brief → one coherent
generated visual system. Treat this phase as designing a brand asset kit, not
"getting a hero image".

Commands (all async — submit everything up front with
`higgsfield generate create <job_type> …` WITHOUT `--wait` so each returns a
job id, build while rendering, poll `higgsfield generate wait <id>` /
`higgsfield generate get <id>`). Job types: `gpt_image_2` (art-directed
images) / `nano_banana_pro` (photoreal + reference-driven images),
`seedance_2_0` (seamless video loops), `image_background_remover`
(transparent cutouts), `multi_image_to_3d` (image(s) → GLB; 1-4 repeated
`--image` flags, `--should_texture true`), `bytedance_image_upscale`
(upscale), `outpaint` (extend an image). Media flags (`--image`,
`--start-image`, …) accept a local file path or a UUID of a prior job/upload —
the CLI auto-uploads paths. If a param/model is rejected, run
`higgsfield model list` + `higgsfield model get <job_type>` and use what they
report.

## The asset kit (generate per tier; palette-locked to the boards)

**Precedence rule: the user's own assets always win.** Anything the user
provides (logo, brand marks, product photos, team photos, fonts, existing
icon set) is used as-is — never regenerate a replacement for something they
gave you. Generation fills the GAPS only. The one soft exception: if their
photos clash with the chosen direction, offer a re-grade of THEIR photos
(image-edit, boards as grade reference) — don't substitute generated
strangers for their real product/team.

Every prompt carries the locked palette (name the hexes/mood words), the
narrative spine motif, and "no text, no logos, no watermark" (you set type in
HTML). Download everything into `app/public/assets/` and reference
same-origin. Downscale: hero ≤2k, cutouts ~800px, icons ~256px.

**Always (every build):**

1. **Hero visual** — the centerpiece. Generate 2 candidates, pick one, and
   consider an interaction pair (e.g. a dark/desaturated grade + a lit/color
   grade of the SAME composition for reveal effects — generate the base, then
   a re-grade via image-edit with the base as reference so they align).
2. **Section plates** — 2-3 background textures / atmospheric plates matching
   the boards' background modes (paper grain, graded gradients, material
   macro shots) so sections aren't flat CSS fills.
3. **Content imagery** — portraits, product shots, project screenshots,
   testimonial faces: everything the sections need, style-matched. Fictional
   project/product UIs are generated as images (never div-built fakes).
4. **Custom icon set** — do NOT default to an icon font. Generate the site's
   icons as ONE consistent set: a single image containing a grid of 6-12
   glyphs in the brand's stroke style + palette ("icon set, consistent
   2px-stroke line glyphs, [motifs], flat on solid background, no text"),
   then slice, or generate individually and run `image_background_remover`
   for transparent PNGs. Same visual weight, same corner language, sized on a
   shared grid. (Library icons — Phosphor/Radix — remain the fallback for
   dense functional UI like form chrome, where 20+ tiny consistent glyphs
   beat generated ones.)
5. **Logo / monogram** — ONLY when the user has no logo: a simple generated
   brand mark or monogram cutout for the nav and the head kit below. If they
   have one, use theirs everywhere and skip this item.
6. **OG image** — a proper 1200×630 social card composed in the brand
   language (generate wide, not a crop of the hero), wired into `<head>`.
   Multi-page sites: distinct OG per major route (same template, swapped
   subject/title), not one card everywhere.
7. **Head kit (the full favicon/meta set — the FILES exist on every build).**
   Derived from the user's own logo when provided, from the generated
   monogram only as the fallback. Work from a high-res source (≥512px,
   downscale — never upscale a small render), background-removed or set on a
   solid brand ground:
   - `favicon.ico` (32) + `favicon.svg` if the mark is simple enough to
     vectorize, else `favicon-32.png` / `favicon-16.png`
   - `apple-touch-icon.png` (180, opaque background, comfortable padding)
   - `icon-192.png` / `icon-512.png` + a **maskable** 512 variant (mark within
     the 80% safe zone) referenced from a minimal `site.webmanifest`
     (name, colors, icons)
   - `<meta name="theme-color">` set to the brand ground (light + dark values
     when the page has both)
   - Full social block: `og:title/description/image/url/type` +
     `twitter:card=summary_large_image`, absolute image URLs
   Sanity-check the favicon at 16px: if the mark turns to noise, use a
   simplified glyph (initial letter on brand ground) for the small sizes
   rather than shrinking the full logo.

**Cinema tier adds:**

7. **Hero video — cinema tier REQUIRES the scroll-scrub, not the loop.**
   (The DEFAULT website is the **animated website** — the full-site seam-locked
   chain in `references/scroll-scrub.md` — whose MP4 chain replaces this single
   hero scrub; see the note after this list. This §7 single-hero recipe is the
   hero mechanic only when the user explicitly asked for a non-animated-website
   treatment.) A
   static image + CSS effect is the floor; an autoplay ambient loop is barely
   above it (it moves, but the user's scroll does nothing — passive motion
   doesn't register as craft). The cinema-tier Tier-1 carrier is the
   **interactive scrub**: the user's scroll literally plays a film. Recipe
   (proven end-to-end):
   - Generate the approved hero image first, then image-to-video
     (`seedance_2_0`, the hero image via `--start-image`) with a slow, cut-free
     ~5s motion whose progression maps to scroll: push-in + rack focus
     soft→sharp, subject turn/eyes to camera, light sweep, object assembling.
     START state ≠ END state, or the scrub has no payoff. Prompt "no cuts, no
     camera shake, slow steady motion only" and name the grade/hexes.
   - ffmpeg: `fps=20,scale=1280:-2` → ~100 jpg/webp frames (a 5s clip lands
     ~4MB at q4 — well under the 15MB cap) → `public/frames/hero/`.
   - Canvas image-sequence renderer bound to the pinned hero's ScrollTrigger
     progress: preload+paint frame 1 IMMEDIATELY (screenshot-safe at scroll
     0), stream remaining frames, cover-fit draw, fall back to nearest loaded
     frame while streaming. Reduced-motion: static final (sharp) frame, no
     pin.
   - **Feed the hero image by job id or path:** pass the approved hero
     generation's job UUID (or the downloaded file path) straight to
     `--start-image` — the CLI resolves UUIDs to prior jobs/uploads and
     auto-uploads local paths.
   - **Ambient loop** (muted autoplay + poster) is the documented FALLBACK —
     acceptable only when the composition genuinely can't carry a scrub
     (dense collage heroes) or video generation failed per the failure rules;
     say so in the report. A mid-page band may still use a loop freely.

For the **animated website (A4 — Seam-locked scroll scrub, the default)**, read
`references/scroll-scrub.md` and let its entry still, exact deployed-segment
posters, and chained MP4s replace the ordinary single hero scrub above. Those
posters also satisfy hero/content imagery for their chapters. Continue the
logo/icon, section-UI, head-kit, and OG work, but do not generate a redundant
second hero film. Batch independent B stills/dives; keep A's exact-frame leg
handoffs sequential even though the default Phase 2 rule prefers submitting
early.

**Spectacle tier adds:**

8. **3D subject** — approved hero image → `multi_image_to_3d` → `.glb`
   for an R3F scene (verify the source image BEFORE the expensive 3D step).

## The personalization ladder — generate what the user doesn't have

When the user arrives with nothing but an idea, you are also the brand studio.
Read what they DO have from intake (logo? photos? brand colors?) and generate
everything missing. Beyond the core kit, reach for these whenever the site has
a natural slot for them — each one compounds the "this was made for me" effect:

- **Brand identity kit** — logo + wordmark + monogram as a consistent family
  (not three unrelated marks): generate the primary mark, then derive the
  others via image-edit with the primary as reference. Favicon renders,
  ink/inverse variants for dark and light grounds.
- **Animated logo sting** — 1-2s image-to-video of the mark assembling or a
  light sweep; use as nav-load flourish or footer sign-off (frames or muted
  video, reduced-motion static).
- **Seamless brand pattern / texture** — a tileable motif in the palette for
  section dividers, card backs, packaging-style bands. Prompt "seamless
  repeating pattern" and verify the tile edge.
- **Spot illustration set** — 3-6 scene illustrations in ONE named style
  (same line weight, same palette, same perspective logic) for features,
  process steps, and about sections. Generate as a batch with the style
  spelled identically in every prompt.
- **State artwork** — 404 page art, empty states, success/confirmation
  moments, loading poster. These forgotten corners are where bespoke sites
  most obviously beat templates.
- **People** — founder/team portraits (stylized consistently if no real
  photos), testimonial faces, community shots — same grade as the rest of
  the kit, locale-appropriate.
- **Product universe** — multiple angles + lifestyle context shots derived
  from one approved product image via reference-driven generation
  (`nano_banana_pro`), so every view is recognizably the SAME product.
- **Restyle what they bring** — if the user has real photos that don't match
  the direction, re-grade them via image-edit with the boards as the grade
  reference instead of discarding them.
- **Diagrams as images** — process flows, architecture "how it works" panels
  composed as art-directed images in the brand language, not box-and-arrow
  divs.
- **Brand sound (sparingly)** — generate a short brand sting or ambient loop
  with an audio model (`seed_audio`) behind an explicit user-triggered toggle
  (never autoplay); fits music/game/creative-studio briefs.
- **Micro-animation sequences** — short generated clips → frame strips for
  hover/scroll micro-moments on signature components (the same pipeline as
  the hero scrub, smaller).

Pick by fit, not by count: 3 ladder items executed coherently beat 8 scattered
ones. Everything joins the same coherence check as the core kit, and every
generated deliverable gets listed in the final report so the user knows what
brand property they now own.

## Rules

- **Submit early, never idle.** All kit jobs go in right after the boards are
  chosen; poll between build steps. A build that waits on renders is
  mis-sequenced.
- **Coherence check:** when the kit lands, view the assets together (read the
  images). Any piece whose grade/palette fights the boards gets re-generated
  with the hexes named harder. A mixed-grade asset kit reads cheaper than no
  assets. **Off-grade video budget: ONE re-roll.** If the re-roll drifts
  scene/composition (video models often do), keep the better take and
  color-grade it toward the palette in post with ffmpeg — a graded first
  take beats a re-roll lottery; regenerate the poster from the graded
  frame 1 so first paint matches playback.
- **Multi-image results:** batch/`count` parameters may return grid sheets
  (e.g. four images as one 2×2) instead of singles. Check what actually came
  back before wiring slots; a consistent grid can be sliced like the icon
  sheet, but don't assume N requests = N standalone files.
- **Failures:** if a generation fails twice, change model or restructure the
  prompt — never silently fall back to stock/picsum/CSS-only. If an asset is
  genuinely unavailable, say so in the final report. Known failure mode:
  **false-positive `nsfw` flags on innocuous product prompts** — the fix is
  removing mood/atmosphere words ("seamless loop feel", "ambient",
  "intimate") and re-describing the shot as a plain product film/photo.
- **Rejects live in `refs/`, not `public/`.** Multi-candidate generations
  (e.g. the 2 hero candidates) leave exactly one winner in `app/public/`;
  move unpicked candidates and intermediates to `refs/` so the
  "everything in public/ is referenced" gate stays clean.
- **Icon sheet slices need background removal.** Slicing a one-image icon
  sheet leaves each cell carrying the sheet's background, which fights page
  backgrounds. Run slices through `image_background_remover` (or generate the
  sheet on a solid chroma ground and key it out) so icons composite cleanly.
- **Everything referenced.** Every downloaded file must be used by a
  route/component (gate-checked). Unused generations are wasted credits;
  missing references are broken slots.
- Monochrome direction → force grayscale in the prompt AND on export.
- People imagery: locale-appropriate, believable, never watermarked stock
  faces; testimonial faces are generated.
