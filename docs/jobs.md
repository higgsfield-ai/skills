# Jobs

## Poll

```bash
curl -s https://dev-fnf.higgsfield.ai/agents/jobs/<job_id> \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Poll every 3 seconds until terminal status: `completed`, `failed`, `canceled`, `nsfw`, `ip_detected`. Poll all returned IDs in parallel.

Response: `{id, status, display_name, job_set_type, result_url, min_result_url, created_at, params}`. `result_url` and `min_result_url` are populated when `status=completed`. Use `display_name` for user-facing labels.

Do not use `status` as a bash variable name — reserved in zsh.

## List completed

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/jobs?type=image&size=20" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Date|Model|URL",
           (.items[] | "\(.created_at | todateiso8601 | split("T") | "\(.[0]) \(.[1][0:5])")|\(.display_name)|\(.result_url)")' \
  | column -t -s '|'
```

Filter: `?type=image` or `?type=video`. Cursor pagination: `cursor` (float), `size` (max 100, default 20). Each item has the same shape as poll.
