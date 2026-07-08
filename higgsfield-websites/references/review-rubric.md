# review-rubric — Phase 5 mechanical gate

§A runs BEFORE deploy (grep/read the code — every item is mechanically
checkable). It is a completion gate, not a suggestion. There is no post-deploy
visual/screenshot review — this mechanical gate is the only verification.

## §A. Mechanical gate (pre-deploy, code-level)

Check each item; fix every hit before deploying.

1. **Placeholders** — zero `<...>`-style tokens (e.g. `<brand name>`, `<product>`),
   `lorem`, `REMOVE_THIS`, `blank-app-v1`, or empty `src=""`. Grep for the
   literal markers: `grep -rniE 'lorem ipsum|REMOVE_THIS|blank-app-v1' app/src/`,
   and scan for any remaining `<...>` placeholder tokens in quoted strings.
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
