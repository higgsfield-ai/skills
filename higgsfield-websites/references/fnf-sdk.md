# Skill: FNF SDK

Use this when the task touches `@higgsfield/fnf`: generation jobs, media upload,
profile/workspace data, adapters, observability, or server-side job submission.

Before coding, read:

- `app/packages/fnf/ai/AGENTS.md`
- `references/auth.md`

## Template Rules

- Adapter location: `@higgsfield/fnf` ships the SDK core, the backend ports,
  and exactly ONE bundled adapter — `createWorkflowPlatformAdapter`, at the
  `@higgsfield/fnf/workflow-platform` subpath (implementation:
  `app/packages/fnf/src/workflow-platform/`). That is the only adapter
  generated websites use, so the vendored `fnf` package is self-sufficient.
  The old `@higgsfield/fnf/adapters` subpath NO LONGER EXISTS — importing it
  is a build error. All other adapters (fnf-web, dev, apps-marketplace,
  memory) live in the separate `@higgsfield/fnf-adapters` package, which
  generated websites must not use.
- Keep fnf API calls server-side: `createServerFn` or `*.server.ts`.
- Do not call fnf from browser components.
- An SDK website is a real END-TO-END product, never a mock. It MUST have a real
  backend (server functions/routes) AND real persistence: opt into D1
  (`"db": true` in `app/app.manifest.json`) and store the app's own product
  state — saved/favorited generations, collections, projects, prompt presets,
  share records, in-app user data. fnf stays the source of truth for the
  generations themselves; D1 is your product layer on top of it. In-memory
  arrays, module-level state, `localStorage`-as-database, hardcoded fixtures, and
  memory/mock adapters shipped as the product are NOT a backend — they are bugs.
- A real generation website is never "just a form." If the prompt mentions using a
  Higgsfield model, SDK, generation, media upload, or model settings, the website
  must include auth, profile/credits/workspace display, submit/cost/media server
  operations, and a generation feed/history by default.
- If the website has any real SDK-backed generation/media/profile/credits feature,
  it must require auth. Implement `/api/user`, signed-out UI, login/logout, and
  a server-side auth check before each SDK operation.
- Do not use app-local/in-app auth as the guard for Higgsfield SDK operations.
  In-app auth can coexist for product users, but SDK submit/upload/profile/
  credits/feed routes must still be protected by Higgsfield auth through
  `/api/user` and server-side `https://fnf.internal/user`.
- Browser auth/user UI calls `/api/user`; that route proxies
  `https://fnf.internal/user` server-side. Do not call `fnf.internal` from the
  browser.
- Generated websites must use `createWorkflowPlatformAdapter` with
  `baseUrl: 'https://fnf.internal'` from server code. Do not use
  env-controlled backend URL selectors, public fnf URLs, dev fnf URLs,
  apps-marketplace, or direct product routes in generated websites.
- This strict rule is for Supercomputer/template-generated websites. If the user
  explicitly asks for a separate SDK consumer with another approved endpoint,
  use that host's adapter or custom SDK backend ports instead of forcing
  `fnf.internal`.
- Do not expose service secrets, dev user ids, bearer tokens, media upload URLs,
  prompts, or raw backend bodies to the client.
- Register only the job models the website uses.
- Upload/resolve media before submit.
- Display credits are already normalized when using `client.cost(input).credits`
  or `profile.getCredits()`. Raw wallet fields from `getWallet()` are
  credit-cents; divide by 100 or use `getCredits()` for UI.
- Observability is safe metadata only. Never emit prompts, params, headers,
  tokens, URLs, filenames, emails, workspace names, or raw bodies.

## Mandatory Generation Website Checklist

For prompts like "create a Nano Banana generation app", "build a Seedance form",
"make an image/video generator", or anything equivalent, deliver all of this:

- `GET /api/user` route that proxies `https://fnf.internal/user` server-side.
- Signed-out state with a Quanta sign-in button to
  `/__auth/login?return=<current path>`.
- Logout action to `/__auth/logout?return=/`.
- Server-side auth guard before every SDK submit, upload, cost, feed, profile,
  credits, workspace, Elements, character-training, realtime edit/finalize,
  and saved-style operation.
- Profile tab/panel showing safe user fields, current workspace, and display
  credits from profile APIs.
