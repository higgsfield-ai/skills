# app-layouts — the standard Higgsfield app layouts (`type: "app"` builds ONLY)

A `type: "app"` product must look and feel like a Higgsfield product, so you do
NOT invent app chrome. The template ships the standard layouts and the UI they
are built from as **real code** — you build by copying/composing those, not by
reproducing a screenshot.

Two hard rules, no exceptions:

1. **Start from one of the six shipped layouts — Studio, Preset, App detail, AI
   Stylist, Skin Enhancer, or Shots.** Match the app to whichever is closest
   (`app/src/layouts/*.tsx`) and adapt it; an unusual request still maps to the
   nearest one — adapt within it, never invent a different app shell. A fully
   custom layout is fine only when the user asks for something none covers.
2. **Read the code, then build.** After `higgsfield website repo-access` + clone, read
   `app/src/layouts/AGENTS.md` (the layout catalog — anatomy + rules for each)
   AND `app/src/components/AGENTS.md` (the MANDATORY component contract, with
   copy-paste wiring), then open the layout/component files you'll use. They are
   the source of truth for structure; build from them, not from memory.

Everything is code in the repo — there are no external reference images to open.

## The six layouts (`app/src/layouts/`)

Copy the closest one into your route and adapt freely. Full anatomy per layout
is in `app/src/layouts/AGENTS.md`.

| Layout | When to pick |
|---|---|
| `studio.tsx` (`StudioTemplate`) | A full creative workspace: projects-first `Sidebar` + hero + a floating prompt dock (`@/components/prompt-box` — mode toggle, inline setting pills, lime GENERATE) over an edge-to-edge generations feed. The richest shell — for multi-project generation tools. |
| `preset.tsx` (`PresetTemplate`) | **Pick-a-style-then-generate**: a persistent left creation rail (`@/components/composer` + `@/components/setting-trigger` rows + costed Generate) beside a browsable preset gallery (Presets/History/How-it-works tabs + search). Tiles are horizontal (default) or vertical/portrait via `presetOrientation` — pick to match the output (vertical for 9:16 apps). |
| `app-detail.tsx` (`AppDetailTemplate`) | A single tool's **public landing page** (the "simple app"): a centered `max-w-7xl` scroll page with a two-column generator hero (`@/components/dropzone` inputs on the left, a large `Media` preview on the right) and a "how it works in 3 steps" explainer. For a marketing/detail page around one tool, not a full workspace. |
| `ai-stylist.tsx` (`AiStylistTemplate`) | **Configure-then-generate workspace**: a persistent creation rail (`@/components/upload-field` uploads → `AssetLibraryModal`, `TemplateModal` preset picker, `Select`/`SettingTrigger` rows, costed Generate) beside a segmented `Tabs` workspace (options / live Results canvas / `HistoryGrid` / How-it-works). For a tool where the user uploads inputs, picks options, and iterates (try-on, restyle, character). |
| `skin-enhancer.tsx` (`SkinEnhancerTemplate`) | **Before/after enhance tool**: a centered single-tool page built around a draggable before/after compare slider (`@/components/before-after-compare`) — upload → enhance → compare original vs result, plus How-it-works and a personal `HistoryGrid`. For enhance / retouch / restore / upscale tools whose payoff is a comparison. |
| `shots.tsx` (`ShotsTemplate`) | **Step-by-step wizard** (`@/components/step-rail`): step 1 upload one input → step 2 generate a grid of variations (`GenerationCard`) and favorite the best → step 3 upscale/refine (with a `BeforeAfterCompare`). For a linear generate → select → refine flow. |

Map any request to the closest of the six; only build a fully custom shell when
the user asks for something none covers.

## Reusable UI components (`app/src/components/`)

Build the moving parts from these instead of hand-rolling them — they are the
cross-app contract (`app/src/components/AGENTS.md` is the full, mandatory
reference with wiring examples). Never fork, copy, or hand-roll a replacement;
if one lacks a prop, extend it there.

