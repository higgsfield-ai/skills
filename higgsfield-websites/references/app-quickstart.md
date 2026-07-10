# App quickstart — the working critical path

Read this FIRST when building a `type: "app"` product. It is the copy-paste
spine every generation app shares: auth → SDK client → submit/poll → render, plus
the handful of Quanta components you'll reach for. Everything here is real,
correct, and enough to build from — you do **not** need to open
`app/packages/{quanta,fnf,fnf-react}/src/**` to confirm any of it. For the full
detail behind each step, the deeper references are cross-linked; for component
props, `app/packages/quanta/ai/AGENTS.md` has the per-component reference.

**Golden rules (violating these is the usual cause of a broken or slow build):**

1. **Don't read package source.** Props are in `app/packages/quanta/ai/AGENTS.md`;
   SDK/hooks are in `app/packages/fnf/ai/AGENTS.md` + `.../fnf-react/ai/AGENTS.md`
   (mirrored by `references/fnf-sdk.md` + `references/fnf-react.md`). Reading
   `src/` is the single biggest time sink. If a detail is truly missing, make the
   reasonable call and let `bun run typecheck` catch a mistake.
2. **fnf runs server-side only** against `https://fnf.internal` — never from the
   browser, never with tokens in app code (`references/auth.md`, rule 3 in
   `app-flow.md`).
3. **Always dark, no app header.** `data-theme="default-dark"` is pinned; the
   Higgsfield host provides the global header/account chrome. Container is
   `mx-auto w-full max-w-7xl` (`references/quanta-design.md`).
4. **Real backend + real D1, never a mock.** (rule 3a in `app-flow.md`.)

---

## 1. Auth — the `/api/user` proxy + login/logout

Every app is authenticated. Full contract in `references/auth.md`; the three
pieces you always write:

```ts
// app/src/routes/api/user.ts — browser-safe proxy; preserve status + body 1:1
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/user')({
  server: {
    handlers: {
      GET: async () => {
        const upstream = await fetch('https://fnf.internal/user')
        const body = await upstream.text()
        return new Response(body, {
          status: upstream.status, // a 401 must stay a 401
          headers: {
            'content-type': upstream.headers.get('content-type') ?? 'application/json',
            'cache-control': 'no-store',
          },
        })
      },
    },
  },
})
```

```ts
// Browser: read the current user; null = signed out (don't crash the page)
export async function fetchCurrentUser() {
  const res = await fetch('/api/user', { credentials: 'include' })
  if (res.status === 401) return null
  if (!res.ok) throw new Error('Failed to load user')
  return res.json()
}

// Login / logout are browser NAVIGATION, not SDK calls:
const login = (ret = location.pathname + location.search) =>
  { location.href = `/__auth/login?return=${encodeURIComponent(ret)}` }
const logout = (ret = '/') =>
  { location.href = `/__auth/logout?return=${encodeURIComponent(ret)}` }
```

A signed-out surface renders a sign-in action that calls `login()`; a server-side
re-check guards every SDK operation. Do not invent an email/password form.

## 2. Create the SDK clients (server-side)

One adapter satisfies jobs + media + profile. Import the adapter from
`@higgsfield/fnf/workflow-platform` (NOT `/adapters` — that subpath is gone):

```ts
import { createJobClient } from '@higgsfield/fnf/client'
import { createMediaClient } from '@higgsfield/fnf/media'
import { createProfileClient } from '@higgsfield/fnf/profile'
import { createWorkflowPlatformAdapter } from '@higgsfield/fnf/workflow-platform'
import { gptImage2 } from '@higgsfield/fnf/jobs' // register ONLY the jobs you use

const adapter = createWorkflowPlatformAdapter({ baseUrl: 'https://fnf.internal' })
const jobs = createJobClient({ adapter, jobs: [gptImage2] })
const media = createMediaClient({ mediaAdapter: adapter })
const profile = createProfileClient({ profileAdapter: adapter })
```