- Model form with validated settings for the requested model.
- Cost preview using the SDK cost path when supported by the chosen model.
- Submission confirmation gate: a browser confirmation modal (model, settings
  summary, cost preview) BEFORE calling the generate route, plus the adapter
  `confirm` option wired server-side (see "Submission Confirmation Gate"
  below). A declined confirmation surfaces as the typed
  `confirmation_rejected` error and renders as a cancelled state, not a
  failure.
- Media upload route using multipart `FormData` when the model accepts media.
- Submit route/server function using `createJobClient` and registered jobs.
- Feed/history panel using SDK list/get/getSet data so the user can see queued,
  running, completed, and failed generations after submit.
- Real persistence in D1 for the app's own product state (e.g. saved/favorited
  generations, collections, projects, prompt presets, share records):
  `"db": true` in `app/app.manifest.json` plus an additive
  `app/migrations/000N_*.sql`. Do not fake persistence with in-memory or
  `localStorage` state.
- Poll submitted generations until terminal status; do not stop after the
  submit response if jobs are still queued/running.
- Render actual SDK result media in the feed/history. Use
  `HiggsfieldGenerationCard` and `selectGenerationMedia`, or equivalent logic
  using SDK selectors (`getPreviewUrl`, `getRawUrl`, `getMediaType`,
  `getJobPhase`, `hasResult`, `isTerminalJobStatus`).
- Show prompt, model, status, created time, and failure reason where available.
  Do not render completed jobs as blank cards with only status/id text.
- Keep one truthful export-format contract for every media type. Preserve and
  label provider-native output, or carry a supported model format field through
  preview, confirmation, submit, and download. Never fake PNG/JPEG/WebP
  consistency by renaming a URL or filename.
- Request/debug logs on server SDK routes: method, logical operation/path,
  response status, SDK error code/status/message. Never log prompts, raw params,
  headers, tokens, cookies, upload URLs, filenames, emails, workspace names, or
  file bytes.

Omission is a bug. The ONLY exception is when the user EXPLICITLY asks for an
offline/mock demo (memory adapters, no network) — never choose a mock as the
default; the default is a real, end-to-end app with a real backend and D1.

## Output and download format contract

Choose the app's public export behavior once and apply it to every submit and
download path:

- If the registered model's documented schema exposes an output-format field,
  offer only its supported values, choose one app default, and carry that field
  in the same canonical SDK input used by `getWirePreview`, confirmation, and
  submit. Do not invent a universal `outputFormat` key; use the exact current
  job-schema field.
- Treat optimized previews as display derivatives only. `getPreviewUrl()` may
  legitimately resolve to WebP or another optimized encoding even when the
  raw/export asset is PNG or JPEG. Use `getRawUrl()` for open/download, or the
  URL of bytes the app genuinely transcoded server-side.
- Make bytes, MIME type, and filename agree. Derive the extension and
  `Content-Type` from trusted result metadata or the fetched raw response; a
  download proxy must forward/set matching `Content-Type` and
  `Content-Disposition`. Never save WebP bytes under `.png`, or infer format
  from the preview URL's suffix.
- If the product promises a fixed format that the model cannot guarantee,
  transcode the raw bytes in a real server-side path that supports the codec
  (a container when Worker-native capabilities are insufficient). If that path
  is not built, label and preserve the provider-native format instead of
  advertising a false fixed format.

For protected app-local downloads inside the Higgsfield iframe, also follow
`references/auth.md` → "Authenticated File Downloads". A direct raw link is
valid only when it is public or a self-contained signed URL requiring no
session.

## Elements and custom-reference character training

Use these capabilities when an app needs reusable user assets or a consistent
trained subject. Keep the concepts distinct:

- **Elements** are the signed-in user's reusable asset library. A Character is
  one kind of Element. Browse Elements with `createReferenceClient` from
  `@higgsfield/fnf/references`; do not call them all characters and do not
  invent app-local copies of the library.
- **Character training** is a separate multi-image custom-reference operation.
  Use `createCharacterClient` from `@higgsfield/fnf/characters`. Training
  creates a processing Character Element and returns a custom-reference id.
- **Generation** uses that custom-reference id as
  `settings.customReferenceId` on a compatible Soul job. Presets are not part
  of this flow.

All calls stay server-side after the Higgsfield auth guard and reuse the same
`createWorkflowPlatformAdapter({ baseUrl: 'https://fnf.internal' })`:

