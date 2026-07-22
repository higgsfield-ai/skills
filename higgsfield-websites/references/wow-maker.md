# wow-maker — everything you need to make a website wow

This is THE design source for every site you build. There are no fixed templates to
pick and fill — you **compose** a distinctive, award-tier site from the directory
below: bespoke AI-generated assets, signature animation patterns, motion/3D
libraries, and copy-paste component/block registries.

**The mandatory wow on a website is the ANIMATED WEBSITE.** On every
`--type website` build the Tier-1 wow is fixed by the brief's `Animation mode`
(`references/website-flow.md` Phase 0): the DEFAULT is the **animated website** —
the seam-locked scroll-scrub camera journey in `references/scroll-scrub.md` — and
that is what "ships a real wow moment" MEANS here. This file is the ingredient
directory you build the SURROUNDING craft with (bespoke assets, section motion,
component registries); it is NOT a menu of alternatives to the animated website.
Use `design-recipe.md` for HOW to execute with taste; this file is WHAT to build
the supporting layer with.

## What counts as "done" (every site)

Wow is part of DONE, not optional polish. The bar is the `Animation mode` the
brief committed to — nothing lighter:

1. **The Tier-1 wow matches `Animation mode`.** Default `animated-website` → the
   scroll-scrub camera journey is built (component + scene media), per
   `references/scroll-scrub.md` and enforced by the Phase 5 gate item 9f. The
   items below are the craft AROUND it, not a substitute: a ticker, hover motion,
   entrance transitions, animated numbers, a shader gradient, or any single §2
   effect DO NOT satisfy the animated-website requirement. Only when the brief
   records `Animation mode: override — "<user request>"` does a §2 signature
   effect become the Tier-1 wow.
2. **≥1 bespoke generated asset**, downloaded into `app/public/` and actually
   referenced — never stock, picsum, an icon-font hero, or a CSS-only hero. (§1)
3. **Motivated entrance motion** (scroll reveals / spring transitions via
   `motion/react`, GSAP, or a registry reveal), `prefers-reduced-motion`-gated. Not a
   dead static page.
4. **Reach into the component/block directory (§5) instead of hand-rolling** generic
   sections — Tailark for full marketing sections; Magic UI / Cult UI / SmoothUI /
   motion-primitives for effects. Hand-built-from-scratch is slower and more generic.
5. **Where they fit:** an animated headline (`split-type` + GSAP, Magic UI
   `morphing-text`/`aurora-text`) and animated numbers (`@number-flow/react`) instead
   of static text.

**Order of work — the camera journey FIRST.** On the animated-website default,
decide the journey and generate the scene media BEFORE you build the page, so the
scroll-scrub spine drives the design. Do not ship a generic static structure and
plan to "add the animation later" — you won't, and the gate will fail it.

**Restraint is NOT an escape hatch from the animated website.** "Clean",
"minimal", "trustworthy", "Linear-like", "Notion-like" briefs are STILL
`Animation mode: animated-website` — restraint means the journey is *calm and
deliberate* (slower camera, quieter scenes), not absent. A minimal or serious
brief is never an `override`; only the user's explicit request for a different
treatment is. Never use "it's minimal" as cover to ship a plain page or downgrade
the animated website to a soft effect.

## Rules (short)

- **License (the only hard rule for us):** use ONLY what is listed here — every entry
  is free + permissively licensed (MIT / Apache-2.0 / BSD / Zlib / Unlicense). Never
  add a proprietary/paid source (Unicorn Studio, Cult Pro, React Bits, Spline, Rive,
  Origin UI, hover.dev, Aceternity Pro, Motion+). What the end user adds to their own
  site later is their responsibility.
- **SSR tags (Cloudflare Worker):** `[S]` static = server-safe anywhere. `[C]`
  client-only = render under a mounted gate / client boundary, no `window` at module
  top. `[W]` webgl/canvas = `[C]` **plus** `React.lazy` + code-split so it never
  enters the SSR render path. See the SSR pattern at the bottom.
