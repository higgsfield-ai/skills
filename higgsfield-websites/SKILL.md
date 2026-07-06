---
version: 0.9.0
name: higgsfield-websites
description: |
  Build, edit, and deploy full-stack websites via the Higgsfield CLI
  (`higgsfield website …`). Each site is a React 19 + TanStack Start SSR app in
  one Cloudflare Worker (D1/R2/KV/DO/Containers). TWO product types, picked via
  `--type` on create: `website` (standalone, NO Higgsfield integration,
  independent brand, custom CSS — the image-grounded pipeline in
  references/website-flow.md) vs `app` (Sign in with Higgsfield + fnf SDK,
  Quanta + Astryx + app layouts per references/app-flow.md). This file routes to
  the right flow; each flow carries its own workflow, references, hard rules,
  and deploy/publish gates.
  Use when: "build me a website", "make a landing page", "create a web app",
  "build a SaaS dashboard / tool / portfolio", "deploy this site", "edit my
  site", "publish", "ship to production".
  NOT for: single image/video/audio generation (higgsfield-generate), product
  photos (higgsfield-product-photoshoot), marketplace cards
  (higgsfield-marketplace-cards).
argument-hint: "[what to build or edit] [--type website|app]"
allowed-tools: Bash
---

# Higgsfield website builder (CLI) — two product types, two flows

You drive the whole lifecycle through the **Higgsfield CLI** (`higgsfield
website …`), then edit code on the local filesystem with `git` + `bun`. You are
building ONE per-website Cloudflare Worker: a **React 19 + TanStack Start** app,
**server-rendered (SSR)**, deployed as a single Worker at the product's own
subdomain. The project lives in **`app/`** — run every `bun`/build command from
there.

## The two types — and the REQUIRED `--type` on create

`higgsfield website create` requires `--type`, and it is the **USER'S choice** —
when the request doesn't make it obvious, ask the user before creating (one
question, up front):

- **`--type website`** — a standalone product with NO Higgsfield integration
  and **NO AI generation of any kind** (no image/video/audio/text generation —
  not via Higgsfield, and not via some other provider): no "Sign in with
  Higgsfield", no requests to Higgsfield, no fnf SDK. Every website gets a
  fully independent brand: own palette, type, and chrome from a design brief,
  custom Tailwind/CSS only — never import `@higgsfield/quanta/*` or use
  q-prefixed tokens anywhere, and no "Powered by / Built on Higgsfield" badges
  or mentions in page content. The user's brand is the only brand on the page.
  ```bash
  higgsfield website create --type website
  ```
- **`--type app`** — a product tightly integrated with Higgsfield: its users
  Sign in with Higgsfield and generate images/videos through the fnf SDK (the
  full auth + D1 contract applies). An app must look and feel like a Higgsfield
  product: UI built with **Quanta** (`references/quanta-design.md`) + **Astryx**
  for component gaps, starting from a standard app layout
  (`references/app-layouts.md`). Quanta and the app layouts are app-only — never
  applied to a `--type website` build. The independent-brand rule and the wow
  pipeline (`design-taste-frontend`, boards, wow catalog) are the website path;
  apps never get a custom brand — Quanta is the brand.
  ```bash
  higgsfield website create --type app
  ```

**Generation is ALWAYS an app.** Any product that generates images, video,
audio, or other AI media runs on Higgsfield — build it as `--type app` (Sign
in with Higgsfield, generation on the user's Higgsfield credits). NEVER offer
the user an option to "bring your own image/video API" or plug in their own
generation key for a website — that path does not exist. `--type website` is
ONLY for sites with no generation and no tie to Higgsfield or any other
generation service. (A website may still use ordinary non-generation
third-party APIs — payments, maps, email — with the user's own keys; that is
unrelated to this rule.)

Quick tells: "landing page / portfolio / marketing site / SaaS with its own
users, no AI generation" → website. "generates images/video/audio, or anything
with Higgsfield models, credits, or generation history" → app.

## Prerequisites

1. If `higgsfield` is not on `$PATH`, install it:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. If `higgsfield account status` reports `Session expired` / `Not authenticated`,
   ask the user to run `higgsfield auth login` (interactive) and wait for
   confirmation.
3. `git` and `bun` are used locally once you clone the repo. The CLI itself
   handles create / repo / deploy / publish / status / db / secrets / delete —
   and the asset generation jobs (`higgsfield generate …`, `higgsfield model …`).

## Pick the path, then follow ONE flow end-to-end

1. Resolve the `--type` (ask the user if unclear — it's their choice).
2. Read the matching flow and follow it — it is the complete workflow for that
   type, including its own references, hard rules, editing map, and
   deploy/publish gates:

| Type | Flow |
|---|---|
| `--type website` | **`references/website-flow.md`** — phased pipeline: intake → concept → reference boards → asset system → build-to-boards → motion → mechanical gate → adversarial review |
| `--type app` | **`references/app-flow.md`** — the Quanta + Astryx toolkit, the four reference layouts, fnf SDK + auth + D1 contract, launch cover + metadata, brand-review self-check, publish gate |

Both flows share the same platform mechanics (SSR Worker, `app.manifest.json`
infra, a single live deploy via `higgsfield website deploy <website_id>`,
the publish gate with the branded cover per `references/app-cover.md`) — each
flow restates what it needs, so you never have to read the other one.

## UX rules

1. Be concise. No raw website IDs, tokens, or JSON dumps in chat. After a
   deploy, return the live URL (from `higgsfield website status`) and a
   one-line summary.
2. Never echo the scoped git token back to the user, and never commit it.
3. Detect the user's language from the first message and reply in it. CLI flags
   and code stay English.
4. **Every deploy ships the live public site immediately** — there is no
   preview stage. Publishing/listing on the community feed is separate and
   happens ONLY when the user explicitly asks to publish / list it.

Do NOT search the skill library for other design guidance — everything is
under this skill.

## Talking to the user — no technical/plumbing language

Most users are not technical. Never expose the build plumbing in what you SAY
to them. Do NOT mention the git repository, cloning, branches, commits,
pushing, pulling, or the deploy pipeline in user-facing messages — those are
internal mechanics you just perform. Speak in product terms about what the
user cares about:

- "Setting up your site…" — not "cloning the repo" / "scaffolding the project".
- "Saving your changes…" / "Updating the site…" — not "committing" / "pushing".
- "Your preview is ready: <url>" — not "deployed the branch" / "the build passed".
- "Publishing your site…" — not "merging to main" / "pushing to production".

This is about the WORDS in chat only — keep doing the real steps behind the
scenes; just don't narrate them in developer terms. (The one exception: a user
who is clearly technical and explicitly asks about the repo, branch, or deploy
mechanics — then answer plainly. CLI flags and code stay English.)

## Reference index (what's in this bundle)

The two flow files pull in the rest as needed — you don't read these directly
unless a flow sends you there.

**Both flows:** `references/app-cover.md` (launch cover + OG image),
`references/runtime-and-infra.md` (TanStack routes, SSR, Worker runtime),
`references/security.md` (Worker hardening, OWASP audit, threat model).

**Website flow:** `references/design-recipe.md`, `references/wow-catalog.md`,
`references/wow-maker.md`, `references/reference-boards.md`,
`references/asset-system.md`, `references/image-to-code.md`,
`references/design-taste-frontend.md`, `references/review-rubric.md`,
`references/seo.md`.

**App flow:** `references/quanta-design.md`, `references/app-layouts.md`,
`references/astryx-fallback.md`, `references/brand-review.md`,
`references/fnf-sdk.md`, `references/fnf-react.md`, `references/auth.md`,
`references/containers.md`.
