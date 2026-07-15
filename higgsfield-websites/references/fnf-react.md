# Skill: FNF React

Use this when the task touches `@higgsfield/fnf-react`: React providers,
TanStack Query options, generation run controllers, attachments, profile
queries, workspace switching, cache keys, or request previews.

Before coding, read `app/packages/fnf-react/ai/AGENTS.md` and, for model contracts,
`app/packages/fnf/ai/AGENTS.md`. For generated apps with real generation/media/
profile/credits, also read `references/auth.md`. For the visible UI around these
hooks, also read `app/packages/quanta/ai/AGENTS.md` and `references/quanta-design.md`.

## Package Philosophy

- `fnf-react` is UI-free.
- It provides stable clients, query options, cache helpers, and external-store
  controllers.
- It must not add product copy, toasts, auth redirects, plan gates, or visual
  components.
- It pairs with Quanta in generated websites: fnf-react owns data/lifecycles,
  Quanta owns controls/layout/feedback.
- It does not make anonymous generation safe. The host must provide auth gating
  and safe adapter boundaries before exposing generation/media/profile actions.
- Any real generation screen must include both the submit lifecycle and a
  feed/history surface. Do not build a submit-only page for SDK-backed models.

## Provider Shape

Use `QueryClientProvider` above the website, then `FnfProvider` where SDK clients
are needed.

For real SDK-backed generation/media/profile/credits, render `FnfProvider` only
inside an authenticated website boundary or pass clients that call authenticated
server functions. Signed-out users should see sign-in UI, not active generation
controls.

This boundary means Higgsfield auth, not the generated website's own local sign-in.
If the website also has in-app accounts for its product data, keep those sessions
separate. `FnfProvider` and every SDK-backed route still require `/api/user` and
server-side `https://fnf.internal/user` guards.

```tsx
import { FnfProvider } from '@higgsfield/fnf-react'

<FnfProvider
  adapter={adapter}
  jobs={jobs}
  mediaAdapter={adapter}
  profileAdapter={adapter}
  scopeKey={workspaceId}
>
  {children}
</FnfProvider>
```

Provider hooks:

- `useFnf()` returns the composed client bundle.
- `useFnfJobClient()` returns the SDK job client.
- `useFnfRealtimeClient()` returns the stateful image-editing/custom-style
  client when the adapter implements the realtime backend (or an explicit
  `realtimeAdapter` is supplied).
- `useFnfCharacterClient()` returns the character-training client.
- `useFnfReferenceClient()` returns the signed-in user's Elements client.
- `useFnfMediaClient()` returns the SDK media client.
- `useFnfProfileClient()` returns the SDK profile client.
- `useFnfLlmClient()` returns the LLM chat/text client (OpenAI-shape
  `complete`/`stream`, tool-calling) when a browser-safe `llm` backend is
  passed to `FnfProvider`; the hook throws if none was provided. The raw
  `createLlmClient({ baseUrl: 'https://fnf.internal/llm' })` client is
  Worker-side only (zero-token — the platform attaches the visitor's identity
  and bills their credits) and must be called through authenticated app-local
  server functions or routes. Discover the exact available model ids there via
  `listModels()`; never ship the raw client or a hardcoded catalog to browser
  code. App-only, not for a `type: "website"` build. See
  `references/fnf-sdk.md` → "LLM chat / text".
- `useFnfJobs()` returns the registered model entries.
- `useFnfScopeKey()` returns the cache scope.
- `useFnfObservability()` returns the observer config.

Keep `adapter`, `jobs`, `blobUploader`, `resolveJob`, and `observability`
references stable. Do not create a new adapter or new job array on every render.

## Cache Rules

- Use exported query option factories and `fnfKeys`.
- Do not hand-build query key arrays.
- Use cache-door helpers for generation updates.
- Workspace switches should scope or clear generation/feed/job-set/cost and
  realtime caches.
- Use `scopeKey` for user/workspace-aware websites, usually
  `${userId}:${workspaceId}`.
- Use profile query options for profile panels and workspace switchers.

Common query helpers:

