# Meshy API — verified animated-character pipeline (FALLBACK ONLY)

> **STOP — check the native CLI path first.** If `image_to_3d` and `3d_rigging`
> appear in `higgsfield model list`, do NOT use this raw API and
> do NOT ask the user for any API key. The native tool covers this entire
> pipeline with workspace credits: stage [1] = model `image_to_3d`
> (`should_texture:true`), stage [2] = `enable_rigging:true` (same job), stage
> [3] = one clip per job via `enable_animation:true` + `animation_action_id`
> (extra clips: model `3d_rigging` on the result GLB; ids via
> `higgsfield preset list animation-action`), stage [4] = the same local merge script.
> This document exists only for environments with no native 3D tool.

Verified end-to-end 2026-06-10 (image → 3D → rig → 4 clips → merged GLB).
Endpoint shapes re-checked against docs.meshy.ai 2026-11-06.

**Before building ANY request, read `meshy-input-rules.md`** (single-figure
rule, cropping, polygon-budget params). Skipping it wastes credits.

## Basics

- Base URL: `https://api.meshy.ai`
- Auth: `Authorization: Bearer <msy_... key>`. Require the user to configure it
  as `MESHY_API_KEY` outside chat; never print or commit it.
- All generation endpoints are async: POST returns `{"result": "<task_id>"}`,
  then poll `GET <same path>/<task_id>` until `status` is `SUCCEEDED` /
  `FAILED` (`CANCELED` is Creative Lab only). Between polls wait the
  `Retry-After` response header, or 5 s if it's missing. SSE `.../stream`
  exists but plain polling is simpler in a sandbox.
- Wait at least **60 min from `created_at`** before giving up on a task. Busy
  periods are slow but still succeed, and a task can go from `IN_PROGRESS`
  back to `PENDING` with `progress` reset to 0 (rescheduled, same task ID).
  A timed-out poll or create request is not a failed task: never create a
  second task because of one, or you pay twice.
- Result URLs expire (`expires_at`, ~3 days; Text to 3D tasks have no
  `expires_at` but are deleted after 3 days too) — **download assets
  immediately** after SUCCEEDED.
- Credits: `GET /openapi/v1/balance`. Failed tasks are refunded
  (`consumed_credits: 0` on FAILED).

## Pipeline overview (humanoid)

```
input image ──> [1] image-to-3d ──> [2] rigging ──> [3] animations ──────> [4] merge clips
 (validated)      textured GLB       rigged GLB        action_ids: 1 GLB,     only if several
                                     + walk/run free   1 clip per action      files remain
```

Current prices: image-to-3d **15** credits textured with Smart Topology
(**30** on Meshy 7.1), rigging **5** (walk + run clips included), animation
**3 per action**. A full character with 2 extra clips: **26 credits** on Smart
Topology, 41 on Meshy 7.1. Live table: https://docs.meshy.ai/api/pricing

## [1] Image → 3D

`POST /openapi/v1/image-to-3d`

```json
{
  "image_url": "<public URL or data URI>",
  "model_type": "smart-topology",
  "ai_model": "meshy-t2.5",
  "target_polycount": 20000,
  "pose_mode": "t-pose",
  "should_texture": true,
  "texture_model": "meshy-n1",
  "target_formats": ["glb"],
  "multi_view_thumbnails": true
}
```

- `model_type: "smart-topology"` + `ai_model: "meshy-t2.5"` — a clean
  triangle mesh generated at `target_polycount` (100–30 000). Replaces the
  deprecated `model_type: "lowpoly"`, which returns `400` from 2026-11-30.
- `texture_model: "meshy-n1"` — clean stylized color from the input image;
  no `texture_prompt`, no PBR. Omit it for the default `meshy-7` when you need
  those. The price is the same.
- `pose_mode: "t-pose"` straightens the character regardless of the
  reference pose — fixes "awkward" references before auto-rig.
- `target_formats: ["glb"]` — don't generate fbx/obj/usdz you won't use;
  task finishes faster.
- `multi_view_thumbnails: true` — 4 cardinal-view PNGs in `thumbnail_urls`
  for vision QC without downloading the GLB (~5 s extra latency).