```ts
import { createCharacterClient } from '@higgsfield/fnf/characters'
import { createJobClient } from '@higgsfield/fnf/client'
import { soulV2Image } from '@higgsfield/fnf/jobs'
import { createReferenceClient } from '@higgsfield/fnf/references'
import { createWorkflowPlatformAdapter } from '@higgsfield/fnf/workflow-platform'

const adapter = createWorkflowPlatformAdapter({
  baseUrl: 'https://fnf.internal',
  confirm: async () => confirmationToken,
})

const elements = createReferenceClient({ adapter })
const characters = createCharacterClient({ adapter })
const jobs = createJobClient({ adapter, jobs: [soulV2Image] })

const library = await elements.list({ category: 'character', size: 50 })

// images are MediaRef values returned by media.upload(...) or compatible
// image job refs. Upload browser Files with multipart FormData first.
const pending = await characters.create({
  name: 'My character',
  type: 'soul_2',
  images,
})
const character = await characters.wait(pending)
if (character.status === 'failed')
  throw new Error(character.failReason ?? 'Character training failed')

const result = await jobs.submit({
  model: 'text2image_soul_v2',
  prompt: { instruction: 'Candid flash photo at a late-night diner' },
  settings: {
    customReferenceId: character.id,
    aspectRatio: '3:4',
    batchSize: 4,
  },
})
```

Character contract:

- Supported training types are `soul`, `soul_2` (default), and
  `soul_cinematic`. Expose the requested types; do not hard-code a
  `/soul-v2` transport or reimplement one backend variant.
- Training accepts 1–100 image references. `soul` accepts uploaded
  `media_input` refs only; `soul_2` and `soul_cinematic` also accept
  compatible image job refs whose type ends in `_job`.
- Poll `characters.get(id)` or `characters.wait(character)` until
  `completed` or `failed`. On completion, refresh the Elements list; the
  result may also expose `elementId`.
- Existing Character Elements expose `reference.characterId`; use that value
  as `customReferenceId`. The Element id and custom-reference character id
  are different ids.
- `references.list({ cursor, size, category })`,
  `references.get(elementId)`, `characters.create(...)`, and
  `characters.get(characterId)` are the public SDK operations. Never
  hand-write `/reference-elements` or `/custom-references` fetches.
- Do not add a custom per-image/per-job approval workaround around character
  training. Reuse platform auth, upload, submission, and approval
  infrastructure; the normal confirmation gate still applies to the Soul
  generation submission.

A complete Elements-and-character flow includes auth/profile/credits, an
existing Elements picker, multipart multi-image upload, create + poll character
states, Elements refresh, Soul generation using `customReferenceId`, the
normal confirmation/cost flow, generation polling, and history/result
rendering.

## Stateful realtime image editing and saved custom styles

Use the realtime client when an app needs successive image edits in one chain or
user-level saved styles:

```ts
import {
  buildRealtimeChainEditRequest,
  createRealtimeClient,
  type RealtimeChainEditInput,
} from '@higgsfield/fnf/realtime'
import { createWorkflowPlatformAdapter } from '@higgsfield/fnf/workflow-platform'

const adapter = createWorkflowPlatformAdapter({ baseUrl: 'https://fnf.internal' })
const realtime = createRealtimeClient({ adapter, jobAdapter: adapter })

const input: RealtimeChainEditInput = {
  params: {
    prompt: 'Turn this into a candid editorial portrait',
    resolution: '1k',
    aspectRatio: '1:1',
    images, // explicit MediaRef/image-job refs; at most four
  },
}
const cost = await realtime.estimateChainCost({
  resolution: input.params.resolution,
  aspectRatio: input.params.aspectRatio,
})
// Browser: request approval for the exact validated wire.
const wire = buildRealtimeChainEditRequest(input)
const confirmationToken = await window.hf.requestGeneration(
  'flux_klein_realtime',
  wire,
  { credits: cost.credits },
)
// Authenticated server function: submit the same input with its opaque token.
const edit = await realtime.editChain(input, { confirmationToken })
const generation = await realtime.pollEditJob(edit.jobId)

// Continue by passing edit.chainId and a new explicit image set.
await realtime.finalizeChain({ chainId: edit.chainId })
```

