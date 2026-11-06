# Animated 3D Characters (rigged GLB pipeline)

> **Asset reference for game-generation.** Use for ANIMATED (rigged, multi-clip)
> GLB characters in 3D games — walk/run/attack clips, FBX→GLB conversion that
> preserves all clips, CC0 character sources, the Meshy image→3D→rig→animations
> pipeline, and the procedural branch for non-humanoid creatures. **Mandatory for
> every 3D asset — creating a model or animating it; never model or animate 3D
> without this reference.** Static-only meshes follow the same image→3D steps
> (`meshy-api.md`) and stop before the rigging step.
> Style: concept/reference images for 3D follow the
> 3D rules in `stylization.md` §8 (white background, three-quarter
> isometric view, formula in the concept prompt, token in `texture_prompt`).

> **Use the native CLI path first.** `higgsfield generate create` covers image→3D→rig→animation
> pipeline natively: model `image_to_3d` with `should_texture` /
> `enable_rigging` / `enable_animation` + `animation_action_id`, extra clips
> via model `3d_rigging` on the result GLB, clip ids via
> `higgsfield preset list animation-action`. Billed in workspace credits — **no
> external API key exists or is needed; never ask the user for one.** The raw
> provider API (`meshy-api.md`) is a fallback ONLY when no native 3D
> tool is available in the environment.

`sam_3_3d` only makes STATIC meshes. When the user
needs characters that walk/run/attack in Three.js or a game engine, use this
pipeline. Verified end-to-end on 2026-06-10 in the Higgsfield sandbox.
The scripts in `scripts/` are reconstructions of that verified logic —
smoke-test on a small asset before a long batch run.

## Decision table

| Need | Path |
|---|---|
| Stylized game character, fast, zero manual steps | CC0 packs (KayKit/Quaternius) → convert → done |
| CUSTOM character from text/image, zero manual steps, free | 2D→3D rig-transfer pipeline (Step 4 below) — fully local, but skinning quality is rough on image-to-3D meshes; user rejected it for production. Prefer the native 3D tool |
| Custom-look humanoid, best skinning quality | Generate T-pose ref → user runs Mixamo manually (no API!) → user gives FBX → convert here |
| Fully automated 2D→animated GLB, best quality, paid | **Native 3D path — preferred**: inspect `image_to_3d`, select an action with `higgsfield preset list animation-action`, then create with texture, rigging, animation, A-pose, and the chosen integer action ID. Extra clips use `3d_rigging` on the result GLB, then merge locally. **Before any submit read `meshy-input-rules.md`.** Workspace credits only; no provider key. Raw API is fallback only. |
| Non-humanoid CREATURE (dragon, quadruped, snake, spider, fish) | The auto-rig is humanoid-only (non-bipeds rig poorly or fail). Options: (a) Tripo3D API — rig types quadruped/hexapod/octopod/avian/serpentine/aquatic + locomotion presets (needs Tripo key, unverified); (b) **Procedural branch — VERIFIED on a dragon**: build skeleton+weights+sine-based clips in headless Blender, `procedural-animation.md` + `scripts/proc_rig_dragon.py`/`proc_weights.py`/`proc_anim_dragon.py` |
| Non-rigged props (doors, drones, slimes, turrets) | Procedural animation in Three.js code — no rig needed |

**Mixamo has NO official API.** Internal REST API exists but auto-rig marker
placement is interactive-only; browser automation is fragile (Adobe login,
captcha). Don't promise Mixamo automation — frame it as "one manual step,
once per character".

### Native CLI example

```bash
higgsfield model get image_to_3d
higgsfield preset list animation-action --query idle --json
higgsfield generate create image_to_3d \
  --image ./character-reference.png \
  --should_texture true \
  --enable_rigging true \
  --enable_animation true \
  --pose_mode a-pose \
  --animation_action_id <integer> \
  --wait \
  --json
```

Inspect `higgsfield model get 3d_rigging` before requesting extra clips because the
accepted source-media field is contract-driven.

## Step 1 — Headless Blender in the sandbox (no root)

`apt-get install` fails (no sudo). Use the portable build:

```bash
cd <workspace> && mkdir -p blender && cd blender
curl -sL -o blender.tar.xz https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz   # ~336MB, run in background
tar xf blender.tar.xz
```

Binary fails with `libSM.so.6: cannot open shared object file`. Fix without
root by downloading debs to a local apt state and extracting:

```bash
mkdir -p aptstate aptcache libs deb
apt-get -o Dir::State::Lists=./aptstate -o Dir::Cache=./aptcache -o Debug::NoLocking=1 update
cd deb && apt-get -o Dir::State::Lists=../aptstate -o Dir::Cache=../aptcache -o Debug::NoLocking=1 \
  download libsm6 libice6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libgl1 libglx0 libglvnd0 libegl1 libopengl0
for d in *.deb; do dpkg -x "$d" ../libs/; done
export LD_LIBRARY_PATH=<workspace>/blender/libs/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
./blender-4.2.3-linux-x64/blender -b --version   # must print version
```

