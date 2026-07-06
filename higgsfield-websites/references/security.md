# Security

## Threat model

### When to Load

Only when the site has auth, user data, or storage bindings. Load when ANY of these conditions is true:

- `references/auth.md` is loaded for this build
- `app.manifest.json` contains `"db": true`, `"r2": true`, or `"kv": true`
- The website has `createServerFn` calls that write or mutate data
- The website has `/api/user`, `__auth`, or session-related routes

**Skip** for static landing pages, portfolios, brochure sites, and websites with no user-submitted data.

#### Detection

```ts
// Check app.manifest.json
const manifest = JSON.parse(fs.readFileSync('app.manifest.json', 'utf-8'));
const hasStorage = manifest.db || manifest.r2 || manifest.kv;

// Check for auth routes
// Grep for: /api/user, __auth, createServerFn with .bind() or INSERT/UPDATE/DELETE
```

---

### Trust Boundaries

Map these boundaries for every website with data. Each boundary is a point where input trust level changes.

#### Browser → Worker (untrusted → trusted)

All data crossing this boundary is attacker-controlled:
- URL path and query parameters
- Request headers (including cookies, but cookies are tamper-resistant if `HttpOnly`)
- Form submissions and JSON request bodies
- File uploads

Every `createServerFn`, page loader, and API route handler sits on this boundary. Inputs must be validated.

#### Worker → D1/R2/KV (trusted → trusted)

Both run in the same Cloudflare environment. The channel is trusted, but SQL injection is still possible if queries use string concatenation instead of parameterized `.bind()`. R2 key construction from user input can cause path traversal.

#### Worker → External API (trusted → semi-trusted)

Outbound `fetch()` from server functions. Risks:
- SSRF if the URL comes from user input
- Response injection if the external API is compromised
- Secret leakage if auth headers are sent to the wrong host

Validate outbound URLs. Validate response shapes before trusting them.

#### Worker → fnf.internal (trusted → trusted)

The platform's internal API. Auth is injected by the platform -- website code does not handle fnf tokens. Still validate response shapes; a malformed response should not crash the website or expose internal state.

#### Auth Routes → Public Routes (access control boundary)

Routes that require authentication vs. routes that are public. Map which is which. Every protected route must verify session before rendering or returning data. A missing check on one route is the most common access control bug.

---

### Entry Point Inventory

Enumerate every entry point before analyzing threats. Build this list by scanning the codebase.

#### Page Routes (`app/src/routes/**`)

For each route file, record:
- Path pattern (e.g., `/dashboard`, `/settings/$userId`)
- Auth required: yes/no
- Data loaded: what server functions or loaders run
- Writable: does the page submit forms or call mutation server functions

#### Server Functions (`createServerFn`)

For each server function, record:
- Name and location
- HTTP method (GET/POST)
- Input shape (what data it accepts from the client)
- Data accessed (which D1 tables, R2 buckets, KV namespaces)
- Auth check: present/absent

#### API Routes (`app/src/routes/api/**`)

For each API route, record:
- Path and HTTP methods handled
- Auth check: present/absent
- Input sources (body, query params, path params)
- Response data (what it returns, any sensitive fields)

#### File Upload Surfaces

- R2 write operations (where file data comes from, size limits, type validation)
- Form file inputs (which pages accept file uploads)
- Filename/key construction (is user input used in R2 keys?)

#### Webhook/Callback Endpoints

- External services that call back into the website (payment processors, OAuth providers, etc.)
- Signature verification on incoming webhooks
- Idempotency handling (replayed webhooks should not duplicate side effects)

---

### Asset Classification

| Asset | Location | Sensitivity | Protection |
|-------|----------|-------------|------------|
| User credentials (passwords) | D1 | Critical | Hashed (bcrypt/argon2), never logged, never returned to client |
| Session tokens | Cookie | Critical | `HttpOnly; Secure; SameSite=Strict`, rotated on login |
| PII (email, name, etc.) | D1 | High | Access-controlled by user ID, not in client bundle |
| Uploaded files | R2 | Medium-High | Access-controlled, validated MIME/size, sanitized filenames |
| Application data (posts, etc.) | D1 | Medium | Access-controlled per ownership or visibility settings |
| R2 objects (public assets) | R2 | Low | Public by design, no sensitive content |
| KV cache entries | KV | Low-Medium | May contain derived data; TTL-bounded; no secrets as values |
| API keys (external services) | Cloudflare Secrets | Critical | Never in code, injected via `env`, never logged |

---

### Attacker Model

#### Anonymous Internet User

