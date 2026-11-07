#!/usr/bin/env python3
"""Build the deterministic scene-based manifest v2 from narration timestamps."""

from __future__ import annotations

import argparse
import json
import math
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


WORD_PATTERN = re.compile(r"[\w]+(?:[-'’][\w]+)*", re.UNICODE)
MIN_FRAME_SECONDS = 0.7
TARGET_MAX_FRAME_SECONDS = 1.2
HARD_MAX_FRAME_SECONDS = 1.5
REQUESTED_DURATION_TOLERANCE_RATIO = 0.10
REQUESTED_DURATION_MINIMUM_TOLERANCE_SECONDS = 3.0


def _tokens(value: str) -> list[str]:
    return [token.casefold() for token in WORD_PATTERN.findall(value)]


def _word_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        candidates = payload
    elif isinstance(payload, dict) and isinstance(payload.get("words"), list):
        candidates = payload["words"]
    elif isinstance(payload, dict) and isinstance(payload.get("segments"), list):
        candidates = [
            word
            for segment in payload["segments"]
            if isinstance(segment, dict)
            for word in segment.get("words", [])
            if isinstance(word, dict)
        ]
    else:
        raise ValueError("timestamps must contain a words array")
    words = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        text = str(item.get("word") or item.get("text") or "").strip()
        start = item.get("start")
        end = item.get("end")
        if (
            text
            and isinstance(start, (int, float))
            and isinstance(end, (int, float))
            and 0 <= start < end
        ):
            words.append({"word": text, "start": float(start), "end": float(end)})
    if not words:
        raise ValueError("timestamps contain no usable timed words")
    return words


def _beat_phrase(beat: dict[str, Any]) -> str:
    return str(beat.get("phrase") or beat.get("vo_line") or "").strip()


def _aligned_beat_spans(
    beats: list[dict[str, Any]],
    words: list[dict[str, Any]],
    audio_duration: float,
) -> tuple[list[tuple[float, float]], float]:
    authored_tokens = [
        token
        for beat in beats
        for token in _tokens(_beat_phrase(beat))
    ]
    spoken_tokens = [
        token
        for word in words
        for token in _tokens(str(word["word"]))
    ]
    matcher = SequenceMatcher(a=authored_tokens, b=spoken_tokens, autojunk=False)
    similarity = matcher.ratio()
    if similarity < 0.5:
        raise ValueError(
            f"narration/script similarity {similarity:.3f} is below 0.500"
        )
    authored_to_spoken: dict[int, int] = {}
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            authored_to_spoken[block.a + offset] = block.b + offset

    raw_spans: list[tuple[float, float]] = []
    authored_offset = 0
    for beat in beats:
        count = len(_tokens(_beat_phrase(beat)))
        spoken_indexes = [
            authored_to_spoken[index]
            for index in range(authored_offset, authored_offset + count)
            if index in authored_to_spoken
        ]
        if not spoken_indexes:
            raise ValueError(f"beat {beat.get('n')} has no aligned narration words")
        raw_spans.append(
            (
                words[min(spoken_indexes)]["start"],
                words[max(spoken_indexes)]["end"],
            )
        )
        authored_offset += count

    boundaries = [0.0]
    for index in range(len(raw_spans) - 1):
        left_end = raw_spans[index][1]
        right_start = raw_spans[index + 1][0]
        boundaries.append(max(boundaries[-1], (left_end + right_start) / 2))
    boundaries.append(audio_duration)
    spans = [
        (boundaries[index], boundaries[index + 1])
        for index in range(len(beats))
    ]
    return spans, similarity


def _frame_count(duration: float) -> int:
    if duration <= 0:
        raise ValueError("beat span must be positive")
    count = max(1, math.ceil(duration / TARGET_MAX_FRAME_SECONDS))
    while count > 1 and duration / count < MIN_FRAME_SECONDS:
        count -= 1
    if duration / count > HARD_MAX_FRAME_SECONDS:
        raise ValueError(
            f"beat span {duration:.3f}s cannot satisfy the {HARD_MAX_FRAME_SECONDS}s "
            "hard frame hold limit"
        )
    return count


