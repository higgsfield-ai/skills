#!/usr/bin/env bash
# Usage: assemble_partial_edit.sh --source source.mp4 --source-seconds N --requested-seconds N --manifest patches.json --out edited.mp4
set -euo pipefail

SOURCE=""
SOURCE_URL=""
SOURCE_SECONDS=""
REQUESTED_SECONDS=""
MANIFEST=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="$2"; shift 2 ;;
    --source-url) SOURCE_URL="$2"; shift 2 ;;
    --source-seconds) SOURCE_SECONDS="$2"; shift 2 ;;
    --requested-seconds) REQUESTED_SECONDS="$2"; shift 2 ;;
    --manifest) MANIFEST="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "ERROR: unknown argument $1" >&2; exit 2 ;;
  esac
done

for binary in ffmpeg ffprobe python3; do
  command -v "$binary" >/dev/null 2>&1 || {
    echo "ERROR: '$binary' not found" >&2
    exit 1
  }
done

[[ -f "$SOURCE" ]] || { echo "ERROR: --source file not found" >&2; exit 1; }
[[ -f "$MANIFEST" ]] || { echo "ERROR: --manifest file not found" >&2; exit 1; }

[[ -n "$SOURCE_SECONDS" ]] || { echo "ERROR: --source-seconds is required" >&2; exit 1; }
[[ -n "$REQUESTED_SECONDS" ]] || { echo "ERROR: --requested-seconds is required" >&2; exit 1; }
[[ -n "$OUT" ]] || { echo "ERROR: --out is required" >&2; exit 1; }

TMP="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT

SEGMENTS_TSV="$TMP/segments.tsv"
PARTS_TSV="$TMP/parts.tsv"
python3 - "$MANIFEST" "$REQUESTED_SECONDS" "$SEGMENTS_TSV" "$PARTS_TSV" <<'PY'
import json
import pathlib
import sys

manifest_path, requested_raw, segments_path, parts_path = sys.argv[1:]
requested_seconds = float(requested_raw)
segments = json.loads(pathlib.Path(manifest_path).read_text())
if not isinstance(segments, list) or not segments:
    raise SystemExit("ERROR: patch manifest must be a non-empty JSON array")

previous_end = 0
segment_lines = []
part_lines = []
for index, segment in enumerate(segments, start=1):
    if not isinstance(segment, dict):
        raise SystemExit(f"ERROR: segment {index} must be an object")
    start = segment.get("start_seconds")
    end = segment.get("end_seconds")
    if (
        not isinstance(start, int)
        or not isinstance(end, int)
        or start % 10
        or end - start != 10
        or end > requested_seconds
        or start < previous_end
    ):
        raise SystemExit(f"ERROR: segment {index} is not an ordered 10-second grid range")
    patch_video = segment.get("patch_video")
    parts = segment.get("parts")
    if (isinstance(patch_video, str)) == isinstance(parts, list):
        raise SystemExit(
            f"ERROR: segment {index} must provide exactly one of patch_video or parts"
        )
    if isinstance(patch_video, str):
        if "\t" in patch_video or "\n" in patch_video:
            raise SystemExit(f"ERROR: segment {index} patch path is invalid")
        segment_lines.append(f"{index}\t{start}\t{end}\tpatch\t{patch_video}")
    else:
        if not parts or len(parts) != 1:
            raise SystemExit(f"ERROR: segment {index} must contain one 10s part")
        durations = []
        for part_index, part in enumerate(parts, start=1):
            if not isinstance(part, dict):
                raise SystemExit(f"ERROR: segment {index} part {part_index} is invalid")
            video = part.get("video")
            audio = part.get("audio")
            seconds = part.get("seconds")
            if (
                not isinstance(video, str)
                or not isinstance(audio, str)
                or seconds != 10
                or any(character in video + audio for character in "\t\n")
            ):
                raise SystemExit(f"ERROR: segment {index} part {part_index} is invalid")
            durations.append(seconds)
            part_lines.append(
                f"{index}\t{part_index}\t{seconds}\t{video}\t{audio}"
            )
        if durations != [10]:
            raise SystemExit(f"ERROR: segment {index} parts must be exactly one 10s part")
        segment_lines.append(f"{index}\t{start}\t{end}\tparts\t")
    previous_end = end

