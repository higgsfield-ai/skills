---
version: 0.5.0
name: higgsfield-websites
description: |
  Build, edit, and deploy full-stack websites via the Higgsfield CLI
  (`higgsfield website …`). Each site is a React 19 + TanStack Start SSR app in
  one Cloudflare Worker (D1/R2/KV/DO/Containers). The loop: create →
  repo-access → clone → edit → push → deploy preview. This is the website
  template's AGENTS.md: an IMAGE-GROUNDED, phased build pipeline (intake →
  concept → reference boards → asset system → build-to-boards → motion →
  review gates), hard rules, editing map, verify/deploy/publish flow, and
  per-task references. Everything is here.
  Use when: "build me a website", "make a landing page", "create a web app",
  "build a SaaS dashboard / tool / portfolio", "deploy this site", "edit my
  site", "publish", "ship to production".
  Create requires --type: "website" (no Higgsfield integration) vs "app"
  (Higgsfield sign-in + SDK, Quanta + standard layouts).
  NOT for: single image/video/audio generation (higgsfield-generate), product
  photos (higgsfield-product-photoshoot), marketplace cards
  (higgsfield-marketplace-cards).
argument-hint: "[what to build or edit] [--type website|app] [--env preview|production]"
allowed-tools: Bash
---

# Agent guide — Higgsfield website (full-stack, server-rendered)

You are editing ONE per-website Cloudflare Worker: a **React 19 + TanStack Start**
app that is **server-rendered (SSR)** and deploys as a single Worker served at the
website's own subdomain. The rules below are hard constraints — breaking them ships
a broken or insecure website.

