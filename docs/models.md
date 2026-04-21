# Models

```bash
curl -s https://dev-fnf.higgsfield.ai/agents/models \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r 'group_by(.type) | .[] |
      "**\(.[0].type | ascii_upcase) models**",
      (.[] | "- \(.display_name)"),
      ""'
```

Filter: `?type=image` or `?type=video`.

When the user picks a model, fetch its params as a compact table (skips `$defs` / `$ref` noise):

```bash
curl -s https://dev-fnf.higgsfield.ai/agents/models \
  -H "Authorization: Bearer $(python3 get_token.py)" \
  | jq -r '.[] | select(.display_name == "<chosen>") | .params as $p
    | ($p.required // []) as $req
    | ($p."$defs" // {}) as $defs
    | "Param|Type|Default|Required",
      ($p.properties | to_entries[] | .key as $k
        | "\($k)|\(
            .value as $v
            | if $v.enum then ($v.enum | join(","))
              elif $v."$ref" then
                ($defs[$v."$ref" | split("/")[-1]]) as $ref
                | if $ref.enum then ($ref.enum | join(","))
                  else ($ref.type // "object") end
              elif $v.type then $v.type
              else "object" end
          )|\(.value.default // "-")|\(if ($req | index($k)) then "yes" else "no" end)")' \
  | column -t -s '|'
```

`job_set_type` is what you pass as `job_set_type` in the generate body (see `docs/generate.md`).
