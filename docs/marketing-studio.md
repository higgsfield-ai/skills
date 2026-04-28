# Marketing Studio

Generate branded marketing images and videos with curated avatars and products imported from a URL.

## Avatars

### List

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/marketing-studio/avatars?size=20" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Name|Type|Gender",
           (.items[] | "\(.name)|\(.type)|\(.gender // "—")")' \
  | column -t -s '|'
```

Optional query: `search`, `user_cursor`, `preset_cursor`. `type` is `custom` (user-uploaded) or `preset` (curated). Save the `id` only when you need to pass it into video generation — otherwise show only `name`.

### Create custom avatar

Batch create from already-uploaded images (1–4 per call). Get `id` + `url` from the upload create response (see `docs/uploads.md`) — the upload `url` must be from the Higgsfield CDN.

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/marketing-studio/avatars \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{
        "avatars": [
          {
            "name": "<avatar name>",
            "media": {
              "id": "<media_input_id>",
              "url": "<cloudfront url from /uploads response>",
              "type": "media_input"
            },
            "is_pinned": false
          }
        ]
      }'
```

`media` is optional (omit for an empty avatar slot), `is_pinned` defaults to false. `media.type` is `media_input` (user upload) or `image_job` (a generated job). Returns the created avatars; pass `id` as `{id, type: "custom"}` into video generation.

## Products

User products are imported from a URL: title + description + reference images. Use them for product-aware video ads.

### List

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/marketing-studio/products?limit=20&offset=0" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Title|Status|Domain",
           (.items[] | "\(.title)|\(.status)|\(.scrape_url_domain // "—")")' \
  | column -t -s '|'
```

### Create from uploaded images

Use when you already have product images uploaded — skips the URL fetch and creates a `completed` product directly.

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/marketing-studio/products \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "<product title>",
        "description": "<optional description>",
        "media_input_ids": ["<media_input_id>"]
      }'
```

`media_input_ids` requires at least one `media_input` UUID (from `docs/uploads.md`). Returns the product entity ready to use; no polling needed.

### Import from URL

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/marketing-studio/products/fetch \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"url": "<url>"}'
```

Returns the product entity immediately with `status: queued|in_progress`. Poll the list endpoint every 2s (filter by `id`) until `status` is `completed` or `failed`. Cap at ~45s. The product is ready when `medias[]` is non-empty.

```bash
# poll loop (zsh / bash):
PRODUCT_ID=<id-from-fetch>
for i in {1..23}; do
  STATUS=$(curl -s "https://dev-fnf.higgsfield.ai/agents/marketing-studio/products?limit=50" \
    -H "Authorization: Bearer $(python3 get_token.py)" \
    | jq -r ".items[] | select(.id == \"$PRODUCT_ID\") | .status")
  [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]] && break
  sleep 2
done
echo "$STATUS"
```

If `status: failed`, read `fail_reason` to surface a useful error. Use `id` from a `completed` product as `product_ids` in video generation.

## Webproducts

For App Store / web pages where a basic product record isn't enough — favicon, screenshots, and marketing copy are imported. App Store URLs auto-route to webproducts.

### List

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/marketing-studio/webproducts?limit=20&offset=0" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Title|Status|URL",
           (.items[] | "\(.title // "—")|\(.status)|\(.url // "—")")' \
  | column -t -s '|'
```

### Create manually

Use when you already have screenshots/copy and don't need a URL fetch.

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/marketing-studio/webproducts \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{
        "url": "<homepage url>",
        "title": "<title>",
        "subtitle": "<subtitle>",
        "description": "<description>",
        "favicon_url": "<favicon url>",
        "medias": [
          {"url": "<screenshot url>", "type": "desktop"}
        ]
      }'
```

All fields are optional. `medias[].type` is `desktop` or `mobile`. Returns the webproduct ready to use; no polling needed.

### Import from URL

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/marketing-studio/webproducts/fetch \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"url": "<url>"}'
```

Same poll pattern as products — re-list and filter by `id` until `status` terminal. Pass the resulting `id` as `web_product_ids` in video generation.

## Generate Image (`marketing_studio_image`)

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/jobs \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{
        "job_set_type": "marketing_studio_image",
        "params": {
          "prompt": "<enhanced description>",
          "aspect_ratio": "1:1",
          "resolution": "1k",
          "input_images": [{"id": "<media_input_id>", "type": "media_input"}]
        }
      }'
```

`aspect_ratio`: `auto`, `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`. `resolution`: `1k`, `2k`, `4k`. `input_images` is optional reference media (see `docs/uploads.md` for IDs and `docs/generate.md` for media types).

Poll job UUIDs via `docs/jobs.md`.

## Generate Video (`marketing_studio_video`)

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/jobs \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{
        "job_set_type": "marketing_studio_video",
        "params": {
          "prompt": "<enhanced description>",
          "aspect_ratio": "9:16",
          "duration": 15,
          "resolution": "720p",
          "generate_audio": false,
          "mode": "ugc",
          "avatars": [{"id": "<avatar_id>", "type": "preset"}],
          "product_ids": ["<product_id>"]
        }
      }'
```

Params:
- `aspect_ratio`: `auto`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`. Default `16:9`.
- `duration`: integer ≥ 4 seconds. Default 15.
- `resolution`: `480p`, `720p`. Default `720p`.
- `mode`: `ugc`, `ugc_how_to`, `ugc_unboxing`, `product_showcase`, `product_review`, `tv_spot`, `wild_card`, `ugc_virtual_try_on`, `virtual_try_on`. Default `ugc`.
- `avatars`: at most one — `{id, type: preset|custom}`. From the avatars endpoint above.
- `product_ids`: at most one product ID (from `/products`).
- `web_product_ids`: at most one webproduct ID (from `/webproducts`). Use this OR `product_ids`, not both.
- `generate_audio`: bool, default false.
- `medias`: optional reference frames (see `docs/generate.md` `medias` field).

Poll job UUIDs via `docs/jobs.md`.
