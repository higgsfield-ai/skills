# app-layouts — the standard Higgsfield app layouts (`type: "app"` builds ONLY)

A `type: "app"` product must look and feel like a Higgsfield product, so you do
NOT invent app chrome. Every `type: "app"` build starts from ONE of the four
reference layouts below — each is a screenshot of a real Higgsfield app.

Two hard rules, no exceptions:

1. **You MUST pick one of the four layouts.** Match the app to the CLOSEST one;
   an unusual request still maps to the nearest layout — adapt within it, never
   invent a different app shell.
2. **You MUST open the picked layout's reference image and build from it.** The
   image is the ONLY description of the layout — there is deliberately no text
   breakdown of where the form / canvas / feed / composer sit, so you CANNOT
   build the screen without viewing it. Open the URL (fetch / view the image),
   read the real composition — spacing, structure, the controls — then reproduce
   it with Quanta components (Astryx only for gaps). Building from the layout's
   name alone, without opening the image, is wrong.

There are NO prebuilt layout scaffolds — you compose the screen yourself.

## The four reference layouts

The table only tells you WHICH image to open — the "when to pick" column is a
selector, not a build spec. The image is what you build from; open it before
writing any layout code.

| Layout | Reference image — OPEN IT before building | When to pick |
|---|---|---|
| **Simple app** | `https://static.higgsfield.ai/website-builder/layout-references/simple-app.png` | A one-shot transform: a few inputs and a single action (e.g. Face Swap). |
| **Preset app** | `https://static.higgsfield.ai/website-builder/layout-references/preset-app.png` | Browsing a gallery of styles/templates is the main surface (e.g. Shorts Studio). |
| **Complex app** | `https://static.higgsfield.ai/website-builder/layout-references/complex-app.png` | Editing ONE asset with many controls/parameters (e.g. Relight). |
| **Studio app** | `https://static.higgsfield.ai/website-builder/layout-references/studio-app.png` | A full multi-project creative workspace (e.g. Cinema Studio). |

## Invariants (every layout)

- **No app header/top bar** — apps render INSIDE Higgsfield, whose chrome
  provides the global header, credits/balance, and account controls. Never add
  a brand/logo row, top nav bar, or sign-out/credits UI. In-app navigation is a
  Quanta `Sidebar` (studio) or inline controls (tabs, segmented mode toggles);
  a page title is just a heading inside the content area.
- **Permanently DARK** — `data-theme="default-dark"` is pinned on `<html>` in
  the template. No theme toggle, no light mode, no `dark:` variants.
- **Container width** — `mx-auto w-full max-w-7xl` on the shell (the body
  background fills the viewport). The exception is the studio layout — a
  full-bleed workspace (sidebar + edge-to-edge feed under the composer).
- **Buttons** — the GENERATE action is always Quanta `variant="marketingPrimary"`
  (the 3D lime CTA) with the credit cost INSIDE the button as
  `{label} {sparkles icon} {credits}` — the sparkle is the branded asset
  `@/assets/icon-sparkles-soft.svg?react` at 14px, and the credits number
  inherits the button label's font (never smaller/other). Quanta variant colors
  do NOT follow the names: `primary` = flat LIME, `secondary` = solid WHITE,
  `tertiary` = dark white/10 glass. Ordinary/nav actions use the dark
  `tertiary`/`ghost`; `secondary` (white) only where the real product shows a
  white button.
- **Quanta first** — `Button`, `Input`, `Textarea`, `Dropdown`, `Select`,
  `Modal`, `Tabs`, `Sidebar`, `Avatar`, `Badge`, `Tooltip`, `sonner` toasts,
  `Loader`, `Media`, `Grid`. Spacing = native Tailwind (`p-4`, `gap-3`);
  semantics = `q-` utilities (`bg-q-background-primary`,
  `text-q-body-md-regular`). Astryx only for components Quanta lacks
  (`references/astryx-fallback.md`).
- **Real end-to-end app** — Higgsfield auth (`references/auth.md`), server-side
  generation submit + poll, and the app's own product state in D1
  (saved/favorited, collections, presets, history). The signed-out state, auth
  guards, `/api/user`, cost preview, submit/poll routes, and D1 persistence are
  MANDATORY — see the checklist in `references/fnf-sdk.md`.

## Building the moving parts (studio / preset composer, feeds, results)

These recur across the layouts; build them from Quanta:

- **Prompt composer** (studio, and any prompt surface): a glass card —
  `bg-q-background-glass` + `backdrop-blur-2xl` + `rounded-[1.25rem]` — with an
  attachment-thumbnail strip on top (40px `rounded-lg` thumbs, quanta
  `CloseButton` to remove); an inner surface `bg-q-transparent-dark-30
  rounded-[1.125rem]` holding an auto-growing transparent textarea (Enter
  submits, never empty; real placeholders: image "Describe what you want to
  create...", video "Describe your scene - use @ to add characters &
  locations") over a settings-chips row (quanta `Chip` size="xs"
  color="neutral" — model / aspect / resolution / duration / batch, not
  full-width selects); and the tall GENERATE button filling the right edge
  (marketingPrimary, uppercase `text-q-accent-xs-bold` label stacked over the
  sparkle + credit cost). The studio's Image/Video mode switcher is a small
  separate glass rail card (stacked icon-over-caption buttons, selected mode on
  a white/10 fill), docked left of the composer.
- **Generation feed**: build from quanta pieces (CSS-columns masonry or `Grid`
  `cols="auto-fit"`, resize `minColWidth` rather than breakpoint ladders):
  image cards plus hover-play video cards (poster swaps to a muted looping
  video on hover), real empty-state copy, in-flight status cards (Loader +
  "In queue" / "In progress" Badge) while polling, failure cards with retry.
- **Results**: designed cards composed from quanta `Media` inside `Card` (or
  your feed cell) with a model/time meta strip — never a bare `<img>`. The
  helpers in `app/src/lib/higgsfield-generation-results.ts` map a Generation to
  its preview URL with the right precedence.
- **Polish** per `references/quanta-design.md` Layer 1: real empty/loading/error
  states, keyboard focus states, responsive down to mobile.
