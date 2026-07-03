# app-layouts — the standard Higgsfield app layouts (`type: "app"` builds ONLY)

A `type: "app"` product must look and feel like a Higgsfield product. Instead of
inventing app chrome from scratch, START from one of the four standard layouts
below — they mirror how Higgsfield's own tools (fnf-web) are laid out, and each
one ships as a READY SCAFFOLD in the template under **`app/src/layouts/`** (read
`app/src/layouts/AGENTS.md`). Copy the closest scaffold into your route and
adapt it: the scaffolds are prop-driven (data, handlers, and slot nodes all
arrive via props) and each file's header comment carries its exact fnf-react
wiring recipe. **If the user asks for a different layout, build what they ask
for** — the standard layouts are the default, not a cage (a custom layout is
still built with Quanta components + `q-` tokens).

Every layout is composed from Quanta (`references/quanta-design.md`,
`app/packages/quanta/ai/AGENTS.md` for the canonical API) and must be a real
end-to-end app per `references/fnf-sdk.md`: Higgsfield auth
(`references/auth.md`), server-side generation submit + poll, results rendered
with `higgsfield-generation-card.tsx`, and the app's own product state in D1
(saved/favorited, collections, presets, history).

## Choosing a layout

| Product shape | Layout | Scaffold file |
|---|---|---|
| Multi-asset creative workspace: prompt → many generations, browse/organize output | **Marketing studio** | `app/src/layouts/marketing-studio-layout.tsx` |
| Guided flow with a fixed sequence of choices ending in one result | **Stepper** | `app/src/layouts/stepper-layout.tsx` |
| One transform, minimal inputs (e.g. swap a face, restyle one photo) | **Simple app** | `app/src/layouts/simple-app-layout.tsx` |
| Enhance/convert ONE uploaded asset with a couple of options | **Upscaler** | `app/src/layouts/upscaler-layout.tsx` |
| Anything else the user describes | Custom — compose it from Quanta, keep the anatomy rules below | — |

## 1. Marketing studio — the workspace

The full creative-tool layout (fnf-web's Marketing Studio is the reference).

- **Left rail** — Quanta `Sidebar` (`@higgsfield/quanta/sidebar`): logo/title in
  the header, nav rows for the app's surfaces (Create, Library/History,
  Collections, Settings), the signed-in user (Avatar) at the bottom. Collapsible.
- **Main canvas** — a responsive grid of generation results (media cards built
  on `higgsfield-generation-card.tsx`; empty state via `not-found`/empty
  patterns; skeleton `loader` while polling).
- **Prompt/settings panel** — bottom-docked: **`PromptBox`**
  (`@higgsfield/quanta/prompt-box`), the standard generation prompt surface.
  `PromptBox.Root` owns value/maxLength/disabled/submitting/onSubmit;
  `PromptBox.Input` auto-grows and submits on Enter (Shift+Enter = newline);
  drop the model/options `Dropdown`/`Select` controls into
  `PromptBox.Toolbar`; the cost preview + `PromptBox.Counter` +
  `PromptBox.Submit` (Loader while submitting) go in `PromptBox.Actions`;
  reference/upload chips go in `PromptBox.Attachments`. Use PromptBox for the
  prompt surface in EVERY layout that takes a prompt — never hand-roll it.
- Product state in D1: every generation the user keeps, plus
  collections/projects.

## 2. Stepper — the guided flow

A linear wizard for products where the user makes a fixed sequence of choices
(upload → configure → generate → result).

- A step indicator across the top (compose from `Tabs` or `Progress` + labels);
  steps are navigable backward, never skippable forward.
- ONE focused decision per step, centered card (`card`) with the step's input:
  media upload, `Radio`/`Select` options, prompt text.
- Final step: submit → poll with `loader` + progress copy → result rendered
  large with actions (download, regenerate, save).
- Persist the flow state so a refresh doesn't lose progress (D1 or route state).

## 3. Simple app — the one-shot tool (faceswap-style)

A single screen, no navigation: two or three inputs and one primary action.

- Centered column: input slots (e.g. source photo + target photo as two upload
  cards), the option row if any, one primary `Button`.
- Result appears in place (before/after where it fits), with download / try
  again / save actions.
- History strip (the user's previous runs, from D1) under the tool — optional
  but recommended.

## 4. Upscaler — the single-asset enhancer

One asset in, an enhanced asset out.

- A large drop zone / upload card as the hero of the page.
- An options row (scale/quality via `Select` or `Toggle`s) + cost preview +
  primary `Button`.
- Result: a before/after compare (slider where feasible), then download + save.
- Recent enhancements from D1 below.

## Anatomy rules (all layouts, incl. custom)

- Quanta components before custom markup: `Button`, `Input`, `Textarea`,
  `Dropdown`, `Select`, `Modal`, `Tabs`, `Sidebar`, `Avatar`, `Badge`,
  `Tooltip`, `sonner` toasts, `loader`. Spacing = native Tailwind (`p-4`,
  `gap-3`); semantics = `q-` utilities (`bg-q-background-primary`,
  `text-q-body-md-regular`).
- The signed-out state, auth guards, `/api/user`, cost preview, submit/poll
  routes, and D1 persistence are MANDATORY — see the checklist in
  `references/fnf-sdk.md`.
- Generation results always render through `higgsfield-generation-card.tsx`,
  never a bare `<img>`.
- Polish per `references/minimalist-ui.md`: real empty/loading/error states,
  keyboard focus states, responsive down to mobile.