def build_scene_manifest(
    script: dict[str, Any],
    timestamps: Any,
    audio_duration: float,
    requested_duration_seconds: float | None = None,
) -> dict[str, Any]:
    beats = script.get("beats")
    if not isinstance(beats, list) or not beats:
        raise ValueError("script manifest must contain a non-empty beats array")
    if audio_duration <= 0:
        raise ValueError("audio_duration must be positive")
    if requested_duration_seconds is not None:
        if requested_duration_seconds <= 0:
            raise ValueError("requested_duration_seconds must be positive")
        tolerance_seconds = max(
            REQUESTED_DURATION_MINIMUM_TOLERANCE_SECONDS,
            requested_duration_seconds * REQUESTED_DURATION_TOLERANCE_RATIO,
        )
        if abs(audio_duration - requested_duration_seconds) > tolerance_seconds:
            raise ValueError(
                f"narration duration {audio_duration:.3f}s is outside the allowed "
                f"range for {requested_duration_seconds:.3f}s requested duration"
            )
    normalized_beats = []
    for index, raw_beat in enumerate(beats, start=1):
        if not isinstance(raw_beat, dict) or raw_beat.get("n") != index:
            raise ValueError(f"beat {index} is invalid")
        if not _beat_phrase(raw_beat):
            raise ValueError(f"beat {index} has no phrase")
        normalized_beats.append(raw_beat)

    words = _word_items(timestamps)
    spans, similarity = _aligned_beat_spans(
        normalized_beats,
        words,
        audio_duration,
    )
    frames: list[dict[str, Any]] = []
    variation_depth = 0
    if len(normalized_beats) != len(spans):
        raise ValueError("beat and timing counts differ")
    for beat, (start, end) in zip(normalized_beats, spans):
        duration = end - start
        count = _frame_count(duration)
        for part in range(count):
            frame_start = start + duration * part / count
            frame_end = start + duration * (part + 1) / count
            frame_number = len(frames) + 1
            wants_variation = part > 0 or (
                bool(frames) and beat.get("image_mode") == "variation"
            )
            is_variation = (
                bool(frames)
                and wants_variation
                and variation_depth < 2
            )
            variation_depth = variation_depth + 1 if is_variation else 0
            frame = {
                "n": frame_number,
                "beat_n": beat["n"],
                "start": round(frame_start, 3),
                "end": round(frame_end, 3),
                "duration": round(frame_end - frame_start, 3),
                "output_slot": f"frame-{frame_number:03d}",
                "image_mode": "variation" if is_variation else "new",
                "generation_wave": variation_depth,
            }
            if is_variation:
                frame["variation_of_frame"] = frame_number - 1
                frame["reference_output_slot"] = f"frame-{frame_number - 1:03d}"
                frame["change_only"] = (
                    str(beat.get("change_only") or "advance the named action")
                )
            frames.append(frame)

    generation_waves = [
        {
            "wave": wave,
            "output_slots": [
                frame["output_slot"]
                for frame in frames
                if frame["generation_wave"] == wave
            ],
        }
        for wave in range(3)
        if any(frame["generation_wave"] == wave for frame in frames)
    ]

    return {
        **script,
        "manifest_version": 2,
        "narration": {
            "audio_duration_seconds": round(audio_duration, 3),
            "alignment_similarity": round(similarity, 4),
            "timeline_source": "whisper_word_timestamps",
        },
        "frames": frames,
        "generation_waves": generation_waves,
    }


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--timestamps", required=True, type=Path)
    parser.add_argument("--audio-duration", required=True, type=float)
    parser.add_argument("--requested-duration", type=float)
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    script = json.loads(arguments.script.read_text())
    timestamps = json.loads(arguments.timestamps.read_text())
    manifest = build_scene_manifest(
        script,
        timestamps,
        arguments.audio_duration,
        arguments.requested_duration,
    )
    temporary = arguments.out.with_suffix(arguments.out.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(arguments.out)
    print(
        json.dumps(
            {
                "valid": True,
                "manifest_version": 2,
                "beats": len(manifest["beats"]),
                "frames": len(manifest["frames"]),
                "duration_seconds": arguments.audio_duration,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
