# Skill: Runtime And Infra

Use this for TanStack Start routing, SSR, server functions, server routes,
Cloudflare Worker runtime, D1/R2, Durable Objects, and deployment-facing
changes. If the task touches current user, login, logout, or `/api/user`, also
read `references/auth.md`.

## Stack

- React 19 + TanStack Start.
- File-based routes live under `app/src/routes/`.
- SSR entry goes through `app/src/server.ts`, which exports the Worker handler.
- Build emits `dist/server/server.js` and `dist/client`.
- No Next.js, Remix, Astro, `app/src/pages`, Hono app, Express app, or separate API
  framework. App-local API endpoints are TanStack server routes under
  `app/src/routes/api/**`.

## SSR Safety

- Every route renders on the server per request.
- Never touch `window`, `document`, `localStorage`, `navigator`, or
  `matchMedia` at module top level or during render.
- Browser globals belong in `useEffect`, event handlers, or guarded branches.

## Server-Only Code

- Put server logic in `createServerFn(...).handler(...)` or `*.server.ts`.
- Secrets and Cloudflare bindings are read server-side per request.
- Do not pass secrets, bindings, or account tokens through React props.
- Use `createServerFn({ method: "POST" })` for mutations such as generation
  submit, cost preview, media upload, workspace switch, database writes, and
  other operations that change user-owned state. Use GET only for pure reads.

## Supercomputer Design Mode

- `fnf-web` owns the parent inspector UI. The generated website owns only the child
  bridge that runs inside the iframe.
- Child bridge code lives in `app/src/module/design-inspector`:
  `registry.ts`, `runtime.ts`, and `vite.ts`.
- `bun run build` is inspector-free by default: no inspector runtime, no
  source metadata, and no per-element debug attributes. Setting
  `HF_DESIGN_INSPECTOR=1` in the env turns the same build into the
  inspector-enabled one (for LOCAL work only).
- The deploy platform CI sets `HF_DESIGN_INSPECTOR=1` on every deploy build,
  so the live deployed site always carries the inspector.
- There is ONE deploy per website (`higgsfield website deploy <website_id>`),
  and it ships the live public site immediately. The live site is the surface
  Supercomputer Design mode opens.
- Never hard-code `HF_DESIGN_INSPECTOR=1` into the `build` script and never
  hand-edit the build script to toggle it — the deploy build is controlled by
  CI, not by these scripts.
- The design build attaches source metadata through callback refs and a
  `WeakMap` registry. It must not add per-element DOM attributes.
- The design build instruments intrinsic DOM tags and ref-capable component
  usages, including small icon components and compound component members. This
  is automatic; agents must not add marker props by hand. Components that do not
  forward refs fall back to nearest DOM/heuristic metadata.
- Keep the guarded dynamic import in `app/src/routes/__root.tsx`; do not make the
  inspector a static root import. Inspector-free tree-shaking depends on the
  compile-time `__HF_DESIGN_INSPECTOR__` guard.
- Never manually write `data-hf-*` attributes, source markers, inspector refs,
  or postMessage handlers in website components. The design-inspector module and Vite config own all
  child-side instrumentation.
- The only selector state allowed in DOM is global state such as
  `body[data-selector-active="true"]` while Design mode is active.
- Do not log or post cookies, auth headers, tokens, local/session storage, input
  values, raw HTML, raw uploaded bytes, or raw result URLs from the inspector.

## Server Routes

Use TanStack Start server routes for browser-safe API proxies such as
`/api/user`:

```ts
// app/src/routes/api/user.ts
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/user')({
  server: {
    handlers: {
      GET: async () => {
        return Response.json({ ok: true })
      },
    },
  },
})
```

Server routes are part of the same Worker. Do not add Hono/Express or a second
backend process.

Do not manually edit or hand-write `app/src/routeTree.gen.ts`. After adding nested
routes such as `app/src/routes/api/user.tsx` or
`app/src/routes/api/media/upload.tsx`, let the TanStack Router plugin regenerate the
route tree. A stale route tree that imports nested routes but never adds them as
children can make `/api/user` or `/api/media/upload` look like backend failures
when the route was never registered.

## Binary Upload Routes

Do not send files through JSON server-function input. Browser `File`, `Blob`,
`ArrayBuffer`, `Uint8Array`, base64 strings, and byte arrays must not be
serialized into `createServerFn` data. This can produce `Maximum call stack size
exceeded`, huge payloads, and corrupted upload sources.