- Polygon-budget rules and polycount budgets: see `meshy-input-rules.md`.
- Multi-image variant: `POST /openapi/v1/multi-image-to-3d` (1–4 views,
  same pose on every view, front first — see input rules). Smart Topology is
  single-image only, so multi-image uses a standard model + remesh.

## text-to-3d note (two-phase) + stuck-refine recovery

`text-to-3d` is two tasks on `POST /openapi/v2/text-to-3d`: **preview**
(geometry, gray) then **refine** (texture, created with `preview_task_id`).
Verified failure mode: a refine stuck at `IN_PROGRESS` `progress: 0` for 1.5 h.

Recovery recipe:
- Keep polling for at least 60 min from `created_at`. A task can sit at
  `progress: 0`, or drop back to `PENDING`, and still succeed.
- **Don't `DELETE` it.** Since 2026-09-11, `DELETE` on an `IN_PROGRESS` task
  returns `409 Conflict` and the task keeps running. Only a `PENDING` task is
  deleted and refunded.
- Still not final after 60 min: a new refine with the **same**
  `preview_task_id` is a workaround, but it is charged again (the old task is
  refunded only if it ends `FAILED`). Report the task ID to support@meshy.ai.
- **Rig the textured model, not the gray preview.** Meshy documents Rigging
  as unsupported for untextured meshes. To skip the separate refine, use
  image-to-3d, which textures in the same task.

## [2] Rigging

`POST /openapi/v1/rigging`

```json
{
  "input_task_id": "<image-to-3d task id>",   // OR "model_url": "<public GLB url>"
  "height_meters": 1.8
}
```

- Returns task id; on SUCCEEDED the result has `rigged_character_glb_url`,
  `rigged_character_fbx_url`, and **`basic_animations`** — walking + running
  GLB/FBX **for free**, no separate animation tasks needed for those two.
- **Humanoid only.** Docs: "not suitable for non-humanoid assets". A
  quadruped/creature returns `422 — Pose estimation failed`. Branch to
  Tripo3D or the procedural pipeline (`procedural-animation.md`).
  Nuance: Meshy's **web app** offers a 4-legs (quadruped) rig option, but the
  public **API** endpoint is humanoid-only — don't promise API quadruped
  support; suggest the web UI as a manual fallback for quadrupeds.
- Not supported: untextured meshes, unclear limb structure. A `model_url`
  character must face **+Z** (glTF forward), or pose estimation fails (`422`).
- Hard limit: **380 000 triangles** (a quad counts as 2) → `400`. Smart
  Topology meshes always fit; remesh a heavier mesh first
  (`POST /openapi/v1/remesh`, `target_polycount` ≤ 300 000, or ≤ 150 000
  with `topology: "quad"`).
- `model_url` must be a `.glb`: up to 400 MB from an http(s) URL, 100 MB as
  a data URI. Prefer `input_task_id` while the source task is under 3 days
  old; a stored signed URL stops working at its `expires_at`.
- `height_meters` aids rig scaling (default 1.7) — pass a sensible value
  (1.7–1.9 humans).

## [3] Animations (library retarget)

`POST /openapi/v1/animations`

```json
{
  "rig_task_id": "<rigging task id>",
  "action_ids": [0, 4]
}
```

- `action_ids` (1–10 ids, no repeats): **one task, one GLB, one clip per
  action**, in list order, each clip named after its library entry. Billed 3
  credits per action. Use `"action_id": <int>` instead for a single clip.
- Catalog: `GET /openapi/v1/animations/library` (same Bearer key, free).
  Filters: `search` (name or key), `category` (`WalkAndRun`,
  `BodyMovements`, `DailyActions`, `Fighting`, `Dancing`), `sub_category`,
  `action_ids` (check stored ids are still valid). Each entry has
  `action_id`, `name`, `key`, `category`, `sub_category`, `preview_url`. The
  old web URL `api.meshy.ai/web/public/animations/resources` uses different
  field names (`id`, `subCategory`) and also lists the rig's free walk/run
  as ids `-2` and `-1`, which the documented endpoint doesn't — use the
  documented endpoint.
  Used in the verified run: `idle = action_id 0`, `attack = action_id 4`.
  Don't trust ids from memory — fetch the catalog and match by name.
- **~680 mocap presets** (locomotion, combat, deaths, dances, emotes), all
  **biped** — they only fit humanoid rigs.
