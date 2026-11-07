---
name: higgsfield-faceless-video
description: |
  Create a finished faceless explainer, documentary, illustrated story or children's music video, or edit a previously created faceless video. Use when: "make a faceless video", "create a narrated explainer", "make a children's song video", "edit this faceless video". NOT for: a single silent clip, ads or UGC, unrelated footage edits, or script-only requests.
metadata:
  version: "0.14.0"
  argument-hint: "[topic or source] [duration] [language] [aspect ratio]"
allowed-tools: Bash
---

# Faceless video

Create one finished video with a consistent visual style and narration. For an illustrated explainer use deliberate, diagram-led scenes; for a story or documentary adapt the pacing and visuals to the brief. Do not treat an explainer as a request for rapid cuts. Preserve choices and assets supplied by the user.

Choose the requested mode before generating: illustrated explainers use `references/production.md`; fast-cut channel motion uses `references/channel-motion.md`; stills and picture stories use `references/picture-story.md`; a sung children's music video uses `references/song.md`; explicitly requested talking characters use `references/talking-characters.md`; a requested presenter overlay uses `references/presenter.md` alongside the motion workflow; edits to a previously generated video use `references/editing.md`. A request for background music alone is not a song request. Never infer a presenter from an incidental photo.

When the brief supplies `animation_mode`, treat `fully_animated` as motion and `scene_based` as stills without asking again. Resolve song intent from the complete brief, including topic and script; an explicitly sung children's video uses song mode even when a voice is supplied. Preserve the production mode when continuing or editing an existing video.

## Before spending credits

Resolve missing topic, approximate duration, aspect ratio, language, visual style, voice, music and subtitle choices. Never invent a preset or voice ID. Use `higgsfield preset list video-explainer --json` and `higgsfield voices list --json` for current choices, and resolve a selected preset with `higgsfield preset resolve video-explainer <id> --json`. Confirm photo roles before using reference images. Honor the requested duration; never silently round it up.

Find this skill's installed directory and retain its absolute path as `SKILL_DIR`. Keep all work in a persistent session directory, not the skill directory. Before generation verify `higgsfield account status`, `ffmpeg`, `ffprobe`, `python3`, `curl`, and `awk`, and inspect the live schemas using `higgsfield model get` for each planned model. Estimate generation costs with `higgsfield generate cost` where supported; if an estimate is unavailable, disclose that before generation. If any required stage, model, dependency, or requested feature is unavailable, explain and stop before paid work. Do not call `explainer_video` or `video_explainer`.

Read `references/production.md` for the generation, assembly, QC, recovery and delivery procedure. For subtitles, read `references/captions.md` and check its dependencies before paid generation. Read `references/creative.md` for style, assets, long-form planning and review, `references/styles.md` for style guidance, and `references/prompts.md` when writing the scene plan. The executable helper `scripts/assemble_blocks.sh` assembles ordered video/audio pairs without changing speech speed; read its usage before running it. The previous skill name is supported for existing installations.