Pitfall: plain `apt-get download libsm6` fails with "Unable to locate package"
because the default list dir is unreadable — the local `Dir::State::Lists`
override is mandatory.

## Step 2 — FBX → GLB with ALL animation clips

**CRITICAL PITFALL:** naive `import_scene.fbx` + `export_scene.gltf` exports
only ONE clip (the active action, e.g. `Rig|T-Pose`) even when 76 actions
imported. Fix: push every action onto an NLA track before export, and export
with `export_animation_mode='NLA_TRACKS'`. Use `scripts/fbx2glb.py`:

```bash
blender -b -P scripts/fbx2glb.py -- input.fbx output.glb
```

This also strips the `Rig|` prefix so Three.js clip names are clean
(`Idle`, `Walking_A`, ...), recomputes normals outward, and forces materials
to OPAQUE (see Material pitfall below).

## Step 3 — Verify the GLB

Run `scripts/glb_inspect.py output.glb` (stdlib-only) — prints clip count,
clip names, skins/meshes/images, material alphaMode, and root-bone scale
channels per clip. A correct character GLB has skins ≥ 1 and the expected
clip count. If clips == 1 and the name contains `T-Pose`, the NLA step was
skipped. If any clip's root scale ≠ 1.0, see the Meshy scale pitfall below.

## Step 4 — 2D image → animated GLB (rig transfer, fully automated, verified)

Full chain with zero manual steps and no external services:

1. `z_image` text-to-image: character in **strict T-pose**, 3/4 view, plain
   white background, full body, matte materials (3d-generation composition
   rules). T-pose matters — the donor skeleton's rest pose is T-pose.
2. `sam_3_3d` on that image → static textured GLB (no skins, no anims).
3. `scripts/rig_transfer.py` — borrows the skeleton + ALL animations from a
   rigged donor FBX (KayKit knight or any Mixamo rig):
   `blender -b -P scripts/rig_transfer.py -- target_static.glb donor.fbx out.glb`
   It scales/aligns the donor armature to the target's bbox, transfers skin
   weights, fixes normals, exports all clips via NLA tracks.

**Critical pitfalls baked into the script (do not regress):**
- `parent_set(type='ARMATURE_AUTO')` (bone heat) FAILS on image-to-3D meshes
  ("failed to find solution for one or more bones") — photogrammetry-style
  topology. Use **Data Transfer of vertex weights from the donor's body
  meshes** instead (`data_transfer`, `VGROUP_WEIGHTS`, `POLYINTERP_NEAREST`).
- `data_transfer` direction: with `use_reverse_transfer=False` it goes
  **ACTIVE → SELECTED** — the weight source must be the ACTIVE object. Getting
  this backwards silently produces 0 weighted verts (and `skins: 0` in the
  exported GLB). Always verify weighted-vert count > 0 before export.
- One donor (e.g. a one-time manual Mixamo session, or KayKit) animates
  unlimited generated characters — the donor is reusable.

Quality limits to state honestly: skinning quality depends on donor/target
proportion similarity; humanoid T-pose targets only; thin dangling parts
(capes, skirts) inherit approximate weights.

## Step 5 — Meshy clip merge + root-scale check (MANDATORY for Meshy)

Meshy returns one GLB per animation task (`action_id`). On the raw-API
fallback, `action_ids` returns up to 10 clips in one GLB instead
(`meshy-api.md` [3]); the rig's free walk/run still arrive as separate files.
Two merge options:

- **No Blender needed (preferred for Meshy outputs, VERIFIED on a live run
  2026-06-11):** `python3 scripts/glb_merge_anims.py rigged.glb walk.glb:Walk
  run.glb:Run idle.glb:Idle attack.glb:Attack out.glb` — stdlib-only, remaps
  clips by node NAME, applies the root-scale fix and OPAQUE patch
  automatically.
  A multi-clip input (an `action_ids` GLB) keeps its clip names:
  `python3 scripts/glb_merge_anims.py rigged.glb walk.glb:Walk run.glb:Run clips.glb out.glb`.
- Blender path (when the scene needs other edits anyway; single-clip inputs
  only, it keeps one action per file):
  `blender -b -P scripts/merge_anim_glbs.py -- rigged.glb idle.glb:Idle attack.glb:Attack out.glb`.

**Scale pitfall (verified bug):** Meshy *library* animations (via
`/animations`) can bake a scale factor into the root bone's scale channel
(observed: `Hips` scale 1.176 on `idle` while walk/run from the rig were 1.0)
— the character visibly "grows" when that clip plays. Fix after every merge:
check root-bone scale channels in all clips; if min/max ≠ 1.0, zero the scale
to 1.0 AND divide the same clip's root translation by the same factor
(otherwise the character floats). `merge_anim_glbs.py` does this
automatically; `glb_inspect.py` reports it.

## Material pitfall — alphaMode: BLEND masquerading as inverted normals