For uploads, use an app-local multipart route:

```ts
// app/src/routes/api/media/upload.ts
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/media/upload')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const form = await request.formData()
        const file = form.get('file')
        if (!(file instanceof File)) {
          return Response.json({ ok: false, code: 'missing_file' }, { status: 400 })
        }

        const bytes = new Uint8Array(await file.arrayBuffer())
        return Response.json({
          ok: true,
          contentType: file.type,
          size: bytes.byteLength,
        })
      },
    },
  },
})
```

Client code must use `FormData` and must not set the `content-type` header:

```ts
const form = new FormData()
form.append('file', file)
await fetch('/api/media/upload', { method: 'POST', body: form })
```

For generation flows, upload first and return a small media reference/id. The
later generation JSON request should contain prompt/settings/media refs only,
never raw bytes.

Route handlers must declare the HTTP methods the browser will use. For example,
a generation proxy route must expose `POST`, not only `GET`:

```ts
// app/src/routes/api/generate.ts
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/generate')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = await request.json()
        return Response.json({ ok: true, body })
      },
    },
  },
})
```

If a generated website shows `Method Not Allowed`, first check whether the browser is
POSTing to a route that only registered `GET`, or whether a mutation was built as
a GET server function. This commonly breaks generation submit/cost/media flows.

## Cloudflare Bindings

- Read D1/R2 bindings through `app/src/lib/bindings.server.ts`.
- Use `import { env } from "cloudflare:workers"` only in server-only modules.
- `app/app.manifest.json` declares infra. `app/wrangler.jsonc` is build/dev input; the
  deploy platform overwrites authoritative bindings.

## Live Data Warning

There is one deploy and one set of D1 and R2 resources backing it. Every
migration or data change hits live production data directly. `env.HF_ENV` is
always `"production"` on deployed builds; it does not give you a separate
database or bucket to test against.

- Prefer additive migrations.
- Avoid `DROP`, destructive `UPDATE`, and destructive backfills unless the user
  explicitly approves production data changes.

## Durable Objects

If `app/app.manifest.json` declares `"durableObject": "ClassName"`, also export the
class from `app/src/server.ts`:

```ts
export class ClassName extends DurableObject {
  // ...
}
```

Containers/code sandboxes are not deployable through this template yet.

## SEO Infrastructure

Every site with a public face must include:

1. **robots.txt** — TanStack server route at `/robots.txt` returning
   `User-agent: * / Allow: / / Sitemap: <origin>/sitemap.xml`. Drop-in:
   `app/src/routes/robots.txt.ts`.
2. **sitemap.xml** — TanStack server route at `/sitemap.xml` enumerating all
   public page routes. Drop-in: `app/src/routes/sitemap.xml.ts`.
3. **Canonical URLs** — every page route's `head()` must include
   `links: [{ rel: 'canonical', href: '<absolute URL>' }]`.
4. **Security headers** — apply `applySecurityHeaders()` to every response — see
   `## Worker Security` below.
5. **No trailing slash** — `/pricing/` must 301 to `/pricing`. Handle in
   `server.ts` before the SSR handler.

These are not optional for deployed sites. The SEO audit
(`references/seo.md#audit`) checks them before deploy.

## Worker Security

Every Worker must follow these constraints. Load
`references/security.md#worker-hardening` for the full rules.

1. **No global mutable state.** Module-level variables are shared across requests
   in the same V8 isolate. Never store request-scoped data at module scope.
2. **Cryptographic randomness only.** Use `crypto.randomUUID()` and
   `crypto.getRandomValues()`. Never `Math.random()` for IDs, tokens, or nonces.
3. **No hardcoded secrets.** The platform injects auth via the outbound Worker.
   Website code never handles platform tokens directly. For your OWN secrets (API
   keys, etc.), set them with `higgsfield website secrets set <website_id> --name … --value …`
   and read them server-side as `bindings().SECRET_NAME` — never hardcode them in source.
4. **Security headers on every response.** Apply `applySecurityHeaders()`
   (frame-ancestors allowlist, no X-Frame-Options) — see
   `references/security.md#worker-hardening`.
5. **Validate server function inputs.** `createServerFn` inputs come from the
   client. Always validate shape and types before processing.
