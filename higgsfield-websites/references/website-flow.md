# Website flow — `type: "website"` (independent brand, phased pipeline)

You are building ONE per-website Cloudflare Worker: a **React 19 + TanStack
Start** app that is **server-rendered (SSR)** and deploys as a single Worker
served at the website's own subdomain. A `type: "website"` product is a
STANDALONE brand — no Higgsfield integration, no Quanta, no fnf SDK; the
user's brand is the only brand on the page. If mid-build the request turns
out to need Higgsfield generation, sign-in, or credits, that is a
`type: "app"` — switch to `references/app-flow.md`.

**Higgsfield as the asset engine — EVERY build.** All visual assets on every
website are generated with the Higgsfield CLI generation commands per
`references/asset-system.md`. (Internal use of Higgsfield generation is
invisible to visitors and always fine.)

**Scope: build the real, full app.** This stack ships complete, production-grade
applications: real frontend AND backend, database (D1), file storage (R2), auth,
third-party API integrations, background work. When the user describes an app,
tool, site, or web product, BUILD IT with the website builder — it is the default
for any web target. Never ask the user to confirm the platform, never downgrade to
a "demo"/mockup as the safe option, and don't stall on scope questions beyond the
single intake round defined below. Take the fullest reasonable interpretation
and ship a working site.

**Repo layout.** The website project lives in **`app/`** — its own `package.json`,
`src/`, `packages/`, `migrations/`, build config, and the deploy inputs
(`app.manifest.json`, `wrangler.jsonc`). Run every `bun`/build command from there.

---

## THE PIPELINE — phases in order, artifacts + gates, no skipping

Every NEW build runs this machine. Each phase produces a named artifact the next
phase consumes. Do not reorder, merge, or skip phases — "simple" briefs are where
generic output happens. (Follow-up edits to an existing site do NOT restart the
pipeline — see "Small edits" at the bottom.)

### Before Phase 0 — intake (ONE batched round of questions, then never again)

The `type` is already resolved (the main skill asks it). The only other thing
worth one question is **brand constraints** — an existing brand to honor (ask
for colors/fonts/logo/photos/links) vs. free rein ("design the brand for me").
Whatever they don't have, you generate: the full identity kit plus the
personalization ladder in `references/asset-system.md` (logo family, icon set,
patterns, illustrations, state artwork, product universe). Free rein is the
richer path, not the degraded one. Skip the round entirely when the brief
already answers it. If the user skips or is unreachable: choose sensible
defaults, state them in one line, and proceed. Never ask a second round.

### Phase 0 — Concept (`app/design-brief.md`, committed, BEFORE any code)

