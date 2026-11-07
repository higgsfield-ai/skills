#!/usr/bin/env bash
# Usage: assemble_final.sh --out final.mp4 --blocks N --manifest clips.txt --song song.wav
set -euo pipefail

OUT="final.mp4"; CLIP=10; MUSIC=""; MVOL="0.10"; SFXVOL="0.12"; SFXSET=0; BLOCKS=""; MANIFEST=""; ALLOWMM=0; SONG=""; STEPPED=""; SCRIPT=""; SOFT_BLOCKS=""; ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --clip-seconds) CLIP="$2"; shift 2 ;;
    --stepped) STEPPED="$2"; shift 2 ;;
    --song) SONG="$2"; shift 2 ;;
    --music) MUSIC="$2"; shift 2 ;;
    --music-vol) MVOL="$2"; shift 2 ;;
    --sfx-vol) SFXVOL="$2"; SFXSET=1; shift 2 ;;
    --blocks) BLOCKS="$2"; shift 2 ;;
    --manifest) MANIFEST="$2"; shift 2 ;;
    --script) SCRIPT="$2"; shift 2 ;;
    --accept-soft-blocks) SOFT_BLOCKS="$2"; shift 2 ;;
    --subs) echo "ERROR: --subs was removed. Assemble first, then follow the bundled captions instructions using the clean voice takes and assembly receipt." >&2; exit 2 ;;
    --allow-mismatch) ALLOWMM=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
[[ -z "$SOFT_BLOCKS" || "$SOFT_BLOCKS" =~ ^[1-9][0-9]*(,[1-9][0-9]*)*$ ]] || { echo "ERROR: --accept-soft-blocks requires comma-separated block numbers" >&2; exit 1; }
if [[ -n "$MANIFEST" ]]; then
  [[ -f "$MANIFEST" ]] || { echo "ERROR: --manifest not found: $MANIFEST" >&2; exit 1; }
  while read -r mc mv _extra; do
    [[ -z "$mc" || "$mc" == \#* ]] && continue
    if [[ -n "$SONG" ]]; then
      [[ -n "$mv" ]] && { echo "ERROR: --song manifest lines carry ONE clip each (no voice files): '$mc $mv'" >&2; exit 1; }
      ARGS+=("$mc")
    else
      [[ -n "$mv" ]] || { echo "ERROR: manifest line has no voice file: '$mc'" >&2; exit 1; }
      ARGS+=("$mc" "$mv")
    fi
  done < "$MANIFEST"
fi
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK=""
if [[ -n "$SCRIPT" ]]; then
  LOCK="$(dirname "$SCRIPT")/script.lock"
  [[ -f "$LOCK" ]] || { echo "ERROR: no script lock at $LOCK; validate the script before assembly." >&2; exit 1; }
elif [[ -f script.lock ]]; then
  LOCK="script.lock"
fi
if [[ -n "$LOCK" && -f "$LOCK" ]]; then
  [[ -n "$SCRIPT" ]] || { echo "ERROR: $LOCK exists but --script was not passed. The assembler checks the narration against the locked script — pass --script <script_manifest.json>." >&2; exit 1; }
  [[ -f "$SCRIPT" ]] || { echo "ERROR: --script not found: $SCRIPT" >&2; exit 1; }
  python3 "$SELF_DIR/validate_motion_script.py" --script "$SCRIPT" \
    --duration-seconds "$(awk -v b="${BLOCKS:-1}" -v c="$CLIP" 'BEGIN{print (b*c>0? b*c : 10)}')" \
    --lock "$LOCK" --verify-lock >&2 || {
      echo "ERROR: the narration no longer matches $LOCK — a line changed after SCRIPT LOCK. A line changes ONLY by rewriting it and re-running validate_motion_script.py; appending or reusing text to reach a length is never allowed. Re-validate, regenerate the takes for the changed blocks, then assemble." >&2; exit 1; }
fi
if [[ -n "$SONG" ]]; then
  [[ -f "$SONG" ]] || { echo "ERROR: --song file not found: $SONG" >&2; exit 1; }
  [[ -n "$MUSIC" ]] && { echo "ERROR: --song and --music are mutually exclusive (the song IS the music)." >&2; exit 1; }
  [[ "$SFXSET" == "0" ]] && SFXVOL="0.06"
fi
MVOL="$(awk -v v="$MVOL" 'BEGIN{v=v+0; if(v<0)v=0; if(v>0.2){print "WARN: --music-vol clamped to 0.20 (voice stays 1.0)" > "/dev/stderr"; v=0.2} printf "%.3f", v}')"
bed_gain_db() {
  local vmean bmean trim
  vmean="$(ffmpeg -hide_banner -i "$1" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1)"
  bmean="$(ffmpeg -hide_banner -i "$2" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1)"
  awk -v v="${vmean:--20}" -v b="${bmean:--20}" -v mv="$3" 'BEGIN{
    trim = 20*log(mv/0.10)/log(10);
    g = (v - 14) - b + trim;
    if (g > 0) g = 0; if (g < -40) g = -40;
    printf "%.2f", g }'
}
sfx_gain_db() { # $1 = normalised voice file, $2 = clip, $3 = --sfx-vol
  local vmean cmean
  vmean="$(ffmpeg -hide_banner -i "$1" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1)"
  cmean="$(ffmpeg -hide_banner -i "$2" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1)"
  awk -v v="${vmean:--20}" -v c="${cmean:--60}" -v sv="$3" 'BEGIN{
    trim = 20*log(sv/0.12)/log(10);
    g = (v - 18) - c + trim;
    if (g > 10) g = 10; if (g < -40) g = -40;
    printf "%.2f", g }'
}