- Clip not in the library (a roar, a custom emote): Text to Motion
  (`POST /openapi/v1/text-to-motion`, 3 or 10 credits), then send
  `motion_task_id` instead of `action_id(s)`. Biped rigs only.
- Result: `animation_glb_url` — skinned, same skeleton as the rig task.
- Optional `post_process`: `change_fps` (24/25/30/60), `fbx2usdz`,
  `extract_armature`. With `action_ids` it applies to the merged file.

## [4] Merge clips into one multi-clip GLB

With `action_ids` you usually have two files: the rig's free walk/run and the
multi-clip GLB. Merging is still needed to put them together, or for clips
made in separate tasks. Preferred: stdlib merger, no Blender (verified on a
live run 2026-06-11 — full pipeline cost 41 credits: text-to-3d + rig + 2
anims). It keeps the clip names of a multi-clip input:

```bash
python3 scripts/glb_merge_anims.py \
  rigged.glb walk.glb:Walk run.glb:Run clips.glb out.glb
```

Blender alternative (same semantics, but single-clip inputs only: it keeps
one action per file, so it would drop clips from an `action_ids` GLB):

```bash
blender -b -P scripts/merge_anim_glbs.py -- \
  rigged.glb walk.glb:Walk run.glb:Run idle.glb:Idle attack.glb:Attack out.glb
```

Note: `rigged.glb` may carry a service clip named like
`Armature|clip0|baselayer` (bind pose) — drop it from the merged file before
delivery.

**MANDATORY post-merge check — root-bone scale bug (verified):** library
animations can bake a scale factor into the root bone's scale channel.
Observed: `Hips` scale **1.176** baked into `idle` while walk/run were 1.0 —
the character visibly grew 18% when idle played. Fix (automated in the merge
script): for every clip, if the root bone's scale min/max ≠ 1.0 — set scale
keys to 1.0 AND divide that clip's root translation keys by the same factor
(otherwise the character hovers above ground). Verify with
`scripts/glb_inspect.py` — it prints per-clip root-scale ranges. Check an
`action_ids` GLB the same way even when nothing needs merging; passing it
through `glb_merge_anims.py` applies the fix.

Finish with the standard checks: `glb_inspect.py` (skins ≥ 1, all clips
present, alphaMode OPAQUE) and zip before `higgsfield upload create` (raw `.glb`
is a blocked extension).

## Polling skeleton (bash)

```bash
TASK=$(curl -s -X POST https://api.meshy.ai/openapi/v1/image-to-3d \
  -H "Authorization: Bearer $MESHY_API_KEY" -H 'Content-Type: application/json' \
  -d @payload.json | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"])')
while :; do
  S=$(curl -s -D headers.txt https://api.meshy.ai/openapi/v1/image-to-3d/$TASK \
    -H "Authorization: Bearer $MESHY_API_KEY")
  ST=$(echo "$S" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("status","RETRY"),d.get("progress",""))' 2>/dev/null)
  echo "$ST"; case "$ST" in SUCCEEDED*|FAILED*|CANCELED*) break;; esac
  W=$(awk 'tolower($1)=="retry-after:"{print $2+0}' headers.txt)
  sleep "${W:-5}"
done
```

If the create `POST` itself times out, don't resend it: the task may exist
and be charged. Wait ~1 min, list the newest tasks
(`GET /openapi/v1/image-to-3d?sort_by=-created_at`), and create again only
if it isn't there.

## Error cheat-sheet

| Code | Meaning | Action |
|---|---|---|
| 400 | bad params / unreachable image URL / >380k triangles on rig / `lowpoly` or `meshy-t1` | fix payload; remesh first; use Smart Topology |
| 402 | out of credits, or free plan | tell user, show balance |
| 404 | source task's files deleted after `expires_at` (~3 days) | re-create the source task |
| 409 | `DELETE` on an `IN_PROGRESS` task | wait for a final status; the task keeps running |
| 422 (rigging) | pose estimation failed — non-humanoid, unclear limbs, or `model_url` not facing +Z | procedural branch / Tripo |
| 429 | rate limit | wait `Retry-After` seconds, retry |
| refine at progress 0 | busy queue or rescheduled task | keep polling to 60 min from `created_at`, then stuck-refine recovery |
