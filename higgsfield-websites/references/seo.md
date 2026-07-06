# SEO

## Meta tags & OG

The `__root.tsx` template ships with placeholder meta (`<App Title>`, generic description). This skill ensures those placeholders NEVER reach production. Every deploy must have real, keyword-targeted meta tags.

### Global Meta in `__root.tsx`

Set these in the root route's `head()` function. They apply site-wide and are overridden per-route where needed.

```tsx
export const Route = createRootRouteWithContext()({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'Acme Studio — Creative Agency for Bold Brands' },
      { name: 'description', content: 'Acme Studio builds brand identities, websites, and campaigns that stand out. Based in NYC, working worldwide.' },
      { name: 'author', content: 'Acme Studio' },
      { name: 'theme-color', content: '#0A0A0A' },
      { name: 'robots', content: 'index, follow, max-image-preview:large' },
      { property: 'og:type', content: 'website' },
      { property: 'og:site_name', content: 'Acme Studio' },
      { property: 'og:locale', content: 'en_US' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ],
  }),
  // ...
});
```

### Per-Route Meta in Page `head()`

Each page route overrides title, description, and OG tags. This goes in the route definition, not the component.

```tsx
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/services')({
  head: () => ({
    meta: [
      { title: 'Services — Acme Studio' },
      { name: 'description', content: 'Brand identity, web design, and digital campaigns. See what Acme Studio can build for you.' },
      { property: 'og:title', content: 'Services — Acme Studio' },
      { property: 'og:description', content: 'Brand identity, web design, and digital campaigns.' },
      { property: 'og:url', content: 'https://acme-studio.higgsfield.app/services' },
      { property: 'og:image', content: 'https://acme-studio.higgsfield.app/og-services.png' },
      { name: 'twitter:title', content: 'Services — Acme Studio' },
      { name: 'twitter:description', content: 'Brand identity, web design, and digital campaigns.' },
    ],
    links: [
      { rel: 'canonical', href: 'https://acme-studio.higgsfield.app/services' },
    ],
  }),
  component: ServicesPage,
});
```

### Title Formula

- **Homepage:** `[Brand] — [Tagline]` → `Acme Studio — Creative Agency for Bold Brands`
- **Subpages:** `[Page] — [Brand]` → `Services — Acme Studio`

Keep titles under 60 characters. The brand always appears.

### Description Rules

- 150-160 characters max. Google truncates beyond that.
- Primary keyword in the first 100 characters.
- Write for humans — it shows in search result snippets.
- Derive from intake: the user's stated purpose/service IS the description seed.

### Canonical URL Pattern

All Higgsfield apps follow: `https://<slug>.higgsfield.app/<path>`

- Homepage: `https://acme-studio.higgsfield.app`
- Subpage: `https://acme-studio.higgsfield.app/services`
- No trailing slash. No query params. No fragments.

### Robots Directive

| Page type | `robots` value |
|---|---|
| Public pages (homepage, services, about, blog) | `index, follow, max-image-preview:large` |
| Auth pages, admin, dashboard | `noindex, nofollow` |
| Legal (privacy, terms) | `index, nofollow` |

Set the default in `__root.tsx`. Override per-route for protected pages.

### Deriving Values from Intake

Map user input directly:

| Intake field | Meta target |
|---|---|
| Brand / business name | `title` (brand part), `og:site_name`, `author` |
| Purpose / tagline | `title` (tagline part), homepage `description` |
| Primary service / product | Subpage `description` seed |
| Brand color | `theme-color` |
| Logo / hero image | `og:image` |

### Page metadata file (`app/src/app-meta.json`) + Cover video

`app/src/app-meta.json` is the machine-editable page-metadata file the template
reads at BUILD time for the global head, and the marketplace syncs onto the
website's feed/listing card on every deploy. Its keys:

```jsonc
{
  "og_title":       "…",   // browser <title> + og:title
  "og_description": "…",   // meta description + og:description
  "og_image_url":   "…",   // og:image + twitter:image (the feed card cover)
  "marketplace_cover_url": "…", // plain (unmasked) cover art — marketplace/preview slot
  "favicon_url":    "…",   // <link rel="icon">
  "og_video_url":   "…"    // og:video — the COVER VIDEO (feed cards play it on hover)
}
```