SFXVOL="$(awk -v v="$SFXVOL" 'BEGIN{v=v+0; if(v<0)v=0; if(v>0.2){print "WARN: --sfx-vol clamped to 0.20 (voice stays 1.0)" > "/dev/stderr"; v=0.2} printf "%.3f", v}')"
for b in ffmpeg ffprobe awk; do command -v "$b" >/dev/null 2>&1 || { echo "ERROR: '$b' not found" >&2; exit 1; }; done
STEPPRE=""
if [[ -n "$STEPPED" ]]; then
  awk -v s="$STEPPED" 'BEGIN{exit (s+0>=2 && s+0<=30)?0:1}' || { echo "ERROR: --stepped must be an fps between 2 and 30 (e.g. 12 for on-twos)." >&2; exit 1; }
  STEPPRE="fps=${STEPPED},"
  echo "  --stepped ${STEPPED}: on-twos cadence (image updates ${STEPPED}x/sec)" >&2
fi
n=${#ARGS[@]}
if [[ -n "$SONG" ]]; then
  (( n >= 1 )) || { echo "ERROR: pass CLIPS (one per block) or --manifest in --song mode" >&2; exit 1; }
  pairs=$n
else
  (( n >= 2 && n % 2 == 0 )) || { echo "ERROR: pass clip/voice PAIRS: clip1 voice1 clip2 voice2 ..." >&2; exit 1; }
  pairs=$(( n / 2 ))
fi
if [[ -n "$BLOCKS" ]] && (( pairs != BLOCKS )); then
  echo "ERROR: --blocks $BLOCKS declared but $pairs pairs supplied — a missing/extra block. Fix the manifest; do NOT assemble a partial video." >&2; exit 1
fi
[[ -z "$BLOCKS" ]] && { echo "ERROR: --blocks N is REQUIRED — pass the expected pair count (a dropped pair must FAIL, not ship; this is not optional on short runs either)." >&2; exit 1; }
[[ -n "$MUSIC" && ! -f "$MUSIC" ]] && { echo "ERROR: --music file not found: $MUSIC" >&2; exit 1; }
if [[ -n "$SONG" ]]; then
  SDUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SONG")"
  awk -v s="$SDUR" -v e="$(( pairs * CLIP ))" 'BEGIN{x=s-e; if(x<0)x=-x; exit (x<=3)?0:1}' || {
    echo "ERROR: --song is ${SDUR}s but the video is $(( pairs * CLIP ))s (N x ${CLIP}) — regenerate the song at the target length (or fix N); do NOT trim either side." >&2; exit 1; }
fi

FINAL_OUT="$OUT"
ASSEMBLY_ATTEMPT=1
TMP="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT
OUT="$TMP/final-candidate.mp4"
PBJSON=()   # per-block sidecar entries (machine-readable assembly manifest)
c0="${ARGS[0]}"
DIMS="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$c0")"
W="${DIMS%%,*}"; H="${DIMS##*,}"
FPS_RAW="$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$c0")"
FPS="$(awk -F/ '{ if(NF==2 && $2>0) printf "%.4f",$1/$2; else print $1 }' <<< "$FPS_RAW")"; [ -z "$FPS" ] && FPS=30
echo "[1/3] ${pairs} blocks -> ${W}x${H} @ ${FPS}fps, fixed ${CLIP}s each; speech-centered, no atempo" >&2

