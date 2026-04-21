# Generate

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/jobs \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"job_set_type": "<job_set_type>", "params": {"prompt": "<prompt>"}}'
```

Returns a JSON array of job UUIDs. Poll each via `docs/jobs.md`.

Build `params` from the model's JSON schema (see `docs/models.md`). For fields the user didn't mention, use defaults from the schema.

If the user asks for several generations in one go ("generate 4 images"), make separate requests in parallel and poll each independently.

## Estimate cost

Before running, estimate credits (same body as generate):

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/jobs/cost \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"job_set_type": "<job_set_type>", "params": {...}}'
```

Returns `{credits: <int>}`.

## Media inputs

Most models accept references via `input_images` or `medias` in `params`:

- **Uploaded image**: `{"id": "<id>", "type": "media_input"}`
- **Uploaded video**: `{"id": "<id>", "type": "video_input"}`
- **Uploaded audio**: `{"id": "<id>", "type": "audio_input"}`
- **Previous generation**: `{"id": "<job_id>", "type": "image_job"}`

### `input_images` field

```json
{"prompt": "...", "input_images": [{"id": "<id>", "type": "<type>"}]}
```

### `medias` field

Array of `{role, data: {id, type}}`. Common roles: `image` (image models), `start_image` / `end_image` (video transitions), `audio` (lipsync).

```json
{"prompt": "...", "medias": [
  {"role": "start_image", "data": {"id": "<id>", "type": "media_input"}},
  {"role": "end_image", "data": {"id": "<id>", "type": "media_input"}}
]}
```

Check the model's `params` schema to know which field it expects.
