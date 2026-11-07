# Sung children's video

Use this mode for an explicitly requested sung kids song or music video. A background-music request alone does not select it. Validate the original requested duration before all paid generation; only 60 or 120 seconds is supported. Ask for an explicit supported choice if another duration was requested. Never replace a song with narration or silently shorten it. The song is the only voice and music track. Captioning singing is not supported by this workflow; if captions are required, explain that before generation.

```bash
python3 "$SKILL_DIR/scripts/validate_song_prompt.py" --duration-seconds "$REQUESTED_SECONDS" --duration-only
```

Write lyrics in the requested language, using verse and a repeating chorus. Keep the prompt under 2048 characters. State a single steady 100 or 112 BPM, 4/4, no tempo changes, eight-syllable lines, one syllable per beat, each line starting on beat one, four-bar phrases, and a verbatim repeating chorus. Validate the actual prompt before submission:

```bash
python3 "$SKILL_DIR/scripts/validate_song_prompt.py" --duration-seconds "$REQUESTED_SECONDS" --prompt song_prompt.txt --lyrics-language "$LANGUAGE_CODE"
```

The meter counter supports English and Russian; for another language it reports that manual meter review is required. Check the lyrics in that language before submission. Generate the song first with `higgsfield generate create seed_audio --prompt "$(cat song_prompt.txt)" --wait --json`; omit voice ID and voice type. Check the returned track is within three seconds of the requested length. Make at most three generation attempts in total, including the initial request and any failed jobs; after the third failure or wrong-length result, stop. Change the prompt for each retry. Do not stretch, concatenate or substitute a different duration.

Build six or twelve 10-second scene blocks matching the song's lyrics and repeated chorus. Keep visual style and characters consistent, show the named action, and avoid lip-sync. Inspect the first generated clip before submitting the rest. Save the actual completed clips in `clips.txt`, one local path per line in chronological order. Assemble with one song and no extra music bed:

```bash
bash "$SKILL_DIR/scripts/assemble_final.sh" --out final.mp4 --blocks "$BLOCKS" \
  --manifest clips.txt --song song.wav
```

The script checks block count, song length, audio coverage and decode. Review the audio against the planned lyrics, repeating chorus and timing, and review the video against those lyrics before delivering it. Automatic speech recognition may help flag discrepancies but does not reliably verify singing; report any unverified wording or chorus rather than claiming they match. Do not ship a partial result if any gate fails.