LIST="$TMP/list.txt"; : > "$LIST"
VOLIST="$TMP/volist.txt"; : > "$VOLIST"
for ((i=0;i<pairs;i++)); do
  if [[ -n "$SONG" ]]; then
    clip="${ARGS[i]}"; voice=""
  else
    clip="${ARGS[i*2]}"; voice="${ARGS[i*2+1]}"; original_voice="$voice"
  fi
  [[ -f "$clip"  ]] || { echo "ERROR: clip not found: $clip" >&2; exit 1; }
  [[ -z "$SONG" && ! -f "$voice" ]] && { echo "ERROR: voice not found: $voice" >&2; exit 1; }
  if [[ -n "$SONG" ]]; then
    D="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")"
    awk -v d="$D" -v c="$CLIP" 'BEGIN{exit (d < c-0.5) ? 0 : 1}' && {
      echo "ERROR: clip $((i+1)) ($clip) is only ${D}s (<${CLIP}s) — REGENERATE the block." >&2; exit 1; }
    FRZH="$(ffmpeg -v info -t 1.5 -i "$clip" -vf "freezedetect=n=-60dB:d=1.0" -an -f null - 2>&1 | grep -c freeze_start || true)"
    [[ "$FRZH" != "0" ]] && echo "WARN: clip $((i+1)) ($clip) opens on ~static frames — regenerate this block (rule 21)." >&2
    FRZT="$(ffmpeg -v info -sseof -2 -i "$clip" -vf "freezedetect=n=-60dB:d=1.2" -an -f null - 2>&1 | grep -c freeze_start || true)"
    [[ "$FRZT" != "0" ]] && echo "WARN: clip $((i+1)) ($clip) ends on ~static frames (frozen tail) — consider regenerating." >&2
    out="$TMP/b_$(printf '%03d' "$i").mp4"
    HASAUD="$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$clip" | head -1)"
    if [[ "$HASAUD" == "audio" && "$SFXVOL" != "0.000" ]]; then
      FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,${STEPPRE}fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP}[v];[0:a]volume=${SFXVOL},apad[a]"
      ffmpeg -y -loglevel error -i "$clip" -filter_complex "$FC" \
        -map "[v]" -map "[a]" -t "$CLIP" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k "$out"
    else
      FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,${STEPPRE}fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP}[v]"
      ffmpeg -y -loglevel error -i "$clip" -f lavfi -t "$CLIP" -i "anullsrc=r=44100:cl=stereo" -filter_complex "$FC" \
        -map "[v]" -map 1:a -t "$CLIP" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k "$out"
    fi
    echo "file '$out'" >> "$LIST"
    printf '  block %02d: clip %.2fs (song mode, sfx %.2f)\n' "$((i+1))" "$D" "$SFXVOL" >&2
    PBJSON[i]="$(printf '{"n":%d,"clip":"%s","voice":"","clip_s":%.2f,"speech_s":0,"speech_abs_s":0,"lead_silence_s":0,"internal_pauses":0,"freeze_head":%s,"freeze_tail":%s}' \
      "$((i+1))" "$(basename "$clip")" "$D" \
      "$([[ "${FRZH:-0}" != "0" ]] && echo true || echo false)" "$([[ "${FRZT:-0}" != "0" ]] && echo true || echo false)")"
    continue
  fi
  cn="$(basename "$clip"  | sed 's/\.[^.]*$//' | grep -Eo '[0-9]+' | tail -1 || true)"
  vn="$(basename "$voice" | sed 's/\.[^.]*$//' | grep -Eo '[0-9]+' | tail -1 || true)"
  if [[ -n "$cn" && -n "$vn" ]] && (( 10#$cn != 10#$vn )); then
    if [[ "$ALLOWMM" == "1" ]]; then
      echo "WARN: pair $((i+1)) mixes numbers: $(basename "$clip") + $(basename "$voice") (--allow-mismatch)." >&2
    else
      echo "ERROR: pair $((i+1)) mixes numbers: $(basename "$clip") + $(basename "$voice") — the audio would land on the WRONG block. Fix the manifest order (or pass --allow-mismatch only if the files are truly unnumbered)." >&2
      exit 1
    fi
  fi
  A="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$voice")"
  D="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")"
  EVENTS="$(ffmpeg -i "$voice" -af silencedetect=noise=-45dB:d=0.25 -f null - 2>&1 | grep -Eo 'silence_(start|end): *-?[0-9.]+' || true)"
  read -r SS SE <<< "$(awk -v A="$A" '
    /silence_start/ { s=$NF+0; if(first==""){first=s}; last=s; open=1; next }
    /silence_end/   { e=$NF+0; if(first!="" && first<0.1 && ssdone==""){ss=e; ssdone=1};
                      e_last=e; s_before=last; open=0 }
    END {
      if (open==1)                      se=last;        # file ended inside silence
      else if (e_last>0 && A-e_last<0.2) se=s_before;   # EOF auto-closed the tail silence
      else                               se=A;          # speech runs to the end
      printf "%.3f %.3f", ss+0, se+0 }' <<< "$EVENTS")"
  [[ -z "${SS:-}" ]] && SS=0; [[ -z "${SE:-}" ]] && SE="$A"
  SPEECH="$(awk -v a="$SS" -v b="$SE" 'BEGIN{d=b-a; if(d<=0)d=0; printf "%.3f", d}')"
  awk -v s="$SPEECH" 'BEGIN{exit (s<0.3)?0:1}' && { SS=0; SE="$A"; SPEECH="$A"; }
  read -r IPN IPMAX <<< "$(awk -v lo="$SS" -v hi="$SE" '
    /silence_start/ { s=$NF+0; open=1; next }
    /silence_end/   { e=$NF+0; if(open==1 && s>lo+0.1 && e<hi-0.1 && e-s>=0.8){n++; if(e-s>mx)mx=e-s}; open=0 }
    END{ printf "%d %.2f", n+0, mx+0 }' <<< "$EVENTS")"
  [[ "${IPN:-0}" != "0" ]] && echo "WARN: voice $((i+1)) ($voice) has ${IPN} internal pause(s) >=0.8s (longest ${IPMAX}s) — pausey take: rewrite the line as ONE flowing clause (fewer full stops) and regenerate." >&2
  SPEECH_MIN="$(awk -v c="$CLIP" 'BEGIN{printf "%.3f", c-2.8}')"
  SPEECH_TARGET_MIN="$(awk -v c="$CLIP" 'BEGIN{printf "%.3f", c-2.2}')"
  SPEECH_MAX="$(awk -v c="$CLIP" 'BEGIN{printf "%.3f", c-0.5}')"
  awk -v s="$SPEECH" -v lo="$SPEECH_MIN" -v hi="$SPEECH_MAX" 'BEGIN{exit (s < lo || s > hi) ? 0 : 1}' && {
    echo "ERROR: voice $((i+1)) ($voice) carries ${SPEECH}s of speech; required ${SPEECH_MIN}–${SPEECH_MAX}s. Fix it by CHANGING THE WORDS OF THAT ONE LINE and regenerating that take: too long — cut modifiers, keep the facts; too short — add one more FACT. Forbidden: appending a sentence or clause to the line, reusing a sentence from another block, atempo, trimming speech, or touching any other block. Then re-run validate_motion_script.py (it rewrites script.lock) before assembling again." >&2; exit 1; }
  if awk -v s="$SPEECH" -v target="$SPEECH_TARGET_MIN" 'BEGIN{exit (s < target) ? 0 : 1}'; then
    case ",$SOFT_BLOCKS," in
      *,"$((i+1))",*) echo "WARN: accepted retried voice $((i+1)) in the soft band at ${SPEECH}s." >&2 ;;
      *) echo "ERROR: voice $((i+1)) is in the soft band at ${SPEECH}s; retry it and explicitly accept the block if needed." >&2; exit 1 ;;
    esac
  fi
  awk -v d="$D" -v c="$CLIP" 'BEGIN{exit (d < c-0.5) ? 0 : 1}' && {
    echo "ERROR: clip $((i+1)) ($clip) is only ${D}s (<${CLIP}s) — REGENERATE the block; a held still frame is not a scene." >&2; exit 1; }
  FRZH="$(ffmpeg -v info -t 1.5 -i "$clip" -vf "freezedetect=n=-60dB:d=1.0" -an -f null - 2>&1 | grep -c freeze_start || true)"
  [[ "$FRZH" != "0" ]] && echo "WARN: clip $((i+1)) ($clip) opens on ~static frames — regenerate this block (rule 21)." >&2
  FRZT="$(ffmpeg -v info -sseof -2 -i "$clip" -vf "freezedetect=n=-60dB:d=1.2" -an -f null - 2>&1 | grep -c freeze_start || true)"
  [[ "$FRZT" != "0" ]] && echo "WARN: clip $((i+1)) ($clip) ends on ~static frames (frozen tail) — consider regenerating." >&2
  VN="$TMP/v_$(printf '%03d' "$i").wav"
  PREMEAN="$(ffmpeg -hide_banner -i "$voice" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1 || true)"
  if ffmpeg -y -loglevel error -i "$voice" -af "loudnorm=I=-19:TP=-1.5:LRA=11" -ar 48000 -ac 2 "$VN" 2>/dev/null; then
    POSTMEAN="$(ffmpeg -hide_banner -i "$VN" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1 || true)"
    printf '  block %02d: voice level %s dB -> %s dB (matched)\n' "$((i+1))" "${PREMEAN:-?}" "${POSTMEAN:-?}" >&2
    voice="$VN"
  else
    echo "WARN: could not level-match $voice — mixing it as-is; block loudness may differ from its neighbours." >&2
  fi
  BLOCK_KIND="narration"
  if [[ -n "$SCRIPT" ]]; then
    BLOCK_KIND="$(python3 - "$SCRIPT" "$i" <<'PYCODE'