FBX import into Blender often sets materials to blend/transparent; the export
inherits it as glTF `alphaMode: BLEND`. In Three.js BLEND renders without
depth-write and sorts by object centers, so back faces (face, helmet
interior) draw ON TOP of front faces — visually identical to inverted
normals, but geometry is fine. Telltale difference: with BLEND you see
correctly-lit "innards"; with truly inverted normals the model is dark/black.

Fix layers (all baked into the scripts):
1. **Geometry**: `normals_make_consistent(inside=False)` on every mesh before
   export. Sanity check: mean dot(poly normal, poly center − mesh centroid)
   should be positive.
2. **Material**: force `alphaMode: OPAQUE` + `doubleSided: true`. Belt and
   suspenders: `scripts/glb_patch.py` (stdlib) patches the JSON chunk of any
   existing GLB directly — use it on files you didn't export yourself.
3. **Renderer side**: thin one-sided surfaces (capes, cloth planes) still look
   "inverted" from the back in Three.js — `material.side = THREE.DoubleSide`.
4. **Cache trap**: after re-exporting a fixed GLB to a deployed site, the CDN
   keeps serving the old file despite hard refresh — rename the asset
   (`knight_v2.glb`) instead of fighting the cache.

## Headless-browser limitation

The agent's controlled browser has **no WebGL** (`webglAvailable: false`) —
a deployed Three.js viewer renders as a blank white canvas in browser_vision
screenshots even when it works fine. Verify via DOM/console probes (button
count, mixer status text, fetch HEAD on the GLB) and ask the user to confirm
visuals in their own browser. Do not conclude "the site is broken" from a
white canvas screenshot.

## CC0 asset sources (no attribution, commercial OK)

- **KayKit Adventurers** — `git clone --depth 1 https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0.git`
  → `addons/kaykit_character_pack_adventures/Characters/gltf/*.glb` already
  contain all 76 clips (Knight, Mage, Rogue, Barbarian + Rogue_Hooded); the
  `Characters/fbx/` versions are the conversion test bed. Clips include Idle,
  Walking_A/B/C, Running_A/B, Jump_*, 1H/2H_Melee_Attack_*, Spellcast_*,
  Block*, Death_A/B, Dodge_*, Hit_*, Sit_*, Cheer, Interact, PickUp, Throw.
- **Quaternius** (quaternius.com) — low-poly animated characters, CC0.
- **Kenney** (kenney.nl/assets) — game kits, CC0.

## Delivery pitfalls

- `higgsfield upload create` REJECTS `.glb` ("Invalid or blocked file extension") —
  zip it first, upload the `.zip`.
- In Three.js consume via `GLTFLoader` + `AnimationMixer`;
  `mixer.clipAction(THREE.AnimationClip.findByName(gltf.animations, 'Idle'))`.
- Cross-fade clips: `next.reset().fadeIn(0.25).play(); prev.fadeOut(0.25)`.
- **Disk overflow (happened once):** portable Blender (~1.5 GB unpacked) +
  multi-GLB batches can fill the sandbox disk; the system may wipe and
  recreate the whole workspace mid-task. Mirror deliverables early (deployed
  site folder, uploaded zips, CDN links) and clean up tarballs/intermediates
  as you go — losing the workspace must not lose the assets.

## Support files

- `scripts/fbx2glb.py` — Blender CLI converter preserving all clips (NLA tracks, normals fix, OPAQUE).
- `scripts/glb_inspect.py` — stdlib GLB inspector: clips, skins, alphaMode, root-scale channels.
- `scripts/glb_patch.py` — stdlib JSON-chunk patcher: force OPAQUE/doubleSided on any GLB.
- `scripts/rig_transfer.py` — static GLB + rigged donor FBX → animated GLB (Step 4).
- `scripts/glb_merge_anims.py` — stdlib merger of single-clip GLBs (Meshy outputs) + root-scale fix, no Blender (Step 5, verified live).
- `scripts/merge_anim_glbs.py` — same merge via Blender CLI (when Blender is already in play).
- `scripts/proc_rig_dragon.py` — procedural skeleton from bbox analysis (non-humanoids).
- `scripts/proc_weights.py` — distance-based skin weights (ARMATURE_AUTO is broken headless).
- `scripts/proc_anim_dragon.py` — sine-based idle/fly clips baked to keyframes.
- `meshy-api.md` — verified Meshy API pipeline: image→3D→rig→animations, endpoints, action_id catalog, stuck-refine recovery, costs.
- `meshy-input-rules.md` — MANDATORY pre-submit rules: input-image validation (character sheets MUST be cropped to one figure or split into multi-image views; pose_mode), polygon-budget paths (Smart Topology `meshy-t2.5` vs remesh `target_polycount`; deprecated `model_type: lowpoly` returns 400 from 2026-11-30), polycount budgets per asset class, payload templates. Read BEFORE building any Meshy request.
- `procedural-animation.md` — non-humanoid branch: skeleton/weights/clip recipes per creature type, vision-QC loop, phase-sampling pitfall.
