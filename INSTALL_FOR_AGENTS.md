# Install for Agents

You are an AI coding agent. The user asked you to install Higgsfield skills. Follow this exactly.

## Step 1 — Install Higgsfield CLI

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
```

The script asks for sudo password to write to `/usr/local/bin/`. If sudo isn't available, install to home:

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh -s -- --prefix=$HOME/.local
```

Verify: `higgsfield version`. Expect `higgsfield v0.1.X (...) built ...`.

## Step 2 — Authenticate

Ask the user to run:

```bash
higgsfield auth login
```

This opens a browser for OAuth. Wait for them to confirm.

Verify: `higgsfield account status`. Expect `<email> — <plan> plan, <N> credits`.

## Step 3 — Install the skills

Detect the agent platform.

**Claude Code** discovers each skill at `~/.claude/skills/<skill-name>/SKILL.md` — one directory per skill, not one directory per repo. This repo's 8 skills each live in their own `higgsfield-*` folder at the repo root, so clone it somewhere else and symlink each skill folder into place:

```bash
git clone https://github.com/higgsfield-ai/skills.git ~/.agents/vendor/higgsfield-skills
mkdir -p ~/.claude/skills
for d in ~/.agents/vendor/higgsfield-skills/higgsfield-*/; do
  ln -s "$d" "$HOME/.claude/skills/$(basename "$d")"
done
```

Cloning straight to `~/.claude/skills/higgsfield` (one folder per repo) nests every `SKILL.md` one level too deep for Claude Code to find.

**Cursor, Codex, and other agents** that expect one clone per plugin:

| Agent | Path |
|---|---|
| Cursor | `~/.cursor/plugins/higgsfield` |
| Codex | `~/.codex/plugins/higgsfield` |
| Other | `~/.<agent>/skills/higgsfield` |

```bash
git clone https://github.com/higgsfield-ai/skills.git <path>
```

## Step 4 — Verify

Ask the agent (yourself):

> "Generate a tiny test image with Higgsfield."

Run `higgsfield generate create z_image --prompt "test" --wait`. The `--wait` flag blocks until the job finishes; confirm a URL is printed on stdout.

If anything fails:
- 401 / `Session expired` → repeat Step 2
- 4xx → check the error message; read `higgsfield-generate/references/troubleshooting.md`
- Network error → user's connectivity issue

## Step 5 — Done

Report to the user: "Skills installed. Try generating media, creating a complete brand identity, making a narrated explainer or YouTube thumbnail, building a browser game, or training a Soul Character."

Do NOT explain the internals (skill paths, file structure). Just confirm install + give starter prompts.