import json, sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
blocks = payload.get("blocks", [])
index = int(sys.argv[2])
if payload.get("talking_characters") is True:
    if index >= len(blocks) or blocks[index].get("block_kind") not in ("narration", "dialogue"):
        raise SystemExit("invalid talking-character block")
    print(blocks[index]["block_kind"])
else:
    print("narration")
PYCODE
)"
  fi
  HEAD_GUARD=0.5
  read -r PAD_MS TRIM_S <<< "$(awk -v ss="$SS" -v sp="$SPEECH" -v c="$CLIP" -v hg="$HEAD_GUARD" 'BEGIN{
    t0=(c-sp)/2; if(t0<0)t0=0;          # centre the speech
    pad=t0-ss; if(pad<0)pad=0;
    trim=ss-t0; if(trim<0)trim=0;
    lim=ss-hg; if(lim<0)lim=0;          # keep hg seconds of real audio ahead of the cut
    if(trim>lim)trim=lim;
    printf "%d %.3f", pad*1000, trim }')"
  if [[ "$BLOCK_KIND" == "dialogue" ]]; then
    PAD_MS=0
    TRIM_S=0
  fi
  awk -v d="$TRIM_S" 'BEGIN{exit (d>0.001)?0:1}' && \
    echo "  block $((i+1)): trimming ${TRIM_S}s of the take's own leading silence so the speech fits the window" >&2
  out="$TMP/b_$(printf '%03d' "$i").mp4"
  HASAUD="$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$clip" | head -1)"
  if [[ "$HASAUD" == "audio" && "$SFXVOL" != "0.000" && "$BLOCK_KIND" != "dialogue" ]]; then
    SFXG="$(sfx_gain_db "$voice" "$clip" "$SFXVOL")"
    printf '  block %02d: clip SFX %s dB under the mix\n' "$((i+1))" "$SFXG" >&2
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,${STEPPRE}fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP}[v];[1:a]atrim=start=${TRIM_S},asetpts=PTS-STARTPTS,adelay=${PAD_MS}:all=1,apad[vo];[0:a]volume=${SFXG}dB,apad[sfx];[sfx][vo]amix=inputs=2:duration=first:normalize=0[a]"
  else
    if [[ "$HASAUD" == "audio" ]]; then
      printf '  block %02d: clip SFX muted (excluded from mix)\n' "$((i+1))" >&2
    else
      echo "WARN: clip $((i+1)) ($clip) has NO audio stream — block goes in voice-only, its background sound is lost. Re-download or regenerate the block." >&2
    fi
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,${STEPPRE}fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP}[v];[1:a]atrim=start=${TRIM_S},asetpts=PTS-STARTPTS,adelay=${PAD_MS}:all=1,apad[a]"
  fi
  ffmpeg -y -loglevel error -i "$clip" -i "$voice" \
    -filter_complex "$FC" \
    -map "[v]" -map "[a]" -t "$CLIP" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k "$out"
  echo "file '$out'" >> "$LIST"
  vout="$TMP/vo_$(printf '%03d' "$i").wav"
  ffmpeg -y -loglevel error -i "$voice" \
    -af "atrim=start=${TRIM_S},asetpts=PTS-STARTPTS,adelay=${PAD_MS}:all=1,apad" \
    -t "$CLIP" -ar 48000 -ac 2 "$vout"
  echo "file '$vout'" >> "$VOLIST"
  MIXMEAN="$(ffmpeg -hide_banner -i "$out" -vn -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1 || true)"
  VOMEAN="$(ffmpeg -hide_banner -i "$vout" -af volumedetect -f null - 2>&1 | grep -Eo 'mean_volume: *-?[0-9.]+' | grep -Eo '\-?[0-9.]+' | head -1 || true)"
  if [[ -n "$MIXMEAN" && -n "$VOMEAN" ]] && awk -v m="$MIXMEAN" -v v="$VOMEAN" 'BEGIN{exit (m < v-3) ? 0 : 1}'; then
    echo "ERROR: block $((i+1)) mixes to ${MIXMEAN} dB but its voice alone is ${VOMEAN} dB — the narration did not reach the mix. Do NOT deliver." >&2
    exit 1
  fi
  BLOCK_START="$(awk -v p="$PAD_MS" -v ss="$SS" -v tr="$TRIM_S" 'BEGIN{printf "%.3f", p/1000 + ss - tr}')"
  printf '  block %02d: clip %.2fs, file %.2fs, speech %.2fs (%.2f..%.2f) -> speech starts at %.2fs\n' \
    "$((i+1))" "$D" "$A" "$SPEECH" "$SS" "$SE" "$BLOCK_START" >&2
  SPEECH_ABS="$(awk -v i="$i" -v c="$CLIP" -v b="$BLOCK_START" 'BEGIN{printf "%.3f", i*c + b}')"
  PBJSON[i]="$(printf '{"n":%d,"clip":"%s","voice":"%s","clip_s":%.2f,"speech_s":%.2f,"speech_abs_s":%.3f,"lead_silence_s":%.3f,"internal_pauses":%d,"freeze_head":%s,"freeze_tail":%s}' \
    "$((i+1))" "$(basename "$clip")" "$(basename "$original_voice")" "$D" "$SPEECH" "$SPEECH_ABS" "$SS" "${IPN:-0}" \
    "$([[ "${FRZH:-0}" != "0" ]] && echo true || echo false)" "$([[ "${FRZT:-0}" != "0" ]] && echo true || echo false)")"