**Capabilities:**
- Reach all public routes and API endpoints
- Submit arbitrary form data, JSON bodies, file uploads
- Craft malicious URLs (XSS payloads in query params, path traversal)
- Replay and tamper with requests (no CSRF token = no protection on state changes)
- Enumerate routes and server functions by observing client JavaScript

**Goals:** Access other users' data, inject content, abuse server resources, exfiltrate secrets.

#### Authenticated User

**Capabilities:**
- Everything anonymous users can do, plus valid session
- Access own data and attempt to access other users' data (IDOR)
- Attempt privilege escalation (modify role claims, access admin routes)
- Abuse rate-unlimited endpoints (spam, resource exhaustion)

**Goals:** Read/modify other users' data, escalate to admin, abuse platform resources.

#### What Attackers CANNOT Do

These are platform guarantees -- do not model threats against them:

- **Access Worker internals at runtime.** V8 isolates provide memory isolation between requests and between Workers. An attacker cannot read another request's memory.
- **Intercept Worker-to-binding traffic.** D1, R2, KV communication happens in-process or over Cloudflare's internal network. There is no network path for an attacker to intercept.
- **Read Cloudflare Secrets.** Secrets are injected at deploy time into the Worker's `env` object. They are not in the code, not in the git repo, and not accessible via any API the attacker can reach.
- **Bypass Cloudflare edge security.** HTTPS termination, DDoS mitigation, and bot management happen before traffic reaches the Worker.

---

### Common Threat Patterns for the Stack

#### 1. IDOR via Predictable Resource IDs

**Attack:** User changes `/api/notes/123` to `/api/notes/124` to read another user's note. Sequential integer IDs are trivially enumerable.

**Mitigation:** Always filter by authenticated user ID in D1 queries.

```ts
// VULNERABLE
db.prepare('SELECT * FROM notes WHERE id = ?').bind(noteId).first();

// SAFE
db.prepare('SELECT * FROM notes WHERE id = ? AND user_id = ?').bind(noteId, session.userId).first();
```

Using UUIDs as IDs adds defense-in-depth but does NOT replace access control checks.

#### 2. Server Function Input Manipulation

**Attack:** Client sends unexpected shape to `createServerFn` -- extra fields, wrong types, oversized strings, negative numbers, SQL fragments.

**Mitigation:** Validate every input field before processing.

```ts
import { z } from 'zod';

const CreateNoteSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().max(10000),
});

const createNote = createServerFn({ method: 'POST' })
  .validator((data: unknown) => CreateNoteSchema.parse(data))
  .handler(async ({ data, request }) => {
    const session = await getSession(request);
    if (!session) throw new Error('Unauthorized');
    await db.prepare('INSERT INTO notes (id, user_id, title, body) VALUES (?, ?, ?, ?)')
      .bind(crypto.randomUUID(), session.userId, data.title, data.body).run();
  });
```

#### 3. Test Data Contamination (Live D1)

**Attack:** There is one deploy and one D1 database — the live one. Test data created while building or debugging lands in production data, and destructive "test" queries modify real user data.

**Mitigation:**
- Never use real user data for testing
- If you must seed test rows, tag them explicitly (e.g. an `is_test` column or a reserved prefix) and clean them up
- Get explicit user approval before destructive migrations, `UPDATE`s, or backfills

#### 4. Privilege Escalation via Client State

**Attack:** Client stores `role: 'admin'` in localStorage or sends `{ role: 'admin' }` in a server function call. Server trusts the client-provided role.

**Mitigation:** Never trust client-sent roles, permissions, or user IDs for authorization decisions.

```ts
// VULNERABLE -- role from client
const { role } = data;
if (role === 'admin') return getAdminData();

// SAFE -- role from server session
const session = await getSession(request);
const user = await db.prepare('SELECT role FROM users WHERE id = ?').bind(session.userId).first();
if (user?.role === 'admin') return getAdminData();
```

#### 5. SSRF via Server Function

**Attack:** Server function accepts a URL from the client and fetches it. Attacker provides `http://169.254.169.254/latest/meta-data/` (cloud metadata), `http://localhost:8787/internal-api`, or internal network addresses.

**Mitigation:**

```ts
const ALLOWED_HOSTS = new Set(['api.example.com', 'cdn.example.com']);

function validateUrl(input: string): URL {
  const url = new URL(input);
  if (!['https:'].includes(url.protocol)) throw new Error('HTTPS only');
  if (!ALLOWED_HOSTS.has(url.hostname)) throw new Error('Host not allowed');
  // Block private IPs
  if (/^(127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.)/.test(url.hostname)) {
    throw new Error('Private IP blocked');
  }
  return url;
}
```