```ts
characterQueryOptions(characterClient, characterId, { scopeKey })
referenceQueryOptions(referenceClient, elementId, { scopeKey })
referencesQueryOptions(referenceClient, { category: 'character' }, { scopeKey })
generationQueryOptions(jobClient, id, { scopeKey })
jobSetQueryOptions(jobClient, jobSetId, { scopeKey })
jobsFeedQueryOptions(jobClient, { type: 'image', size: 20 }, { scopeKey })
profileSnapshotQueryOptions(profileClient, { scopeKey })
profileCreditsQueryOptions(profileClient, { scopeKey, includeOnDemand: true })
costQueryOptions(jobClient, input, { scopeKey, enabled })
realtimeChainCostQueryOptions(realtimeClient, input, { scopeKey, enabled })
realtimeCustomStylesQueryOptions(realtimeClient, query, { scopeKey, enabled })
```

The realtime query helpers cache read-only cost estimates and saved-style
pages. Run `editChain`, `finalizeChain`, and style mutations through the
realtime client and the authenticated server boundary; after a style mutation,
invalidate the matching `fnfKeys.realtime({ scopeKey })` subtree. Poll edit
results with `getEditJob` / `pollEditJob` and render their normal `Generation`
shape. Workspace switching clears the previous scope's realtime cache. Full
contract: `references/fnf-sdk.md` → "Stateful realtime image editing and saved
custom styles".

For Elements and character workflows, use `referencesQueryOptions` for the
Elements picker and `characterQueryOptions` to poll newly trained characters.
After training
completes, invalidate the matching `fnfKeys.references(...)` query so the new
Character Element appears. The Element id and `reference.characterId` are
different; Soul generation uses `characterId` as
`settings.customReferenceId`. Full server recipe:
`references/fnf-sdk.md` → "Elements and custom-reference character training".

Use `flattenFeedPages` with infinite feeds. Use `applyGenerations`,
`prependGenerations`, and `removeGenerationQueries` for generation cache writes.
Do not call `queryClient.setQueryData` on generation caches directly unless the
package guide documents the exact helper path.

For any model form generated from a prompt, the default React structure is:

- auth gate from `/api/user`
- profile/credits/workspace tab or side panel
- settings form and upload controls
- cost preview query
- confirmation modal before submit: `run.start` fires only after the user
  confirms (model + settings summary + cost preview); the server wires the
  adapter `confirm` gate — see the fnf-sdk reference, "Submission Confirmation
  Gate"
- `useGenerationRun` for submit + poll
- `jobsFeedQueryOptions` / `jobSetQueryOptions` for feed/history
- `prependGenerations` after submit when the returned generations should appear
  immediately in the visible feed
- `HiggsfieldGenerationCard` for every submitted and historical generation item
  so completed jobs render real previews, not status-only placeholders

If the website uses SDK generation and lacks a feed/history view, treat it as
incomplete.

## Generation Feed And Preview Rendering

For SDK-backed generators, React UI must handle both the submit lifecycle and
the historical feed:

```tsx
import { HiggsfieldGenerationCard } from "@/components/higgsfield-generation-card"
import { jobsFeedQueryOptions, flattenFeedPages, useGenerationRun } from "@higgsfield/fnf-react"
```

Required behavior:

- Use `useGenerationRun` for submit + polling until terminal status.
- After EVERY accepted submit, insert the returned queued/running generations
  into the visible feed with `prependGenerations` before polling completes.
  `preset` activates History/Results in the same transition; inline-feed
  layouts scroll or focus the inserted card. Never leave an accepted submit
  visible only on the form or preset screen.
- Use `applyGenerations` or the built-in run/cache helpers to fold polling
  updates into generation caches.
- Load history with `jobsFeedQueryOptions` and `flattenFeedPages`; refresh by
  invalidating the exported `fnfKeys` query, not by hand-building keys.
- Render all run results and feed items with `HiggsfieldGenerationCard` or an
  equivalent component using `getPreviewUrl`, `getRawUrl`, `getMediaType`,
  `getJobPhase`, `hasResult`, and `isTerminalJobStatus` from
  `@higgsfield/fnf/client`.
