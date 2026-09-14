# Workflow Generation

Workflows are higher-level generation flows exposed separately from the model catalog. They still create normal generation jobs, so results are fetched with `higgsfield generate get` / `higgsfield generate wait`.

## Discover workflows

```bash
higgsfield workflow list
higgsfield workflow get draw_to_video
higgsfield workflow get reframe --json
```

Every workflow returned by `workflow list` is accepted by `generate workflow`, including image workflows. Use `workflow get` before creating a job when unsure about params. Do not expect workflows to appear in `higgsfield model list`.

Examples of public workflows (use the live list for all available names):

| Workflow | Use when |
|---|---|
| `draw_to_video` | Edit a source video using an edited sketch/image frame at a timestamp. Business name may be "Draw To Edit"; CLI name is `draw_to_video`. |
| `reframe` | Reframe a source video to another aspect ratio and optional resolution. |

Do not use or mention `game_character_creator` unless the current CLI exposes it publicly and the user explicitly asks for it.

## Create jobs

### Draw To Video

Use when the user has:
- a source video
- an edited/sketched frame image
- the timestamp for that frame
- an edit instruction

```bash
higgsfield generate workflow draw_to_video \
  --video ./source.mp4 \
  --sketch ./frame.png \
  --timestamp 3.2 \
  --prompt "make the jacket red" \
  --wait
```

`--image` is an alias for `--sketch`.

### Reframe

Use when the user wants a different video aspect ratio.

```bash
higgsfield generate workflow reframe \
  --video ./source.mp4 \
  --aspect-ratio 9:16 \
  --resolution 720p \
  --wait
```

Optional:
- `--mode std|pro`; default `std`
- `--start-image <path-or-id>`
- `--image <path-or-id>` references for `--mode pro`; use 1-2 images
- `--folder-id <folder_id>`

## Cost

Workflow cost uses `generate cost workflow`, not `generate workflow cost`.

```bash
higgsfield generate cost workflow draw_to_video --duration 8.2 --resolution 720p
higgsfield generate cost workflow reframe --duration 7.1 --resolution 1080p
```

Cost parameters come from `workflow get <name> --json` (`cost_params`), independently of creation parameters. No cost schema means estimation is unavailable; an empty schema means no parameters are required. The CLI accepts cost estimates for every listed workflow with a cost schema.

If the user asks "how much will this workflow cost?", run cost first and report credits before creating.

## Results

With `--wait`, the CLI waits for the workflow job and prints the result. Without `--wait`, it prints the job id; use normal generation job commands:

```bash
higgsfield generate get <job_id>
higgsfield generate wait <job_id>
```

Do not tell the user to use `workflow get` for a job result. `workflow get` describes the workflow schema; `generate get` fetches the created job.

## Maintainer note

When FNF adds a public chain, document it here as a workflow:

1. Verify it appears in `higgsfield workflow list`.
2. Inspect params with `higgsfield workflow get <workflow_name> --json`.
3. Add it to the Current public workflows table with a clear use case.
4. Add a create example using `higgsfield generate workflow <workflow_name> ... --wait`.
5. Add a cost example only when `workflow get` exposes `cost_params`.
6. Keep result retrieval on `higgsfield generate get/wait <job_id>`.

Do not add workflow-only items to `model-catalog.md`. Public docs say "workflow"; FNF source may say "chain".
