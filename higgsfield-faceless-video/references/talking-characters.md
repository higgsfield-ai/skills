# Talking characters in a children's video

Use only when the user explicitly requests characters speaking in a narrated children's video. It is separate from a sung music video and from a photo-presenter overlay. Preserve the same character references, style and story continuity throughout.

In the channel script, set `talking_characters` to `true`. Alternate narration on odd blocks with dialogue on even blocks. Set each block's `block_kind` accordingly. Narration blocks have no on-screen speakers; dialogue blocks name one or two characters in `speakers`, each with one short turn. Write the dialogue as part of the story: each exchange follows from the previous scene and leads into the next. The normal channel script validator checks the block types, speakers and dialogue length.

Create narration takes for narration blocks as described in `references/channel-motion.md`. For a dialogue block, generate a matching video with the exact dialogue and the character reference, explicitly requesting audible synchronized speech. Verify that the returned clip has audio, that it says the intended words and that the mouth motion matches. Extract its original audio without shifting it:

```bash
ffmpeg -v error -y -i clip02.mp4 -vn -c:a pcm_s16le voice02.wav
```

Use these audio files in the numbered voice ledger and run the narration measurement. Pass the same validated script to `assemble_final.sh`. Dialogue blocks keep their original audio alignment and do not mix the clip audio a second time; narration blocks follow the normal narration pipeline. Review the assembled dialogue for synchronization and content. If the video model does not deliver usable dialogue or a gate fails, stop and report the failure; do not substitute silent clips or fabricate speech.