Fill the five text/image keys with real values before any deploy or
publish (URLs: absolute https, or a root-relative path to a file in
`app/public/` — it is resolved against the site's own host).

**Cover video (`og_video_url`).** The animated counterpart of the cover image —
the Higgsfield feed plays it on the website's card. It is OPTIONAL and costs
credits to produce, so:

1. **ASK THE USER FIRST.** Offer it when publishing ("want a short cover video
   for the feed card?"); never generate one unprompted.
2. If yes: generate a SHORT seamless loop (3-6s, no cuts, loop-friendly motion)
   of the site's hero visual with the Higgsfield video tools (the video-loop
   recipe in `references/asset-system.md` / `references/wow-maker.md` applies).
3. Put the result where the card can load it: download it into `app/public/`
   (e.g. `app/public/cover-video.mp4`) and set
   `"og_video_url": "/cover-video.mp4"`, or use the generation result's hosted
   https URL directly.
4. Commit + deploy — the metadata (and the feed card) update on the next
   deploy, like every other `app-meta.json` change.

### Pitfalls

1. **Duplicate titles across routes.** Every page needs a unique `title` and `description`. Copy-paste from root is the #1 SEO mistake.
2. **Missing `og:image`.** Social shares without an image get 80% less engagement. Use a 1200x630 image minimum. If no custom OG image exists, use the hero or logo on a colored background.
3. **Placeholder text in production.** Search `__root.tsx` for `App Title`, `MyApp`, or `Lorem` before every deploy. Automated check: the build should grep for these.
4. **Description too short or generic.** "Welcome to our website" is not a description. It must describe what the user gets.
5. **Canonical mismatch.** The canonical URL in `head()` must exactly match the deployed URL. Wrong canonical = Google ignores the page.

## Technical SEO

Technical SEO infrastructure that every Higgsfield website needs. This skill covers the server routes, headers, and performance patterns that search engines require before they'll properly index a site.

### robots.txt Server Route

Create `app/src/routes/robots.txt.ts`:

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/robots')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const origin = new URL(request.url).origin;
        const body = [
          'User-agent: *',
          'Allow: /',
          '',
          `Sitemap: ${origin}/sitemap.xml`,
        ].join('\n');

        return new Response(body, {
          status: 200,
          headers: { 'Content-Type': 'text/plain' },
        });
      },
    },
  },
});
```

The file path is `robots.txt.ts` — TanStack Start maps the `.txt` extension to serve at `/robots.txt`. Origin is derived from the request so it works on any host the site is served from.

### sitemap.xml Server Route

Create `app/src/routes/sitemap.xml.ts`:

#### Single-page site (landing page)

```ts
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/sitemap')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const origin = new URL(request.url).origin;
        const today = new Date().toISOString().split('T')[0];

        const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${origin}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>`;

        return new Response(xml, {
          status: 200,
          headers: { 'Content-Type': 'application/xml' },
        });
      },
    },
  },
});
```

#### Multi-page site