#### 6. Webhook Replay / Forgery

**Attack:** Attacker sends forged webhook payloads to callback endpoints, or replays legitimate webhooks to duplicate side effects (double payment credits, duplicate notifications).

**Mitigation:**
- Verify webhook signatures using `crypto.subtle.timingSafeEqual()` (see worker-hardening rule 4)
- Track processed webhook IDs in D1/KV to enforce idempotency
- Reject webhooks with timestamps older than 5 minutes

---

### Output

Present threat model findings inline in chat as a summary table. Do not write to a file.

```
## Threat Model Summary

| # | Threat | Severity | Likelihood | Impact | Mitigation Status |
|---|--------|----------|------------|--------|-------------------|
| 1 | IDOR on /api/notes/:id | High | High | User data leak | MITIGATED -- queries filter by user_id |
| 2 | Server function input manipulation | Medium | High | Data corruption | OPEN -- no validation on createNote |
| 3 | SSRF via /api/proxy | High | Medium | Internal network access | MITIGATED -- allowlist in place |
| 4 | Privilege escalation | Critical | Low | Full admin access | MITIGATED -- role derived from DB |
| 5 | Webhook replay | Medium | Medium | Duplicate transactions | OPEN -- no idempotency check |

**Open items: 2 | Mitigated: 3 | Total attack surface: 5 entry points, 3 server functions, 1 webhook**
```

Severity scale: Critical > High > Medium > Low. Base severity on worst-case impact. Likelihood accounts for how easy the attack is to execute (High = no special tools needed, just a browser).

---

### Pitfalls

1. **Don't threat-model brochure sites.** A static landing page with no auth, no database, and no user input has no meaningful attack surface beyond XSS (covered by web-audit). Skip threat modeling for these.

2. **Don't assume D1 is multi-tenant by default.** Each website gets its own D1 database backing its single live deploy. Cross-tenant risk exists only between the website's own users sharing that one database, not between different websites.

3. **Don't model attacks against Cloudflare infrastructure.** V8 isolate escapes, edge network compromises, and Cloudflare-internal attacks are outside the website's threat model. The platform is the trust boundary.

4. **Don't confuse authentication with authorization.** A user being logged in (authenticated) does not mean they can access any resource (authorized). IDOR is an authorization bug, not an authentication bug. Check both.

5. **Don't skip the entry point inventory.** Jumping straight to threat patterns without enumerating entry points misses the routes and server functions unique to the website. The inventory is the foundation; patterns are applied against it.

## Worker hardening

### When to Load

Every website build. These are hard constraints of the Cloudflare Workers runtime, not optional best practices. Violating them causes data leaks, request cross-contamination, or runtime crashes. Load unconditionally alongside the build skill.

---

### Hard Rules

#### 1. No Global Mutable State

Module-level variables persist across requests in the same V8 isolate. A `let` at module scope is shared by every concurrent request hitting that isolate.

```ts
// BAD -- leaks between requests
let currentUser: User | null = null;

export default {
  async fetch(request: Request) {
    currentUser = await getUser(request); // overwrites for ALL concurrent requests
    return handleRequest();
  }
};
```

```ts
// GOOD -- request-scoped data flows through params
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const user = await getUser(request);
    return handleRequest(user, env);
  }
};
```

Module-level `const` for static config (strings, frozen objects) is fine. Any `let` or mutable object at module scope is a bug. React context resets per SSR render and is safe for per-request data.

#### 2. Cryptographic Randomness Only

`Math.random()` is not a CSPRNG. In Workers, its output may be predictable across requests in the same isolate.

```ts
// BAD
const sessionId = `sess_${Math.random().toString(36)}`;

// GOOD
const sessionId = crypto.randomUUID();

// GOOD -- for raw bytes (tokens, nonces)
const token = new Uint8Array(32);
crypto.getRandomValues(token);
```

`Math.random()` is acceptable only in client-side UI code (animations, layout jitter). Flag any server-side usage.

#### 3. No Hardcoded Secrets

Never put API keys, tokens, passwords, or connection strings in source code or `wrangler.jsonc`.

```ts
// BAD
const API_KEY = "sk-proj-abc123...";

// GOOD -- store it with `higgsfield website secrets set <website_id> --name … --value …`
// Access SERVER-SIDE via bindings().API_KEY (add it to AppEnv in bindings.server.ts)
```

