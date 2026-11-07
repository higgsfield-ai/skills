#!/usr/bin/env bash
# Usage: check_voice.sh voice.wav window_seconds
set -euo pipefail
[[ $# -eq 2 && -s "$1" ]] || { echo 'Usage: check_voice.sh voice.wav window_seconds' >&2; exit 2; }
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && command -v awk >/dev/null || { echo 'Missing audio tools' >&2; exit 2; }
awk -v t="$2" 'BEGIN{exit !(t>3 && t<=10)}' || { echo 'Spoken window must be greater than 3 and at most 10 seconds' >&2; exit 2; }
ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$1" | grep -qx audio || { echo 'No readable audio stream' >&2; exit 1; }
end=$(ffmpeg -v error -i "$1" -af 'aformat=channel_layouts=mono,aresample=16000,asetnsamples=n=1600:p=0,astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-' -f null - 2>/dev/null | awk -F= '/RMS_level/{n++;v=$2;if(v!="-inf" && v+0> -34)last=n} END{printf "%.2f",last*0.1}')
awk -v t="$2" -v s="$end" 'BEGIN{printf "Speech ends at %.2fs; required %.2f–%.2fs\n",s,t-2,t-.2; exit !(s>=t-2 && s<=t-.2)}'
