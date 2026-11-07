#!/usr/bin/env bash
# assemble_blocks.sh — per-block assembly. Every block is a FIXED length
# (--clip-seconds, default 10). NOTHING is time-stretched — not the video and
# not the audio (atempo is not used: sped-up narration is audible and
# banned; regenerate the take instead). Each take's trailing silence is
# trimmed and a TWO-SIDED duration gate enforces that real speech fits its
# window (see GATE below). Total duration stays exact (N × clip-seconds) and
# burned captions stay in sync.
#
# Usage:
#   scripts/assemble_blocks.sh --out FILE [--clip-seconds N] [--last-seconds R] \
#       [--music FILE|URL] [--music-vol 0.10] [--sfx-vol 0.12] clip1 audio1 ... clipN audioN
#
# LEVEL LAW — voice 1.0 always; the clips' own diegetic SFX are KEPT under the
# voice at --sfx-vol (default 0.12, clamped <=0.20; clips without audio fall
# back to voice-only). --music adds one background MUSIC bed under the whole
# video at --music-vol (default 0.10), looped to cover the full duration, and
# the sum is limited to ~-3 dBFS so it never clips.
#
# Per block (T = clip-seconds, fixed):
#   GATE (two-sided, HARD — do not bypass): real speech must end inside
#   [T-2.0, T-0.2]s (8.0-9.8s for a 10s block), measured by 100ms RMS energy
#   (NEVER silencedetect — it misreads fast dense speech). Trailing SILENCE
#   inside a take is trimmed first (seed TTS pads up to ~2.5s of digital
#   silence into its wavs), so only REAL violations fail:
#     - speech > T-0.2 -> FAIL: regenerate that take SHORTER (fewer words).
#     - speech < T-2.0 -> FAIL: rewrite that take DENSER (more words) —
#       dead-air tails read as stalls and make captions linger.
#     - in range       -> audio trimmed to speech+0.25s; the voice starts
#       promptly (small capped head pad <=0.12s) and silence is padded onto
#       the TAIL (not centered, which floated a short TTS take up to ~0.7s
#       into the block).
#   Video is normalized to the first clip's resolution + the FIRST clip's fps
#   (hard-coding a rate re-times the sources -> pulldown judder) and, if a clip
#   is under T, its last frame is held to reach T. Blocks are concatenated in order.
#
# --last-visual-only allows an intentionally unvoiced last window <=3s.
# All voiced blocks still pass the unchanged speech gates.
# --last-seconds R (0 < R <= clip-seconds) fits the FINAL block to R instead of
# clip-seconds — the last clip is trimmed to R and its audio is fit to the R
# window. Use it when a fixed requested duration is not a multiple of the block
# length (e.g. 15s = one 10s block + a 5s final block), so the assembled total
# is EXACTLY the requested seconds, not rounded up to N x clip-seconds.
#
# Also writes a poster frame next to the output (<out>_poster.jpg) for the
# video thumbnail, and an ASSEMBLY SIDECAR (<out>.assembly.json)
# with the per-take speech metrics used to align captions.
#
# Requires: ffmpeg, ffprobe, curl, awk
set -euo pipefail

OUT="explainer.mp4"; CLIP=10; LAST=""; LAST_VISUAL_ONLY=0; MUSIC=""; MUSIC_VOL="0.10"; SFXVOL="0.12"; ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --clip-seconds) CLIP="$2"; shift 2 ;;
    --last-seconds) LAST="$2"; shift 2 ;;
    --last-visual-only) LAST_VISUAL_ONLY=1; shift ;;
    --music) MUSIC="$2"; shift 2 ;;
    --music-vol) MUSIC_VOL="$2"; shift 2 ;;   # HARD-CAPPED at 0.4 below — VO is always 1.0
    --sfx-vol) SFXVOL="$2"; shift 2 ;;        # clip's own diegetic audio under the voice
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
# LEVEL LAW: voice 1.0 always; clip SFX default 0.12, music default 0.10.
SFXVOL="$(awk -v v="$SFXVOL" 'BEGIN{v=v+0; if(v<0)v=0; if(v>0.2){print "WARN: --sfx-vol clamped to 0.20 (voice stays 1.0)" > "/dev/stderr"; v=0.2} printf "%.3f", v}')"
if [[ -n "$LAST" ]]; then
  awk -v r="$LAST" -v c="$CLIP" 'BEGIN{exit !(r>0 && r<=c)}' \
    || { echo "ERROR: --last-seconds must be in (0, --clip-seconds]" >&2; exit 1; }
fi
if [[ "$LAST_VISUAL_ONLY" -eq 1 ]]; then
  [[ -n "$LAST" ]] && awk -v r="$LAST" 'BEGIN{exit !(r>0 && r<=3)}' || {
    echo "ERROR: --last-visual-only requires --last-seconds in (0,3]" >&2; exit 1; }
