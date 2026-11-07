# Captions

Before any paid generation, verify that Python can import `faster_whisper`, a compatible transcription model is already available as a local directory, and `ffmpeg -filters` lists `subtitles`. Do not silently install dependencies or download a model. If any prerequisite is missing, explain the limitation and let the user decide whether to proceed without subtitles.

Keep clean voice files and a `script_manifest.json` with one ordered `{ "vo_line": "..." }` per spoken block (omit a silent visual-only tail) in a `blocks` array. After assembly, use the receipt to align authored text to the clean takes. Pass the user's narration language and the local model directory:

```bash
python3 "$SKILL_DIR/scripts/audio_to_captions.py" final.mp4 \
  --per-block final.mp4.assembly.json --voice-dir . \
  --script script_manifest.json --language en --model "$LOCAL_MODEL_DIR" \
  --max-words 4 --max-chars 42 --min-duration 0.4 --max-cps 30 --srt captions.srt
bash "$SKILL_DIR/scripts/burn_captions.sh" --in final.mp4 \
  --srt captions.srt --out final_captioned.mp4 --no-caps
```

Never present captions from a failed alignment as successful. Inspect the rendered video for readability, exact wording and synchronization, and rerun decoding and duration checks on the final captioned file. Do not send audio to an external transcription provider.
