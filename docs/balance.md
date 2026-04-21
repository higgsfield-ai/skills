# Balance & Transactions

## Balance

```bash
curl -s https://dev-fnf.higgsfield.ai/agents/balance \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"\(.credits) credits — \(.subscription_plan_type) plan"'
```

Returns `{email, credits, subscription_plan_type}` for the currently selected workspace (or user's default if none selected).

## Transactions

```bash
curl -s "https://dev-fnf.higgsfield.ai/agents/transactions?cursor=0&size=10" \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '"Date|Model|Credits|Action",
           (.items[] | "\(.created_at | split("T") | "\(.[0]) \(.[1][0:5])")|\(.display_name)|\(.credits)|\(.action)")' \
  | column -t -s '|'
```

Cursor pagination: `cursor` (int), `size` (max 100, default 10). Each item: `{display_name, credits, action, created_at}`. Pass `next_cursor` from the response as the next `cursor`.