- **Motion budget:** one signature/hero effect per page (don't stack two). Motion must
  be motivated (`design-recipe.md` §6). Honor `prefers-reduced-motion`:
  every animated effect needs a static fallback.

---

## 1. Generate bespoke AI assets — this is our biggest edge

A site with real, generated art looks dramatically cooler than one built from stock,
icon-fonts, CSS gradients, or empty placeholders — and generating it is **our
product's superpower**. Treat bespoke asset generation as a **default step on every
build**, not an afterthought. A hero with a generated image / video / 3D subject is
often the single biggest wow upgrade available.

**Commands** (`higgsfield generate create <job_type> --prompt "…" [flags]`).
Jobs are async — **submit (no `--wait` when batching; each prints a job id) →
poll `higgsfield generate wait <id>` / `higgsfield generate get <id>` → use the
result** (a single job can pass `--wait` to block and print the result URL). If
a param/model is rejected, run `higgsfield model list` +
`higgsfield model get <job_type>` and use what they report.

- Images — `gpt_image_2` (general / art-directed), `nano_banana_pro`
  (photoreal + reference-image driven, e.g. try-ons / product normalization).
- Video — `seedance_2_0` (seamless loops + short films).
- `image_background_remover` — turn a product/subject shot into a transparent
  PNG cutout.
- `multi_image_to_3d` — turn 1-4 approved images into a textured `.glb`
  (repeated `--image`, `--should_texture true`; no rigging).

**Pipeline:** generate → poll → **download into `app/public/`** (e.g. `assets/`,
`media/`, `frames/`) → reference **same-origin** (`/assets/...`). The Worker serves
`public/` at the root. Never ship `<img src="">` / `<video src="">` blanks or
stock/picsum as the final asset.

**What to generate, and where it lands:**
- **Hero image / background** — the centerpiece visual (full-bleed or behind glass).
- **Section textures / atmospheric plates** — backdrops that crossfade per section.
- **Video loop / showreel** — a seamless `seedance_2_0` clip for a hero or band.
- **Product cutouts** — generate the image → `image_background_remover` →
  transparent PNG.
- **3D subject** — approved image → `multi_image_to_3d` → `.glb` for an R3F scene.
- **OG image + favicon** — generate, wire into `<head>` / `app-meta`.
- **People / avatars / testimonial faces, icon & logo glyphs** — bespoke, not stock.

**Rules:** prompt for "no text, no logos, no watermark" (IP-safe + lets you set type
in HTML); match the palette/mood to the brief; downscale large outputs (hero ≤2k,
cutouts ~800px); **verify an image before the expensive `multi_image_to_3d`
step**; for a monochrome look force grayscale in the prompt AND on export.

---

## 2. Signature effects you can build (patterns)

High-impact, award-tier mechanics — build any of these from scratch with the libs
named, adapt them to the brief, combine, or invent your own. These are ideas, not
mandates. Pair every one with generated assets (§1) and the SSR pattern (bottom).

- **Particle-morph hero** `[W]` — ~4-6k Three.js instanced points that morph through
  the scroll (sphere → the product's silhouette → disperse), recolored/relit per
  scroll stage. *Build:* `three` instanced points + a scroll-driven lerp between
  precomputed target positions. *Fits:* premium product/brand (perfume, spirits,
  jewelry, tech). Tune shape/finish/`envColor` to the niche so it never reads generic.
- **Fluid + smooth-scroll studio** `[W]` — a fixed WebGL fluid/gradient backdrop with
  a rotating point cloud, weighty Lenis scroll, GSAP ScrollTrigger reveals, and a
  **staggered 2-column video grid** (not a carousel). *Build:* `three` + `gsap` +
  `lenis` (or `@shadergradient/react` for the backdrop). *Fits:* studios, agencies.
- **Camera-dolly product switcher** `[W]` — the active product dollies toward camera
  while the next approaches from depth and the bg color lerps; drag/wheel/tabs +
  spring snap + autoplay. *Build:* `@react-three/fiber` + `gsap`, scenes as data.
  *Fits:* multi-variant product / flavor showcases.
- **Hold-to-spin 3D showroom** `[W]` — a clay/toy-look turntable: a 3D subject on a
  stepped platform, hold to spin with inertia, click hotspots for detail. *Build:*
  `three` + `@react-three/fiber` + `@react-three/drei` (+ `image_to_3d` assets).
  *Fits:* apparel, physical products, collectibles.
- **Cursor X-ray reveal** `[C]` — a full-screen photo with an aligned "X-ray"
  substrate beneath; a soft feathered lens follows the cursor and dissolves the cover
  into the truth underneath. *Build:* pure React + a CSS `mask-image` at the cursor,
  no 3D/GSAP. *Fits:* editorial deep-dives, "look inside" product stories. (Strictly
  B&W + one breathing accent reads most premium.)
- **Scroll-scrub film** `[C]` — an AI-generated ~15s film extracted to frames and
  drawn on a `<canvas>`, scrubbed forward/back by scroll, caption cards fading in.
  *Build:* generate the film (§1) → ffmpeg frames into `public/frames/` → canvas +
  rAF scrub. *Fits:* high-impact brand reveals / launches (dark, cinematic).
- **Frosted-card scrubber** `[C]` — the warm, light variant: a lifestyle film scrubs
  behind translucent frosted serif cards, then resolves into content panels. *Fits:*
  boutiques, cafés, florists, ateliers.
- **Magnetic gallery wall** `[C]` — an infinite draggable wall of tiles with magnetic
  hover, 3D tilt, a burst intro, and click-to-zoom into a circular gallery. *Build:*
  one shared pointer-physics handler + inertia + modulo wrap. *Fits:* portfolios,
  galleries, visual merch.
- **Kinetic portfolio** `[C]` — the full motion suite: Lenis smooth scroll, GSAP
  reveals + scroll-velocity skew, magnetic elements, custom cursor + hero spotlight,
  one marquee, a Swiper vinyl carousel, live clock. *Build:* `gsap` + `lenis` +
  `swiper`. *Fits:* personal sites, résumés, creative showcases.

---

## 3. Quick "I need X" index

- **Animated hero backdrop** → `@shadergradient/react`, `three`+R3F, Magic UI
  `light-rays`/`warp-background`/`retro-grid`, Cult UI `hero-*`, Kokonut
  `beams-background`, `@tsparticles/slim`, `cobe` (globe) — or generate a hero image/video (§1).
- **Animated headline / text** → Magic UI `aurora-text`/`morphing-text`/`hyper-text`,
  motion-primitives `text-*`, Cult UI `text-animate`, chanhdai `apple-hello-effect`,
  Eldora `*text`, or `split-type` + GSAP.
- **Scroll reveal** → motion-primitives `in-view`/`animated-group`, Magic UI
  `blur-fade`/`text-reveal`, `motion/react` `useInView`, GSAP ScrollTrigger.
- **Marquee / logo strip** → Magic UI `marquee`/`scroll-based-velocity`,
  motion-primitives `infinite-slider`, Animata/Eldora `marquee`.
- **Card with flair** → Magic UI `magic-card`/`neon-gradient-card`, motion-primitives
  `tilt`/`border-trail`, Cult UI `shift-card`, SmoothUI `glow-hover-card`.
- **Nav / dock / command** → shadcn `navigation-menu`/`command`, Cult UI
  `dock`/`floating-panel`, motion-primitives `dock`.
- **Animated numbers** → `@number-flow/react`, motion-primitives `sliding-number`,
  Magic UI `number-ticker`.
- **Custom cursor / magnetic** → motion-primitives `cursor`/`magnetic`, Magic UI
  `smooth-cursor`, SmoothUI `magnetic-button`.
- **Full marketing section** (hero/features/pricing/testimonials/CTA/footer) → **Tailark**.
- **App shell / dashboard / auth / table / chart** → **shadcn blocks**.
- **Confetti / celebration** → `@tsparticles/confetti`, Magic UI `confetti`.
- **3D scene / particle field** → `three`+R3F+`drei` (+`@react-three/postprocessing`, `maath`).

---

## 4. Framework toolkit (npm deps — add to `app/package.json` when used)

| Library (npm) | License | Wow it adds | SSR |
|---|---|---|---|
| `motion` (`motion/react`) | MIT | enter/exit (`AnimatePresence`), layout/FLIP, springs, `useScroll`/`useInView`, gestures | `[C]` |
| `gsap` + `@gsap/react` | GSAP Standard License (free, all plugins) | ScrollTrigger pinned/scrubbed sequences, timelines, `SplitText`; use `useGSAP()` | `[C]` |
| `lenis` (`lenis/react`) | MIT | weighted buttery smooth scroll; `<ReactLenis root>` | `[C]` |
| `three` + `@react-three/fiber` + `@react-three/drei` | MIT | real-time 3D, GLTF/PBR, glass, particle fields, camera flythroughs | `[W]` |
| `@react-three/postprocessing` + `postprocessing` | Zlib/MIT | bloom, DOF, glitch, chromatic aberration on the R3F stack | `[W]` |
| `@shadergradient/react` | MIT | premium animated 3D gradient hero/section backdrop (peers: `three`, `@react-three/fiber`, `three-stdlib`, `camera-controls`) | `[W]` |
| `@tsparticles/react` + `@tsparticles/slim` / `@tsparticles/confetti` | MIT | particle fields, interactive backgrounds, confetti (vanilla canvas) | `[C]` |
| `cobe` | MIT | the 5KB rotating WebGL globe | `[W]` |
| `ogl` | Unlicense | bespoke custom-shader hero without three.js bulk | `[W]` |
| `maath` | MIT | math/easing helpers for R3F (point spheres, `easing.damp`) | `[S]` |
| `animejs` (v4) | MIT | SVG line-draw/morph, staggered reveals, timelines | `[C]` |
| `@number-flow/react` | MIT | animated odometer number/price transitions | `[C]` |
| `split-type` | MIT | split text into lines/words/chars (pair with GSAP/Motion) | `[C]` |
| `swiper` | MIT | touch sliders / coverflow carousels | `[C]` |

drei caveat: use `<Environment files={…}>` with a self-hosted CC0 HDRI in `public/`,
not `preset=` (it fetches a CDN at runtime). Keep all `three`/shader code in a
`React.lazy` + mounted client boundary.

---

## 5. Component & block directory (copy-paste; the source lands in the repo)

`shadcn add` drops the component SOURCE into `app/src/components/` — the user owns it.
Namespaced registries must be registered in `app/components.json` first (block below);
URL-based ones install directly.

### `app/components.json` → `registries`
```jsonc
"registries": {
  "@magicui":           "https://magicui.design/r/{name}.json",
  "@cult-ui":           "https://www.cult-ui.com/r/{name}.json",
  "@smoothui":          "https://smoothui.dev/r/{name}.json",
  "@ncdai":             "https://chanhdai.com/r/{name}.json",
  "@motion-primitives": "https://motion-primitives.com/c/{name}.json",
  "@kokonutui":         "https://kokonutui.com/r/{name}.json",
  "@tailark":           "https://tailark.com/r/{name}.json",
  "@eldoraui":          "https://eldoraui.site/r/{name}.json"
}
```
(`@shadcn` is built in. Verify a URL at wire-time if an `add` 404s.)

### shadcn/ui — base layer + app blocks · `npx shadcn@latest add <name>`
Primitives (mostly `[S]`/`[C]`): `button` `card` `input` `select` `dialog` `drawer` `sheet` `sonner` `tabs` `accordion` `breadcrumb` `navigation-menu` `command` (⌘K) `table` `skeleton` `spinner`. Rich `[C]`: `carousel` (embla), `data-table` (TanStack Table), `chart` (recharts), `date-picker`. Full blocks: `sidebar-07/03/08/15/16`, `dashboard-01`, `login-01/03/04`, `calendar-01…32`, `products-01`.

### Magic UI — effects/backgrounds/text · `npx shadcn@latest add "https://magicui.design/r/<name>.json"`
Backgrounds: `light-rays` `[W]`, `warp-background` `[C]`, `retro-grid` `[S]`, `ripple` `[S]`, `meteors` `[S]`, `particles` `[C]`, `flickering-grid` `[C]`, `dot-pattern`/`grid-pattern` `[S]`, `border-beam` `[S]`. Cards: `magic-card` `[C]`, `neon-gradient-card` `[S]`, `bento-grid` `[S]`, `shine-border` `[S]`. Buttons: `shimmer-button`/`rainbow-button`/`interactive-hover-button`/`pulsating-button` `[S]`. Text: `aurora-text`/`animated-shiny-text` `[S]`, `sparkles-text`/`morphing-text`/`hyper-text`/`number-ticker` `[C]`. Scroll/marquee: `text-reveal`/`blur-fade` `[C]`, `marquee` `[S]`, `scroll-based-velocity` `[C]`. Misc: `globe` `[W]`, `orbiting-circles` `[S]`, `animated-beam` `[C]`, `confetti` `[C]`, `dock` `[C]`, `terminal` `[C]`, `safari`/`iphone` mockups `[S]`, `smooth-cursor` `[C]`.

### Cult UI (free) · `npx shadcn@latest add https://www.cult-ui.com/r/<name>.json`
Heroes: `hero-liquid-metal`/`hero-dithering`/`hero-heatmap` `[W]`, `hero-color-panel` `[C]`, `hero-static-radial-gradient` `[S]`. Backgrounds/shader: `shader-lens-blur`/`canvas-fractal-grid`/`distorted-glass`/`dither-image`/`morph-surface` `[W]`, `bg-animated-gradient`/`bg-media` `[C]`, `stripe-bg-guides` `[S]`. Text: `gradient-heading` `[S]`, `text-animate`/`typewriter`/`pixel-heading-word`/`text-gif` `[C]`. Buttons: `texture-button`/`metal-button`/`neumorph-button` `[S]`, `family-button`/`bg-animate-button`/`border-beam-button` `[C]`. Cards: `texture-card`/`minimal-card`/`cutout-card` `[S]`, `expandable-card`/`shift-card` `[C]`. Nav/misc `[C]`: `dock`/`floating-panel`/`side-panel`/`direction-aware-tabs`/`three-d-carousel`/`feature-carousel`/`logo-carousel`/`dynamic-island`/`sortable-list`/`color-picker`/`terminal-animation`/`animated-number`.

### SmoothUI · `npx shadcn@latest add @smoothui/<name>`
Cards: `apple-invites`/`app-download-stack`/`expandable-cards`/`glow-hover-card`/`scrollable-card-stack` `[C]`. Text: `reveal-text`/`scramble-hover`/`typewriter-text`/`wave-text`/`number-flow`/`price-flow`/`scroll-reveal-paragraph` `[C]`. Buttons: `magnetic-button`/`clip-corners-button`/`dot-morph-button`/`button-copy` `[C]`. Inputs: `power-off-slide`/`exposure-slider`/`scrubber`/`animated-file-upload` `[C]`. Misc: `siri-orb`/`dynamic-island`/`animated-tabs`/`gooey-popover`/`cursor-follow`/`infinite-slider`/`reviews-carousel`/`book`/`animated-avatar-group` `[C]`, `contribution-graph` `[S]`.

### chanhdai (@ncdai) · `npx shadcn@latest add @ncdai/<name>`
Text: `apple-hello-effect` (handwritten SVG signature)/`shimmering-text`/`fluid-gradient-text`/`text-flip` `[C]`, `spinning-circular-text` `[S]`. Hero/bg/cards `[C]`: `hero-01`/`dot-grid-spotlight`/`glow-card-grid`/`testimonial-spotlight`/`team-01`. Inputs `[C]`: `wheel-picker`/`elastic-slider`/`slide-to-unlock`. Marquee/nav: `testimonials-marquee` `[S]`, `logos-carousel`/`line-nav`/`share-menu`/`toc-minimap`/`scroll-fade-effect` `[C]`. Misc `[C]`: `theme-switcher`/`copy-button`/`spotlight-logo`/`icon-swap`/`github-contributions`.

### motion-primitives · `npx shadcn@latest add "https://motion-primitives.com/c/<name>.json"`
Text `[C]`: `text-effect`/`text-shimmer`/`text-morph`/`text-scramble`/`text-roll`/`text-loop`/`spinning-text`/`animated-number`/`sliding-number`. Scroll `[C]`: `in-view`/`animated-group`/`scroll-progress`. Surfaces: `glow-effect`/`spotlight`/`border-trail`/`tilt`/`animated-background` `[C]`, `progressive-blur` `[S]`. Interaction `[C]`: `magnetic`/`cursor`/`dock`/`infinite-slider`/`carousel`/`image-comparison`/`morphing-dialog`/`morphing-popover`/`transition-panel`/`disclosure`/`accordion`.

### Kokonut UI (free) · `npx shadcn@latest add @kokonutui/<name>`
Backgrounds/hero `[C]`: `background-paths`/`beams-background`/`shape-hero`. Cards: `liquid-glass-card`/`tweet-card`/`bento-grid` `[S]`, `card-flip`/`card-stack`/`apple-activity-card`/`carousel-cards` `[C]`. Text: `shimmer-text`/`glitch-text` `[S]`, `type-writer`/`matrix-text`/`dynamic-text`/`scroll-text` `[C]`. Buttons: `gradient-button`/`social-button`/`switch-button` `[S]`, `particle-button`/`attract-button`/`hold-button` `[C]`. AI inputs `[C]`: `ai-prompt`/`ai-input-search`/`ai-voice`/`action-search-bar`/`file-upload`. Nav/misc `[C]`: `smooth-tab`/`toolbar`/`profile-dropdown`/`smooth-drawer`.

### Tailark — full marketing blocks · `npx shadcn@latest add @tailark/<name>` (themes: `dusk` dark, `mist` light) — nearly all `[S]`
Heroes: `hero-section-1/4/7/9`, `mist-hero-section-1`. Features: `features-2/8/11`, `mist-features-3`. Pricing: `pricing-1/4`, `mist-pricing-1`. Testimonials: `testimonials-1/4`, `mist-testimonials-2`. CTA: `call-to-action-1/3`. Footer: `footer-1/4`, `mist-footer-2`. Also: `faqs-2` `[C]`, `stats-1`, `logo-cloud-1`, `integrations-1`, `team-1`, `comparator-1`, `content-1`, `contact-1`/`login-1`/`sign-up-1` `[C]`.

### Animata · `npx shadcn add https://animata.design/r/<category>/<name>.json`
Backgrounds: `animated-beam`/`blurry-blob`/`moving-gradient` `[S]`, `shooting-stars`/`interactive-grid` `[C]`, `boids-ecosystem` `[W]`. Buttons: `ai-button`/`shining-button`/`duolingo`/`slide-arrow-button` `[S]`, `ripple-button` `[C]`. Cards: `flip-card`/`animated-border-trail` `[S]`, `glowing-card`/`tilted-card`/`card-stack`/`expandable` `[C]`. Text: `animated-gradient-text`/`glitch-text` `[S]`, `typing-text`/`wave-reveal`/`counter`/`scroll-reveal` `[C]`. Misc: `marquee`/`spinner` `[S]`, `animated-dock`/`cursor-tracker`/`trailing-image`/`images-reveal`/`orbiting-items`/`split-reveal` `[C]`.

### Eldora UI (@eldoraui) · `npx shadcn@latest add @eldoraui/<name>`
Text `[C]`: `wavytext`/`blurintext`/`wordpullup`/`letterpullup`/`fadetext`/`gradualspacing`/`multidirectionslide`/`scaleletter`/`docktext`. Backgrounds: `novatrixbackground` `[W]`, `grid`/`hackerbackground`/`photonbeam` `[C]`. 3D/maps: `cobeglobe` `[W]`, `map`/`animatedframeworks` `[C]`. Sections/misc: `marquee` `[S]`, `animatedlist`/`testimonialslider`/`logotimeline`/`integrations`/`terminal` `[C]`, `cardfliphover`/`animatedbadge`/`animatedshinybutton`/`livebutton` `[S]`, device frames (`safaribrowser`/`macbookpro`/`iphone17pro`/`ipad`/`browser`) `[S]`.

---

## 6. SSR pattern (use for every `[C]` / `[W]` item)

```tsx
// app/src/components/client-only.tsx — render children only after mount
import { useEffect, useState, type ReactNode } from "react";
export function ClientOnly({ children, fallback = null }: { children: ReactNode; fallback?: ReactNode }) {
  const [m, setM] = useState(false);
  useEffect(() => setM(true), []);
  return m ? <>{children}</> : <>{fallback}</>;
}
```
```tsx
// [W] WebGL: lazy + ClientOnly so three/shaders never run during SSR
const Scene = lazy(() => import("./scene")); // default export
<ClientOnly fallback={<div className="min-h-dvh bg-[var(--bg)]" />}>
  <Suspense fallback={null}><Scene /></Suspense>
</ClientOnly>
```
Gate motion behind reduced-motion: `useReducedMotion()` (Motion) or
`matchMedia("(prefers-reduced-motion: reduce)")`, and render the static fallback when set.