pathlib.Path(segments_path).write_text("\n".join(segment_lines) + "\n")
pathlib.Path(parts_path).write_text(
    ("\n".join(part_lines) + "\n") if part_lines else ""
)
PY

PROBED_SOURCE_SECONDS="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SOURCE")"
python3 - "$SOURCE_SECONDS" "$PROBED_SOURCE_SECONDS" <<'PY'
import sys

declared, probed = map(float, sys.argv[1:])
if declared <= 0 or probed <= 0 or abs(declared - probed) > 1:
    raise SystemExit(
        f"ERROR: declared source duration {declared:.3f}s does not match "
        f"the source file {probed:.3f}s"
    )
PY

DIMS="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$SOURCE")"
WIDTH="${DIMS%%,*}"
HEIGHT="${DIMS##*,}"
FPS_RAW="$(ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of csv=p=0 "$SOURCE")"
FPS="$(python3 - "$FPS_RAW" <<'PY'
import sys

raw = sys.argv[1]
numerator, separator, denominator = raw.partition("/")
value = float(numerator) / float(denominator) if separator and float(denominator) else float(numerator)
print(f"{value:.6f}")
PY
)"

normalize_video() {
  local input_video="$1"
  local input_audio="$2"
  local duration="$3"
  local output_video="$4"
  [[ -f "$input_video" ]] || { echo "ERROR: missing video $input_video" >&2; exit 1; }
  if [[ -n "$input_audio" ]]; then
    [[ -f "$input_audio" ]] || { echo "ERROR: missing audio $input_audio" >&2; exit 1; }
    ffmpeg -v error -y -i "$input_video" -i "$input_audio" \
      -filter_complex \
      "[0:v]scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps=${FPS},trim=duration=${duration},setpts=PTS-STARTPTS[v];[1:a]apad,atrim=duration=${duration},asetpts=PTS-STARTPTS[a]" \
      -map "[v]" -map "[a]" -t "$duration" \
      -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 \
      -c:a aac -ar 48000 -ac 2 -b:a 192k "$output_video"
  else
    ffmpeg -v error -y -i "$input_video" \
      -filter_complex \
      "[0:v]scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps=${FPS},trim=duration=${duration},setpts=PTS-STARTPTS[v];[0:a]apad,atrim=duration=${duration},asetpts=PTS-STARTPTS[a]" \
      -map "[v]" -map "[a]" -t "$duration" \
      -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 \
      -c:a aac -ar 48000 -ac 2 -b:a 192k "$output_video"
  fi
}

normalize_source_range() {
  local start="$1"
  local duration="$2"
  local output_video="$3"
  ffmpeg -v error -y -ss "$start" -i "$SOURCE" -t "$duration" \
    -vf "scale=${WIDTH}:${HEIGHT},fps=${FPS},setpts=PTS-STARTPTS" \
    -af "apad,atrim=duration=${duration},asetpts=PTS-STARTPTS" \
    -c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 \
    -c:a aac -ar 48000 -ac 2 -b:a 192k "$output_video"
}

CONCAT_LIST="$TMP/concat.txt"
: > "$CONCAT_LIST"
PER_SEGMENT_JSON="$TMP/per-segment.jsonl"
: > "$PER_SEGMENT_JSON"
CURSOR="0"
CHUNK_NUMBER=0

while IFS=$'\t' read -r segment_number start_seconds end_seconds patch_kind patch_video; do
  [[ -n "$segment_number" ]] || continue
  if python3 - "$start_seconds" "$CURSOR" <<'PY'
import sys
raise SystemExit(0 if float(sys.argv[1]) > float(sys.argv[2]) else 1)
PY
  then
    CHUNK_NUMBER=$((CHUNK_NUMBER + 1))
    source_chunk="$TMP/chunk-$(printf '%03d' "$CHUNK_NUMBER").mp4"
    source_duration="$(python3 - "$start_seconds" "$CURSOR" <<'PY'
