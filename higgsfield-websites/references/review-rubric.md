# review-rubric — Phase 5 mechanical gate + Phase 6 adversarial review

Two checklists. §A runs BEFORE the first deploy (grep/read the code — every item
is mechanically checkable). §B runs AFTER the preview deploy, against real
screenshots, in the voice of a skeptical outside reviewer whose default verdict
is NEEDS_WORK. Both are completion gates, not suggestions.

## §A. Mechanical gate (pre-deploy, code-level)

Run `bun run qa:fill -- --strict` first. Then check each item; fix every hit
before deploying.

1. **Placeholders** — `qa:fill --strict` passes; zero `<...>` tokens, `lorem`,
   `REMOVE_THIS`, `blank-app-v1`, empty `src=""`.
2. **Em-dash ban** — `grep -rn "—\|–" app/src/` over user-visible strings returns
   nothing (code comments exempt).
3. **Banned default palette** — none of the banned palette families from
   `design-recipe.md` §2 appear in `styles.css`/tokens: beige/brass/espresso
   hexes, graphite/near-black + orange/amber/ember accent, near-black + neon
   cyan/blue/green accent, AI purple/violet glow, or the palette family of your
   previous build in this chat. Overridable ONLY by the user's explicit brand
   colors, justified in the design brief.
4. **Eyebrow ration** — count **eyebrow-position section labels only**. An
   eyebrow is a small uppercase/mono kicker sitting DIRECTLY above the
   section's display headline in the same column; nothing else counts. Must
   be ≤ ceil(sectionCount / 3). Uppercase mono in non-eyebrow roles (spec
   strips, table/metric captions, rail labels, footer column heads) is
   exempt — especially when the reference boards show them. Grep for
   `uppercase tracking` to find candidates, then classify by position.
5. **Asset kit complete + referenced** — every file downloaded into
   `app/public/` is actually referenced by a route/component; the hero
   references a real generated asset (no picsum/stock/CSS-gradient-only hero);
   the icon slots use the generated icon set (or the documented library
   fallback), and no kit item from `asset-system.md`'s "always" list is
   silently missing.
5b. **Head kit complete** — the full favicon/meta set from `asset-system.md`
   §7 is present and wired: favicon (ico/svg + png sizes), apple-touch-icon,
   192/512 + maskable icons with a `site.webmanifest`, `theme-color`, and the
   full OG + twitter card block with absolute image URLs. An empty `<head>`
   or the scaffold's default favicon is a gate failure.
6. **`h-screen`** — zero occurrences; use `h-dvh` / `min-h-dvh`.
7. **SSR safety** — no `window` / `document` / `localStorage` / `navigator` at
   module top level or in render; every `[C]`/`[W]` component behind a mounted
   gate; `[W]` additionally `React.lazy`.
8. **Reduced motion** — every animation source (`motion/react`, GSAP, registry
   components) paired with a `prefers-reduced-motion` guard or static fallback.
9. **CTA integrity + bespoke chrome** — one label per intent page-wide (no "Get
   in touch" + "Contact us"); no CTA label longer than ~3 words for primaries;
   AND no shared site-wide button style: grep for a repeated CTA class string /
   `Button` utility component reused across sections — every CTA per the brief's
   inventory has its own component with its own interaction identity.
9b. **Screenshot-safe reveals** — flag any `opacity: 0` / `opacity-0` **whose
   removal depends on a viewport/scroll trigger** (`whileInView`,
   IntersectionObserver entry, ScrollTrigger-gated fade-ins). Hover-state
   decorations at opacity-0 are fine. Nothing may sit invisible waiting for a
   viewport trigger; animate from visible states (y-offset/blur) or fire on
   mount. Video elements need a `poster` (or a rendered first frame) so
   headless shots never show a black box. A full-page headless screenshot
   must show every section.
9c. **No Higgsfield branding on `type: "website"` builds** —
   `grep -rin "higgsfield\|quanta" app/src/` returns no user-visible strings,
   no Quanta imports, no q-prefixed tokens, no "Powered by / Built on" badge,
   no Higgsfield marks in page chrome. fnf/auth strings in server/service
   code are fine — that's the functional contract, not branding. On
   `type: "app"` builds this check inverts for the design system: Quanta
   imports and q- tokens are REQUIRED there and "Sign in with Higgsfield" is
   part of the product — only gratuitous "Powered by / Built on Higgsfield"
   marketing badges remain forbidden.
9d. **Anti-convergence ledger honored** — the brief lists the previous
   build's six identity axes (palette family, type pairing, hero
   architecture, Tier-1 technique, CTA garments, corner language) and this
   build differs on ≥4; the rationed garments (drawing underline, hover
   flood-fill, framed block) appear at most once page-wide combined; the
   Tier-1 technique carries a `wow-catalog.md` ID and is interactive (not a
   passive loop) on cinema/spectacle.
10. **Section plan honored** — the built page matches `app/design-brief.md`'s
    section plan (families, order, no consecutive family repeats). If the plan
    changed during the build, the brief was updated to match.
11. **Copy self-audit** — every visible string re-read; nothing grammatically
    broken, referent-unclear, filler-verb ("Elevate", "Seamless"…), or fake-precise
    (`92%`, `4.1×` without a source).

## §B. Visual rubric (post-deploy, screenshot-level)

Screenshot the deployed preview: full-page at ~1440px wide AND ~390px wide. Grade
each item PASS / FAIL with one sentence of evidence. Be adversarial — you are
hunting for reasons the page reads as AI-template output. Collect every FAIL into
one batch fix list, apply, redeploy once.

1. **First impression (the squint test).** Blur your eyes at the hero: is there
   one clear focal point and an obvious next action? Does it look like a site a
   studio charged real money for, or like a component demo?
2. **Hero discipline.** Everything critical inside the first viewport; headline
   ≤2 lines; no stacked micro-elements (eyebrow + tagline + trust strip); the
   generated hero asset is actually visible and well-composed (not cropped into
   mush, not buried under an overlay).
3. **Type hierarchy.** Clear 3-level scale (display / section head / body); line
   lengths ≤65ch; no headline wrapping into 4 lines; italic descenders not
   clipped; consistent font usage per the brief.
4. **Palette lock.** One accent everywhere; page reads as ONE theme top to
   bottom; contrast holds (no white-on-white buttons, no gray-on-gray body); no
   accidental beige+brass default.
5. **Layout variance.** Scrolling the full page: no layout family repeats
   back-to-back, no 3+ zigzag chain, no identical-trio card row, bento cells all
   filled with real visual variation.
6. **Asset integration.** Generated images look intentional: aspect ratios fit
   their slots, palette matches the page, no obvious AI artifacts (garbled text,
   warped hands/objects), no empty image boxes or broken image icons.
7. **Density & copy.** Sections breathe; no data-dump tables; copy is short and
   specific with zero AI-tell phrases visible; footer/nav read as finished.
8. **Mobile integrity (390px).** Nav collapses properly; hero still fits and the
   asset still works; no horizontal scroll; multi-column sections stack in a
   deliberate order; tap targets aren't microscopic; signature effect degrades
   gracefully (or is replaced by its static fallback).
9. **Board faithfulness (per section).** Compare each built section against its
   `refs/` reference board: does it still carry the board's composition, type
   character, and component logic, or did it drift back to a template pattern
   the board never showed? Any section that no longer resembles its board is a
   FAIL for that section.

Scoring: 9/9 = done. Any FAIL in items 1-4, 8, or 9 is blocking. FAILs in 5-7
are blocking on the first pass; on the second pass, note remaining taste-level
nits to the user instead of looping again.