In the Supercomputer builder, the platform injects secrets via the outbound Worker. Website code accesses them through `env` bindings at runtime. Secrets never appear in the git repo.

#### 4. Timing-Safe Secret Comparison

String `===` leaks secret length via timing side-channels. Use `crypto.subtle.timingSafeEqual()` for any secret, token, or API key comparison.

```ts
async function safeCompare(a: string, b: string): Promise<boolean> {
  const encoder = new TextEncoder();
  const aBuf = encoder.encode(a);
  const bBuf = encoder.encode(b);
  if (aBuf.byteLength !== bBuf.byteLength) return false;
  return crypto.subtle.timingSafeEqual(aBuf, bBuf);
}

// Usage in a webhook handler
const signature = request.headers.get('X-Webhook-Signature') ?? '';
if (!(await safeCompare(signature, env.WEBHOOK_SECRET))) {
  return new Response('Forbidden', { status: 403 });
}
```

#### 5. Stream Large Payloads

Workers have a 128 MB memory limit. `await response.text()` or `await response.json()` buffers the entire body into memory. On unbounded external responses this causes OOM crashes.

```ts
// BAD -- buffers entire response
const data = await fetch(externalUrl).then(r => r.text());

// GOOD -- stream through
const upstream = await fetch(externalUrl);
return new Response(upstream.body, {
  headers: { 'Content-Type': upstream.headers.get('Content-Type') ?? 'application/octet-stream' },
});
```

For JSON processing of large payloads, use streaming JSON parsers or paginate the upstream API. Only call `.json()` when you control the response size (e.g., your own D1 queries).

#### 6. Handle Every Promise

Every `Promise` must be `await`ed, `return`ed, or passed to `ctx.waitUntil()`. Floating promises silently swallow errors, may execute after the response is sent, and can leak data into subsequent requests.

```ts
// BAD -- fire-and-forget
logAnalytics(event); // returns Promise, nobody awaits it

// GOOD -- defer non-critical work
ctx.waitUntil(logAnalytics(event));

// GOOD -- critical work
await saveToDatabase(record);
```

#### 7. No `passThroughOnException()`

This Cloudflare API forwards the original request to origin when the Worker throws, bypassing all security logic (auth checks, rate limiting, header injection).

```ts
// BAD -- security bypass on any error
export default {
  async fetch(request, env, ctx) {
    ctx.passThroughOnException();
    return handleRequest(request, env);
  }
};

// GOOD -- explicit error handling
export default {
  async fetch(request, env, ctx) {
    try {
      return await handleRequest(request, env);
    } catch (err) {
      console.error('Worker error:', err);
      return new Response('Internal Server Error', { status: 500 });
    }
  }
};
```

#### 8. Security Headers on Every Response

Security headers are owned by a single canonical helper:
`app/src/lib/security-headers.server.ts`. Import `applySecurityHeaders()` in
`app/src/server.ts` and wrap every response leaving the Worker — including
redirects and error responses. Do not hand-roll a second header function.

The canonical helper is the drop-in `app/src/lib/security-headers.server.ts`:

```ts
export function applySecurityHeaders(response: Response): Response {
  const headers = new Headers(response.headers);
  // Framing: the Supercomputer Design-mode inspector renders the live app
  // inside an iframe from a higgsfield.app origin (cross-origin to the app's own
  // subdomain). `X-Frame-Options` has no cross-origin allowlist, so SAMEORIGIN/
  // DENY would blank Design mode. We deliberately DO NOT set X-Frame-Options and
  // control framing via the CSP `frame-ancestors` allowlist below. Reviewer:
  // confirm/tighten the editor origin for your deployment.
  headers.set(
    'Content-Security-Policy',
    "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline'; " +
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
      "font-src 'self' https://fonts.gstatic.com; " +
      "img-src 'self' data: https:; media-src 'self' https:; " +
      "connect-src 'self' https:; " +
      "frame-ancestors 'self' https://*.higgsfield.app https://higgsfield.app " +
      "https://*.higgsfield.ai https://fnf-dev.anwar-695.workers.dev " +
      "https://feat-apps-marketplace-tools-fnf-dev.anwar-695.workers.dev; " +
      "base-uri 'self'; form-action 'self'",
  );
  headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  headers.set('X-XSS-Protection', '0');
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
```

Adjust CSP directives per website needs (e.g., add specific CDN origins), but keep
`X-Content-Type-Options` and keep `frame-ancestors` as the editor allowlist.
**Never set `X-Frame-Options`** — it has no cross-origin allowlist, so
`DENY`/`SAMEORIGIN` would blank the Supercomputer Design-mode iframe,
which loads the live website from a cross-origin `higgsfield.app` host. Framing is
controlled exclusively by the CSP `frame-ancestors` allowlist: it permits the
Supercomputer hosts while still blocking arbitrary third parties. Keep that
allowlist — never narrow it to `'none'` and never remove it.

