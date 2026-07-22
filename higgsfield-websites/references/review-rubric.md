# review-rubric — Phase 5 mechanical gate

§A runs BEFORE deploy and is a completion gate, not a suggestion. Most items
are verified by grep/code inspection. **Item 9f is the hard machine gate for the
animated-website default: a website that ships without the scroll-scrub component
+ scene media (and without an explicit `override` in the brief) FAILS, no matter
how polished the rest is** — this is the single most common miss, so run 9f every
time. For the animated website, item 9e adds its interactive runtime checks in
local preview before the final deploy. There is no post-deploy visual/screenshot
review — this mechanical gate is the only verification.

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
   flood-fill, framed block) appear at most once page-wide combined. On the
   `override` path the Tier-1 technique carries a `wow-catalog.md` ID and is
   interactive (not a passive loop); on the default `animated-website` path the
   Tier-1 technique IS the scroll-scrub animated website (enforced by 9f) — a
   generic wow-catalog ID does NOT satisfy the default path.
9e. **Animated website — A4 seam-locked scroll scrub (every website by default;
   skip only if the user explicitly opted out)** — verify every media segment
   has a first-frame poster extracted from the
   exact deployed clip; chapter copy is server-rendered in semantic document
   flow (not hidden until a viewport callback); `prefers-reduced-motion`
   performs no video fetch and shows the complete static story; desktop and
   lighter mobile encodes are wired; connector/leg handoffs use the neighboring
   rendered clips' ACTUAL boundary frames; camera velocity does not reverse
   accidentally; initialization runs only in an effect; and teardown aborts
   fetches, removes listeners/video nodes, cancels RAF, and revokes Blob URLs.
   Scrub videos directly from seekable MP4/Blob URLs, ensure CSP `media-src`
   permits `blob:`, and ensure no second ScrollTrigger timeline drives the same
   media. Inspect each seam immediately before/after in both scroll directions
   and test source swapping, a fast mobile flick, and unmount/remount in local
   preview before final deploy.
9f. **Animation mode gate (machine-verifiable — HARD, every website).** This is
   the completion gate for the animated-website default; a site that passes every
   other check but this one is NOT done. Steps:
   1. `grep -n "^Animation mode:" app/design-brief.md` — there MUST be exactly
      one such line. Zero matches → FAIL (the brief never declared the state).
   2. If the value is **`animated-website`**, ALL of these must hold, or FAIL:
      - the scroll-scrub component exists —
        `ls app/src/components/scroll-scrub/scroll-scrub.tsx` succeeds — and is
        actually imported/rendered by a route (grep for its import);
      - real scene media shipped — at least 2 clips under
        `app/public/assets/**/*.mp4` (the seam-locked chain), each with a
        first-frame poster (item 9e);
      - the brief carries the journey block (Journey scenes + Camera
        architecture A/B) written in Phase 0.
      A website on this path with no scroll-scrub component or no scene MP4s is
      the failure mode this gate exists to catch — do NOT deploy it; go build the
      camera journey.
   3. If the value is **`override — "..."`**, the line MUST quote the user's
      explicit request verbatim. No scroll-scrub artifacts are required; instead
      confirm the chosen `wow-catalog.md` technique is actually built (9d). An
      `override` with no quoted user request → FAIL (treat as `animated-website`
      and go back to step 2).
10. **Section plan honored** — the built page matches `app/design-brief.md`'s
    section plan (families, order, no consecutive family repeats). If the plan
    changed during the build, the brief was updated to match.
11. **Copy self-audit** — every visible string re-read; nothing grammatically
    broken, referent-unclear, filler-verb ("Elevate", "Seamless"…), or fake-precise
    (`92%`, `4.1×` without a source).