The confirmation call runs in the browser through
`window.hf.requestGeneration`; the client creation, edit, polling, finalize,
and style calls stay behind authenticated server functions. Send the opaque
token and the exact same input to the server; never log it. If one action
launches several independent edits, build every wire request first and use the
existing batch confirmation form, matching returned tokens by index. Every
`editChain` call is billable and intentionally not retried.

Realtime contract:

- Omit `chainId` to start; pass the returned `chainId` to continue. Previous
  outputs are not appended automatically: every attempt supplies its own
  `images` array of up to four uploaded `media_input` or image-job refs.
- Provide exactly one of `prompt` or structured `settings`. Structured
  settings may select a saved style with `style: 'custom'` and
  `customStyleId`.
- Use `getEditJob` / `pollEditJob` and normal `Generation` selectors to
  render the result. Call `finalizeChain` when the editing session ends.
- Saved styles are authenticated user-level data. Manage them only through
  `listCustomStyles`, `createCustomStyle`, `updateCustomStyle`, and
  `deleteCustomStyle`. A style reference `mediaId` must be an upload or job
  the user/app may access; a listed Element's metadata is not a raw-media
  picker.
- Never hand-write `/realtime/*` requests or invent a separate approval
  mechanism. Reuse the platform adapter, auth guard, multipart upload path, and
  confirmation infrastructure.

## Common Imports

```ts
import { createJobClient } from '@higgsfield/fnf/client'
import { createMediaClient } from '@higgsfield/fnf/media'
import { createProfileClient } from '@higgsfield/fnf/profile'
import { createWorkflowPlatformAdapter } from '@higgsfield/fnf/workflow-platform'
import { nanoBanana2, seedance2_0 } from '@higgsfield/fnf/jobs'
```

## Server Pattern

Create the adapter inside server-only code after auth has been checked.

```ts
const auth = await requireCurrentUser()
if (!auth.ok) {
  return new Response(JSON.stringify(auth.body), {
    status: auth.status,
    headers: { 'content-type': 'application/json' },
  })
}
```

Then create SDK clients with the fnf.internal logical-operation adapter:

```ts
const FNF_INTERNAL_BASE_URL = 'https://fnf.internal'

const adapter = createWorkflowPlatformAdapter({
  baseUrl: FNF_INTERNAL_BASE_URL,
  observability,
})

const jobs = createJobClient({ adapter, jobs: [seedance2_0, nanoBanana2] })
const media = createMediaClient({ mediaAdapter: adapter })
const profile = createProfileClient({ profileAdapter: adapter })
```

Generated websites use fnf.internal only:

```ts
const adapter = createWorkflowPlatformAdapter({
  baseUrl: 'https://fnf.internal',
  observability,
})
```

Do not pass `getToken`. Do not send `Authorization`. The platform attaches
identity automatically for server-side calls to `https://fnf.internal`.

This adapter sends SDK operations only under the fnf.internal logical route
families `/user`, `/workspaces/*`, and `/jobs/*`. The platform behind
fnf.internal decides final internal routing.

Do not add model-specific route logic in website code. The SDK builds validated wire
params, fnf.internal resolves final endpoints, and the website handles only safe
request/response state.

Generated websites must never use:

```ts
process.env.FNF_BASE_URL
const backendUrl = process.env.SOME_BACKEND_URL
createWorkflowPlatformAdapter({ baseUrl: backendUrl })
createFnfWebAdapter({ baseUrl: '...' })
createDevFnfWebAdapter(...)
createAppsMarketplaceAdapter(...)
fetch('https://fnf.internal/jobs') // hand-written request; use the SDK adapter
```

## fnf.internal Method Contract

Generated websites must not decide fnf.internal HTTP methods themselves. Use SDK
clients, and let `createWorkflowPlatformAdapter` send the correct operation:

| SDK operation | fnf.internal method/path |
| --- | --- |
| job submit | `POST /jobs/submit` |
| job cost | `POST /jobs/cost` |
| job cancel | `POST /jobs/{id}/cancel` |
| media presign | `POST /jobs/media/presign` |
| media confirm | `POST /jobs/media/{id}/confirm` |
| job get | `GET /jobs/{id}` |
| job set get | `GET /jobs/sets/{id}` |
| job list/feed | `GET /jobs?gen_type=...&size=...` |
| media get/list | `GET /jobs/media/{id}` / `GET /jobs/media?...` |
| Element get/list | `GET /reference-elements/{id}` / `GET /reference-elements?...` |
| character train/read | `POST /custom-references` / `GET /custom-references/{id}` |
| realtime edit/cost/finalize | `POST /realtime/chain/edit` / `POST /realtime/chain/cost` / `POST /realtime/chain/finalize` |
| saved style list/create | `GET /realtime/custom-styles` / `POST /realtime/custom-styles` |
| saved style update/delete | `PATCH /realtime/custom-styles/{id}` / `DELETE /realtime/custom-styles/{id}` |
| profile user | `GET /user` |
| workspace list/current/wallet | `GET /workspaces`, `/workspaces/current`, `/workspaces/wallet` |
| workspace switch | `POST /workspaces/switch` |

