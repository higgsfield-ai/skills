# Channel-style motion

Use for a requested fast-cut channel episode, documentary, story or children's narration. For a one-off diagram-led explainer, use `references/production.md`. Preserve the exact requested duration; for a short or non-multiple-of-ten request, use the exact-duration assembly in `references/production.md` rather than rounding. For an explicitly sung children's video, use `references/song.md`.

For a standard run of at least three 10-second blocks, develop a continuous visual identity and a roster of reference assets. Create an ordered `script.json` with `genre` (`education`, `history`, `kids`, or `storytelling`), `cast` (`[{"name":"...","asset":"..."}]` or `[]`), source URLs for factual work, and a `through_line` object with `name`, `asset`, `progression` and `resolution`. Add an `arc` object naming block numbers for `hook`, `build` (array), `turn`, and `payoff`. Each numbered block contains `arc_role`, authored `vo_line`, `location`, `through_line_state`, `assets_used`, and `shots`. Use five varied shot descriptions per block, or four for kids; start every shot with a size such as `WIDE:`, `MEDIUM:`, `CU:` or `DETAIL:` and alternate sizes. Include the through-line asset in each block; carry named characters' reference assets with every scene that names them.

Write natural spoken lines, approximately 20–23 words per full block (17–21 for kids), without delivery tags or timecodes inside `vo_line`. Run the script gate before generating paid assets:

```bash
python3 "$SKILL_DIR/scripts/validate_motion_script.py" --script script.json --duration-seconds "$REQUESTED_SECONDS"
```

Repair reported errors and rerun until it passes. The generated `script.lock` ties the assembly to the authored narration; revalidate after changing a line. Inspect the live schema for `elevenlabs_v4`, select a voice and voice type, and save one ordered dialogue entry per block to JSON. For example, each file contains `[{"text":"<block narration>","voice_id":"<selected id>","voice_type":"preset"}]`; submit `higgsfield generate create elevenlabs_v4 --dialogue @dialogue01.json --wait --json`. Save each completed result as `voice01.wav`, `voice02.wav`, and so on. Use the selected type from the voice list rather than assuming `preset`.

Before video generation, measure the actual narration against the script. For talking characters, first generate and verify the dialogue clips and extract their audio as described in `references/talking-characters.md`; measure those and the narration takes together before generating the remaining clips:

```bash
python3 "$SKILL_DIR/scripts/measure_narration_takes.py" --script script.json --voice-dir voices
```

Rewrite and retry only the failing lines. Speech must meet the reported timing and rate gates. A take in the 7.2–7.8s soft window can be accepted only after one retry and must be explicitly named with `--accept-soft-blocks` to both measurement and assembly. Never adjust playback speed. Stop after three attempts per line if it still fails.

Generate 10-second motion blocks from the approved plan and its referenced assets. Verify the first completed clip's style and characters, then generate the remaining clips and inspect each. Save an ordered `pairs.txt`, one `clipNN.mp4 voiceNN.wav` pair per line. Assemble the validated script:

```bash
bash "$SKILL_DIR/scripts/assemble_final.sh" --out final.mp4 --blocks "$BLOCKS" \
  --manifest pairs.txt --script script.json
```

Add a user-requested music file with `--music`; follow `references/captions.md` for requested subtitles. Check output duration, audio, picture order and readability. Never mark a failed gate or missing block as a finished video.

For explicitly requested talking characters, also follow `references/talking-characters.md`; dialogue is the original synchronized clip audio, not a second narration take.