done

VOTRACK="$TMP/joined.mp4"
echo "[2/3] concat -> single track" >&2
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c:v libx264 -preset veryfast -crf 20 -c:a aac -movflags +faststart "$VOTRACK"

if [[ -n "$SONG" ]]; then
  SM="$TMP/songmix.mp4"
  ffmpeg -y -loglevel error -i "$VOTRACK" -i "$SONG" \
    -filter_complex "[1:a]aformat=sample_rates=44100:channel_layouts=stereo,apad[s];[0:a][s]amix=inputs=2:duration=first:normalize=0[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "$SM"
  VOTRACK="$SM"
  echo "  song laid over the cut at 1.0 (clip SFX ${SFXVOL})" >&2
fi

if [[ -z "$SONG" ]]; then
  ASSERT_SRC="$TMP/voiceonly.wav"
  ffmpeg -y -loglevel error -f concat -safe 0 -i "$VOLIST" -ar 48000 -ac 2 "$ASSERT_SRC"
  VOD="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ASSERT_SRC")"
  awk -v d="${VOD:-0}" -v n="$pairs" -v c="$CLIP" 'BEGIN{exit (d > n*c-0.5) ? 1 : 0}' && {
    echo "ERROR: the voice-only track is ${VOD}s, not ${pairs}x${CLIP}s — the narration assert cannot be trusted. Do NOT deliver." >&2; exit 1; }
