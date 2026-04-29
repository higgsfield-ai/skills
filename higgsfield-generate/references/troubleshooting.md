# Troubleshooting

## Authentication

- `Session expired.` → `hf auth login`
- `Stored credentials are for ... but current environment ...` → `hf auth login` for the current API URL.
- `Not authenticated.` → first `hf auth login`.

## Validation

- `Missing required params: prompt` — user gave no prompt. Ask.
- `Invalid values: <param>=<v> (allowed: ...)` — pick from allowed enum.
- `Unknown params: <name>` — schema doesn't accept this flag. Run `hf model get <jst>` and check.

## Job lifecycle

- `Job ended with status "failed"` — server-side failure. Often prompt content / safety. Try rephrasing.
- `nsfw` / `ip_detected` — content policy. Rephrase.
- `Timeout after 10m` — model is slow today. Bump `--timeout 30m` or retry.

## Rate limits

`Higgsfield API error (HTTP 429)` — too many requests. Back off.

## CloudFlare / DataDome

If `Failed to decode response. Body: <html>...captcha-delivery...` appears, the server's anti-bot fired. Wait 30s and retry. If persistent, ping the team.

## Cost

`hf generate cost <jst> ...` returns credit estimate without submitting. Useful when the user asks "how much will this cost?".
