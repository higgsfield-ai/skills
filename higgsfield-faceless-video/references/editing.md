# Edit a previously generated video

Use this path when the user supplies a prior faceless video and requests changes to specific 10-second ranges. Preserve the source and all unselected ranges. Save the original file and measured duration. Resolve the requested ranges and edits before generation; ranges must be ordered, non-overlapping, aligned to 10 seconds and exactly 10 seconds long.

Generate only the requested replacement video and audio or a complete replacement clip. Check every replacement before assembly. Prepare an ordered `patches.json`, for example:

```json
[{"start_seconds":10,"end_seconds":20,"patch_video":"patch-001.mp4"}]
```

For separate video and audio use `{"start_seconds":10,"end_seconds":20,"parts":[{"video":"clip.mp4","audio":"voice.wav","seconds":10}]}`. Then run:

```bash
bash "$SKILL_DIR/scripts/assemble_partial_edit.sh" --source source.mp4 \
  --source-seconds "$ACTUAL_SOURCE_SECONDS" --requested-seconds "$REQUESTED_SECONDS" \
  --manifest patches.json --out edited.mp4
```

The script validates ranges and produces a full-length review draft and receipt. Verify duration, decode, edited ranges and unchanged surrounding content. Present the result as a draft; do not publish it automatically. If any patch fails, keep the original and report the failure instead of shipping a partial edit.
