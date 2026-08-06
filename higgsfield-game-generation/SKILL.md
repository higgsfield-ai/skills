---
version: 0.12.0
name: higgsfield-game-generation
description: |
  Build and iterate playable browser games, or create game-specific sprites,
  textures, animated 3D assets, music, SFX, and voice with Higgsfield CLI.
  Use when: "make a game", "build a browser game", "create game assets",
  "make a spritesheet", "generate a tileable texture", "animate a 3D game
  character", or "deploy/publish my game". Supports solo, local multiplayer,
  and online multiplayer games. NOT for: ordinary image/video generation,
  game trailers, native mobile/desktop builds, or editing a game without its
  source files.
argument-hint: "[game brief or asset request] [reference files]"
allowed-tools: Bash
models:
  # This skill's asset pipelines are deterministic: their output feeds ffmpeg frame
  # extraction, spritesheet assembly, and rigging steps whose parameters are tuned to a
  # specific model's behavior. These pins are load-bearing — a substitution silently
  # produces unusable assets rather than an error. Re-tune the pipeline before changing one.
  pinned:
    - id: seedance1_5
      reason: 2D spritesheet frame extraction is tuned to this model's 4s/720p motion cadence
    - id: flux_2
      reason: key-pose stage depends on this model's full-body pose adherence at explicit AR
    - id: image_background_remover
      reason: per-frame alpha extraction; the only background remover in the catalog
    - id: z_image
      reason: 3D rigging needs a strict T-pose text-to-image, which this model holds reliably
    - id: gpt_image_2
      reason: seamless-tile edit and grid sheets depend on its documented border/palette drift
    - id: nano_banana_2
      reason: sprite/tile/texture batch stage is calibrated to its 1k output at fixed AR
---

# Higgsfield Game Generation

Create a coherent, playable web game and deliver the URL, or produce only the requested game assets. Higgsfield CLI owns generation, 3D action discovery, deployment, and optional marketplace publication.

## Bootstrap

Before work begins:

1. If `higgsfield` is unavailable, install it:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. If `higgsfield account status` reports an expired or missing session, ask the user to run `higgsfield auth login`, then continue after confirmation.
3. For a full game, confirm `higgsfield game deploy --help` works before generating assets. This is the delivery capability check.
4. Locate this installed skill directory and set it explicitly:
   ```bash
   export GAME_SKILL="/absolute/path/to/higgsfield-game-generation"
   test -f "$GAME_SKILL/scripts/pipeline.py"
   python3 "$GAME_SKILL/scripts/pipeline.py" --help
   ```
   Never recreate bundled scripts from memory.

## Route the request

- **Full playable game** — follow the full workflow below.
- **Assets only** — read `references/stylization.md`, then the matching asset reference. Do not deploy a game.
- **Design only** — read `references/game-design-system.md`; return the requested design artifact and asset manifest.
- **Existing game iteration** — inspect the supplied source, preserve its architecture and unchanged assets, amend the manifest, rebuild, verify, and redeploy with its existing game ID.
- **Trailer or promotional video** — use `higgsfield-generate`, not this skill.
- **Native mobile/desktop/console runtime** — explain that this skill ships browser games; offer a web build unless the user supplied another toolchain.

## Full game workflow

### 1. Plan

Read `references/game-design-system.md` first and in full. Resolve the game profile, delivery context, core loop, win/lose/restart behavior, performance budgets, input methods, and language handling.

Create `design/assets.csv` with one row per visual or audio asset:

```csv
id,role,type,description,size/ratio,style line ref,source
```

Read `references/multiplayer.md` whenever Players is not solo. Local same-screen multiplayer remains client-side; online multiplayer requires the platform server module.

Read `references/stylization.md` before producing any visual, including procedural canvas art. Derive one STYLE FORMULA and insert it byte-for-byte into every visual prompt. If the brief already fixes the style, state the formula and continue. If several materially different styles fit, show concise options and wait for selection.

No game code or generated visual should exist before the manifest and STYLE FORMULA.

### 2. Generate assets and build