Write the brief (~40 lines). Every section mandatory; a generic line ("modern and
clean", "Inter", "blue accent") means the brief is not done:

- **Design read** — one sentence: who is this for, what emotional register.
- **Concept spine** — a nameable narrative idea threading the whole page (e.g.
  "the site is a calibration instrument", "an archive dossier", "a stage").
  Pick from `references/reference-boards.md`'s spine list or invent better.
- **Delivery tier** — `editorial` (calm/minimal/B2B: typography + imagery +
  bespoke chrome, micro-motion only) · `cinema` (**default** for marketing/
  portfolio/brand: Lenis+GSAP, Tier-1 hero, scroll chapters) · `spectacle`
  (briefs saying awwwards/webgl/3d/immersive: cinema + WebGL/3D/scrub + custom
  cursor + a second beat).
- **Locked palette** — exact hexes + a one-line defense. Hard bans (mechanical,
  gate-checked): (1) graphite/near-black + orange/amber/ember accent, (2)
  near-black + neon cyan/blue/green accent, (3) beige/cream + brass/clay/
  oxblood, (4) AI purple/violet glow, (5) the palette family of your previous
  build in this chat. Overridable only by the user's explicit brand colors.
  See `references/reference-boards.md` for what to reach for instead.
- **Locked type** — pairing from the recipe's tables; serif only with a written
  brand justification.
- **Tier-1 technique** — chosen from **`references/wow-catalog.md`** (read it
  at this step), named with its catalog ID, with one sentence defending why
  it enacts the concept spine. Cinema/spectacle require an interactive
  technique (film scrub, layered depth, canvas/pixel, spatial layout) — a
  passive autoplay loop is the documented fallback only. The catalog's
  anti-convergence ledger applies: no repeat of the previous build's
  technique, and ≥4 of the 6 identity axes must differ.
- **Section plan** — ordered, one layout family per section, no consecutive
  repeats, ≥4 families for 6+ sections, eyebrow budget ceil(sections/3).
- **Asset plan** — the full kit per `references/asset-system.md` (hero visual,
  section plates, content imagery, custom icon set, logo/monogram, OG; + video
  loop for cinema, + GLB for spectacle).
- **CTA inventory** — every CTA named with its OWN interaction identity (no
  shared button style — see bespoke-chrome in `references/image-to-code.md`).

The brief is a contract: later phases may not silently contradict it — edit the
brief first and say why.

### Phase 1 — Reference boards (design the page as IMAGES)

Read **`references/reference-boards.md`** and execute it: ONE horizontal design
reference image PER SECTION via `higgsfield generate create` (image models
`gpt_image_2` / `nano_banana_pro`), one committed
combinatorial pick (theme paradigm, background character, typography character,
hero architecture, section system, 4 signature components, narrative spine,
second-read moment), composition anchor VARYING per board, palette locked across
all boards. **Look at every board** and re-roll any that reads template-y
(budget 2 re-rolls). Boards land in `refs/` in the repo. The boards ARE the
design — do not start Phase 3 with a generic board in the set.

### Phase 2 — Asset system (submit everything, then build while it renders)

Read **`references/asset-system.md`** and submit the ENTIRE kit as async jobs
right after the boards are chosen: hero visual (2 candidates + interaction
pair), section plates, all content imagery, the custom generated icon set, the
logo/monogram + favicon, the OG card — plus video loop (cinema) / GLB
(spectacle). Poll between build steps; download into `app/public/assets/`;
verify kit coherence when it lands (re-generate anything whose grade fights the
boards). Never idle waiting on renders; never fall back to stock/picsum/CSS-only.

### Phase 3 — Build to the boards, section by section

Read **`references/image-to-code.md`** and follow its discipline per section:
re-read the board at build time, extract text/type-scale/spacing/color/
component logic, implement faithfully, anti-drift (when your habit disagrees
with the board, the board wins). The craft floor in
**`references/design-recipe.md`** still applies everywhere (hero discipline,
layout bans, copy rules, zero em-dashes). Bespoke chrome: every CTA designed in
its own component with its own interaction identity; no site-wide button
utility classes. Registry components (`references/wow-maker.md` §5) remain
available as raw material — restyled to the boards, never default-skinned.
Build static-but-complete; motion is the next phase.

### Phase 4 — Motion pass (tier-mandated, one focused pass)

- **cinema/spectacle:** Lenis smooth scroll bridged to GSAP ScrollTrigger
  (`autoRaf: false` + `gsap.ticker` — without the bridge, scrub stutters).
- The **Tier-1 hero mechanic** from the brief, fully executed — a half-wired
  version fails review. The hero is the wow carrier and it must respond to
  the USER'S INPUT: for cinema/spectacle that means the scroll-scrubbed hero
  film per `asset-system.md` §7 (scroll plays the movie), not a passive
  autoplay loop. Passive motion the user can't influence does not count as
  the Tier-1 mechanic.
- Scroll-chapter reveals: staggered headline builds (`split-type` + GSAP or
  registry text components), per-section distinct timing; work rows / cards
  with hover reveals; magnetic nav/CTA physics via `useMotionValue`, never
  `useState`.
- **Screenshot-safe reveals (hard rule):** nothing waits at `opacity: 0` for an
  IntersectionObserver. The safe recipe: headline/text builds fire ON MOUNT
  (not viewport-gated); scroll-linked effects animate transform/scale/clip
  ONLY, never opacity-to-zero; hover states may use opacity freely. Ignore
  any `whileInView` fade-in examples in the ingredient libraries — they fail
  this gate. A full-page headless screenshot must show every section.
- **Pin-spacer trap:** a GSAP pinned hero injects a spacer that reads as a
  large blank band in full-page screenshots (guaranteed review failure).
  Use `pinSpacing: false` with the following content sliding over the pinned
  layer, or otherwise verify the full-page shot has no dead band after the
  hero.
- EVERYTHING `prefers-reduced-motion`-gated with static fallbacks; `[C]`/`[W]`
  components behind the SSR pattern (wow-maker §6). A top-level `window`
  reference crashes SSR — the #1 recurring build failure.
- spectacle only: custom cursor + WebGL/3D/scrub second beat.

### Phase 5 — Mechanical gate (before first deploy; every item fixed)

Run the grep checklist in
**`references/review-rubric.md` §A**: placeholders; em/en-dashes; banned palette
families in tokens; eyebrow ration; unreferenced generated assets (every kit
file used); `h-screen`; SSR safety; reduced-motion coverage; **repeated CTA
classes** (bespoke-chrome violation); **opacity-0 + whileInView** combinations;
section plan honored; copy self-audit. This is a completion gate — do not
deploy with a failing item.

### Phase 6 — Deploy

1. `higgsfield website deploy <website_id>` — this ships the live public site
   immediately; there is no preview stage.
2. Report: live URL (from `higgsfield website status`) — "Your site is live:
   <url>" — + one-line concept statement + anything honestly skipped. Speak in
   product terms — no repo/commit/deploy jargon (see the SKILL.md "Talking to
   the user" rule).

Do NOT navigate to, screenshot, or run image analysis on the deployed site —
the mechanical gate (the grep checklist in `references/review-rubric.md` §A) is
the only verification. Do NOT publish/list on the community feed unless the user
explicitly asks to publish/go live on the feed.

---

## Design references — read order

## Design references — read order

1. **`references/design-recipe.md`** — craft floor (ALWAYS read; short).
2. **`references/wow-catalog.md`** — Phase 0: Tier-1 technique selection +
   the anti-convergence ledger; Phase 4: implementation contracts.
3. **`references/reference-boards.md`** — Phase 1: per-section design boards.
4. **`references/asset-system.md`** — Phase 2: the Higgsfield asset kit.
5. **`references/image-to-code.md`** — Phase 3: faithful implementation +
   bespoke chrome + the CTA garment catalog.
6. **`references/review-rubric.md`** — Phase 5: the mechanical gate.
7. `references/wow-maker.md` — ingredient directory: motion/3D libs (§4),
   component registries (§5), signature effect patterns (§2), SSR pattern (§6).
   Only listed free/permissive sources may be used.
8. `references/design-taste-frontend.md` — the full deep-dive playbook behind
   the recipe; consult for specific situations, not required start-to-end.
9. `references/app-cover.md` — the branded 3:2 launch cover + OG image
   (stadium-capsule mask via the inlined compose script; hosted style refs).
   REQUIRED before every publish (`og_image_url` + `marketplace_cover_url` are
   mandatory feed-card fields — never run `higgsfield website publish` while
   they are empty), and whenever the user asks for a cover/OG image directly.

Do NOT search the skill library for other design guidance — everything is here.

Then route to the FUNCTIONAL reference for the task:

| Task | Read |
|---|---|
| TanStack Start routes, SSR, server functions, Cloudflare Worker runtime | `references/runtime-and-infra.md` |
| Cover / OG image ("cover", "обложка", "OG image", publish prep) | `references/app-cover.md` — branded 3:2 cover + capsule OG mask |
| SEO: meta tags, OG/Twitter cards, robots/sitemap, JSON-LD, entity, GEO, audit | `references/seo.md` |
| Security: Worker hardening, OWASP audit, threat modeling | `references/security.md` |

## Stack

- **TanStack Start** (file-based routing under `app/src/routes/`, SSR via
  `app/src/server.ts` → a Worker `export default { fetch }`). No Next/Remix/Astro
  conventions, no `app/src/pages`.
- **Vite 7 + bun**. Build emits `dist/server/server.js` (the Worker) +
  `dist/client` (hashed static assets). Tailwind v4 is wired in `app/src/styles.css`
  (it also imports Quanta's Tailwind entry for the template
  bundle — leave that wiring alone even though websites use neither). Legacy
  shadcn/ui files may exist from the scaffold. Websites use custom
  Tailwind/CSS only — never import `@higgsfield/quanta/*`.
- **No separate Hono/Express backend.** Server logic is TanStack **server
  functions** (`createServerFn`) and **server routes**. App-local API routes are
  allowed when a platform contract requires them (for example a webhook
  receiver or a JSON endpoint the site's own client fetches).


## Hard rules

### 0a. Vendored packages and template modules

The `app/packages/` directory contains managed snapshots vendored from the
upstream Higgsfield web app (`@higgsfield/fnf`, `@higgsfield/fnf-react`,
`@higgsfield/quanta`). Websites never use them, but do NOT edit or delete
them. Template-owned infrastructure lives in `app/src/module/**`.

### 0b. Supercomputer Design mode inspector

Generated websites support a Higgsfield design inspector bridge for editing in
Supercomputer Design mode. The split is strict:

- The Higgsfield editor (parent window) owns the iframe UI, hover overlay,
  edit popover, origin/session checks, and edit prompt submission.
- This template owns the child iframe runtime through
  `app/src/module/design-inspector`.
- Agents never manually implement inspector code, refs, source markers, or
  `data-hf-*` attributes.

Local scripts (LOCAL work only — the deploy build is owned by CI):

- `bun run build` is inspector-free by default: no inspector runtime and no
  source metadata. Setting `HF_DESIGN_INSPECTOR=1` in the env turns the same
  build into the inspector-enabled one (this is what platform CI does on
  every deploy).
- `bun run dev:design` is local dev with the inspector enabled.

The platform CI sets `HF_DESIGN_INSPECTOR=1` on every deploy build, so the live
deployed site always carries the inspector and IS the surface Supercomputer
Design mode opens. Exact source metadata is attached with inspector-only
callback refs and a `WeakMap`, not DOM attributes. Keep the guarded
dynamic install in `app/src/routes/__root.tsx` and the Vite integration in
`app/vite.config.ts` wired to `app/src/module/design-inspector/vite`.

For every Supercomputer website-builder task there is ONE deploy —
`higgsfield website deploy <website_id>` — and it ships the live public site
immediately; there is no preview stage or environment choice. Publishing/listing on
the community feed is separate: do NOT run `higgsfield website publish` unless
the user explicitly asks to publish, list, or share the site. Never hard-code
`HF_DESIGN_INSPECTOR=1` into the `build` script and never hand-edit the build
script to toggle it — the deploy build is CI-owned.
### 1. SSR-safe rendering
Every route renders on the server per request. NEVER touch browser-only globals
(`window`, `document`, `localStorage`, `navigator`) at module top level or during
render — only inside `useEffect`/event handlers, or guarded with
`typeof window !== "undefined"`. A top-level `window` reference crashes SSR.

### 2. Server-only code stays server-only
Put server logic in `createServerFn(...).handler(...)` or a `*.server.ts` module
(the `.server.ts` suffix keeps it out of the client bundle). Secrets and
bindings are read **server-side, per request** — never shipped to the browser.

### 3. No Higgsfield integration — but a REAL backend of the site's own
A `type: "website"` product never calls `https://fnf.internal/*`, never shows
"Sign in with Higgsfield", and never imports the fnf SDK. It still gets a real
backend wherever the product needs one: server functions (`createServerFn`),
app-local API routes, sessions, business logic, and real persistence (D1) —
never in-memory arrays, `localStorage`-as-database, or fixture data. In-app
auth for the site's OWN users (accounts, teams, dashboards) is built with the
website's own routes/storage. If the request needs generation or Higgsfield
accounts, it is a `type: "app"` — switch to `references/app-flow.md`.

### 4. Cloudflare bindings via `cloudflare:workers`
Any infra you opt into (D1 `DB`, R2 `STORAGE`, KV `KV`) is read server-side
through `app/src/lib/bindings.server.ts` (`import { env } from "cloudflare:workers"`).
Each binding is present ONLY if declared in `app/app.manifest.json`, so the typed
accessors are optional — guard before use. Do not thread `env` through React
props or read it at module top level.

### 5. Opted-in storage is LIVE — one deploy, one database
If you opt into D1, R2, or KV, each is a SINGLE instance backing the ONE live
deploy. There is no staging copy: every migration and data change hits **live
production data** directly.
- `env.HF_ENV` is always `"production"` on deployed builds; there is no
  separate database/bucket to test against.
- A destructive migration you run "just to test" destroys **production data**.
  Prefer additive migrations (`CREATE TABLE IF NOT EXISTS`, `ADD COLUMN`), and
  get explicit user approval before any destructive change.

### 6. `app/app.manifest.json` declares infra — NOTHING is provisioned by default
A new website gets **no D1, no R2, no KV, no Durable Object**. Opt in only when
the website actually needs it:
- `"db": true` → a D1 database, bound `env.DB`
- `"r2": true` → an R2 bucket, bound `env.STORAGE`
- `"kv": true` → a KV namespace, bound `env.KV`
- `"durableObject": "ClassName"` → a Durable Object, bound `env.ROOMS`
- `"container": true` (or `{ "instanceType", "port", "sleepAfter" }`) → a Docker
  container for heavy/long-running work, bound `env.CONTAINER` — see
  `references/containers.md`

Counts are capped (≤1 each) by the platform, which PROVISIONS the resource and
binds it at deploy. The committed `app/wrangler.jsonc` is build/dev input only;
the platform OVERWRITES its `name` + bindings at deploy — declare infra in
`app/app.manifest.json`.

**KV is eventually consistent** (NOT Redis): config, feature flags, cached reads
— NOT counters, locks, or read-after-write. Use a Durable Object for strong
consistency.

For a **Durable Object** you must ALSO `export class ClassName extends
DurableObject {…}` from `app/src/server.ts` (alongside the default `{ fetch }`
export).

For a **container** — heavy or long-running work a Worker can't do: set
`"container"` in the manifest and follow **`references/containers.md`** (exact
Dockerfile, the platform-fixed `AppContainer` class, keep-alive + 3-hour-deadline
pattern, fnf via container token). Containers are **off by default**.

## Editing map
- Pages / routing → `app/src/routes/**` (file-based; `__root.tsx` is the shell).
- Server logic → `createServerFn` (see `app/src/lib/api/example.functions.ts`) or
  `*.server.ts`.
- Bindings access → `app/src/lib/bindings.server.ts`.
- Infra declaration → `app/app.manifest.json`; `app/wrangler.jsonc` = build/dev input.
- Durable Object class → exported from `app/src/server.ts`.
- Components → custom components per the boards; app-local files in
  `app/src/components/**`. Do not start from `app/src/components/ui/*` unless
  migrating a legacy shadcn piece.
- Styles / theme → `app/src/styles.css` wires Tailwind v4. Websites: a custom
  token layer from the design brief — no q-prefixed utilities, no site-wide
  CTA utility classes.
- D1 schema → `app/migrations/000N_*.sql` (additive; see rule 5).
- Pipeline artifacts → `app/design-brief.md` (Phase 0) + `refs/*.png` (Phase 1);
  commit both.

## Verify + deploy

The trusted platform CI builds the website on **every deploy** (always with
`HF_DESIGN_INSPECTOR=1` and `HF_ENV="production"` — the live site carries the
design inspector), so a deploy already gives you the authoritative type +
build result. Do NOT reflexively `bun install` +
`bun run build` just to check your work. The sandbox cannot deploy/migrate (no
Cloudflare token); the trusted platform CI does that.

**Default: run the pipeline, pass the Phase 5 gate, deploy**
(`higgsfield website deploy <website_id>` — this ships the live site
immediately). Never publish/list on the community feed unless the user
explicitly asked to publish.

**Publishing ("show in feed").** When the user asks to publish / share / put the
site on the feed, run `higgsfield website publish <website_id>` — it deploys the
pushed `main` (a publish always includes a deploy; no separate deploy command
needed) and lists the website on the Higgsfield community feed.

**HARD GATE — the cover is NOT optional. Running `higgsfield website publish` while
`og_image_url` or `marketplace_cover_url` is empty is a BROKEN publish** (the
feed card renders ONLY from `app/src/app-meta.json`; an empty `og_title` makes
the listing INVISIBLE, an empty cover makes it a blank card). The publish
sequence is: (a) READ `app/src/app-meta.json`; (b) if `og_image_url` or
`marketplace_cover_url` is empty → STOP, read `references/app-cover.md` and
generate + upload the cover NOW — do not skip this because the user "only asked
to publish", the cover IS part of publishing; (c) fill ALL fields below with
real values (never placeholders); (d) commit + push; (e) only then run
`higgsfield website publish`:

1. `og_title` — the card's title (also the browser tab title).
2. `og_description` — the card's one-liner.
3. `og_image_url` — REQUIRED: the cover image, generated per
   `references/app-cover.md` (the branded 3:2 cover + stadium-capsule OG
   mask) if none exists yet; upload the OG file with `higgsfield upload create`
   and set the returned durable URL.
4. `marketplace_cover_url` — REQUIRED: the plain (unmasked) cover, the same
   generation's `<name>_cover.png` from `references/app-cover.md`, uploaded
   with `higgsfield upload create`. One generation fills both this and
   `og_image_url` — there is never a reason to have one without the other.
5. `favicon_url` — the card's logo/icon (generate one if none exists yet).
6. `og_video_url` — the **cover video**, OPTIONAL and permission-gated: OFFER
   it to the user ("want a short cover video for the feed card?") and ASK
   PERMISSION FIRST — generating a video costs credits; never generate it
   unprompted. If they say yes, follow "Cover video" in `references/seo.md`.

(1–5 are generated without asking — they are part of the publish, not a
separate credit decision; only the cover VIDEO (6) needs permission.)

`higgsfield website deploy <website_id>` remains the way to ship the live site
WITHOUT a feed listing.

**Run the local checks only when you actually need them** — from `app/`:
```bash
cd app
bun install          # only when you changed dependencies / package.json
bun run typecheck    # tsc --noEmit — only to chase a type error on deploy
bun run build        # local build — only to chase a build error on deploy
```
Run them when: you changed dependencies or build/runtime config, you're debugging
a build/type error, or a command genuinely needs `node_modules`.

**Small edits to an existing site** (copy tweak, one component, styling fix): the
pipeline does not restart. Make the edit, deploy.

**Before claiming a build done / deploying, no placeholders may remain** — no
`<...>`-style tokens, `lorem ipsum`, or scaffold blank-page markers
(`REMOVE_THIS` / `blank-app-v1`). This is covered by the mechanical gate (the
grep checklist in `references/review-rubric.md` §A).