If the browser calls an app-local route for generation, that app route must be a
mutation route such as `POST /api/generate`; it must not be `GET`. The route
then checks auth server-side and calls `jobs.submit(...)`. Do not forward browser
requests directly to `fnf.internal`, `/jobs`, `/jobs/v2/*`, or `/api/user`.

For TanStack server functions, use `createServerFn({ method: "POST" })` for
submit, cost, media upload, workspace switch, and other write-like SDK
operations. Use GET only for pure read functions. A 405 / "Method Not Allowed"
on generation almost always means the generated website used a GET route/function
for a submit/cost/media operation, or tried to call a fnf.internal write
operation through a query string instead of letting the SDK use the static POST
route.

## Strict Media Upload Contract

Binary files must never cross a JSON server-function boundary. Do not pass
`File`, `Blob`, `ArrayBuffer`, `Uint8Array`, base64 strings, or arrays of bytes
inside `createServerFn` input or JSON request bodies. This causes stack overflows,
huge payloads, broken serialization, or unusable object-shaped bytes.

Use one of these two patterns:

1. Browser uploads to an app-local `POST /api/media/upload` route with
   `FormData`.
2. Browser uses `useAttachments` only when the provided media client has a safe
   browser-capable upload path. For server-only fnf.internal/auth flows, prefer
   the `FormData` route.

Then generation submits only the returned `MediaRef`:

```txt
File in browser
  -> POST multipart FormData /api/media/upload
  -> server auth guard
  -> media.upload({ source: bytes, ... })
  -> returns MediaRef
  -> POST JSON /api/generate with prompt/settings/MediaRef only
  -> server auth guard
  -> jobs.submit(...)
```

Client upload example:

```ts
const form = new FormData()
form.append('file', file)

const response = await fetch('/api/media/upload', {
  method: 'POST',
  body: form,
})

const upload = await response.json()
if (!upload.ok)
  throw new Error(upload.error?.code ?? 'upload_failed')
```

Do not set the `content-type` header manually for `FormData`; the browser must
add the multipart boundary.

Server upload route example:

```ts
import { createFileRoute } from '@tanstack/react-router'
import { createMediaClient } from '@higgsfield/fnf/media'

export const Route = createFileRoute('/api/media/upload')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const auth = await requireCurrentUser()
        if (!auth.ok) {
          return Response.json(
            { ok: false, error: { code: 'unauthorized', status: auth.status } },
            { status: auth.status },
          )
        }

        const form = await request.formData()
        const file = form.get('file')
        if (!(file instanceof File)) {
          return Response.json(
            { ok: false, error: { code: 'missing_file' } },
            { status: 400 },
          )
        }

        console.info('[api/media/upload] file', {
          contentType: file.type,
          size: file.size,
        })

        const bytes = new Uint8Array(await file.arrayBuffer())
        const media = createMediaClient({ mediaAdapter: adapter })
        const result = await media.upload({
          source: bytes,
          filename: 'upload',
          contentType: file.type,
          type: 'image',
          forceIpCheck: true,
        })

        return Response.json({ ok: true, ref: result.ref })
      },
    },
  },
})
```

Generation route input must look like this:

```ts
{
  prompt: string
  settings: { aspectRatio: '3:4', resolution: '1k', batchSize: 1 }
  media?: { image?: MediaRef }
}
```

Do not include `file`, `blob`, `bytes`, `arrayBuffer`, `base64`, or raw
`data:image/...` values in generation input. If upload fails with
`Maximum call stack size exceeded`, the website almost certainly tried to serialize
binary through JSON or used `String.fromCharCode(...bytes)` on a large file.

## Job Client Pattern

Only call the job client after the server auth guard succeeds.

