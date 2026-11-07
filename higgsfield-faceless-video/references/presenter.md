# Optional presenter overlay

Only use a real person's photo when the user explicitly requests a presenter and is authorized to use that photo. Collect the image, selected voice, placement and style (bottom cutout, circular badge or full-frame cameo). An incidental reference image is not a presenter request. Before paid work verify `ffmpeg`, `ffprobe`, Python `numpy` and `PIL`, the required video filters, and current schemas for `gpt_image_2_5`, `gemini_omni_flash_1_1` and `voice_change`. Stop if a required operation is unavailable.

Generate a clean, uniformly green background version of the photo, preserving the person's appearance. Inspect it. Generate one 10-second talking clip per planned block, using that prepared image as the reference and the exact block narration as spoken dialogue. For a full block start with a concise line and measure the actual speech: it must finish within the assembly window. Rewrite a failing line and retry within the normal three-attempt limit; never speed up speech. Inspect the first result and check each talking clip's words and timing. Revoice each completed talking clip to the selected voice using `higgsfield generate workflow voice_change --video <completed_job_id> --voice-id <id> --voice-type <type> --wait --json`; do not also generate separate narration for the same block.

For each clip, check and remove a frozen opening with the prepared reference image, then composite it on the matching background clip:

```bash
bash "$SKILL_DIR/scripts/trim_static_head.sh" talk.mp4 talk_trimmed.mp4 presenter_reference.png
bash "$SKILL_DIR/scripts/presenter_composite.sh" background.mp4 talk_trimmed.mp4 presenter_block.mp4 --style cutout --pos br
```

A frozen clip, failed matte, missing extracted voice or failed QC receipt blocks delivery. Review the person's identity, the key, lip sync, and legibility. Use the script's extracted `_voice.wav` with its matching composite for assembly. If requested, also assemble a clean version without the overlay using the same voice takes. Do not claim identity or lip-sync verification from a technical receipt alone.