**The bar: a $40k studio build in one try.** This is a user-facing skill. The user
types one sentence and must get an art-directed, bespoke, animated site with a
working preview URL — first attempt, no hand-holding. "Clean but generic" is a
failure. The engine that makes this possible is the pipeline below: the design is
decided as **generated reference images** (not prose), the visual layer is a
**Higgsfield-generated asset system** (heroes, plates, imagery, icons, logo, OG,
video, 3D — as much of the site as possible is bespoke-generated; that is this
product's superpower), and the result is verified by an **adversarial screenshot
review** before you report done.

**Website vs app — the REQUIRED `--type` on create, and what each means:**

`higgsfield website create` requires `--type`, and it is the USER'S choice — ask
in the Phase −1 intake when the request doesn't make it obvious:

- **`--type website`** — a standalone product with NO Higgsfield integration:
  no "Sign in with Higgsfield", no requests to Higgsfield, no fnf SDK (site
  classes (a) and (c) below). Every website gets a fully independent brand
  through the full pipeline: own palette, type, and chrome from the design
  brief. Do NOT import `@higgsfield/quanta/*` or use q-prefixed tokens on a
  website, and no "Powered by / Built on Higgsfield" badges, logos, or
  mentions anywhere in page content — the user's brand is the only brand on
  the page.
  ```bash
  higgsfield website create --type website
  ```
- **`--type app`** — a product tightly integrated with Higgsfield: its users
  Sign in with Higgsfield and generate images/videos through the fnf SDK
  (site class (b); the full auth + D1 contract applies — `references/fnf-sdk.md`
  + `references/auth.md`). An app must look and feel like a Higgsfield
  product: build its UI with **Quanta** (`@higgsfield/quanta` — read
  `references/quanta-design.md` and `app/packages/quanta/ai/AGENTS.md`, use
  its components before writing custom chrome) and start from one of the
  standard app layouts in `references/app-layouts.md` (a different layout is
  fine when the user asks for one). The independent-brand rule does NOT apply
  to apps — Quanta is the brand.
  ```bash
  higgsfield website create --type app
  ```

**Higgsfield as the asset engine — EVERY build.** All visual assets on every
site (website or app) are generated with the Higgsfield CLI generation commands
per `references/asset-system.md`. (Internal use of Higgsfield generation is
invisible to visitors and always fine.)

**Scope: build the real, full app.** This stack ships complete, production-grade
applications: real frontend AND backend, database (D1), file storage (R2), auth,
third-party API integrations, background work. When the user describes an app,
tool, site, or web product, BUILD IT with the website builder — it is the default
for any web target. Never ask the user to confirm the platform, never downgrade to
a "demo"/mockup as the safe option, and don't stall on scope questions beyond the
single intake round defined in Phase −1. Take the fullest reasonable interpretation
and ship a working preview.

**Repo layout.** The website project lives in **`app/`** — its own `package.json`,
`src/`, `packages/`, `migrations/`, build config, and the deploy inputs
(`app.manifest.json`, `wrangler.jsonc`). Run every `bun`/build command from there.

**Higgsfield infrastructure (what these names mean).**

- **fnf** — Higgsfield's backend **API**. Server code reaches it at
  `https://fnf.internal/*` (the platform injects the user's auth on server
  egress). `@higgsfield/fnf` is the SDK and `@higgsfield/fnf-react` its React
  bindings (both vendored in `app/packages/`).
- **Quanta** (`@higgsfield/quanta`) — Higgsfield's app UI design system,
  vendored in the template. MANDATORY on `--type app` builds (the app must
  match Higgsfield's product design — `references/quanta-design.md`); never
  used on `--type website` builds (independent brand, custom Tailwind/CSS).
- **fnf-web** — the upstream Higgsfield web repo the vendored `app/packages/*`
  snapshots come from. You don't edit it.

## Prerequisites

You drive the whole lifecycle through the `higgsfield` CLI, then edit code on the
local filesystem with `git` + `bun`.

1. If `higgsfield` is not on `$PATH`, install it:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. If `higgsfield account status` reports `Session expired` / `Not authenticated`,
   ask the user to run `higgsfield auth login` (interactive) and wait for confirmation.
3. `git` and `bun` are used locally once you clone the repo (lifecycle step 2). The
   CLI itself handles create / deploy / status / db / secrets / delete — and the
   asset generation jobs (`higgsfield generate …`, `higgsfield model …`).

## UX Rules

1. Be concise. No raw website IDs, tokens, or JSON dumps in chat. After a deploy,
   return the preview URL (from `higgsfield website status`) and a one-line summary.
2. Never echo the scoped git token back to the user, and never commit it to the repo.
3. Detect the user's language from the first message and reply in it. CLI flags and
   code stay English.
4. Don't stall on scope questions or ask the user to confirm the platform/build
   target — build the fullest reasonable interpretation and iterate on the live
   preview. Intake is ONE batched round of questions (Phase −1), never a second.
5. **Preview is the default and the only environment you deploy on your own.** Deploy
   `--env production` ONLY when the user explicitly asks to publish / go live / ship.
6. Screenshots of the deployed site belong to the Phase 6 adversarial review (new
   builds and layout-changing edits) — when you can take them (e.g. a browser or
   screenshot tool is available), do; otherwise say the visual review was skipped.
   Don't screenshot outside that review unless the user asks — return the URL.

## Website lifecycle (CLI)

Every hosted website operation maps to a `higgsfield website …` subcommand. The
build/edit loop is: **create → repo-access → clone → edit → commit + push →
deploy preview.**

1. **Create** the website + its git repo. `--type` is REQUIRED and is the USER'S
   choice — ask in the Phase −1 intake when the request doesn't make it obvious
   (see "Website vs app" above). Prints a `website_id` (add `--json` for the raw
   object). Use that id in every later command.
   ```bash
   higgsfield website create --type website   # standalone, no Higgsfield integration
   higgsfield website create --type app       # Higgsfield-integrated (sign-in + SDK)
   ```
2. **Get repo access** — clone URL, branch, slug, and a scoped git token. Clone into a
   directory named after the slug so multiple sites can share the workspace. Pass the
   token via a per-command header so it never lands in `.git/config`.
   ```bash
   higgsfield website repo-access <website_id> --json
   # with the returned repo_url / branch / slug / token:
   git -c http.extraHeader="Authorization: token <token>" clone <repo_url> <slug> && cd <slug>
   ```
   The project lives in `app/` (see Repo layout above).
3. **Edit** the code under `app/`, following THE PIPELINE below for new builds
   (and the hard rules always).
4. **Commit + push.** Run push as its own step and confirm it succeeded — the deploy
   builds from the pushed branch.
   ```bash
   git add -A && git commit -m "<what changed>"
   git -c http.extraHeader="Authorization: token <token>" push origin <branch>
   ```
5. **Deploy the preview** (default). The platform CI builds from the pushed branch and
   returns the build result; a build/type error surfaces here.
   ```bash
   higgsfield website deploy <website_id> --env preview
   ```
   Deploy production ONLY on an explicit publish/go-live request: `--env production`.
6. **Status / live URLs** any time:
   ```bash
   higgsfield website status <website_id>
   ```

Other commands (all take `<website_id>`; add `--json` for machine-readable output):

- **Database (read-only D1):** `higgsfield website db tables <id>`,
  `db schema <id> --table <t>`,
  `db rows <id> --table <t> [--limit N] [--filter col:op[:value]]`,
  `db query <id> --sql "SELECT …"` (single read-only `SELECT`/`WITH`).
- **Secrets (staged until the next deploy):**
  `higgsfield website secrets set <id> --name NAME --value VALUE`,
  `secrets list <id>`, `secrets delete <id> --name NAME`.
- **Publish ("show in feed"):** `higgsfield website publish <id>` deploys the pushed
  branch to PRODUCTION (a publish always includes the production deployment) AND lists
  the website on the Higgsfield community feed — only on an explicit publish/share
  request. `deploy --env production` is the no-feed-listing alternative.
  **MANDATORY before every publish:** fill `app/src/app-meta.json` with real values
  for `og_title`, `og_description`, `og_image_url`, and `favicon_url` (the feed card
  renders ONLY from this file — an empty `og_title` is invisible on the feed), and
  OFFER a cover video (`og_video_url`) with the user's PERMISSION first — see
  "Verify + deploy" below and `references/seo-meta-tags.md`.
- **List / delete:** `higgsfield website list`;
  `higgsfield website delete <id>` permanently removes the site, database, storage,
  and repo — only on an explicit delete request.

---

## THE PIPELINE — phases in order, artifacts + gates, no skipping

Every NEW build runs this machine. Each phase produces a named artifact the next
phase consumes. Do not reorder, merge, or skip phases — "simple" briefs are where
generic output happens. (Follow-up edits to an existing site do NOT restart the
pipeline — see "Small edits" at the bottom.)

### Phase −1 — Intake (ONE batched round of questions to the user, then never again)

Ask only what the brief doesn't already answer (skip answered questions; if
everything is clear, skip the round entirely). Up to 3 questions in the single
batched round:

1. **Site class** — (a) standalone brand/marketing/portfolio site (no Higgsfield
   SDK), (b) Higgsfield-SDK app (generation, media, credits — full auth + D1
   contract applies), (c) product tool/app with its own user accounts. This
   drives the functional route: auth mode, persistence, SDK wiring — AND the
   REQUIRED `--type` flag on `higgsfield website create`: class (b) →
   `--type app`; classes (a)/(c) → `--type website`. The type is the user's
   choice — if the brief doesn't make it obvious, this is the question to ask.
   Classes (a)/(c) get a fully independent brand; class (b) apps are built with
   Quanta + a standard app layout (`references/app-layouts.md`).
2. **Brand constraints** — existing brand to honor (ask for colors/fonts/logo/
   photos/links) vs. free rein ("design the brand for me"). Whatever they
   don't have, you generate: the full identity kit plus the personalization
   ladder in `references/asset-system.md` (logo family, icon set, patterns,
   illustrations, state artwork, product universe). Free rein is the richer
   path, not the degraded one.
3. **Direction** — offer 3 named art directions derived from the brief, each
   with 5-8 vibe words (e.g. "Light editorial Swiss — paper, ink, museum
   captions, one cobalt accent" / "Cinematic product film — dark chrome, graded
   photography, scroll chapters" / "Bold print poster — saturated color fields,
   condensed type, brutalist grid"). Include "surprise me".

If the user skips or is unreachable: choose sensible defaults, state them in one
line, and proceed. Never ask a second round.

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

**App builds (site class (b)/(c)) — how the pipeline vocabulary maps.** The
pipeline is written in marketing-page vocabulary; for an app/tool it applies
with this translation, which is legitimate and expected:

- "Sections" = **screens/states** (including the first-run/empty state, which
  gets its own board — it's the first thing a new user sees).
- "Hero" = the **primary screen's masthead**; the Tier-1 mechanic is that
  screen's signature interaction (e.g. a check-in animation), NOT a marketing
  scroll effect. **Default tier for apps is `editorial`** — a daily-use tool
  must feel instant; cinema is for the marketing site *about* the app, not the
  app itself.
- Layout-variance and scroll-cadence rules apply **within each screen**, not
  across screens that never co-exist.
- Boards for an app depict **the real product UI you will then implement with
  real state** — this is the explicit carve-out from the "no fake product UI"
  ban, which targets div-built fake dashboards on marketing pages. On app
  boards, composition/type/palette/component treatments are binding; **invented
  feature surface is not** (a board that draws extra nav items or modules the
  brief never asked for does not obligate you to build them — note the
  deviation in the review instead).
- An app's "wow" lives in its **signature interactions** (a stamp press, an
  odometer total, a check-in bloom) — precise micro-motion IS the wow bar for
  tools; scroll theater is not.
- The asset kit skews to: icon set, logo/monogram, empty-state artwork,
  onboarding illustration, OG + head kit — not big photography plates.

### Phase 1 — Reference boards (design the page as IMAGES)

Read **`references/reference-boards.md`** and execute it: ONE horizontal design
reference image PER SECTION via `higgsfield generate create` (image models
`gpt_image_2` / `nano_banana_pro`), one committed combinatorial pick (theme
paradigm, background character, typography character, hero architecture, section
system, 4 signature components, narrative spine, second-read moment),
composition anchor VARYING per board, palette locked across all boards. **Look
at every board** and re-roll any that reads template-y (budget 2 re-rolls).
Boards land in `refs/` in the repo. The boards ARE the design — do not start
Phase 3 with a generic board in the set.

### Phase 2 — Asset system (submit everything, then build while it renders)

Read **`references/asset-system.md`** and submit the ENTIRE kit as async jobs
right after the boards are chosen (`higgsfield generate create <job_type> …`
without `--wait` prints a job id; collect the ids): hero visual (2 candidates +
interaction pair), section plates, all content imagery, the custom generated
icon set, the logo/monogram + favicon, the OG card — plus video loop (cinema) /
GLB (spectacle). Poll between build steps (`higgsfield generate wait <id>` /
`higgsfield generate get <id>`); download into `app/public/assets/`; verify kit
coherence when it lands (re-generate anything whose grade fights the boards).
Never idle waiting on renders; never fall back to stock/picsum/CSS-only.

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
  film per `references/asset-system.md` §7 (scroll plays the movie), not a
  passive autoplay loop. Passive motion the user can't influence does not
  count as the Tier-1 mechanic.
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

Run `bun run qa:fill -- --strict`, then the grep checklist in
**`references/review-rubric.md` §A**: placeholders; em/en-dashes; banned palette
families in tokens; eyebrow ration; unreferenced generated assets (every kit
file used); `h-screen`; SSR safety; reduced-motion coverage; **repeated CTA
classes** (bespoke-chrome violation); **opacity-0 + whileInView** combinations;
section plan honored; copy self-audit. This is a completion gate — do not
deploy with a failing item.

### Phase 6 — Deploy preview + adversarial review (default verdict: NEEDS_WORK)

1. `higgsfield website deploy <website_id> --env preview`.
2. If you can screenshot the deployed preview (e.g. a browser or screenshot
   tool is available), capture it: full-page desktop ~1440px AND mobile ~390px.
   If you cannot, state plainly in your report that the visual review was
   skipped — do not silently drop it.
3. Review as a **skeptical outside reviewer whose default verdict is
   NEEDS_WORK**: grade §B of `references/review-rubric.md` (all items) AND
   board-faithfulness per section (does the built section still feel like its
   reference board, or did it drift to template?). You are hunting for reasons
   it reads as AI output — a review that waves everything through is itself a
   failure.
4. Grade the FULL rubric before touching any code — do not fix finding #1
   before finding #4 exists. Then collect ALL findings into ONE batch fix,
   apply, redeploy the preview once. A second loop only for broken layout,
   not taste nits.
5. Report: preview URL + one-line concept statement + anything honestly skipped.

Do NOT deploy production unless the user explicitly asks to publish/go live.

---

## Design references — read order

1. **`references/design-recipe.md`** — craft floor (ALWAYS read; short).
2. **`references/wow-catalog.md`** — Phase 0: Tier-1 technique selection +
   the anti-convergence ledger; Phase 4: implementation contracts.
3. **`references/reference-boards.md`** — Phase 1: per-section design boards.
4. **`references/asset-system.md`** — Phase 2: the Higgsfield asset kit.
5. **`references/image-to-code.md`** — Phase 3: faithful implementation +
   bespoke chrome + the CTA garment catalog.
6. **`references/review-rubric.md`** — Phases 5-6: mechanical gate + visual
   rubric.
7. `references/wow-maker.md` — ingredient directory: motion/3D libs (§4),
   component registries (§5), signature effect patterns (§2), SSR pattern (§6).
   Only listed free/permissive sources may be used.
8. `references/design-taste-frontend.md` — the full deep-dive playbook behind
   the recipe; consult for specific situations, not required start-to-end.
9. `references/minimalist-ui.md` — dense functional app chrome guidance
   (forms, consoles, dashboards). It is scoped to Higgsfield-SDK app surfaces
   ONLY — do NOT use `minimalist-ui` for marketing sites or non-SDK apps;
   never load it for a non-SDK site.
10. `references/quanta-design.md` + `references/app-layouts.md` — `--type app`
    builds ONLY: the Quanta design system (tokens, components,
    `app/packages/quanta/ai/AGENTS.md` is the canonical API reference) and the
    standard Higgsfield app layouts (marketing studio / stepper / simple app /
    upscaler — pick the closest; a custom layout is fine when the user asks).
    Never applied to a `--type website` build.

Do NOT search the skill library for other design guidance — everything is here.

Then route to the FUNCTIONAL skill for the task:

| Task | Read |
|---|---|
| fnf SDK: generation jobs, media upload, profile/workspace/credits, adapters | `references/fnf-sdk.md` + `references/auth.md` + `references/runtime-and-infra.md` |
| React query/cache/controllers for fnf | `references/fnf-react.md` + `references/auth.md` |
| Higgsfield-SDK app UI (generation console, fnf-backed tool) | `references/app-layouts.md` + `references/quanta-design.md` + `references/minimalist-ui.md` + `references/fnf-sdk.md` + `references/fnf-react.md` + `references/auth.md` |
| Auth, current user, login/logout, `/api/user`, `__auth` routes | `references/auth.md` + `references/runtime-and-infra.md` |
| TanStack Start routes, SSR, server functions, Cloudflare Worker runtime | `references/runtime-and-infra.md` |
| Heavy / long-running work (ffmpeg, headless browser, background jobs), containers | `references/containers.md` |
| SEO meta tags, Open Graph, Twitter Cards, canonical URLs, robots directives | `references/seo-meta-tags.md` |
| JSON-LD structured data, schema.org markup | `references/seo-schema-markup.md` |
| robots.txt, sitemap.xml, security headers, canonicals, redirects | `references/seo-technical.md` |
| Post-build SEO quality audit | `references/seo-audit.md` |
| GEO optimization for AI search engines | `references/seo-geo-content.md` |
| Brand entity, knowledge graph, sameAs, NAP consistency | `references/seo-entity.md` |
| Cloudflare Workers security: secrets, global state, streaming, headers | `references/security-worker-hardening.md` |
| Post-build web security audit (OWASP Top 10, XSS, CSRF) | `references/security-web-audit.md` |
| Threat modeling for websites with auth, user data, or databases | `references/security-threat-model.md` |

Package-local guides are canonical for package APIs:

| Package | Guide |
|---|---|
| `@higgsfield/fnf` | `app/packages/fnf/ai/AGENTS.md` |
| `@higgsfield/fnf-react` | `app/packages/fnf-react/ai/AGENTS.md` |

## Stack

- **TanStack Start** (file-based routing under `app/src/routes/`, SSR via
  `app/src/server.ts` → a Worker `export default { fetch }`). No Next/Remix/Astro
  conventions, no `app/src/pages`.
- **Vite 7 + bun**. Build emits `dist/server/server.js` (the Worker) +
  `dist/client` (hashed static assets). Tailwind v4 is wired in `app/src/styles.css`
  (it also imports Quanta's Tailwind entry for the template bundle — leave that
  wiring alone). Legacy shadcn/ui files may exist from the scaffold.
  **`--type website` builds use custom Tailwind/CSS only** — never import
  `@higgsfield/quanta/*` there. **`--type app` builds use Quanta** components
  and `q-` tokens (`references/quanta-design.md`).
- **No separate Hono/Express backend.** Server logic is TanStack **server
  functions** (`createServerFn`) and **server routes**. App-local API routes are
  allowed when a platform contract requires them, for example `GET /api/user`
  as the browser-safe proxy to `https://fnf.internal/user`.

## Hard rules

### 0a. Higgsfield packages and template modules

The `app/packages/` directory contains managed snapshots from fnf-web:
`@higgsfield/fnf`, `@higgsfield/fnf-react`, and `@higgsfield/quanta`. Do not
edit these manually unless the task explicitly asks to patch a package snapshot.

Template-owned infrastructure lives in `app/src/module/**`. The Design mode
child bridge lives in `app/src/module/design-inspector`, not in a package and
not in fnf-web.

`type: "website"` surfaces use custom Tailwind/CSS per the pipeline;
`type: "app"` surfaces use Quanta (`references/quanta-design.md` +
`references/app-layouts.md`). fnf API calls stay server-side.

### 0b. Supercomputer Design mode inspector

Generated websites support a Higgsfield design inspector bridge for editable
Supercomputer previews. The split is strict:

- `fnf-web` owns the parent iframe UI, hover overlay, edit popover, origin/
  session checks, and edit prompt submission.
- This template owns the child iframe runtime through
  `app/src/module/design-inspector`.
- Agents never manually implement inspector code, refs, source markers, or
  `data-hf-*` attributes.

Required scripts:

- `bun run build` is the clean production build: no inspector runtime and no
  source metadata.
- `bun run build:design` is the editable preview build:
  `HF_DESIGN_INSPECTOR=1 vite build --mode design`.
- `bun run dev:design` is local dev with the inspector enabled.
- `bun run build:prod` is an alias for the production-clean build.

The platform must deploy editable previews with `build:design` and public
production websites with `build`. Exact source metadata is attached with
preview-only callback refs and a `WeakMap`, not DOM attributes. Keep the guarded
dynamic install in `app/src/routes/__root.tsx` and the Vite integration in
`app/vite.config.ts` wired to `app/src/module/design-inspector/vite`.

For every website-builder task, deploy the editable **preview** only —
`higgsfield website deploy <website_id> --env preview` (which uses
`bun run build:design`). Preview is the default and the ONLY environment you
deploy on your own. Do NOT deploy `--env production` unless the user explicitly
asks to publish, go live, or ship to production. Never rewrite the normal
`build` script to include `HF_DESIGN_INSPECTOR=1`, never rename `build:design`
into `build`, and never ship inspector metadata in production.

### 1. SSR-safe rendering
Every route renders on the server per request. NEVER touch browser-only globals
(`window`, `document`, `localStorage`, `navigator`) at module top level or during
render — only inside `useEffect`/event handlers, or guarded with
`typeof window !== "undefined"`. A top-level `window` reference crashes SSR.

### 2. Server-only code stays server-only
Put server logic in `createServerFn(...).handler(...)` or a `*.server.ts` module
(the `.server.ts` suffix keeps it out of the client bundle). Secrets and
bindings are read **server-side, per request** — never shipped to the browser.

### 3. Higgsfield (fnf) calls are BACKEND-ONLY — and your app needs a real backend
Build whatever backend the website needs: your own database (D1), server
functions (`createServerFn`), app-local API routes, sessions, business logic —
that's expected and fully supported. **For any website that uses the Higgsfield
SDK this is mandatory: it MUST be a real end-to-end app — real server
functions/routes AND real persistence (D1) — never a front-end mock (see rule
3a).** Call Higgsfield internal services exclusively from server code. The
platform attaches identity on server egress, so tokens never live in website
code. NEVER call `https://fnf.internal/*` from client components.

For current user auth, implement `GET /api/user` as a TanStack server route that
calls `https://fnf.internal/user` server-side and returns the upstream status
and JSON unchanged. Browser UI calls `/api/user`. Login/logout are browser
navigations to `/__auth/login?return=<path>` and
`/__auth/logout?return=<path>`. Read `references/auth.md` before touching this.

**If the website uses the Higgsfield (fnf) SDK, adding auth is MANDATORY — not
optional.** Any website that touches the fnf SDK (generation, media upload, job
feed/history, profile, workspace, wallet, credits, or any `https://fnf.internal/*`
call) is an authenticated surface. Before shipping it you MUST implement the
Higgsfield auth contract exactly as written in `references/auth.md`: the
`GET /api/user` server proxy, a signed-out state that links to `/__auth/login`,
`/__auth/logout`, and a server-side auth re-check before every SDK operation.
Do not invent your own login UI, email/password form, or token handling, and do
not build anonymous generation flows unless the user EXPLICITLY asks for an
offline/mock demo (rule 3a).

**Preview sign-in is platform-owned — do NOT improvise a cause if it fails.**
`/__auth/login` is a platform-injected route that hands off to Higgsfield's auth
service (Clerk), then redirects back to `return` so `/api/user` succeeds. If a
user reports sign-in failing on a PREVIEW, FIRST confirm the website side is
correct (links to `/__auth/login?return=<path>`, proxies `/api/user` unchanged);
if it is, the failure is on the platform/auth side — say so plainly instead of
inventing a website-code cause.

Choose the auth mode by what the website is doing:

- **Higgsfield auth** is mandatory for Higgsfield SDK/model features: image/video
  generation, media upload, profile, workspace, credits, and generation history.
- **In-app auth** is for the generated product's own users: todo accounts, SaaS
  team members, dashboards, notes, CRM users. Implement it with the website's own
  routes/storage; do not call `https://fnf.internal/user` unless the website also
  uses Higgsfield SDK features.
- If a website needs both, keep them separate. Never replace Higgsfield auth with
  app-local auth for generation.

If the user prompt asks for a model/generation website, even casually, treat auth,
profile, credits/workspace display, and a generation feed/history as mandatory
acceptance criteria — do not wait for the user to ask.

Generation history cards must render SDK `Generation.results`, not status-only
placeholders. Use `app/src/lib/higgsfield-generation-results.ts` and
`app/src/components/higgsfield-generation-card.tsx`, or an equivalent component
with the same URL precedence. A completed job without a result URL must show an
explicit "preview unavailable" state with refresh/get behavior.

When creating SDK clients in generated websites, use only
`createWorkflowPlatformAdapter({ baseUrl: 'https://fnf.internal' })` from
server-side code. Do not use public/dev fnf URLs, env-selected backend URLs,
`createFnfWebAdapter`, `createDevFnfWebAdapter`, apps-marketplace adapters,
bearer tokens, or dev user headers in generated website code.

### 3a. A Higgsfield-SDK app is end-to-end — real backend + real DB, never a mock

Any website that uses the Higgsfield SDK MUST ship as a real, end-to-end product —
NOT a front-end mock, prototype, or "demo" that fakes the backend.

An SDK app MUST have all three:

- **A real backend.** Every data operation runs through a TanStack **server
  function** or **server route** — fnf calls server-side, reads/writes server-side.
- **Real persistence (D1).** Opt into D1 (`"db": true` in `app/app.manifest.json`)
  and persist the app's OWN product state: saved/favorited generations,
  collections, presets, share records, settings. Schema in
  `app/migrations/000N_*.sql` (additive; rule 5).
- **Real fnf integration.** Generations, media, profile, and credits come from the
  live SDK against `https://fnf.internal`, never hardcoded fixtures.

fnf is the source of truth for the generations themselves — do NOT mirror fnf's
tables into D1. D1 is for YOUR product layer on top.

**These are NOT a backend and are bugs in an SDK app:** in-memory arrays or
module-level state as "the database"; `localStorage` as the persistence layer;
hardcoded/fixture/`lorem` data; a static JSON file faking a list endpoint;
`setTimeout` faking latency; memory/mock SDK adapters shipped as the product.

The ONLY exception is when the user **explicitly** asks for an offline/mock demo —
then say plainly that it is a mock and why.

### 4. Cloudflare bindings via `cloudflare:workers`
Any infra you opt into (D1 `DB`, R2 `STORAGE`, KV `KV`) is read server-side
through `app/src/lib/bindings.server.ts` (`import { env } from "cloudflare:workers"`).
Each binding is present ONLY if declared in `app/app.manifest.json`, so the typed
accessors are optional — guard before use. Do not thread `env` through React
props or read it at module top level.

### 5. Opted-in storage is SHARED — preview data == prod data
If you opt into D1, R2, or KV, each is a SINGLE instance **shared by the preview
and prod deploys**. Only the CODE is split (`vars.HF_ENV`). The DATA is not.
- `env.HF_ENV` tells you which env it is; it CANNOT switch the database/bucket.
- A destructive migration you run "just to test on preview" hits **production
  data**. Prefer additive migrations (`CREATE TABLE IF NOT EXISTS`, `ADD COLUMN`).

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
- Container → `app/container/Dockerfile` + `AppContainer` in `app/src/server.ts`.
- Components → **Websites (`--type website`):** custom components per the
  boards; app-local files in `app/src/components/**`. Do not start from
  `app/src/components/ui/*` unless migrating a legacy shadcn piece.
  **Apps (`--type app`):** Quanta components first (`@higgsfield/quanta/*` —
  Button, Input, Textarea, Dropdown, Modal, Tabs, Sidebar, …), app-local
  composition in `app/src/components/**`; layout per `references/app-layouts.md`.
- Generation result UI → `app/src/components/higgsfield-generation-card.tsx` +
  `app/src/lib/higgsfield-generation-results.ts` for SDK-backed feeds.
- Styles / theme → `app/src/styles.css` wires Tailwind v4. Websites: a custom
  token layer from the design brief — no q-prefixed utilities, no site-wide
  CTA utility classes. Apps: Quanta's `q-` tokens ARE the theme.
- D1 schema → `app/migrations/000N_*.sql` (additive; see rule 5).
- Pipeline artifacts → `app/design-brief.md` (Phase 0) + `refs/*.png` (Phase 1);
  commit both.

## Verify + deploy

The trusted platform CI builds the website on **every deploy** (preview →
`bun run build:design`, production → `bun run build`), so a deploy already gives
you the authoritative type + build result. Do NOT reflexively `bun install` +
`bun run build` just to check your work. You never deploy or migrate with
`wrangler` yourself — the trusted platform CI provisions infra and
deploys/migrates when you run `higgsfield website deploy`.

**Default: run the pipeline, pass the Phase 5 gate, deploy the preview**
(`higgsfield website deploy <website_id> --env preview`), then run the Phase 6
adversarial review. Never deploy production unless the user explicitly asked to
publish.

**Publishing ("show in feed").** When the user asks to publish / share / put the
site on the feed, run `higgsfield website publish <website_id>` — it deploys the
pushed branch to PRODUCTION (a publish always includes the production deployment;
no separate deploy command) and lists the website on the Higgsfield community feed.

**MANDATORY before every publish — the feed card renders ONLY from
`app/src/app-meta.json`, and a listing with an empty `og_title` is INVISIBLE on
the feed.** Fill ALL of these with real values (never placeholders), commit, and
push before running `higgsfield website publish`:

1. `og_title` — the card's title (also the browser tab title).
2. `og_description` — the card's one-liner.
3. `og_image_url` — the cover image (generate one per the asset system if none
   exists yet).
4. `favicon_url` — the card's logo/icon (generate one if none exists yet).
5. `og_video_url` — the **cover video**, OPTIONAL and permission-gated: OFFER it
   to the user ("want a short cover video for the feed card?") and ASK
   PERMISSION FIRST — generating a video costs credits; never generate it
   unprompted. If they say yes, follow "Cover video" in
   `references/seo-meta-tags.md`.

`higgsfield website deploy <website_id> --env production` remains the way to
ship to production WITHOUT a feed listing.

**Run the local checks only when you actually need them** — from `app/`:
```bash
cd app
bun install          # only when you changed dependencies / package.json
bun run typecheck    # tsc --noEmit
bun run build        # production-clean build
bun run build:design # editable Supercomputer preview build
```
Run them when: you changed dependencies or build/runtime config, you're debugging
a build/type error, or a command genuinely needs `node_modules`.

**Small edits to an existing site** (copy tweak, one component, styling fix): the
pipeline does not restart. Make the edit, run `bun run qa:fill -- --strict`,
deploy the preview. Run the Phase 6 screenshot loop only when the edit changed
layout/visual structure (new section, hero change, theme change) — not for a
typo fix.

**Before claiming a build done / deploying, no placeholders may remain.** Run
`bun run qa:fill -- --strict` (add `--url <preview>` to also scan the rendered
page). It fails if any template placeholder survives — a `<...>`-style token,
`lorem ipsum`, or the scaffold blank-page marker (`REMOVE_THIS` / `blank-app-v1`).
It is a completion gate, not a CI build step.