```ts
import { createFileRoute } from '@tanstack/react-router';

const ROUTES = [
  { path: '/', priority: '1.0', changefreq: 'weekly' },
  { path: '/services', priority: '0.8', changefreq: 'monthly' },
  { path: '/about', priority: '0.6', changefreq: 'monthly' },
  { path: '/contact', priority: '0.6', changefreq: 'monthly' },
  { path: '/blog', priority: '0.7', changefreq: 'weekly' },
];

export const Route = createFileRoute('/sitemap')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const origin = new URL(request.url).origin;
        const today = new Date().toISOString().split('T')[0];

        const urls = ROUTES.map(
          (r) => `  <url>
    <loc>${origin}${r.path === '/' ? '' : r.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${r.changefreq}</changefreq>
    <priority>${r.priority}</priority>
  </url>`
        ).join('\n');

        const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

        return new Response(xml, {
          status: 200,
          headers: { 'Content-Type': 'application/xml' },
        });
      },
    },
  },
});
```

Update the `ROUTES` array when adding pages. Keep paths in sync with actual route files.

### Security Headers in server.ts

Security headers (CSP, HSTS, etc.) are not defined here — they have one
canonical owner: `applySecurityHeaders()` in
`app/src/lib/security-headers.server.ts`. Import it in `app/src/server.ts` and
wrap every response (including redirects and error responses):

```ts
import { applySecurityHeaders } from './lib/security-headers.server';

export default {
  async fetch(request: Request, env: any) {
    try {
      const response = await handler.fetch(request, env);
      return applySecurityHeaders(response);
    } catch (error) {
      return applySecurityHeaders(new Response('Internal Server Error', { status: 500 }));
    }
  },
};
```

Do not define a second header function in this file. For the full rules
(framing/CSP rationale, what to keep, what never to set), see
`references/security.md#worker-hardening`.

### Trailing Slash Normalization

Add this at the top of the fetch handler in `app/src/server.ts`, before the `handler.fetch` call. Duplicate URLs (with and without trailing slash) split link equity.

```ts
const url = new URL(request.url);
if (url.pathname !== '/' && url.pathname.endsWith('/')) {
  url.pathname = url.pathname.slice(0, -1);
  return Response.redirect(url.toString(), 301);
}
```

### Canonical URLs

Every page route's `head()` must include a canonical link. This is the single source-of-truth URL for that page.

```ts
export const Route = createFileRoute('/about')({
  head: () => ({
    links: [
      { rel: 'canonical', href: 'https://acme-studio.higgsfield.app/about' },
    ],
    meta: [
      { title: 'About — Acme Studio' },
      // ... other meta
    ],
  }),
  component: AboutPage,
});
```

Pattern: `https://<slug>.higgsfield.app/<path>` — no trailing slash, no query params.

### Performance Hints in `__root.tsx`

Add preconnect hints in the root route's `head()` for any external resources. Google Fonts is the most common:

```tsx
head: () => ({
  links: [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossOrigin: 'anonymous' },
    { rel: 'dns-prefetch', href: 'https://fonts.googleapis.com' },
  ],
  meta: [
    // ... meta tags from the "Meta tags & OG" section above
  ],
}),
```

Place `preconnect` before any stylesheet links. This shaves 100-300ms off font loading, which directly impacts Largest Contentful Paint (LCP).

### Cloudflare Edge Advantage

Higgsfield websites deploy as Cloudflare Workers with SSR. This means:

- **SSR at 300+ edge locations** — the HTML is rendered close to the user, not at a single origin. TTFB under 100ms globally.
- **No hydration delay for crawlers** — search engine bots get fully rendered HTML on first request. No "render budget" concerns.
- **Automatic HTTPS** — Cloudflare handles TLS. No certificate management needed.
- **HTTP/2 and HTTP/3** — enabled by default on Cloudflare. Parallel resource loading with zero config.

This is a structural SEO advantage over client-rendered SPAs. Don't undermine it by adding client-side-only rendering patterns — keep data fetching in `loader()` and critical content in the initial SSR response.

### Pitfalls

1. **Forgetting to update the sitemap ROUTES array.** Every new page route needs a corresponding sitemap entry. Dead sitemap URLs actively hurt crawl efficiency.
2. **CSP blocking inline styles from the design system.** The default CSP includes `'unsafe-inline'` for styles. If you tighten it, test that Tailwind/CSS-in-JS still works.
3. **robots.txt with a hardcoded origin.** The route derives origin from the request URL, so any host the site is served from gets correct sitemaps automatically. Don't hardcode URLs.
4. **Missing canonical on dynamic routes.** Routes with params (`/blog/$slug`) must build the canonical URL from the param value, not use a static string.
5. **Trailing slash redirect loops.** The normalization redirect must be the FIRST check in `fetch()`, before `handler.fetch`. Placing it after can cause double-processing or loops with Cloudflare's own redirects.

## Schema markup

Load this skill for any website build with a public face. Structured data (JSON-LD) is how search engines understand what a page *is* — without it, rich results are off the table.

### Schema Type Decision Matrix

| Site type | Schema types to apply |
|---|---|
| Agency / studio / company | `Organization` + `ProfessionalService` + `WebSite` |
| Product / e-commerce | `Product` + `Organization` + `WebSite` |
| SaaS / app | `SoftwareApplication` + `Organization` + `WebSite` |
| Local business | `LocalBusiness` + `WebSite` |
| Blog / content site | `Article` or `BlogPosting` + `WebSite` |
| Any site | `WebSite` (always include) |
| Page has FAQ section | Add `FAQPage` to the above |

### Reusable Component

Create `app/src/components/StructuredData.tsx`:

```tsx
export function StructuredData({ json }: { json: string }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: json }}
    />
  );
}
```

SSR-safe. No client JS needed. The `json` prop is a pre-stringified JSON-LD object.

### Usage Pattern

1. Define schema objects as module-level constants — `JSON.stringify` runs once at import time, not per render.
2. Place `<StructuredData>` at the top of the page JSX, before any visible content.

```tsx
import { StructuredData } from '~/components/StructuredData';

const ORG_SCHEMA = JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'Acme Studio',
  url: 'https://acme-studio.higgsfield.app',
  logo: 'https://acme-studio.higgsfield.app/logo.png',
});

export function HomePage() {
  return (
    <>
      <StructuredData json={ORG_SCHEMA} />
      {/* visible content */}
    </>
  );
}
```

### Required Fields Per Schema Type

#### Organization

| Field | Value |
|---|---|
| `@type` | `"Organization"` |
| `name` | Brand name |
| `url` | Canonical site URL |
| `logo` | Absolute URL to logo image |
| `sameAs` | Array of social profile URLs (optional but recommended) |

#### WebSite

| Field | Value |
|---|---|
| `@type` | `"WebSite"` |
| `name` | Site name |
| `url` | Canonical homepage URL |
| `potentialAction` | `SearchAction` with `query-input` (if site has search) |

#### ProfessionalService

| Field | Value |
|---|---|
| `@type` | `"ProfessionalService"` |
| `name` | Business name |
| `url` | Canonical URL |
| `description` | One-sentence service description |
| `areaServed` | Geographic area or `"Worldwide"` |
| `serviceType` | Primary service category |
| `priceRange` | e.g. `"$$"` or `"$$$"` |

#### SoftwareApplication

| Field | Value |
|---|---|
| `@type` | `"SoftwareApplication"` |
| `name` | App name |
| `url` | Canonical URL |
| `applicationCategory` | e.g. `"BusinessApplication"` |
| `operatingSystem` | `"Web"` for web apps |
| `offers` | `{ "@type": "Offer", "price": "0", "priceCurrency": "USD" }` |

#### Product

| Field | Value |
|---|---|
| `@type` | `"Product"` |
| `name` | Product name |
| `description` | Short product description |
| `image` | Product image URL |
| `offers` | `Offer` with `price`, `priceCurrency`, `availability` |

#### FAQPage

| Field | Value |
|---|---|
| `@type` | `"FAQPage"` |
| `mainEntity` | Array of `{ "@type": "Question", "name": "...", "acceptedAnswer": { "@type": "Answer", "text": "..." } }` |

### Complete Example: Agency Site

This goes in the homepage component. All three schemas in one `@graph`:

```tsx
const SCHEMA = JSON.stringify({
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      '@id': 'https://acme-studio.higgsfield.app/#org',
      name: 'Acme Studio',
      url: 'https://acme-studio.higgsfield.app',
      logo: 'https://acme-studio.higgsfield.app/logo.png',
      sameAs: [
        'https://twitter.com/acmestudio',
        'https://linkedin.com/company/acmestudio',
      ],
    },
    {
      '@type': 'WebSite',
      '@id': 'https://acme-studio.higgsfield.app/#website',
      name: 'Acme Studio',
      url: 'https://acme-studio.higgsfield.app',
      publisher: { '@id': 'https://acme-studio.higgsfield.app/#org' },
    },
    {
      '@type': 'ProfessionalService',
      '@id': 'https://acme-studio.higgsfield.app/#service',
      name: 'Acme Studio',
      url: 'https://acme-studio.higgsfield.app',
      description: 'Full-service creative agency specializing in brand identity and web design.',
      areaServed: 'Worldwide',
      serviceType: 'Creative Agency',
      priceRange: '$$$',
      provider: { '@id': 'https://acme-studio.higgsfield.app/#org' },
    },
  ],
});
```

### Pitfalls

1. **No relative URLs.** Every `url`, `logo`, `image` field must be an absolute `https://` URL. Schema validators reject relative paths silently.
2. **Don't duplicate schemas.** Use `@graph` to bundle multiple types in one `<script>` tag. Multiple `<script type="application/ld+json">` blocks are valid but harder to maintain.
3. **Match visible content.** Schema `name`/`description` must match what the user sees on the page. Google penalizes mismatches.
4. **Test with Google Rich Results Test** (https://search.google.com/test/rich-results) before shipping. Schema syntax errors are invisible to users but block rich results.
5. **Keep schemas on the pages they describe.** Organization schema goes on the homepage. Product schema goes on the product page. Don't dump everything on every page.

## Entity SEO

### What It Is

Entity optimization establishes the site's primary entity (business, person, product) as a distinct node in knowledge graphs used by Google, Bing, and AI search engines. The goal is unambiguous machine identification — when an AI engine mentions your entity, it should pull the correct name, description, and links.

### Entity Data Model

Collect these fields during the business intake (the "Schema markup" section above handles the base schema; this section enriches it):

| Field          | Example                                      | Required |
|----------------|----------------------------------------------|----------|
| name           | Acme Corp                                    | Yes      |
| description    | Automated invoicing for logistics companies  | Yes      |
| url            | https://acmecorp.com                         | Yes      |
| logo           | https://acmecorp.com/logo.png                | Yes      |
| sameAs[]       | [LinkedIn URL, Instagram URL, ...]           | Yes      |
| foundingDate   | 2019-03-15                                   | If known |
| industry       | Financial Technology                         | If known |
| areaServed     | North America, Europe                        | If known |

### sameAs Strategy

`sameAs` tells search engines which external profiles belong to this entity. Include URLs from:

- **LinkedIn** — company page URL (e.g. `https://linkedin.com/company/acmecorp`)
- **Instagram** — `https://instagram.com/acmecorp`
- **X (Twitter)** — `https://x.com/acmecorp`
- **GitHub** — `https://github.com/acmecorp` (if applicable)
- **Crunchbase** — `https://crunchbase.com/organization/acmecorp` (if listed)
- **Wikidata** — `https://wikidata.org/wiki/Q12345` (if an entry exists)

During intake, ask the client for all active social/professional profiles. Verify each URL resolves (don't include dead links). Order from highest authority to lowest. Only include profiles the entity actually controls.

### Consistent NAP

Name, Address, and Phone must be identical across:

1. **JSON-LD structured data** — the Organization schema on the page
2. **Visible page content** — the footer or contact section
3. **External listings** — Google Business Profile, Yelp, LinkedIn, etc.

Even minor differences ("St." vs "Street", "+1 555" vs "555") fragment the entity in knowledge graphs. Pick one canonical format and enforce it everywhere. If the business has no physical address, omit `address` entirely rather than using a fake or partial one.

### Multi-Entity @graph Pattern

When a page represents multiple entities (the company, its founder, and its product), use the `@graph` array to define them in a single JSON-LD block with cross-references:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://acmecorp.com/#org",
      "name": "Acme Corp",
      "url": "https://acmecorp.com",
      "logo": "https://acmecorp.com/logo.png",
      "founder": { "@id": "https://acmecorp.com/#founder" },
      "sameAs": [
        "https://linkedin.com/company/acmecorp",
        "https://instagram.com/acmecorp"
      ]
    },
    {
      "@type": "Person",
      "@id": "https://acmecorp.com/#founder",
      "name": "Jane Smith",
      "jobTitle": "CEO & Founder",
      "worksFor": { "@id": "https://acmecorp.com/#org" },
      "sameAs": ["https://linkedin.com/in/janesmith"]
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://acmecorp.com/#product",
      "name": "Acme Invoicing",
      "applicationCategory": "BusinessApplication",
      "offers": {
        "@type": "Offer",
        "price": "99",
        "priceCurrency": "USD"
      },
      "provider": { "@id": "https://acmecorp.com/#org" }
    }
  ]
}
```

Key rules: each entity gets a unique `@id` (use URL fragments like `/#org`, `/#founder`). Cross-reference via `{ "@id": "..." }` rather than nesting the full object. This lets search engines build a connected graph rather than treating each entity as isolated.