else
  ASSERT_SRC="$VOTRACK"
fi
QUIET="$(ffmpeg -i "$ASSERT_SRC" -af "silencedetect=noise=-18dB:d=6" -f null - 2>&1 | grep -Eo 'silence_(start|end): *[0-9.]+' || true)"
EMPTY="$(awk -v C="$CLIP" -v P="$pairs" '
  /silence_start/ { s[++k]=$NF+0; next }
  /silence_end/   { e[k]=$NF+0 }
  END {
    for (i=0;i<P;i++) { ws=i*C+2; we=i*C+8;
      for (j=1;j<=k;j++) { ee=(e[j]>0)?e[j]:1e9;
        if (s[j]<=ws && ee>=we) { printf "%s%d", (out++?",":""), i+1; break } } } }' <<< "$QUIET")"
if [[ -n "$EMPTY" ]]; then
  echo "ERROR: blocks [$EMPTY] have NO narration in their windows — the take itself is silent or was trimmed away. Fix the inputs and re-run; do NOT deliver." >&2
  exit 1
fi
echo "  narration present in all ${pairs} windows" >&2

echo "[3/3] finalize -> $FINAL_OUT" >&2
ln2_args() { # $1 = input file -> prints measured loudnorm args
  ffmpeg -hide_banner -i "$1" -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 \
  | awk '/"input_i"/{i=$3}/"input_tp"/{t=$3}/"input_lra"/{l=$3}/"input_thresh"/{h=$3}/"target_offset"/{o=$3}
         {gsub(/[",]/,"",i);gsub(/[",]/,"",t);gsub(/[",]/,"",l);gsub(/[",]/,"",h);gsub(/[",]/,"",o)}
         END{printf "measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s", i,t,l,h,o}'
}
if [[ -n "$MUSIC" ]]; then
  MIXED="$TMP/mixed.mp4"
  BEDG="$(bed_gain_db "$VOTRACK" "$MUSIC" "$MVOL")"
  echo "  music bed: measured against the speech -> ${BEDG} dB (then ducked under the voice)" >&2
  ffmpeg -y -loglevel error -i "$VOTRACK" -stream_loop -1 -i "$MUSIC" \
    -filter_complex "[0:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[vo][key];[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=${BEDG}dB[m];[m][key]sidechaincompress=threshold=0.02:ratio=8:attack=10:release=300[duck];[vo][duck]amix=inputs=2:duration=first:normalize=0[a]" \
    -map 0:v -map "[a]" -shortest -c:v copy -c:a aac -b:a 192k "$MIXED"
  SRC="$MIXED"
else
  SRC="$VOTRACK"
fi
LNARGS="$(ln2_args "$SRC")"
if [[ "$LNARGS" == *measured_I=-* ]]; then
  ffmpeg -y -loglevel error -i "$SRC" -af "loudnorm=I=-16:TP=-1.5:LRA=11:${LNARGS}:linear=true" -c:v copy -c:a aac -b:a 192k "$OUT"
else
  echo "WARN: loudness measurement failed — falling back to single-pass loudnorm." >&2
  ffmpeg -y -loglevel error -i "$SRC" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k "$OUT"
fi

TOT="$(awk -v n="$pairs" -v c="$CLIP" 'BEGIN{printf "%g", n*c}')"
FDUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
awk -v d="$FDUR" -v e="$TOT" 'BEGIN{x=d-e; if(x<0)x=-x; exit (x<=1)?0:1}' || {
  echo "ERROR: final duration ${FDUR}s != expected ${TOT}s (±1s) — do NOT deliver; investigate the inputs." >&2; exit 1; }

ADUR="$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "$OUT" | head -1)"
[[ -z "$ADUR" || "$ADUR" == "N/A" ]] && { echo "ERROR: final has no readable audio stream — do NOT deliver." >&2; exit 1; }
awk -v a="$ADUR" -v d="$FDUR" 'BEGIN{x=a-d; if(x<0)x=-x; exit (x<=1.5)?0:1}' || {
  echo "ERROR: audio stream ${ADUR}s vs video ${FDUR}s — mismatched/truncated audio; do NOT deliver." >&2; exit 1; }
DERR="$( (ffmpeg -v error -xerror -i "$OUT" -f null - ) 2>&1 | head -3 || true)"
[[ -n "$DERR" ]] && { echo "ERROR: final failed decode validation — corrupted stream; do NOT deliver:" >&2; echo "$DERR" >&2; exit 1; }


POSTER="${FINAL_OUT%.mp4}_poster.jpg"
POSTER_CANDIDATE="$TMP/final-poster.jpg"
ffmpeg -y -loglevel error -ss 1 -i "$OUT" -frames:v 1 -q:v 2 "$POSTER_CANDIDATE" || true
if [[ ! -s "$POSTER_CANDIDATE" ]]; then
  ffmpeg -y -loglevel error -i "$OUT" -frames:v 1 -q:v 2 "$POSTER_CANDIDATE" || true
fi

SIDE="${FINAL_OUT}.assembly.json"
SIDE_CANDIDATE="$TMP/assembly.json"
{
  printf '{"script":"assemble_final.sh","manifest_version":2,"assembly_attempts":%d,"out":"%s","blocks":%d,"clip_seconds":%s,"total_s":%s,"actual_s":%s,"width":%s,"height":%s,"fps":"%s","music":%s,"music_vol":%s,"sfx_vol":%s,"song":%s,"gate":"speech in [window-0.6,window-0.2], clip>=window-0.5, speech-centered, narration/song in every window (silencedetect -18dB/6s), song length +/-3s of NxCLIP, no atempo, 2-pass linear loudnorm -16, duration +/-1s, full decode","per_block":[' \
    "$ASSEMBLY_ATTEMPT" "$(basename "$FINAL_OUT")" "$pairs" "$CLIP" "$TOT" "$FDUR" "$W" "$H" "$FPS" \
    "$([[ -n "$MUSIC" ]] && echo true || echo false)" "$MVOL" "$SFXVOL" \
    "$([[ -n "$SONG" ]] && echo true || echo false)"
  for ((i=0;i<pairs;i++)); do printf '%s%s' "${PBJSON[i]}" "$([[ $i -lt $((pairs-1)) ]] && echo ,)"; done
  printf '],"ts":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$SIDE_CANDIDATE"
mv "$OUT" "$FINAL_OUT"
if [[ -s "$POSTER_CANDIDATE" ]]; then
  mv "$POSTER_CANDIDATE" "$POSTER"
  echo "POSTER: $POSTER" >&2
else
  echo "WARN: poster extraction failed (no $POSTER)" >&2
fi
mv "$SIDE_CANDIDATE" "$SIDE"
echo "ASSEMBLY-SIDECAR: $SIDE" >&2
echo "DONE: $FINAL_OUT  (ONE file, ${pairs} blocks x ${CLIP}s = ${TOT}s, actual ${FDUR}s; decode-validated)" >&2