fi
for b in ffmpeg ffprobe curl awk python3; do command -v "$b" >/dev/null 2>&1 || { echo "ERROR: '$b' not found" >&2; exit 1; }; done
n=${#ARGS[@]}
(( n >= 2 && n % 2 == 0 )) || { echo "ERROR: pass clip/audio PAIRS (clip1 audio1 clip2 audio2 ...)" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fetch(){ if [[ "$1" == http://* || "$1" == https://* ]]; then curl -fsSL "$1" -o "$2"; else [[ -f "$1" ]] || { echo "ERROR: not found: $1" >&2; exit 1; }; cp "$1" "$2"; fi; }

pairs=$(( n / 2 ))
echo "[1/3] fetching $pairs block(s)" >&2
clips=(); auds=()
for ((i=0;i<pairs;i++)); do
  # Pair sanity (local files only): numbers in the two names should match —
  # block03 + take05 is the #1 cause of "audio on the wrong block".
  if [[ "${ARGS[i*2]}" != http* && "${ARGS[i*2+1]}" != http* ]]; then
    cA="$(basename "${ARGS[i*2]%.*}"  | grep -Eo '[0-9]+' | tail -1 || true)"
    cB="$(basename "${ARGS[i*2+1]%.*}" | grep -Eo '[0-9]+' | tail -1 || true)"
    if [[ -n "$cA" && -n "$cB" ]] && (( 10#$cA != 10#$cB )); then
      echo "WARN: pair $((i+1)) mixes numbers: $(basename "${ARGS[i*2]}") + $(basename "${ARGS[i*2+1]}") — check the argument order." >&2
    fi
  fi
  cf="$TMP/clip_$i"; af="$TMP/aud_$i"
  fetch "${ARGS[i*2]}" "$cf"; fetch "${ARGS[i*2+1]}" "$af"
  clips+=("$cf"); auds+=("$af")
done

DIMS="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "${clips[0]}")"
W="${DIMS%%,*}"; H="${DIMS##*,}"
# Follow the FIRST clip's frame rate (all clips from one model share it).
# Hard-coding a different rate (e.g. 30 on 24fps sources) duplicates every
# 4th frame -> visible pulldown judder on pans.
FPS="$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "${clips[0]}")"
case "$FPS" in ""|"0/0"|"N/A") FPS="30" ;; esac
echo "[2/3] muxing ${pairs} blocks, fixed ${CLIP}s, ${W}x${H}@${FPS}fps (video not stretched; audio fit)" >&2

# --- speech end (s): last 100ms RMS energy bin above -34 dBFS. RMS energy,
# NEVER silencedetect (it misreads fast dense speech). The aresample sits
# INSIDE the -af chain so the 1600-sample bins are true 100ms at any input rate.
speech_end() {
  ffmpeg -v error -i "$1" -af "aformat=channel_layouts=mono,aresample=16000,asetnsamples=n=1600:p=0,astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null - 2>/dev/null \
    | awk -F= '/RMS_level/{n++; v=$2; if (v!="-inf" && v+0>-34) last=n} END{printf "%.2f", last*0.1}'
}

# --- longest internal pause (s): the longest run of quiet 100ms bins strictly
# BETWEEN the first and last loud bin. A pausey take reads as a stall on screen.
longest_pause() {
  ffmpeg -v error -i "$1" -af "aformat=channel_layouts=mono,aresample=16000,asetnsamples=n=1600:p=0,astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null - 2>/dev/null \
    | awk -F= '/RMS_level/{n++; v=$2; loud=(v!="-inf" && v+0>-34);
        if(loud){ if(started && gap>mx) mx=gap; gap=0; started=1 } else if(started) gap++ }
      END{printf "%.1f", mx*0.1}'
}

# --- pass 1: measure every take and run the two-sided duration GATE before
# encoding anything. All violations are reported at once so the caller can
# fix every bad take in one regeneration round.
sends=(); trims=(); durs=(); errs=()
for ((i=0;i<pairs;i++)); do
  T="$CLIP"
  if [[ -n "$LAST" && "$i" -eq "$((pairs-1))" ]]; then T="$LAST"; fi
  A="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${auds[i]}")"
  if [[ "$LAST_VISUAL_ONLY" -eq 1 && "$i" -eq "$((pairs-1))" ]]; then
    SEND="$(speech_end "${auds[i]}")"
    if awk -v s="$SEND" 'BEGIN{exit !(s>0)}'; then
      errs+=("block $((i+1)): visual-only tail requires a silent pair audio file; keep ambience in the clip SFX stream")
    fi
    sends+=("$SEND"); durs+=("$A"); trims+=("$T")
    continue
  fi
  SEND="$(speech_end "${auds[i]}")"
  MINS="$(awk -v t="$T" 'BEGIN{printf "%.1f", t-2.0}')"
  MAXS="$(awk -v t="$T" 'BEGIN{printf "%.1f", t-0.2}')"
  if awk -v s="$SEND" -v m="$MAXS" 'BEGIN{exit !(s>m)}'; then
    errs+=("block $((i+1)): speech ${SEND}s > ${MAXS}s — REGENERATE this take shorter (fewer words); do NOT time-stretch")
  elif awk -v s="$SEND" -v m="$MINS" 'BEGIN{exit !(s<m)}'; then
    errs+=("block $((i+1)): speech ${SEND}s < ${MINS}s — REWRITE this take denser (target ${MINS}-${MAXS}s of speech); do NOT ship dead air")
  fi
  PSE="$(longest_pause "${auds[i]}")"
  awk -v p="$PSE" 'BEGIN{exit (p>=0.8)?0:1}' && \
    echo "WARN: block $((i+1)) take has an internal pause of ${PSE}s — pausey take: rewrite the line as ONE flowing clause and regenerate." >&2
  sends+=("$SEND"); durs+=("$A")
  trims+=("$(awk -v s="$SEND" -v a="$A" -v t="$T" 'BEGIN{v=s+0.25; if(v>a)v=a; if(v>t)v=t; printf "%.2f", v}')")
done
if (( ${#errs[@]} > 0 )); then
  echo "DURATION GATE FAILED (${#errs[@]} of $pairs takes):" >&2
  for e in "${errs[@]}"; do echo "  $e" >&2; done
  echo "The gate is two-sided BY DESIGN (atempo removed). Fix the takes and re-run — do not bypass." >&2
  exit 1
fi

# --- pass 2: mux. Audio = take trimmed to speech+0.25s (trailing silence
# dropped), small head pad (<=0.12s, see header), silence apad to the tail.
LIST="$TMP/list.txt"; : > "$LIST"
PBJSON=()
for ((i=0;i<pairs;i++)); do
  T="$CLIP"
  if [[ -n "$LAST" && "$i" -eq "$((pairs-1))" ]]; then T="$LAST"; fi
  TRIMS="${trims[i]}"
  PAD_MS="$(awk -v a="$TRIMS" -v c="$T" 'BEGIN{ea=(a>c)?c:a; d=(c-ea)/2; if(d<0)d=0; if(d>0.12)d=0.12; printf "%d", d*1000}')"
  out="$TMP/voiced_$(printf '%03d' "$i").mp4"
  # Keep the clip's own diegetic SFX under the voice (SFXVOL, default 0.12);
  # clips without an audio stream fall back to voice-only.
  HASAUD="$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "${clips[i]}" | head -1)"
  if [[ "$HASAUD" == "audio" ]]; then
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=1[v];[1:a]atrim=0:${TRIMS},asetpts=PTS-STARTPTS,adelay=${PAD_MS}:all=1,apad[vo];[0:a]volume=${SFXVOL},apad[sfx];[sfx][vo]amix=inputs=2:duration=first:normalize=0[a]"
  else
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=1[v];[1:a]atrim=0:${TRIMS},asetpts=PTS-STARTPTS,adelay=${PAD_MS}:all=1,apad[a]"
  fi
  ffmpeg -y -loglevel error -i "${clips[i]}" -i "${auds[i]}" \
    -filter_complex "$FC" \
    -map "[v]" -map "[a]" -t "$T" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k "$out"
  echo "file '$out'" >> "$LIST"
  printf '  block %02d: audio %.2fs, speech %ss -> trim %ss, window %ss\n' "$((i+1))" "${durs[i]}" "${sends[i]}" "$TRIMS" "$T" >&2
  PBJSON+=("$(python3 -c 'import json,sys; print(json.dumps({"n":int(sys.argv[7]),"voice":sys.argv[1],"speech_s":float(sys.argv[2]),"speech_end_s":float(sys.argv[2]),"speech_abs_s":float(sys.argv[3]),"lead_silence_s":0,"audio_s":float(sys.argv[4]),"trimmed_to_s":float(sys.argv[5]),"window_s":float(sys.argv[6])}))' "$(basename "${ARGS[i*2+1]}")" "${sends[i]}" "$(awk -v i="$i" -v c="$CLIP" -v p="$PAD_MS" 'BEGIN{printf "%.3f",i*c+p/1000}')" "${durs[i]}" "$TRIMS" "$T" "$((i+1))")")
done

echo "[3/3] concatenating $pairs blocks${MUSIC:+ + music bed} -> $OUT" >&2
CONCAT="$TMP/concat.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c:v libx264 -preset veryfast -crf 20 -c:a aac -movflags +faststart "$CONCAT"

if [[ -n "$MUSIC" ]]; then
  # Music mix: narration VO stays at full level (front); the music bed is
  # dropped low (MUSIC_VOL, default 0.10), looped to cover the whole video,
  # and a limiter caps the sum at ~-3 dBFS so it never clips. Video is copied
  # (not re-encoded); clip SFX were already mixed under the voice per block.
  # HARD RULE: the voice is ALWAYS 1.0 and the music bed NEVER exceeds 0.4 —
  # any louder value is clamped here so a misconfigured caller cannot drown
  # the narration.
  MUSIC_VOL="$(awk -v v="$MUSIC_VOL" 'BEGIN{v=v+0; if(v<0)v=0; if(v>0.4){print "WARN: --music-vol clamped to 0.4 (voice stays 1.0)" > "/dev/stderr"; v=0.4} printf "%.3f", v}')"
  MUS="$TMP/music_src"; fetch "$MUSIC" "$MUS"
  ffmpeg -y -loglevel error -i "$CONCAT" -stream_loop -1 -i "$MUS" \
    -filter_complex "[1:a]volume=${MUSIC_VOL}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[mix];[mix]alimiter=limit=0.7:level=disabled[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
  echo "  music bed mixed under VO (vol=${MUSIC_VOL}, looped, limited)" >&2
else
  cp "$CONCAT" "$OUT"
fi

# Poster frame for the video thumbnail — 1s in (frame 0 is often a fade-in),
# falling back to the first frame. Best-effort: a missing poster never fails
# the assembly.
POSTER="${OUT%.mp4}_poster.jpg"
ffmpeg -y -loglevel error -ss 1 -i "$OUT" -frames:v 1 -q:v 2 "$POSTER" || true
if [[ ! -s "$POSTER" ]]; then
  ffmpeg -y -loglevel error -i "$OUT" -frames:v 1 -q:v 2 "$POSTER" || true
fi
[[ -s "$POSTER" ]] && echo "POSTER: $POSTER" >&2 || echo "WARN: poster extraction failed (no $POSTER)" >&2

TOTAL="$(awk -v n="$pairs" -v c="$CLIP" -v r="${LAST:-$CLIP}" 'BEGIN{printf "%g", (n-1)*c+r}')"

# --- final self-check:
# exact duration, audio stream present & spanning the video, zero-error decode.
FDUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
awk -v d="$FDUR" -v e="$TOTAL" 'BEGIN{x=d-e; if(x<0)x=-x; exit (x<=1)?0:1}' || {
  echo "ERROR: final duration ${FDUR}s != expected ${TOTAL}s (±1s) — do NOT deliver; fix the inputs and re-run." >&2; exit 1; }
ADUR="$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "$OUT" | head -1)"
[[ -z "$ADUR" || "$ADUR" == "N/A" ]] && { echo "ERROR: final has no readable audio stream — do NOT deliver." >&2; exit 1; }
awk -v a="$ADUR" -v d="$FDUR" 'BEGIN{x=a-d; if(x<0)x=-x; exit (x<=1.5)?0:1}' || {
  echo "ERROR: audio stream ${ADUR}s vs video ${FDUR}s — truncated/mismatched audio; do NOT deliver." >&2; exit 1; }
DERR="$( (ffmpeg -v error -xerror -i "$OUT" -f null - ) 2>&1 | head -3 || true)"
[[ -n "$DERR" ]] && { echo "ERROR: final failed decode validation — corrupted stream; do NOT deliver:" >&2; echo "$DERR" >&2; exit 1; }
echo "  self-check: duration ${FDUR}s, audio ${ADUR}s, decode clean" >&2

# --- assembly sidecar: machine-readable proof the final went through this
# script (gate results included).
SIDE="${OUT}.assembly.json"
{
  printf '{"script":"assemble_blocks.sh","out":"%s","blocks":%d,"clip_seconds":%s,"last_seconds":%s,"total_s":%s,"width":%s,"height":%s,"fps":"%s","music":%s,"music_vol":%s,"gate":"speech in [T-2.0,T-0.2]s per take, trailing silence trimmed, atempo removed","per_block":[' \
    "$(basename "$OUT")" "$pairs" "$CLIP" "${LAST:-$CLIP}" "$TOTAL" "$W" "$H" "$FPS" \
    "$([[ -n "$MUSIC" ]] && echo true || echo false)" "${MUSIC_VOL}"
  for ((i=0;i<pairs;i++)); do printf '%s%s' "${PBJSON[i]}" "$([[ $i -lt $((pairs-1)) ]] && echo ,)"; done
  printf '],"ts":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$SIDE"
echo "ASSEMBLY-SIDECAR: $SIDE" >&2
echo "DONE: $OUT ($pairs blocks, ${TOTAL}s total)" >&2