### Implementation

Use the `StructuredData` component from the "Schema markup" section above. Build the JSON-LD string at module level with all entity fields populated, then pass it as the `json` prop:

```tsx
import { StructuredData } from '~/components/StructuredData';

const entityJson = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [ /* entities as above */ ]
});

export default function Page() {
  return (
    <>
      <StructuredData json={entityJson} />
      {/* visible page content */}
    </>
  );
}
```

The visible page content must reflect every claim in the schema — name, description, address, founding date. Don't put data in JSON-LD that visitors can't see.

### Pitfalls

1. **Dead sameAs links** — Including social URLs that 404 or redirect to a login wall. Verify every URL before adding it to the schema.
2. **NAP fragmentation** — Using "Acme Corp" in schema but "Acme Corporation" in the footer. Pick one canonical name.
3. **Missing @id cross-references** — Defining Organization and Person in the same @graph but not linking them via `founder`/`worksFor`. Without links, search engines treat them as unrelated.
4. **Over-claiming sameAs** — Listing profiles the entity doesn't own (e.g. a Wikipedia article about a different "Acme"). Every sameAs URL must be a profile controlled by or specifically about this entity.
5. **Invisible schema data** — Putting industry, areaServed, or founding date in JSON-LD without showing it anywhere on the page. Search engines increasingly penalize schema that has no visible counterpart.