- Image cards use the optimized preview URL and raw URL for open/download.
- Video cards use raw URL for playback and thumbnail/preview URL as poster.
- Completed jobs with no result URL show an explicit preview-unavailable state
  plus refresh/get behavior.
- Show prompt, model, status, created time, and failure reason where available.
- Opening a ready History generation keeps the feed mounted and presents its
  image/video and metadata in the shipped detail surface. Previous/Next moves
  through the current filtered/sorted feed without closing. Close restores the
  History tab, search/filter state, and scroll position; changing detail
  selection must not refetch or reset the feed.

Never render a completed generation as a blank rectangle that only says
`completed` or only shows an id. That means the website ignored SDK
`Generation.results` or the backend response was not normalized correctly.

## Request Helpers

- Use `useFnfWirePreview(input)` or `getWirePreview(input, jobs)` to show local
  validation/wire params before submit.
- Use `costQueryOptions(jobClient, input, { scopeKey, enabled })` for cached
  cost previews. Returned `credits` are display credits.
- Use `useGenerationRun` for submit-through-poll lifecycle; `run.start()` does
  not throw for normal lifecycle failures, so render from `run.error` and
  generation statuses. Call `run.start` only after the confirmation modal is
  accepted; render `run.error?.code === 'confirmation_rejected'` as a quiet
  user-cancelled state, not an error toast.
- Use `useAttachments` for uploads and submit-ready `MediaRef` values.
- The job client passed to React helpers must ultimately call a server-side SDK
  path. If it wraps TanStack server functions or `/api/*` routes, submit, cost,
  media upload, and workspace switch must be backed by `POST` handlers. GET is
  for reads only. A generation `Method Not Allowed` error usually means the
  generated website built a GET route/function for a write operation.
- Do not pass browser `File`, `Blob`, `ArrayBuffer`, `Uint8Array`, base64, or
  byte arrays through React Query variables or `createServerFn` JSON input. For
  server-only auth/fnf.internal flows, upload files with multipart `FormData` to
  a `POST /api/media/upload` route, then give React generation state only the
  returned `MediaRef`.

`useGenerationRun` is the right default for generator screens:

- `start(input)` submits and polls until terminal state.
- It supersedes/aborts stale runs when a newer run starts.
- It folds progress into TanStack caches.
- It exposes lifecycle state; UI decides copy, toasts, redirects, and billing.
- Do not treat the submit response as the final result. Read statuses and media
  URLs from the polled generations and feed queries.

`useAttachments` is the right default for upload controls:

- Render uploading, ready, blocked, failed, retry, remove, and clear states.
- Use the returned refs in job submit input.
- Keep file names and upload URLs out of logs and observability.
- Use it only with a media client whose upload path is valid for the current
  runtime. If the actual SDK adapter/token must stay server-side, do not push
  raw files through a JSON server function; build a multipart upload route and
  adapt your UI state around its returned `MediaRef`.

## Profile And Workspace

Use profile query options for profile/credits/workspace panels. Use
`useSwitchWorkspaceMutation` or `switchWorkspaceMutationOptions` for backend
context switching. On success, update host auth/session/router state if needed;
the package only updates SDK/profile caches and clears scoped generation data.

## Client Boundary

Use `fnf-react` in client React code only after the server has provided a safe
adapter/proxy boundary. Browser components must not receive fnf service secrets
or raw backend credentials.

When in doubt, keep privileged fnf work in a TanStack server function and let
client components call that app-local server function.

For generated websites, browser auth display should use `/api/user` from
`references/auth.md`. Do not use `fnf-react` profile queries as a replacement for
the app-local auth proxy unless the adapter is explicitly safe for browser use.

Auth enforcement rule:

- Browser checks `/api/user` for signed-in state.
- UI disables or hides `run.start`, upload controls, cost buttons, feed/history,
  profile, credits, and workspace switching when signed out.
- Server functions still call the auth guard before submit/upload/cost/profile
  SDK operations.
- On logout, clear/invalidate scoped fnf query caches before or during
  navigation to `/__auth/logout?return=...`.