#### 9. Validate Server Function Inputs

`createServerFn` code runs server-only, but its inputs arrive from the client over the network. The client can send any shape of data.

```ts
// BAD -- trusts client input shape
const getUser = createServerFn({ method: 'GET' })
  .handler(async ({ data }: { data: { userId: string } }) => {
    return db.prepare('SELECT * FROM users WHERE id = ?').bind(data.userId).first();
  });

// GOOD -- validate before use
const getUser = createServerFn({ method: 'GET' })
  .validator((data: unknown) => {
    if (!data || typeof data !== 'object' || !('userId' in data)) throw new Error('Invalid input');
    const { userId } = data as { userId: string };
    if (typeof userId !== 'string' || userId.length > 36) throw new Error('Invalid userId');
    return { userId };
  })
  .handler(async ({ data }) => {
    return db.prepare('SELECT * FROM users WHERE id = ?').bind(data.userId).first();
  });
```

Use TanStack Start's `.validator()` chain or manual checks. For complex shapes, use zod.

#### 10. No Secrets in React Props

React component props serialize into the client HTML during SSR. Any value passed as a prop is visible in the page source.

```ts
// BAD -- API key appears in client HTML
function Dashboard({ apiKey }: { apiKey: string }) {
  return <Widget config={{ key: apiKey }} />;
}

// GOOD -- fetch server data in a server function, return only safe data
const getDashboardData = createServerFn({ method: 'GET' })
  .handler(async () => {
    const result = await fetch(API_URL, { headers: { Authorization: `Bearer ${env.API_KEY}` } });
    return result.json(); // only the response data reaches the client
  });
```

This includes `env` bindings, database results containing sensitive columns, and internal URLs.

#### 11. Cookie Security

Custom cookies set in server routes or API handlers must use secure attributes.

