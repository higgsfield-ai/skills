#!/usr/bin/env bash
# Usage: speech_metrics.sh audio.wav --text "spoken text" --json
set -euo pipefail

FILE=""; PAUSE="0.8"; NOISE="-45"; JSON=0; TEXT=""; WORDS=""; MAXWPS="2.9"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pause) PAUSE="$2"; shift 2 ;;
    --noise) NOISE="$2"; shift 2 ;;
    --text)  TEXT="$2"; shift 2 ;;
    --words) WORDS="$2"; shift 2 ;;
    --max-wps) MAXWPS="$2"; shift 2 ;;
    --json)  JSON=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) FILE="$1"; shift ;;
  esac
done
[[ -n "$FILE" && -f "$FILE" ]] || { echo "ERROR: pass an audio file" >&2; exit 1; }
for b in ffmpeg ffprobe awk; do command -v "$b" >/dev/null 2>&1 || { echo "ERROR: '$b' not found" >&2; exit 1; }; done

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FILE")"
EVENTS="$(ffmpeg -i "$FILE" -af "silencedetect=noise=${NOISE}dB:d=0.25" -f null - 2>&1 \
          | grep -Eo 'silence_(start|end): *-?[0-9.]+' || true)"

read -r SS SE <<< "$(awk -v A="$DUR" '
  /silence_start/ { s=$NF+0; if(first==""){first=s}; last=s; open=1; next }
  /silence_end/   { e=$NF+0; if(first!="" && first<0.1 && ssdone==""){ss=e; ssdone=1};
                    e_last=e; s_before=last; open=0 }
  END {
    if (open==1)                       se=last;
    else if (e_last>0 && A-e_last<0.2) se=s_before;
    else                               se=A;
    printf "%.3f %.3f", ss+0, se+0 }' <<< "$EVENTS")"
[[ -z "${SS:-}" ]] && SS=0; [[ -z "${SE:-}" || "$SE" == "0.000" ]] && SE="$DUR"
SPEECH="$(awk -v a="$SS" -v b="$SE" 'BEGIN{d=b-a; if(d<0)d=0; printf "%.3f", d}')"
awk -v s="$SPEECH" 'BEGIN{exit (s<0.3)?0:1}' && { SS=0; SE="$DUR"; SPEECH="$DUR"; }

read -r PN PMAX <<< "$(awk -v lo="$SS" -v hi="$SE" -v thr="$PAUSE" '
  /silence_start/ { s=$NF+0; open=1; next }
  /silence_end/   { e=$NF+0; if(open==1 && s>lo+0.1 && e<hi-0.1 && e-s>=thr){n++; if(e-s>mx)mx=e-s}; open=0 }
  END{ printf "%d %.2f", n+0, mx+0 }' <<< "$EVENTS")"

if [[ -z "$WORDS" && -n "$TEXT" ]]; then
  WORDS="$(printf '%s' "$TEXT" | sed -e 's/\[[^][]*\]//g' -e 's/([^()]*)//g' \
            | tr -cs "[:alnum:]'-" ' ' | awk '{print NF}')"
fi
RATE=""; WPS=""
if [[ -n "$WORDS" ]]; then
  read -r WPS RATE <<< "$(awk -v w="$WORDS" -v s="$SPEECH" -v mx="$MAXWPS" 'BEGIN{
    if (s<=0) { print "0.00 unknown"; exit }
    r=w/s; printf "%.2f %s", r, (r>mx ? "RUSHED" : (r<2.1 ? "SLOW" : "ok")) }')"
fi

if [[ "$JSON" == "1" ]]; then
  printf '{"file":"%s","duration":%.3f,"speech_start":%.3f,"speech_end":%.3f,"speech":%.3f,"pauses":%d,"longest_pause":%.2f' \
    "$(basename "$FILE")" "$DUR" "$SS" "$SE" "$SPEECH" "${PN:-0}" "${PMAX:-0}"
  [[ -n "$WORDS" ]] && printf ',"words":%d,"wps":%s,"rate":"%s"' "$WORDS" "$WPS" "$RATE"
  printf '}\n'
else
  printf 'duration=%.3f speech_start=%.3f speech_end=%.3f speech=%.3f pauses=%d longest_pause=%.2f' \
    "$DUR" "$SS" "$SE" "$SPEECH" "${PN:-0}" "${PMAX:-0}"
  [[ -n "$WORDS" ]] && printf ' words=%d wps=%s rate=%s' "$WORDS" "$WPS" "$RATE"
  printf '\n'
fi
if [[ "$RATE" == "RUSHED" ]]; then
  echo "WARN: ${WPS} words/sec is auctioneer pace — REWRITE the line shorter (target <= ${MAXWPS}) and regenerate. Do NOT ship it and do NOT slow the audio down." >&2
fi