Start independent generation jobs together, then write the game while those jobs run. Inspect every model contract before first use:

```bash
higgsfield model list --json
higgsfield model get <job_type>
higgsfield generate create <job_type> ... --wait --json
```

Media flags accept local paths or prior upload/job IDs. Keep job JSON in project files when chaining; do not dump IDs into the user-facing reply.

Read the reference matching each manifest row:

| Asset | Required reference |
|---|---|
| Static sprites, backgrounds, UI | `references/stylization.md` |
| Spritesheets / 2D animation | `references/2d-animation.md` |
| Repeating ground, walls, tiles, PBR maps | `references/textures.md` |
| Any 3D model or animation | `references/3d-animation.md` |
| Music, SFX, voice | `references/audio.md` |

For 3D animation selection:

```bash
higgsfield preset list animation-action --query walk --json
higgsfield preset list animation-action --group Fighting --category Punching --json
```

When multiple actions fit, show their preview URLs and let the user choose. Pass the chosen integer as `--animation_action_id` only after checking the target model schema.

Read `references/build-game.md` last, but before writing game code. Assemble the source ZIP with `index.html` and exactly one root code module (`logic.js` or `server.js`). Use relative asset paths and keep `design/assets.csv` in the shipped project.

Generation failures get at most two retries. After that, use the best valid result and compensate in code, or amend the manifest honestly.

### 3. Verify and deliver

Run the local game over HTTP, not `file://`:

```bash
python3 -m http.server 8000
```

Verify the complete loop, restart, missing assets, console errors, responsive canvas, non-Latin keyboard layout through `event.code`, touch-only play when mobile is in scope, declared gamepad controls, fixed-timestep behavior, and multiplayer in two sessions when applicable.

Package from the directory that contains the required root files:

```bash
zip -r /absolute/path/to/game.zip . -x '*.DS_Store' 'node_modules/*' '.git/*'
higgsfield game deploy /absolute/path/to/game.zip \
  --title "<public title>" \
  --description "<player-facing description>" \
  --thumbnail "<optional https 16:9 image URL>" \
  --favicon "<optional https 1:1 image URL>" \
  --json
```

For an update, add `--game-id <existing_game_id>`; never omit it after an update failure, because that would create a different game.

Deployment creates the playable URL. Publishing to the public marketplace is a separate external action and requires explicit user intent:

```bash
higgsfield game publish <game_id> \
  --name "<optional listing name>" \
  --description "<optional listing description>" \
  --cover-url "<optional https 16:9 URL>" \
  --logo-url "<optional https 1:1 URL>" \
  --json
```

Re-open the returned playable URL and repeat the critical smoke path. Deliver the URL returned by CLI; never construct it manually.

## Reference order

For full games:

1. `references/game-design-system.md`
2. `references/multiplayer.md` when Players is not solo
3. `references/stylization.md`
4. Conditional asset references
5. `references/build-game.md`

Read each selected reference completely. Do not load unrelated references.

Supporting references opened only when their owning route requires them:

- `references/client-reference.md` — online client protocol.
- `references/kernel-reference.md` — platform room-kernel contract.
- `references/logic-reference.md` — turn-based/event-driven rules module.
- `references/meshy-api.md` — raw Meshy fallback only.
- `references/meshy-input-rules.md` — mandatory before any image-to-3D submit.
- `references/procedural-animation.md` — non-humanoid procedural rigs.

## UX rules

- Mirror the user's language; keep generation prompts in English.
- User updates are short and describe the game, not internal gates, phase numbers, job IDs, or tool mechanics.
- Ask only when the answer materially changes the game. Do not batch unrelated questions.
- Preserve one visual system across generated and procedural assets.
- Do not request secrets in chat. Raw Meshy fallback may use a user-configured environment key only when the native Higgsfield 3D model is unavailable.
- Do not publish publicly unless the user requested marketplace publication.

## Output

- Design-only: requested design artifact plus `design/assets.csv`.
- Assets-only: usable files/result URLs and their manifest roles.
- Full game: verified playable URL, a one-line gameplay summary, and marketplace URL only when explicitly published.
