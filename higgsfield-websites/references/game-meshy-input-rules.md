# Image→3D input rules — read BEFORE any submit

These rules prevent the two most expensive failure classes: garbage geometry
from bad reference images, and wrong polycount paths. Every image→3D submit
must pass this preflight — **whether through the native 3D CLI path
(`higgsfield generate create`, preferred) or the raw
fallback API**; the same engine reconstructs the mesh either way. (Param
behavior re-checked against docs.meshy.ai 2026-11-06.)

## Rule 1 — ONE figure per input image (character sheets)

Meshy reconstructs **everything in the frame as a single object**. A
character sheet with 4 views becomes "a statuette of 4 fused figures".

Mandatory preflight on every user-provided reference:

1. Vision check: "how many separate figures/views are in this image?"
2. If more than one figure → crop. Two valid paths:
   - **One best view** (front or 3/4) → regular `image-to-3d`.
   - **Each view as its own file** → `multi-image-to-3d` (1–4 images) —
     better geometry, but ONLY if the pose is identical on all panels.
     Different poses across panels ⇒ fall back to the single-view path.
3. Cropping in the sandbox: use **ffmpeg** (`ffmpeg -i sheet.png -vf
   "crop=w:h:x:y" view.png`) — PIL is not in the system python.

## Rule 2 — pose normalization

Add `"pose_mode": "t-pose"` (or `"a-pose"`): Meshy straightens the character
regardless of the reference pose. This repairs "awkward" references before
auto-rig and matches donor skeletons in the local rig-transfer path.

## Rule 3 — framing

- Full body in frame, nothing cut off.
- Clean/plain background; no shadows, text, watermarks, logos.
- Limbs visually separated from the torso (arms not pressed to the body) —
  fused silhouettes produce fused geometry and break auto-rig.
- One character, no props overlapping the silhouette.
- `image_enhancement: false` only if the exact input style must be preserved
  (standard models only; with `model_type: "smart-topology"` it returns `400`).

## Rule 4 — polygon budget: Smart Topology first

> **`model_type: "lowpoly"` is deprecated (Meshy T1).** Since 2026-10-30 some
> `lowpoly` requests silently run on Smart Topology and ignore
> `target_polycount`; the rest return `400`. From **2026-11-30** every
> `lowpoly` or `meshy-t1` request returns `400`. Never send it.

Two paths. Do not mix them:

| Goal | Params | Caveat |
|---|---|---|
| Game asset at a face budget, single image (**default**) | `"model_type": "smart-topology", "ai_model": "meshy-t2.5", "target_polycount": N` | Generated at that face count, no remesh. Triangles only. Meshy ignores `should_remesh` / `decimation_mode`; `topology: "quad"`, `image_enhancement` and `remove_lighting` return `400` |
| Multi-image input, or quads needed | standard model + `"should_remesh": true, "topology": "triangle"` (or `"quad"`), `"target_polycount": N` | High-detail mesh decimated afterwards. Smart Topology takes one image only |

Native CLI path: field names can differ from the raw API. Run
`higgsfield model get image_to_3d` and use what it lists; if `model_type`
offers `smart-topology` and `smart-topology-t2`, those are T2.5 and T2 (no
`ai_model` field). If it offers no Smart Topology value, use the remesh path.

Faceted low-poly LOOK (what `lowpoly` was for): Smart Topology at a low
`target_polycount`, plus the `low-poly faceted` geometry clause in the concept
image prompt (`stylization.md` §8). `"ai_model": "meshy-t2"` is faster and
keeps parts separate (range 100 – 15 000, default 4 000), good for small props.

Polycount budgets (game-ready guidance):

| Asset class | target_polycount |
|---|---|
| Hero / player character | 15 000 – 30 000 |
| NPC | 5 000 – 15 000 |
| Mob / prop | 1 000 – 5 000 |
| Background filler | 300 – 1 500 |

Valid API range (out of range returns `400`):
- `meshy-t2.5`: **100 – 30 000** (default 15 000)
- `meshy-t2`: **100 – 15 000** (default 4 000)
- remesh on a standard model: **100 – 300 000** (default 30 000)

**Hard rig limit: `/rigging` rejects models over 380 000 triangles (a quad
counts as 2) with `400`.** Smart Topology meshes always fit. If a standard mesh
came out heavier, run `POST /openapi/v1/remesh` with `target_polycount` ≤
300 000 (≤ 150 000 with `topology: "quad"`) before rigging.

## Rule 5 — economy / QC params

- `"texture_model": "meshy-n1"` — Meshy's pick for game characters and
  stylized low-poly assets: clean 2K base color painted from the input image,
  few seams. It takes no `texture_prompt` (the concept image carries the
  style) and no PBR. Use the default `meshy-7` instead when you need
  `texture_prompt`, PBR maps, or 4K/8K. Either way the price is the same.
- `"enable_pbr": false` — skip metallic/roughness/normal maps unless the
  project needs PBR (base color only is faster). `true` with `meshy-n1`
  returns `400`.
- `"target_formats": ["glb"]` — don't generate unused fbx/obj/usdz/stl;
  task completes faster.
- `"multi_view_thumbnails": true` — 4 cardinal-view PNGs (front/right/back/
  left) in `thumbnail_urls` for vision QC without downloading the GLB
  (~5 s extra).

## Payload templates

Game humanoid, exact budget (recommended default, 15 credits):

```json
{
  "image_url": "<cropped single-figure reference>",
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

Small prop or decoration, faceted low-poly look (15 credits):

```json
{
  "image_url": "<cropped single-object reference>",
  "model_type": "smart-topology",
  "ai_model": "meshy-t2",
  "target_polycount": 1500,
  "should_texture": true,
  "texture_model": "meshy-n1",
  "target_formats": ["glb"],
  "multi_view_thumbnails": true
}
```

Multi-view (character sheet split into same-pose panels, front first, 30
credits):

```json
{
  "image_urls": ["front.png", "side.png", "back.png"],
  "pose_mode": "t-pose",
  "should_remesh": true,
  "topology": "triangle",
  "target_polycount": 20000,
  "should_texture": true,
  "target_formats": ["glb"]
}
```
(endpoint: `POST /openapi/v1/multi-image-to-3d`)

## Preflight checklist (run through it verbatim)

- [ ] Vision-counted figures in the reference == 1 (or split for multi-image)
- [ ] Full body, clean background, no text/watermark/shadows
- [ ] `pose_mode` set for characters that will be rigged
- [ ] No `model_type: "lowpoly"` and no `meshy-t1` anywhere
- [ ] Polygon path chosen consciously (Smart Topology vs remesh) — params not mixed
- [ ] `target_polycount` matches asset class table and the model's range
- [ ] `target_formats: ["glb"]`, `enable_pbr: false` unless PBR required
- [ ] Plan stays under rig limit (380k triangles) if rigging follows
