# Uploads

Supports `image`, `video`, `audio`. Every step requires `?type=...`.

## Create + upload

1. Get presigned URL:

```bash
curl -s -X POST "https://dev-fnf.higgsfield.ai/agents/uploads?type=image" \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Returns `{id, type, url, upload_url}`.

2. Upload file (matching Content-Type: `image/png`, `video/mp4`, or `audio/mpeg`):

```bash
curl -s -X PUT "<upload_url>" -H "Content-Type: image/png" --data-binary @<file_path>
```

3. Confirm:

```bash
curl -s -X POST "https://dev-fnf.higgsfield.ai/agents/uploads/<id>/confirm?type=image" \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Use the returned `id` in generate params (see `docs/generate.md`):
- image → `{"id": "<id>", "type": "media_input"}`
- video → `{"id": "<id>", "type": "video_input"}`
- audio → `{"id": "<id>", "type": "audio_input"}`

## List

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/uploads?type=image&size=20" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Date|Type|URL",
           (.items[] | "\(.created_at | todateiso8601 | split("T") | "\(.[0]) \(.[1][0:5])")|\(.type)|\(.url)")' \
  | column -t -s '|'
```

Cursor pagination. Each item: `{id, type, url, created_at}`.