The `jobs: [...]` registry is what gives `model`/`settings` their TypeScript
narrowing. Catalog of models in `app/packages/fnf/ai/AGENTS.md` ("Current SDK
catalog") — e.g. `gptImage2`→`gpt_image_2`, `nanoBanana2`→`nano_banana_2`,
`seedance2_0`, `kling3_0`.

## 3. Submit (with the confirmation gate) → poll → read the URL

The `confirm` gate is passed to the **adapter factory**; it runs once per submit,
after validation, before any network call. Rejecting is a user choice, not a
failure (typed `confirmation_rejected`).

```ts
const adapter = createWorkflowPlatformAdapter({
  baseUrl: 'https://fnf.internal',
  confirm: async ({ jobSetType }) => {
    // UI host opens its cost-preview modal here and resolves; reject to cancel.
    if (!(await openConfirmModal(jobSetType))) throw new Error('declined')
  },
})

const { generations } = await jobs.submit({
  model: 'gpt_image_2',
  prompt: { instruction: userPrompt },
  settings: { aspectRatio: '1:1', quality: 'high', resolution: '2k', batchSize: 1 },
})

const [done] = await jobs.wait(generations, {
  signal,
  onProgress: g => console.log(g.status),
})
```

Prefer `safeSubmit` across a client/server or iframe boundary and branch on
`error.code` (survives JSON; `instanceof` does not):

```ts
const r = await jobs.safeSubmit(input)
if (!r.ok) {
  if (r.error.code === 'out_of_credits') return showBillingUI()
  if (r.error.code === 'confirmation_rejected') return // declined — not an error
  throw r.error
}
```

Common codes: `out_of_credits`, `rate_limit`, `prompt_nsfw`, `ip_detected`,
`job_failed`, `timeout`, `validation`, `confirmation_rejected`
(`app/packages/fnf/ai/AGENTS.md`, "Errors and boundaries").

## 4. Render the result

`generation.results` is a single object `{ rawUrl, minUrl?, thumbnailUrl? }`,
present only once completed. Do NOT hand-roll URL selection — use the selectors:

```ts
import { getPreviewUrl, getRawUrl, getJobPhase } from '@higgsfield/fnf/client'

getPreviewUrl(done)  // grids/cards — precedence minUrl → thumbnailUrl → rawUrl
getRawUrl(done)      // full quality
getJobPhase(done)    // 'progress' | 'completed' | 'failed' — drives state UI
```

In-app, compose result cards from `app/src/lib/higgsfield-generation-results.ts`
(`selectGenerationMedia(generation)` returns a resolved `image | video | empty`
union). A completed generation with no `rawUrl` must show an explicit
"preview unavailable" state with refresh — never a blank card.

## 5. React wiring (fnf-react hooks)

- **`useGenerationRun(client, opts?)`** — drives one submission end-to-end.
  Returns `{ status, generations, isRunning, error, start(input), abort(), reset() }`;
  `start` never rejects (errors land in `error`). `client` must be referentially
  stable. Best for the "generate" button flow.
- **Live read of one job:** `useQuery(generationQueryOptions(jobClient, jobId, { scopeKey }))`
  — polls every 5s while non-terminal, stops when terminal. (There is no
  `useGeneration` hook.)
- **`useAttachments(media, opts?)`** — upload controller for input images/media:
  `{ items, refs, isUploading, add(files, { role }), settled(), remove(key) }`.
  `await controller.settled()` yields submit-ready `MediaRef[]`.

## 6. Media upload — binary never goes through JSON

Never pass `File`/`Blob`/`ArrayBuffer`/base64 through `createServerFn` input or a
JSON body. Use multipart to an app-local route:

```txt
browser File → POST multipart /api/media/upload → media.upload(...) → MediaRef
MediaRef + prompt/settings → submit
```

Server reads `await file.arrayBuffer()`, calls `media.upload({ source: bytes, … })`,
returns only the `MediaRef`. Detail in `references/fnf-sdk.md` ("Media recipes").

## 7. Server functions + bindings

App data operations run through TanStack server functions or `/api/*` routes:

```ts
import { createServerFn } from '@tanstack/react-start'
import { z } from 'zod'

export const generateMeme = createServerFn({ method: 'POST' })
  .inputValidator(z.object({ prompt: z.string().min(1) }))
  .handler(async ({ data }) => {
    // re-check auth, build the server-side adapter, submit, persist to D1…
  })
```

Cloudflare bindings (D1 `DB`, R2 `STORAGE`, KV `KV`) are read server-side via
`app/src/lib/bindings.server.ts` (`import { env } from "cloudflare:workers"`), and
only exist if declared in `app/app.manifest.json` (`"db": true`, etc.). Guard
before use. Runtime detail in `references/runtime-and-infra.md`.

**Return flat, fully-typed DTOs — never a raw SDK object.** TanStack Start
compile-time-checks that every server-function return value is serializable, and
SDK types like `Generation` carry `input.settings: Record<string, unknown>` —
`unknown` fails that check and breaks the build. Map the SDK object to a small
DTO with only the fields the client needs (`{ id, status, previewUrl, … }`),
typed explicitly. Same rule for anything you hand back across the server/client
boundary: no `unknown`, no class instances, plain JSON-shaped data.

**`import type` React types.** In module files there is no `React` UMD global,
so bare `React.ReactNode` / `React.CSSProperties` fail to compile — write
`import type { ReactNode, CSSProperties } from "react"` and use them unqualified.

## 8. The Quanta components you'll actually use

All dark, composed — never restyled. Props reference:
`app/packages/quanta/ai/AGENTS.md` ("Component API reference"). The core set:

```tsx
import { Button } from '@higgsfield/quanta/button'
import { Textarea } from '@higgsfield/quanta/textarea'
import { Media } from '@higgsfield/quanta/media'
import { Loader } from '@higgsfield/quanta/loader'
import { toast } from '@higgsfield/quanta/sonner'

// The generation CTA is ALWAYS marketingPrimary with the credit cost inside:
<Button variant="marketingPrimary">
  Generate <SparklesIcon /> {credits}
</Button>

// Prompt field: helper/error props are `description`/`error` (NOT helperText/errorText)
<Textarea label="Prompt" description="Describe your meme" value={v} onChange={e => setV(e.target.value)} />

// Result tile:
<Media.Root ratio="square" rounded="lg">
  {phase === 'completed'
    ? <Media.Image src={getPreviewUrl(gen)} alt={prompt} />
    : <Media.Fallback><Loader variant="stars" /></Media.Fallback>}
</Media.Root>
```

Reach for: `Button` (actions/CTA), `Textarea`/`Input` (prompt/fields),
`Select`/`Dropdown` (options), `Slider`/`Switch`/`Chip` (settings), `Media`
(result tiles), `Card`/`Glass` (surfaces), `Grid`/`VirtualGrid` (feeds),
`Loader`/`Progress` (busy), `Modal`/`Vault` (dialogs/sheets), `toast` (notices).
For a gap, build a small component from Quanta primitives in
`app/src/components/` — never a third-party UI library, never restyle Quanta.

---

**Then follow `app-flow.md` steps 6–8:** deploy → cover + metadata (generate the
cover per `references/app-cover.md`) → publish (automatically if the user opted in
at intake, else when asked), then suggest the contest.
