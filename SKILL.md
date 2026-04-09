---
name: higgsfield
description: "Generate images and videos using Higgsfield AI."
license: MIT
---

# Higgsfield AI — Image & Video Generation

## Auth

When user asks to login or authenticate, run directly:
```bash
python3 login.py
```

Opens browser for approval, polls until approved, saves token.

## Workspace Selection

On first use, list workspaces:
```bash
curl -s https://fnf.higgsfield.ai/agents/workspaces \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Ask user which workspace to use. Remember their choice for future requests.

## Model Selection

List available models:
```bash
curl -s "https://fnf.higgsfield.ai/agents/models" \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Filter by type with `?type=image` or `?type=video`. Each model returns `job_set_type`, `display_name`, `type`, and `params` (JSON schema of accepted parameters).

## Generate

```bash
curl -s -X POST https://fnf.higgsfield.ai/agents/jobs \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "<workspace_id>", "job_set_type": "<job_set_type>", "params": {"prompt": "<prompt>"}}'
```

Returns list of job IDs. Build params from the model's `params` schema. Use defaults for params the user didn't mention.

## Image Inputs

Models accept images via `input_images` or `medias` fields (check the model's params schema).

### Image reference: `{id, type}`

Two types:
- **Uploaded image**: `{"id": "<media_id>", "type": "media_input"}`
- **Previous generation**: `{"id": "<job_id>", "type": "image_job"}`

### `input_images` field

Array of `{id, type}`:
```json
{"prompt": "...", "input_images": [{"id": "<id>", "type": "<type>"}]}
```

### `medias` field

Array of `{role, data: {id, type}}`. Role is `image` for image models:
```json
{"prompt": "...", "medias": [{"role": "image", "data": {"id": "<id>", "type": "<type>"}}]}
```

Video models use `start_image` and `end_image` roles:
```json
{"prompt": "...", "medias": [
  {"role": "start_image", "data": {"id": "<id>", "type": "<type>"}},
  {"role": "end_image", "data": {"id": "<id>", "type": "<type>"}}
]}
```

## Poll Job

```bash
curl -s https://fnf.higgsfield.ai/agents/jobs/<job_id> \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Poll every 3 seconds until terminal status: `completed`, `failed`, `canceled`, `nsfw`, `ip_detected`. Poll all returned job IDs in parallel. Note: do not use `status` as a bash variable name — reserved in zsh.

## Check Balance

```bash
curl -s "https://fnf.higgsfield.ai/agents/balance?workspace_id=<workspace_id>" \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

## Upload Image

1. Get presigned URL:
```bash
curl -s -X POST https://fnf.higgsfield.ai/agents/upload \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

2. Upload file:
```bash
curl -s -X PUT "<upload_url>" -H "Content-Type: image/png" --data-binary @<file_path>
```

3. Confirm:
```bash
curl -s -X POST https://fnf.higgsfield.ai/agents/upload/<media_id>/confirm \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Use returned `id` as `{"id": "<media_id>", "type": "media_input"}` in generation params.

## Soul Character

Train a personalized model on face photos. Once trained, pass it to Soul 2.0 or Soul Cinema for personalized output.

### Create

1. Upload 5-20 face photos using the Upload flow.
2. Create:
```bash
curl -s -X POST https://fnf.higgsfield.ai/agents/custom-references \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "<workspace_id>", "type": "<soul_2|soul_cinematic>", "name": "<name>", "input_images": [{"id": "<media_id>", "type": "media_input"}, ...]}'
```

### Poll Training

```bash
curl -s https://fnf.higgsfield.ai/agents/custom-references/<reference_id> \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Poll every 10 seconds. Status: `queued` → `in_progress` → `completed` or `failed`.

### List

```bash
curl -s "https://fnf.higgsfield.ai/agents/custom-references?workspace_id=<workspace_id>" \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Optional params: `type` (`soul_2` or `soul_cinematic`), `status` (`completed`, `in_progress`, etc.).

### Generate with Soul Character

Pass `custom_reference_id` in params:
```json
{"workspace_id": "...", "job_set_type": "text2image_soul_v2", "params": {"prompt": "...", "custom_reference_id": "<reference_id>"}}
```

Use `text2image_soul_v2` for Soul 2.0, `soul_cinema_studio` for Soul Cinema. Only use characters with `completed` status.

## UX

- Show result URLs as clickable links
- Do not download files unless user explicitly asks
- Enhance prompts: expand short descriptions into detailed visual prompts (lighting, composition, style, colors, mood). Keep the user's intent intact
- Use defaults from model params. Only ask about params user explicitly mentioned
- If user asks for multiple generations (e.g. "generate 4 images"), make separate requests in parallel and poll each independently
- When user wants to use a Soul Character, list their completed ones first. If none exist, guide them to create one

## Common Failures

- `Session expired` / `401 Unauthorized` — run `python3 login.py`
- `API error 400/422` — check available models and params schema
- `Soul Character not found` — check reference ID and status
- `Minimum Basic plan required` — Soul Character training requires a paid plan
