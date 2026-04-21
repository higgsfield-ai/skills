# Soul Character

Train a personalized model on face photos. Once trained, pass it to Soul 2.0 or Soul Cinema for personalized output.

## Train

1. Upload 5–20 face photos via `docs/uploads.md` (`?type=image`).
2. Create:

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/custom-references \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"type": "<soul_2|soul_cinematic>", "name": "<name>", "input_images": [{"id": "<media_id>", "type": "media_input"}, ...]}'
```

3. Poll training:

```bash
curl -s https://dev-fnf.higgsfield.ai/agents/custom-references/<reference_id> \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Poll every 10 seconds. Status: `queued` → `in_progress` → `completed` or `failed`.

## List

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/custom-references?size=20" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Name|Type|Status",
           (.items[] | "\(.name)|\(.type)|\(.status)")' \
  | column -t -s '|'
```

Optional: `type` (`soul_2` or `soul_cinematic`), `status` (`completed`, `in_progress`, etc.). Cursor-paginated.

When the user wants to use a Soul Character, list their `completed` ones first. If none exist, guide them to create one.

## Use in generate

Pass `custom_reference_id` in params:

```json
{"job_set_type": "text2image_soul_v2", "params": {"prompt": "...", "custom_reference_id": "<reference_id>"}}
```

- Soul 2.0: `text2image_soul_v2`
- Soul Cinema: `soul_cinema_studio`

Only use characters with `completed` status.