```ts
// GOOD
const cookie = `session=${token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=86400`;
return new Response(null, {
  status: 302,
  headers: {
    'Set-Cookie': cookie,
    'Location': '/dashboard',
  },
});
```

- `HttpOnly` -- prevents JavaScript access (XSS can't steal it)
- `Secure` -- HTTPS only (always true on Cloudflare)
- `SameSite=Strict` -- blocks cross-site sends (use `Lax` for OAuth redirect flows)

The platform handles auth cookies automatically. This rule applies to any additional cookies the website sets.

#### 12. CORS Only When Needed

Workers don't add CORS headers by default -- this is the secure default. Only add `Access-Control-Allow-Origin` when the site genuinely serves API responses to a different origin.

```ts
// BAD -- allows any origin with credentials
headers.set('Access-Control-Allow-Origin', '*');
headers.set('Access-Control-Allow-Credentials', 'true'); // browser ignores * with credentials, but intent is wrong

// GOOD -- specific origin, only on API routes that need it
if (request.headers.get('Origin') === 'https://trusted-app.example.com') {
  headers.set('Access-Control-Allow-Origin', 'https://trusted-app.example.com');
  headers.set('Access-Control-Allow-Credentials', 'true');
}
```

Never add CORS headers to page routes. Only add them to `/api/*` routes consumed by external clients.

---

### Anti-Patterns to Flag

| Pattern | Risk | Fix |
|---------|------|-----|
| `Math.random()` for IDs/tokens | Predictable values, session hijacking | `crypto.randomUUID()` or `crypto.getRandomValues()` |
| `let x = ...` at module scope | Cross-request data leakage | Move to function params or request-scoped context |
| `await response.text()` on external fetch | OOM crash on large response | Stream with `Response(upstream.body)` |
| Hardcoded string resembling a key (`sk-`, `ghp_`, `Bearer`) | Secret in source code / git history | `higgsfield website secrets set` + `bindings().SECRET_NAME` server-side |
| `===` comparing secrets/tokens | Timing side-channel leaks secret | `crypto.subtle.timingSafeEqual()` |
| `ctx.passThroughOnException()` | Bypasses all Worker security on error | `try/catch` with explicit error response |
| Missing `await` on async call | Silent error loss, data leak | `await`, `return`, or `ctx.waitUntil()` |
| Secret value in JSX prop `<Comp token={env.KEY}>` | Secret in client HTML source | Fetch in server function, return only safe data |
| `Access-Control-Allow-Origin: *` | Any origin reads responses | Allowlist specific origins or omit CORS |
| `eval()` / `new Function()` | Arbitrary code execution | Remove; use static logic or JSON parsing |

---

### Pitfalls

1. **`const` objects are still mutable.** `const cache = {}` at module scope is mutable state -- properties can be added/modified across requests. Use `Object.freeze()` for true immutability, or scope caches to the request.

2. **`crypto.subtle.timingSafeEqual` requires equal-length buffers.** If the two buffers differ in length, it throws. Always check `.byteLength` equality first and return `false` on mismatch (do not pad to equal length -- that leaks info about which is shorter).

3. **`ctx.waitUntil()` does not extend memory limits.** Deferred work still shares the 128 MB isolate memory. Don't use it to process large payloads after responding.

4. **CSP `'unsafe-inline'` for scripts weakens XSS protection.** It's included above for compatibility with SSR hydration scripts. Prefer hash-based or nonce-based CSP when the framework supports it. Track TanStack Start CSP nonce support.

5. **Security headers on redirects matter.** A `302 Found` response still needs `X-Content-Type-Options` and `Strict-Transport-Security`. Apply `applySecurityHeaders()` to all responses, not just 200s.

## Web audit

### When to Load

After building any website, before running `higgsfield website deploy`. Run alongside the SEO audit (`references/seo.md#audit`) as the security half of the pre-deploy quality gate. This audit applies to every site -- brochure, website, dashboard -- because even static sites can have XSS or misconfiguration.

---

### Precedent Rules

Internalize these before auditing. They prevent false positives that waste time and erode trust in the audit.

1. **React JSX auto-escapes by default.** `<p>{userInput}</p>` is safe. Do NOT flag normal JSX text interpolation `{variable}` as XSS. React escapes all string values rendered in JSX.

2. **`dangerouslySetInnerHTML` IS a real risk.** Flag it unless the content is a hardcoded string literal or sanitized through DOMPurify / a known sanitizer. "It comes from our CMS" is not a defense without sanitization.

3. **Environment variables are trusted input.** Do not flag `process.env.X` or `env.VARIABLE` as tainted user input. These are set at build/deploy time by the platform.

4. **UUIDs are unguessable.** Do not flag UUID-based resource access (`/api/items/550e8400-e29b-...`) as IDOR. UUIDs have 122 bits of entropy -- brute force is infeasible.

5. **Test files are excluded.** Skip `*.test.ts`, `*.test.tsx`, `__tests__/`, `*.spec.ts`, `*.spec.tsx`. Test code does not ship to production.

6. **Example/template files are excluded.** Skip `.example`, `.sample`, `.template` files. They are not deployed.

7. **Dev-only config is excluded.** Skip `Dockerfile`, `docker-compose.yml`, `.devcontainer/`, and local development config that does not deploy to Workers.

8. **Missing HTTPS is not a finding.** Cloudflare enforces HTTPS at the edge for all `*.higgsfield.app` domains. Do not flag HTTP links to the website's own domain.

---

### OWASP Top 10 Checklist

#### A01: Broken Access Control

Check every `createServerFn` that reads or writes user data. It must verify authentication before accessing data.

```ts
// FAIL -- no auth check
const getUserNotes = createServerFn({ method: 'GET' })
  .handler(async ({ data }) => {
    return db.prepare('SELECT * FROM notes WHERE user_id = ?').bind(data.userId).all();
  });

// PASS -- auth check before data access
const getUserNotes = createServerFn({ method: 'GET' })
  .handler(async ({ data, request }) => {
    const session = await getSession(request);
    if (!session?.userId) throw new Error('Unauthorized');
    return db.prepare('SELECT * FROM notes WHERE user_id = ?').bind(session.userId).all();
  });
```

Also check: API routes under `app/src/routes/api/` must verify auth. Page loaders returning private data must check session. Never rely on client-side route guards alone.

#### A02: Cryptographic Failures

- No hardcoded secrets in source (grep for `sk-`, `ghp_`, `Bearer `, long base64 strings)
- No `Math.random()` for security-relevant values (IDs, tokens, nonces)
- No sensitive data (passwords, tokens, PII) in the client bundle -- check props passed from loaders to components
- Cross-reference with the "Worker hardening" section above, rules 2, 3, 4

#### A03: Injection

**SQL Injection (D1):** Every D1 query must use parameterized binding.

```ts
// FAIL -- string concatenation
db.prepare(`SELECT * FROM users WHERE name = '${name}'`).all();

// PASS -- parameterized
db.prepare('SELECT * FROM users WHERE name = ?').bind(name).all();
```

**XSS:** Flag `dangerouslySetInnerHTML` with non-static content. Flag `href={userInput}` without protocol validation (see React-Specific Checks below).

**Command Injection:** Flag any use of `eval()`, `new Function()`, or template literal construction of executable code in server functions.

#### A04: Insecure Design

Check for fail-open defaults on security-critical paths:

- `|| 'default'` fallback on secrets or auth tokens -- should crash, not fall back
- Missing rate limiting on public-facing API routes (POST endpoints, form submissions)
- Admin functionality accessible without role checks
- Password/auth flows without brute-force protection

If the website has no auth or sensitive operations, mark as N/A.

#### A05: Security Misconfiguration

- Missing security headers -- check for `applySecurityHeaders()` or equivalent in `server.ts` (cross-ref worker-hardening rule 8)
- Overly permissive CORS (`Access-Control-Allow-Origin: *`)
- Debug info in production responses (`stack`, `trace`, internal paths in error bodies)
- Source maps served in production (`*.map` files accessible)
- Default credentials or placeholder secrets in committed config

#### A06: Vulnerable Components

```bash
# Run in the app directory
bun audit 2>/dev/null || npm audit 2>/dev/null || echo "No audit tool available"
```

Check `package.json` for:
- Dependencies with known CVEs
- Unmaintained packages (no updates in 2+ years for security-relevant deps)
- Unnecessary dependencies that expand attack surface

If no audit tool is available, manually check critical deps (auth libraries, crypto, parsers) against known vulnerability databases.

#### A07: Authentication Failures

Skip if site has no auth. If auth is present, check:

- Session fixation: session ID must rotate after login
- CSRF: state-changing server functions (POST/PUT/DELETE) must verify origin or use CSRF tokens. TanStack Start server functions include origin checking by default -- verify it's not disabled.
- Session expiry: sessions must have a `Max-Age` or `Expires`. Infinite sessions are a finding.
- Password storage: if the website stores passwords, they must be hashed (bcrypt, scrypt, argon2). Never stored in plain text in D1.

#### A08: Data Integrity Failures

Skip if site has no file uploads or external data processing. If present, check:

- File upload MIME type validation (don't trust `Content-Type` header alone; check magic bytes for critical uploads)
- File size limits enforced server-side (Workers have 100 MB request body limit but the website should enforce lower)
- Filename sanitization for R2 keys (strip path traversal: `../`, null bytes, control characters)
- External data (webhooks, API responses) validated before storage

#### A09: Logging Failures

Flag `console.log` / `console.error` that prints:
- Passwords or password hashes
- API keys, tokens, secrets
- Full request bodies on auth endpoints
- Full database rows containing PII

Check that error responses to clients do not contain:
- Stack traces (`at Object.<anonymous>`, file paths)
- Internal hostnames or IP addresses
- Database error messages with schema details

#### A10: SSRF

Skip if no server functions make outbound HTTP requests. If present, check:

```ts
// FAIL -- fetches arbitrary user-supplied URL
const proxyFetch = createServerFn({ method: 'POST' })
  .handler(async ({ data }) => {
    const res = await fetch(data.url); // user controls destination
    return res.json();
  });

// PASS -- allowlisted domains
const ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com'];
const proxyFetch = createServerFn({ method: 'POST' })
  .handler(async ({ data }) => {
    const url = new URL(data.url);
    if (!ALLOWED_HOSTS.includes(url.hostname)) throw new Error('Blocked');
    const res = await fetch(url.toString());
    return res.json();
  });
```

Also check for: internal network access (`localhost`, `127.0.0.1`, `10.*`, `192.168.*`, `169.254.169.254` -- the metadata endpoint).

---

### Insecure Defaults Check

Scan the codebase for these fail-open patterns:

#### Fail-Open Patterns

```ts
// BAD -- falls back to a default secret instead of crashing
const secret = env.SECRET_KEY || 'default-secret-key';
const jwtSecret = process.env.JWT_SECRET ?? 'changeme';

// BAD -- verification defaults to disabled
const verifySignature = options.verify ?? true; // should be ?? false or mandatory

// BAD -- empty catch swallows auth/crypto errors
try { await verifyToken(token); } catch {} // attacker wins on any error
```

#### Dangerous Zero/Null/Empty Defaults

- `timeout: 0` -- may mean "no timeout" (infinite wait, DoS vector)
- `maxRetries: Infinity` -- retry storm
- Empty string accepted as password or API key
- Missing validation on optional fields that have security implications (e.g., `role` field defaults to `'admin'` if missing)

#### The 5 Rationalizations to Reject

When reviewing code, reject these justifications for insecure defaults:

1. **"It's just for dev"** -- dev config ships to production more often than anyone admits.
2. **"Prod config overrides it"** -- if it doesn't, the fallback is the live value.
3. **"We'll fix it later"** -- later never comes; the default becomes the permanent value.
4. **"It's documented"** -- nobody reads documentation; the default is the behavior.
5. **"Nobody would do that"** -- attackers do exactly that.

---

### React-Specific Checks

#### `dangerouslySetInnerHTML`

```ts
// FAIL -- unsanitized user content
<div dangerouslySetInnerHTML={{ __html: userComment }} />

// PASS -- hardcoded content
<div dangerouslySetInnerHTML={{ __html: '<strong>Welcome</strong>' }} />

// PASS -- sanitized
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userComment) }} />
```

#### `href` with User Input

```ts
// FAIL -- javascript: protocol injection
<a href={userUrl}>Click</a>

// PASS -- protocol validation
function safeHref(url: string): string {
  if (url.startsWith('/') || url.startsWith('#') || url.startsWith('https://')) return url;
  return '#';
}
<a href={safeHref(userUrl)}>Click</a>
```

#### `<iframe>` with User Input

```ts
// FAIL -- no sandbox
<iframe src={userUrl} />

// PASS -- sandboxed
<iframe src={userUrl} sandbox="allow-scripts allow-same-origin" />
```

#### Client-Side State

- Never store tokens, secrets, or API keys in `localStorage`, `sessionStorage`, or React state
- Auth tokens belong in `HttpOnly` cookies, not JavaScript-accessible storage
- If the website uses `zustand`, `jotai`, or React context for auth state, verify the token source is a server function, not client storage

#### `eval()` / `new Function()`

Flag any occurrence in application code. Acceptable only in build tooling (`vite.config.ts`, bundler plugins) which does not execute at runtime.

---

### Output Format

Present audit results as a table. One row per check. Same format as the SEO audit (`references/seo.md#audit`).

```
## Security Audit Results

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1 | A01 Broken Access Control | PASS | All 4 server functions verify session |
| 2 | A02 Cryptographic Failures | PASS | No hardcoded secrets found |
| 3 | A03 Injection | WARN | `dangerouslySetInnerHTML` in BlogPost.tsx -- verify content is sanitized |
| 4 | A04 Insecure Design | N/A | No auth or sensitive operations |
| 5 | A05 Security Misconfiguration | FAIL | Missing security headers in server.ts |
| 6 | A06 Vulnerable Components | PASS | `bun audit` reports 0 vulnerabilities |
| 7 | A07 Authentication Failures | N/A | No auth |
| 8 | A08 Data Integrity Failures | N/A | No file uploads |
| 9 | A09 Logging Failures | PASS | No sensitive data in console output |
| 10 | A10 SSRF | N/A | No outbound fetches from server functions |
| 11 | Insecure Defaults | PASS | No fail-open patterns found |
| 12 | React-Specific | WARN | 1 `dangerouslySetInnerHTML` usage |

**Summary: 5 PASS, 2 WARN, 1 FAIL, 4 N/A**
```

Status values:
- **PASS** -- check passed, no issues
- **FAIL** -- security issue found, must fix before deploy
- **WARN** -- potential issue, needs manual review
- **N/A** -- check does not apply to this site

Any FAIL blocks deploy. WARN items are noted in the deploy message for the user to review.

---

### Pitfalls

1. **Don't flag React JSX interpolation as XSS.** `{variable}` in JSX is auto-escaped. Only `dangerouslySetInnerHTML` and `href`/`src` attributes with user input are real XSS vectors in React.

2. **Don't flag `fetch()` in server functions as SSRF unless the URL comes from user input.** Server functions that fetch hardcoded API endpoints (e.g., `fetch('https://api.stripe.com/...')`) are not SSRF.

3. **Don't audit `node_modules/`.** Dependency code is checked by `bun audit` / `npm audit`, not by manual code review. Focus on application code in `app/src/`.

4. **Don't confuse build-time env vars with runtime secrets.** `VITE_*` env vars are intentionally public (bundled into client code). Only flag non-`VITE_` env vars that appear in client-reachable code.

5. **Don't flag missing rate limiting on static/SSR pages.** Rate limiting is relevant for API routes and form-handling server functions, not for page loads. Cloudflare's DDoS protection handles volumetric attacks at the edge.
