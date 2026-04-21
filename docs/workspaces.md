# Workspaces

## List

```bash
curl -s https://dev-fnf.higgsfield.ai/agents/workspaces \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Name|Plan|Credits|Selected",
           (.[] | "\(.name // "Private")|\(.plan_type)|\(.credits)|\(if .is_selected then "✓" else " " end)")' \
  | column -t -s '|'
```

Each entry also carries `id` (used only for `/workspaces/select`) and `user_role`. `name` is `null` for private workspaces — render as "Private".

## Select

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/workspaces/select \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id": "<workspace_id>"}'
```

## Unselect

```bash
curl -s -X POST https://dev-fnf.higgsfield.ai/agents/workspaces/unselect \
  -H "Authorization: Bearer $(python3 get_token.py)"
```

Falls back to the user's default workspace.