Register exactly the models the website exposes:

```ts
const jobs = createJobClient({
  adapter,
  jobs: [seedance2_0, nanoBanana2],
})
```

Use public camelCase settings:

```ts
await jobs.submit({
  model: 'seedance_2_0',
  prompt: { instruction: prompt },
  settings: {
    mode: 'std',
    duration: 5,
    aspectRatio: '16:9',
    resolution: '720p',
    batchSize: 1,
  },
})
```

Never send snake_case settings from UI code. The SDK maps `aspectRatio` to
`aspect_ratio`, `batchSize` to `batch_size`, and similar wire fields through
job schemas.

Server-function submit example:

```ts
import { createServerFn } from '@tanstack/react-start'
import { z } from 'zod'
import { createJobClient } from '@higgsfield/fnf/client'
import { createWorkflowPlatformAdapter } from '@higgsfield/fnf/workflow-platform'
import { nanoBanana2 } from '@higgsfield/fnf/jobs'

export const generate = createServerFn({ method: 'POST' })
  .inputValidator(z.object({
    prompt: z.string().min(1),
    // set by the browser confirmation modal — see "Submission Confirmation Gate"
    confirmed: z.literal(true),
  }))
  .handler(async ({ data }) => {
    const auth = await requireCurrentUser()
    if (!auth.ok) {
      return {
        ok: false as const,
        code: 'unauthorized',
        status: auth.status,
      }
    }

    const adapter = createWorkflowPlatformAdapter({
      baseUrl: 'https://fnf.internal',
      confirm: async () => {
        if (!data.confirmed)
          throw new Error('user did not confirm the submission')
      },
    })

    const jobs = createJobClient({ adapter, jobs: [nanoBanana2] })
    const result = await jobs.submit({
      model: 'nano_banana_2',
      prompt: { instruction: data.prompt },
      settings: { aspectRatio: '3:4', resolution: '1k', batchSize: 1 },
    })

    return { ok: true as const, result }
  })
```

Do not use `createServerFn({ method: "GET" })` or a `GET` server route for
generation. Generation is a mutation even when the form has no uploaded file.

## LLM chat / text — `createLlmClient` (NOT a job)

Chat/text generation is separate from the media jobs registry. Worker-side
ONLY, zero-token (no `getToken`/`userId` — the platform attaches the visitor's
identity and bills their credits):

```ts
import { createLlmClient } from '@higgsfield/fnf'
const llm = createLlmClient({ baseUrl: 'https://fnf.internal/llm' })

const [model] = await llm.listModels()
if (!model) throw new Error('No LLM models are currently available')

const res = await llm.complete({
  model,
  messages: [{ role: 'user', content: '…' }],
})
// llm.stream(...) yields OpenAI-shape SSE deltas; tool-calling supported
// (LlmToolDef / LlmToolCall). In React: FnfProvider's `llm` prop + useFnfLlmClient().
```

Model availability is runtime gateway configuration. Never hardcode a catalog
or claim that one model is always available. Call `listModels()` server-side,
use the exact returned id, and handle an empty list. Model pickers may receive
those ids through an authenticated app-local server function or route; if a
previously selected id disappears, refresh the list and show that it is no
longer available instead of silently substituting another model.

**App-only.** Text generation is generation → `type: "app"` (Sign in with
Higgsfield, visitor credits). NEVER on a `type: "website"` build, and never a
"bring your own LLM key" path.

## Submission Confirmation Gate

The SDK requires hosts that submit generations on behalf of a user to
implement a confirmation gate. Every generation adapter factory accepts a
`confirm` option (`ConfirmSubmit` from `@higgsfield/fnf`); `jobs.submit` calls
it once per submission — after validation, before any network call. Resolve to
proceed (a resolved string rides the create request as `confirmation_token`);
reject/throw to abort with the typed `confirmation_rejected` error.

In a generated website the submit runs server-side, so split the gate across
the boundary:

1. Browser: before calling the generate server function, show a Quanta
   confirmation modal with the model, a settings summary, and the cost preview.
   Only call the generate function after the user confirms; send
   `confirmed: true` (or an app-minted confirmation token) in the JSON input.
2. Server: wire the adapter's `confirm` to that input — resolve when the
   browser confirmed, throw when it did not:

```ts
const adapter = createWorkflowPlatformAdapter({
  baseUrl: 'https://fnf.internal',
  // Runs during jobs.submit, after validation, before any network call.
  confirm: async () => {
    if (!data.confirmed)
      throw new Error('user did not confirm the submission')
    return data.confirmationToken // optional; sent as confirmation_token
  },
})
```

Rules:

- Never auto-confirm (`confirm: async () => {}` with no browser modal defeats
  the gate). The modal is mandatory for real generation websites.
- Branch on `error.code === 'confirmation_rejected'` and render it as a
  user-cancelled state (quiet), not an error toast.
- The confirmation token is a token: never log it or emit it through
  observability.

## Generation Result Rendering Contract

Every real generation website must show submitted and historical generations with
real media previews. Use the template helpers by default:

```tsx
import { HiggsfieldGenerationCard } from "@/components/higgsfield-generation-card"
import { selectGenerationMedia } from "@/lib/higgsfield-generation-results"
```

The helper uses the SDK read model:

- image cards render `getPreviewUrl(generation)` for the optimized preview and
  `getRawUrl(generation)` for open/download.
- video cards render `getRawUrl(generation)` as the playable `<video src>` and
  `generation.results.thumbnailUrl` / `getPreviewUrl(generation)` as the poster
  when the preview is an image.
- pending/queued/in-progress/ip-detect states render progress UI.
- failed/nsfw/canceled/ip-detected states render the status/failure reason.
- completed jobs with no result URL render "Preview unavailable" and keep a
  refresh/get action available.

When writing custom cards, keep the same selector contract:

```ts
import {
  getJobPhase,
  getMediaType,
  getPreviewUrl,
  getRawUrl,
  hasResult,
  isTerminalJobStatus,
} from "@higgsfield/fnf/client"
```

Never inspect raw backend `results.raw.url` objects in website UI. The SDK adapter
normalizes product/WFP responses into `Generation.results`; render that model.
Never log prompts or raw media URLs. Displaying the signed-in user's prompt in
their own UI is allowed.

## Model Catalog Snapshot

Use the package guide as source of truth, but common generated-website choices are:

- Images: `soulV2Image`, `soulCinemaImage`, `gptImage2`, `seedreamV4_5`,
  `nanoBanana2`, `nanoBananaFlash`, `recraftV41Image`.
- Video: `seedance2_0`, `kling3_0`, `kling3MotionControl`, `happyHorse`,
  `grokImagine`, `grokImagineV15`, `veo3_1Lite`, `wan27`.
- Upscale: `topazImageUpscale`, `topazImageGenerativeUpscale`,
  `nanoBanana2Upscale`, `topazVideoUpscale`, `higgsfieldVideoUpscale`,
  `soraEnhanceVideo`, `bytedanceVideoUpscale`.

Import only the entries the screen needs. The `jobs: [...]` array is the source
of model autocomplete and media-role narrowing.

## Media Pattern

Use `createMediaClient({ mediaAdapter: adapter })` server-side after auth, or
behind a safe client boundary that still reaches a server auth guard. Upload
first, then submit the returned `MediaRef`:

```ts
const upload = await media.upload({
  source: fileBytes,
  filename: 'input.png',
  type: 'image',
  forceIpCheck: true,
})

await jobs.submit({
  model: 'nano_banana_2',
  media: { image: upload.ref },
  prompt: { instruction: prompt },
})
```

Attach/resolve media metadata before submit when local validation depends on
dimensions or duration. Unknown metadata is allowed locally; backend remains
authoritative.

Allowed `media.upload({ source })` values are only `Blob`, `ArrayBuffer`,
`Uint8Array`, or `{ read: async () => Blob | ArrayBuffer | Uint8Array }`. The SDK
throws `invalid_media_source` for JSON-shaped objects so broken upload plumbing
fails clearly before presign/transfer.

## Profile And Workspace

Use the profile domain for account/workspace panels:

```ts
const snapshot = await profile.getSnapshot()
const credits = await profile.getCredits({ includeOnDemand: true })
await profile.switchWorkspace({ workspaceId })
```

Workspace switching updates backend context only. The website still owns routing,
session metadata, adapter header state, and cache invalidation.

Do not use `profile.getUser()` directly in browser components for auth gating.
For browser UI, use `/api/user` from `references/auth.md`. Use the SDK profile
client server-side when the website is already performing SDK-backed account,
workspace, wallet, or credit operations.

Credit display rule:

- `profile.getWallet()` returns raw backend credit-cent values.
- `profile.getCredits()` returns display credits.
- `profile.getCredits()` returns a `ProfileCredits` object, not a number. Use
  `credits?.totalAvailableCredits`, `credits?.availableCredits`, or
  `snapshot.credits?.totalAvailableCredits` in UI.
- `jobs.cost(input).credits` returns display credits.
- Do not show raw wallet values directly in UI.

## Marketplace / Service Adapters Are Not For Generated Websites

Some fnf snapshots include `createAppsMarketplaceAdapter`. It is server-side
only, defaults to the dev apps-marketplace backend for now, and is for SDK smoke
tests or trusted service experiments only. Generated websites must not use it.
Generated websites use
`createWorkflowPlatformAdapter({ baseUrl: 'https://fnf.internal' })`
exclusively.

## Job UI Pattern

For a generated website UI:

1. Build the form with Quanta components.
2. Load `/api/user` before enabling SDK-backed controls.
3. If signed out, show sign-in UI and disable/hide generation, upload, cost,
   feed/history, profile, workspace, and credit actions.
4. Confirm before submit: show the confirmation modal (model + cost) and call
   the generate function only after the user confirms; wire the adapter
   `confirm` option server-side (see "Submission Confirmation Gate").
5. Keep submit/cost/profile/media calls in server functions or safe app-local
   server-only modules.
6. Re-check auth inside each server function before calling SDK clients.
7. Return only safe data to the browser: generation ids, statuses, display
   credits, and sanitized errors.
8. Use `safeSubmit`/typed error codes when crossing worker/iframe boundaries.
9. Show validation, cost, upload state, running state, terminal state,
   cancelled-confirmation state (`confirmation_rejected`), and typed errors as
   real UI states.

Do not build anonymous real generation. The only allowed anonymous SDK-looking
flow is a mock/offline demo the user EXPLICITLY asked for (memory adapters, no
network requests) — never the default.

## Troubleshooting Generation 405

If sign-in works but generation fails with `Method Not Allowed`:

1. Confirm the app-local generation function/route is `POST`, not `GET`.
2. Confirm the code calls `jobs.submit(...)` or `jobs.cost(...)` through the SDK,
   not hand-written `fetch('/jobs?...')`.
3. Confirm `createWorkflowPlatformAdapter({ baseUrl })` uses exactly
   `https://fnf.internal`, not the deployed website URL, `/api/user`, a public fnf
   URL, a dev fnf URL, or a model-specific fnf route.
4. Confirm the server handler re-checks `https://fnf.internal/user` before SDK
   calls, then creates the adapter/client inside the server handler.
5. Confirm reads use SDK-backed GET routes such as `/jobs`, `/jobs/{id}`, or
   `/jobs/sets/{id}`, while submit/cost/cancel/media writes use SDK-backed POST
   routes such as `/jobs/submit`, `/jobs/cost`, and `/jobs/media/presign`. Do
   not send submit/cost/media operations through GET query parameters.

If upload fails with `Maximum call stack size exceeded`:

1. Search for `String.fromCharCode(...`, base64 conversion, `JSON.stringify(file)`,
   `Array.from(bytes)`, or passing `File`/`Blob`/`ArrayBuffer` to
   `createServerFn` input.
2. Replace that flow with `FormData` POST to `/api/media/upload`.
3. Return only `{ ref: MediaRef }` from upload.
4. Send only that `MediaRef` in generation JSON.
5. Add logs for file `size` and `contentType`, but never file bytes, upload URL,
   token, raw prompt, or raw backend body.

## Observability

SDK observability is a safe metadata callback. It is not product analytics by
default and it must not leak prompts, params, headers, tokens, URLs, filenames,
emails, workspace names, or raw bodies.

Allowed metadata examples: model id, operation, status, duration, safe job id,
safe media id, media type, credit estimate, and error code.

Pass observability to the adapter as well as clients when debugging transport
problems:

```ts
const adapter = createWorkflowPlatformAdapter({
  baseUrl: 'https://fnf.internal',
  observability,
})

const jobs = createJobClient({ adapter, jobs: [nanoBanana2], observability })
const media = createMediaClient({ mediaAdapter: adapter, observability })
```

Without adapter observability you may see `fnf.job.submit` fail but not the
underlying `fnf.transport.request` method/path/status.