- `prompt-box/` — the studio prompt dock (mode rail, inline setting pills, upload tiles, GENERATE).
- `composer/` — a simpler side-rail prompt pane (caption + textarea + footer action pills).
- `setting-trigger/` — a compact labelled picker row (label + value + chevron).
- `upload-field/` — THE rail-style upload field for creation rails (opens `AssetLibraryModal`); use it, never a hand-rolled rail upload field.
- `dropzone/` — the bordered upload/select tile (`Dropzone` + `DropzonePreview`) for the app-detail generator hero; also an `AssetLibraryModal` trigger.
- `rail-footer/` — the pinned Generate CTA footer for a creation rail (`sticky bottom-0` + gradient scrim) so the costed CTA stays reachable when the rail overflows.
- `asset-library.tsx` — THE assets modal; every "+"/upload/attach/add-media action opens it (`trigger` + `onSelect`). Never build a custom picker/upload modal.
- `template-modal/` — the generic "choose one option" modal (grid of tiles); `template-picker.tsx` — the tabbed, searchable Studio-style gallery.
- `generation-card/` — the generation tile: `state="generating"` (pulsing brand glow) or ready (media + title). `generation-detail.tsx` — the fullscreen detail view.
- `history-grid.tsx` — THE History section (the current user's OWN generations, personal — never a public feed), a batch-grouped `generation-card` grid.
- `media-card/` — a cover/preview card (title + action); `ratio` picks landscape vs portrait.
- `before-after-compare/` — the draggable before↔after slider (Skin Enhancer / refine steps).
- `step-rail/` — the numbered multi-step wizard indicator (Shots).
- `icon-tile/` — a small gradient icon tile for sidebars/nav rows.

Anything these don't cover, build your own component from Quanta primitives
(`references/quanta-design.md` rule 5) — never a third-party UI library.

## Invariants (every layout)

- **Compact panels — progressive disclosure (EVERY layout).** A settings /
  creation panel shows only its PRIMARY inputs plus the costed Generate CTA by
  default. **If it would expose more than ~6 controls, keep the primary few
  visible and move the rest behind an "Additional settings" disclosure** — use
  the Quanta `Accordion` (`import { Accordion } from '@higgsfield/quanta/accordion'`,
  `multiple={false}` so only one section opens at a time), never a flat
  always-open list and never a hand-rolled collapsible. The creation rail (tall
  left input panel) has a field budget: at most **3 large fields** (`UploadField`
  / cover `MediaCard` / `Dropzone`) and **4 compact fields** (`SettingTrigger` /
  `Select`) visible at once in the default/collapsed state; make the rail a
  scroll container and pin the Generate CTA with `RailFooter`.
- **Simple app → the right side always shows an example output.** For a
  single-tool ("simple") app — the App detail hero especially — the large right
  panel is NEVER an empty frame in the default state: seed it with a
  representative example of the generation output (a real generated sample, or
  the first result once produced) so the user sees what the tool makes before
  they run it.
- **No app header/top bar** — apps render INSIDE Higgsfield, whose chrome
  provides the global header, credits/balance, and account controls. Never add
  a brand/logo row, top nav bar, breadcrumb crumb row, or sign-out/credits UI.
  In-app navigation is a Quanta `Sidebar` (studio) or inline controls (tabs,
  step indicators); a page title is just a heading inside the content area.
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
  white button. **Default button `size="md"`** — Quanta's own default is `sm`
  (too small for app surfaces), so pass `md` explicitly; use `sm`/`xs` only in
  dense toolbars/pills. **Default button `size="md"`** — Quanta's own default is `sm`
  (too small for app surfaces), so pass `md` explicitly; use `sm`/`xs` only in
  dense toolbars/pills.
- **Quanta first** — `Button`, `Input`, `Textarea`, `Dropdown`, `Select`,
  `Modal`, `Tabs`, `Sidebar`, `Accordion`, `Avatar`, `Badge`, `Tooltip`,
  `sonner` toasts, `Loader`, `Media`, `Grid`, plus the app components above.
  Spacing = native Tailwind (`p-4`, `gap-3`); semantics = `q-` utilities
  (`bg-q-background-primary`, `text-q-body-md-regular`). For anything Quanta
  lacks, build your own component from Quanta primitives — never a third-party
  UI library.
- **Real end-to-end app** — Higgsfield auth (`references/auth.md`), server-side
  generation submit + poll, and the app's own product state in D1
  (saved/favorited, collections, presets, history). The signed-out state, auth
  guards, `/api/user`, cost preview, submit/poll routes, and D1 persistence are
  MANDATORY — see the checklist in `references/fnf-sdk.md`.