## GEO / content

### What is GEO

Generative Engine Optimization (GEO) is the practice of structuring website content so AI-powered search engines (ChatGPT, Perplexity, Gemini, Copilot) can extract, cite, and surface it in generated answers. Traditional SEO gets you ranked; GEO gets you quoted.

### 7 Principles

#### 1. Direct Answer Structure

Lead every section with the answer, not a buildup. AI engines extract the first sentence that resolves the query — if your answer is buried in paragraph three, it won't be selected. Write the topic sentence as a standalone factual statement, then add supporting detail below. Pattern: "X is Y. It works by Z. This matters because W."

#### 2. Entity Clarity

Name and type the primary entity within the first 100 words of the page. "Acme Corp is a B2B SaaS company that provides automated invoicing for mid-market logistics firms." This gives AI engines the subject, category, and scope immediately. Avoid opening with generic statements like "Welcome to our website" or "In today's fast-paced world."

#### 3. Factual Specificity

Replace vague claims with concrete, verifiable data points. AI engines prefer citable facts over marketing language. "Trusted by many clients" → "Used by 200+ logistics companies across 14 countries since 2019." "Industry-leading uptime" → "99.97% uptime over the trailing 12 months, verified by StatusPage." Every stat should be something you can back up if challenged.

#### 4. Schema-Content Alignment