import sys
print(float(sys.argv[1]) - float(sys.argv[2]))
PY
)"
    normalize_source_range "$CURSOR" "$source_duration" "$source_chunk"
    printf "file '%s'\n" "$source_chunk" >> "$CONCAT_LIST"
  fi

  segment_patch="$TMP/segment-$(printf '%03d' "$segment_number").mp4"
  if [[ "$patch_kind" == "patch" ]]; then
    normalize_video "$patch_video" "" 10 "$segment_patch"
  else
    part_list="$TMP/segment-${segment_number}-parts.txt"
    : > "$part_list"
    while IFS=$'\t' read -r part_segment part_number part_seconds part_video part_audio; do
      [[ "$part_segment" == "$segment_number" ]] || continue
      normalized_part="$TMP/segment-${segment_number}-part-${part_number}.mp4"
      normalize_video "$part_video" "$part_audio" "$part_seconds" "$normalized_part"
      printf "file '%s'\n" "$normalized_part" >> "$part_list"
    done < "$PARTS_TSV"
    ffmpeg -v error -y -f concat -safe 0 -i "$part_list" -c copy "$segment_patch"
  fi
  patch_duration="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$segment_patch")"
  python3 - "$patch_duration" <<'PY'
import sys
duration = float(sys.argv[1])
if abs(duration - 10) > 0.25:
    raise SystemExit(f"ERROR: normalized patch is {duration:.3f}s, expected 10s")
PY
  CHUNK_NUMBER=$((CHUNK_NUMBER + 1))
  printf "file '%s'\n" "$segment_patch" >> "$CONCAT_LIST"
  python3 - "$segment_number" "$start_seconds" "$end_seconds" "$patch_duration" >> "$PER_SEGMENT_JSON" <<'PY'
import json
import sys
print(json.dumps({
    "n": int(sys.argv[1]),
    "start_seconds": int(sys.argv[2]),
    "end_seconds": int(sys.argv[3]),
    "patch_seconds": round(float(sys.argv[4]), 3),
}))
PY
  CURSOR="$end_seconds"
done < "$SEGMENTS_TSV"

if python3 - "$PROBED_SOURCE_SECONDS" "$CURSOR" <<'PY'
import sys
raise SystemExit(0 if float(sys.argv[1]) > float(sys.argv[2]) else 1)
PY
then
  CHUNK_NUMBER=$((CHUNK_NUMBER + 1))
  source_chunk="$TMP/chunk-$(printf '%03d' "$CHUNK_NUMBER").mp4"
  source_duration="$(python3 - "$PROBED_SOURCE_SECONDS" "$CURSOR" <<'PY'
import sys
print(float(sys.argv[1]) - float(sys.argv[2]))
PY
)"
  normalize_source_range "$CURSOR" "$source_duration" "$source_chunk"
  printf "file '%s'\n" "$source_chunk" >> "$CONCAT_LIST"
fi

ffmpeg -v error -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy -movflags +faststart "$OUT"
ACTUAL_SECONDS="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
SEGMENT_COUNT="$(wc -l < "$SEGMENTS_TSV" | tr -d ' ')"
PATCH_COUNT="$SEGMENT_COUNT"

python3 - \
  "$OUT.assembly.json" \
  "$SOURCE_URL" \
  "$SOURCE_SECONDS" \
  "$REQUESTED_SECONDS" \
  "$ACTUAL_SECONDS" \
  "$PATCH_COUNT" \
  "$PER_SEGMENT_JSON" <<'PY'
import json
import pathlib
import sys

(
    output_path,
    source_video_url,
    source_seconds,
    requested_seconds,
    actual_seconds,
    patch_count,
    per_segment_path,
) = sys.argv[1:]
per_segment = [
    json.loads(line)
    for line in pathlib.Path(per_segment_path).read_text().splitlines()
    if line
]
payload = {
    "manifest_version": 2,
    "script": "assemble_partial_edit.sh",
    "assembly_attempts": 1,

    "source_s": float(source_seconds),
    "requested_s": float(requested_seconds),
    "actual_s": round(float(actual_seconds), 3),
    "segments": len(per_segment),
    "patch_count": int(patch_count),
    "per_segment": per_segment,
}
pathlib.Path(output_path).write_text(json.dumps(payload, indent=2) + "\n")
PY

echo "OK: $OUT (${ACTUAL_SECONDS}s); sidecar: $OUT.assembly.json" >&2