The JSON-LD structured data must reflect what's visible on the page — not aspirational content, not a different description, not extra services not mentioned in the copy. If the Organization schema says `"description": "AI-powered invoicing platform"`, those words must appear in the visible hero or about section. AI engines cross-reference schema against page text; mismatches reduce trust signals.

#### 5. FAQ Sections

Add a FAQ section with direct question-and-answer pairs. Each answer should be 1-3 sentences — long enough to be useful, short enough to be extractable. Wrap in FAQPage schema.

Component pattern:

```tsx
function FAQ({ items }: { items: { q: string; a: string }[] }) {
  return (
    <section>
      <h2>Frequently Asked Questions</h2>
      {items.map((item, i) => (
        <details key={i}>
          <summary>{item.q}</summary>
          <p>{item.a}</p>
        </details>
      ))}
    </section>
  );
}
```

Matching FAQPage schema (add to the page's JSON-LD):

```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does Acme Corp do?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Acme Corp provides automated invoicing software for mid-market logistics companies, handling billing, compliance, and payment reconciliation."
      }
    }
  ]
}
```

#### 6. Citation-Friendly Headings

Write H2 and H3 headings that match the queries people (and AI) actually ask. Not "Our Approach" but "How Acme Corp Automates Invoice Processing." Not "Features" but "Key Features of Acme Invoicing Software." The heading should be a valid search query on its own. AI engines use headings as section identifiers when constructing citations — a descriptive heading increases the chance your section gets attributed.

#### 7. Topical Authority

Demonstrate depth through internal linking, consistent entity naming, and expertise signals. Link related sections to each other (e.g. the pricing page links to the features page with descriptive anchor text). Use the exact same entity name everywhere — don't alternate between "Acme", "Acme Corp", "ACME Corporation", and "our company." Include an expertise section (team credentials, years in operation, certifications) to strengthen E-E-A-T signals that AI engines evaluate.

---

### Before / After Example

**Before (vague, buried answer):**
```
Welcome to Acme Corp. We've been in business for years and pride
ourselves on excellent service. Our innovative platform helps
companies manage their finances. Many organizations trust us.
Contact us to learn more about what we can do for you.
```

**After (GEO-optimized):**
```
Acme Corp is an automated invoicing platform for mid-market
logistics companies, processing over 2M invoices annually across
14 countries. Founded in 2019, the platform reduces manual billing
time by 73% through AI-powered line-item matching and compliance
checks. Acme serves 200+ customers including DHL Freight and Kuehne+Nagel.
```

---

### Pitfalls

1. **Keyword stuffing for AI** — Repeating the same phrase unnaturally hoping AI will pick it up. AI engines detect and penalize this the same way traditional search does.
2. **Schema without matching content** — Adding FAQPage schema for questions never shown on the page. This is structured-data spam and triggers trust penalties.
3. **Walls of text with no structure** — AI engines rely on headings, lists, and paragraphs to segment content. A 2000-word block with no subheadings is effectively invisible to extraction.
4. **Answering questions indirectly** — "Contact us for pricing" instead of showing actual pricing. AI engines skip sections that don't contain an answer.
5. **Inconsistent entity naming** — Switching between "Acme Corp", "Acme", "the company", and "we" makes it harder for AI to build a coherent entity profile. Pick one primary name and use it consistently, especially in headings and first sentences.

## Audit

### When to Run

Run this audit after building any website and before running `higgsfield website deploy`. It is the SEO quality gate. Do not deploy until every FAIL is resolved. The audit is self-contained — read the project source files directly, no external tools or browser needed.

### Audit Procedure

Read every route/page component in `app/src/routes/`. For each file, evaluate the 10 checks below. Collect results, print the summary table, fix any FAILs, then re-run until clean.

---

#### 1. Heading Hierarchy

Verify exactly one `<h1>` per page. Sections use `<h2>`, subsections `<h3>`, etc. No skipped levels (e.g. `<h1>` followed by `<h3>` with no `<h2>`). The `<h1>` must contain or closely match the page's primary keyword.

FAIL if: multiple `<h1>` tags, zero `<h1>` tags, or any skipped heading level.

#### 2. Image Alt Text

Every `<img>` element must have a non-empty `alt` attribute. For AI-generated images, derive `alt` from the generation prompt (e.g. prompt "modern office interior" → `alt="Modern office interior"`). Decorative images use `alt=""` with `role="presentation"`.

FAIL if: any `<img>` lacks `alt`. WARN if: `alt` is generic like "image" or "photo".

#### 3. Link Text Quality

Anchor text must describe the destination. Flag any `<a>` whose visible text is "click here", "read more", "learn more", "here", or "link". Replace with descriptive text that makes sense out of context.

FAIL if: any non-descriptive anchor text found.

#### 4. Content-to-Code Ratio

Scan each page component for visible text content vs. JS/markup overhead. A page should have at least 200 words of visible text (excluding nav/footer boilerplate). Flag pages that are mostly animations, images, or interactive JS with minimal readable text.

WARN if: visible text is under 200 words. FAIL if: under 50 words.

#### 5. Keyword Alignment

Identify the page's primary keyword (from the business intake or page purpose). Verify it appears in: the `<title>` tag, the `<h1>`, the first paragraph of body text, and the `<meta name="description">` content. Phrasing can vary but the core term must be present.

FAIL if: keyword missing from title or H1. WARN if: missing from first paragraph or meta description.

#### 6. Mobile Readability

Check CSS/Tailwind classes for: no `font-size` below 16px on body text (12px acceptable only for captions/labels), `line-height` at least 1.5 on paragraphs, sufficient color contrast (no light gray on white). Verify the viewport meta tag is present.

FAIL if: viewport meta missing. WARN if: body text under 16px or line-height under 1.4.

#### 7. Keyboard Navigation

All interactive elements (`<button>`, `<a>`, `<input>`, custom clickable `<div>`s) must be keyboard-focusable. Any `<div>` or `<span>` with an `onClick` must also have `role="button"`, `tabIndex={0}`, and a keyboard handler. Check for visible focus indicators (no `outline-none` without a replacement).

FAIL if: clickable element lacks keyboard support. WARN if: `outline-none` used without custom focus style.

#### 8. Fragment Integrity

Find all `href="#..."` links in the page. For each fragment identifier, verify a matching `id` exists in the rendered DOM of the same page. Check both static IDs and dynamically generated ones (section slugs, etc.).

FAIL if: any fragment link points to a non-existent ID.

#### 9. Form Accessibility

Every `<input>`, `<select>`, and `<textarea>` must have an associated `<label>` (via `htmlFor`/`id` pairing) or an `aria-label`/`aria-labelledby`. Required fields must have the `required` attribute or `aria-required="true"`. Error messages must be linked via `aria-describedby`.

FAIL if: any input lacks a label. WARN if: required fields not marked.

#### 10. Social Preview

Verify `<meta property="og:title">`, `<meta property="og:description">`, and `<meta property="og:image">` exist. The `og:image` must be an absolute URL (starts with `https://`), not a relative path. Also check for `<meta name="twitter:card">`.

FAIL if: `og:image` missing or relative. WARN if: `og:title` or `og:description` missing.

---

### Output Format

After scanning, print this table to the build log:

```
┌─────────────────────────┬────────┬──────────────────────────────────┐
│ Check                   │ Status │ Detail                           │
├─────────────────────────┼────────┼──────────────────────────────────┤
│ Heading hierarchy       │ PASS   │                                  │
│ Image alt text          │ FAIL   │ 2 images missing alt in Hero.tsx │
│ Link text quality       │ PASS   │                                  │
│ Content-to-code ratio   │ WARN   │ 120 words on /pricing            │
│ Keyword alignment       │ PASS   │                                  │
│ Mobile readability      │ PASS   │                                  │
│ Keyboard navigation     │ PASS   │                                  │
│ Fragment integrity      │ FAIL   │ #team target missing             │
│ Form accessibility      │ PASS   │                                  │
│ Social preview          │ PASS   │                                  │
├─────────────────────────┼────────┼──────────────────────────────────┤
│ RESULT                  │ BLOCK  │ 2 FAIL — fix before deploy       │
└─────────────────────────┴────────┴──────────────────────────────────┘
```

Status values: **PASS** (good), **WARN** (acceptable, note for improvement), **FAIL** (must fix before deploy).

### Fix-and-Recheck Loop

1. For each FAIL, open the source file and apply the fix directly.
2. After fixing all FAILs, re-run the full 10-item audit from the top.
3. Repeat until the table shows zero FAILs.
4. WARNs are acceptable for deploy but should be noted in the deploy summary.
5. Only after a clean pass (zero FAILs), proceed to `higgsfield website deploy`.
