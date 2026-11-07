#!/usr/bin/env python3
"""Build timed captions using authored text and Whisper's word clock.

Whisper supplies timing only when a script manifest is available. Caption text
is aligned back to the exact ``vo_line``/``phrase`` values, preventing
transcription substitutions from being burned into generated videos.
"""

from __future__ import annotations

import argparse
import difflib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any


NORMALIZE_PATTERN = re.compile(r"[^\w]+", re.UNICODE)
TOKEN_PATTERN = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*[.,!?;:]?", re.UNICODE)
NONVERBAL_DIRECTION_PATTERN = re.compile(r"\[[^\]]+\]")


def _normalize(value: str) -> str:
    return NORMALIZE_PATTERN.sub("", value.casefold())


def _load_authored_rows(script_path: Path) -> list[list[str]]:
    """Authored tokens, kept GROUPED BY ROW (one row = one block or beat).

    The grouping is what lets the per-block path align each line inside its own
    block window: a word the STT swallowed can then only be interpolated across
    that block's speech, never across the silence between two blocks.
    """
    payload = json.loads(script_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("script manifest must be an object")

    rows = payload.get("beats")
    fields = ("phrase", "vo_line")
    if not isinstance(rows, list):
        rows = payload.get("blocks")
        fields = ("vo_line",)
    if not isinstance(rows, list) or not rows:
        raise ValueError("script manifest must contain blocks or beats")

    grouped: list[list[str]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"script row {index} must be an object")
        text = next(
            (
                row[field].strip()
                for field in fields
                if isinstance(row.get(field), str) and row[field].strip()
            ),
            "",
        )
        if not text:
            raise ValueError(f"script row {index} has no authored narration")
        spoken_text = NONVERBAL_DIRECTION_PATTERN.sub("", text)
        grouped.append(TOKEN_PATTERN.findall(spoken_text))
    if not any(grouped):
        raise ValueError("script manifest contains no authored narration words")
    return grouped


def _load_authored_tokens(script_path: Path) -> list[str]:
    return [token for row in _load_authored_rows(script_path) for token in row]


def _timed_script_span(
    script_tokens: list[str],
    *,
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    if not script_tokens:
        return []
    duration = max(end - start, 0.05 * len(script_tokens))
    weights = [max(len(_normalize(token)), 1) for token in script_tokens]
    total_weight = sum(weights)
    timed: list[dict[str, Any]] = []
    cursor = start
    for index, (token, weight) in enumerate(zip(script_tokens, weights)):
        token_end = (
            end
            if index == len(script_tokens) - 1
            else cursor + duration * weight / total_weight
        )
        timed.append(
            {
                "word": token,
                "start": round(cursor, 3),
                "end": round(max(token_end, cursor + 0.01), 3),
            }
        )
        cursor = token_end
    return timed


def align_words_to_script(
    words: list[dict[str, Any]],
    script_tokens: list[str],
    *,
    minimum_similarity: float = 0.55,
    span_floor: float = 0.0,
    span_ceiling: float | None = None,
) -> tuple[list[dict[str, Any]], float]:
    """Return exact script tokens carrying timings derived from Whisper words.

    `span_floor` / `span_ceiling` bound where an INTERPOLATED span may live when
    the STT dropped words at the very start or end of this text (VAD eats quiet
    openers like "you know?"). Without them a dropped opener is spread from 0.0 —
    or from the previous block's last word — and the caption shows up seconds
    before it is spoken. Callers that align one block at a time pass that block's
    speech window.
    """
    whisper_tokens = [_normalize(str(word["word"])) for word in words]
    normalized_script_tokens = [_normalize(token) for token in script_tokens]
    matcher = difflib.SequenceMatcher(
        a=whisper_tokens,
        b=normalized_script_tokens,
        autojunk=False,
    )
    similarity = matcher.ratio()
    if similarity < minimum_similarity:
        raise ValueError(
            f"Whisper/script similarity {similarity:.3f} is below "
            f"{minimum_similarity:.3f}; refusing to burn unverified captions"
        )

    aligned: list[dict[str, Any]] = []
    for tag, whisper_start, whisper_end, script_start, script_end in matcher.get_opcodes():
        authored_span = script_tokens[script_start:script_end]
        if not authored_span:
            continue

        if tag == "equal":
            for offset, token in enumerate(authored_span):
                timed_word = words[whisper_start + offset]
                aligned.append(
                    {
                        "word": token,
                        "start": float(timed_word["start"]),
                        "end": float(timed_word["end"]),
                    }
                )
            continue

        if whisper_end > whisper_start:
            span_start = float(words[whisper_start]["start"])
            span_end = float(words[whisper_end - 1]["end"])
        else:
            previous_end = (
                float(words[whisper_start - 1]["end"])
                if whisper_start > 0
                else span_floor
            )
            next_start = (
                float(words[whisper_start]["start"])
                if whisper_start < len(words)
                else previous_end + 0.05 * len(authored_span)
            )
            span_start = max(previous_end, span_floor)
            span_end = max(next_start, span_start + 0.05 * len(authored_span))
            if span_ceiling is not None:
                span_end = min(span_end, max(span_ceiling, span_start + 0.01))
        aligned.extend(
            _timed_script_span(
                authored_span,
                start=span_start,
                end=span_end,
            )
        )

    if [_normalize(str(word["word"])) for word in aligned] != normalized_script_tokens:
        raise ValueError("caption alignment did not preserve the complete authored script")
    return aligned, similarity


def group_captions(
    words: list[dict[str, Any]],
    *,
    max_words: int = 5,
    max_gap: float = 0.5,
    max_chars: int = 32,
    min_duration: float = 0.0,
    max_cps: float = 0.0,
) -> list[dict[str, Any]]:
    if not all(math.isfinite(value) and value >= 0 for value in (min_duration, max_cps)):
        raise ValueError("caption readability limits must be finite and nonnegative")
    if min_duration or max_cps:
        return _readable_captions(
            words,
            max_words=max_words,
            max_gap=max_gap,
            max_chars=max_chars,
            min_duration=min_duration,
            max_cps=max_cps,
        )
    captions: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    def _flush() -> None:
        if not current:
            return
        text = " ".join(str(word["word"]).strip() for word in current).strip()
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        captions.append(
            {
                "text": text,
                "start": round(float(current[0]["start"]), 2),
                "end": round(float(current[-1]["end"]), 2),
            }
        )
        current.clear()

    for word in words:
        if current:
            gap = float(word["start"]) - float(current[-1]["end"])
            projected_text = " ".join(
                [*(str(item["word"]) for item in current), str(word["word"])]
            )
            if (
                gap >= max_gap
                or len(current) >= max_words
                or len(projected_text) > max_chars
            ):
                _flush()
        current.append(word)
        if re.search(r"[.!?]$", str(word["word"]).strip()):
            _flush()
    _flush()
    return captions


def _readable_captions(
    words: list[dict[str, Any]],
    *,
    max_words: int,
    max_gap: float,
    max_chars: int,
    min_duration: float,
    max_cps: float,
) -> list[dict[str, Any]]:
    """Partition speech on existing word boundaries, never by stretching cues.

    A greedy four-word cut can strand a 0.26s final word. Look ahead within
    each sentence/pause-delimited span to find a readable partition instead.
    Keep the fewest cues; on ties prefer the longer opening phrase.
    """
    if max_words < 1 or max_chars < 1 or not math.isfinite(max_gap) or max_gap <= 0:
        raise ValueError("caption word, character and gap limits must be positive")
    spans: list[list[dict[str, Any]]] = []
    for word in words:
        start, end = float(word["start"]), float(word["end"])
        if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end < start:
            raise ValueError("caption word timings must be finite, ordered and nonnegative")
        if not spans or (
            start - float(spans[-1][-1]["end"]) >= max_gap
            or re.search(r"[.!?]$", str(spans[-1][-1]["word"]).strip())
        ):
            spans.append([])
        spans[-1].append(word)

    captions: list[dict[str, Any]] = []
    for span in spans:
        count = len(span)
        costs = [count + 1] * count + [0]
        choices: dict[int, tuple[int, dict[str, Any]]] = {}
        for start_index in range(count - 1, -1, -1):
            for stop in range(start_index + 1, min(count, start_index + max_words) + 1):
                text = " ".join(str(word["word"]).strip() for word in span[start_index:stop])
                text = re.sub(r"\s+([,.!?;:])", r"\1", text)
                if len(text) > max_chars:
                    break
                start = round(float(span[start_index]["start"]), 2)
                end = round(float(span[stop - 1]["end"]), 2)
                duration = end - start
                if duration <= 0 or duration + 1e-6 < min_duration:
                    continue
                if max_cps and len(text) > max_cps * duration + 1e-6:
                    continue
                if costs[stop] < count + 1 and 1 + costs[stop] <= costs[start_index]:
                    costs[start_index] = 1 + costs[stop]
                    choices[start_index] = (stop, {"text": text, "start": start, "end": end})
        if 0 not in choices:
            raise ValueError(
                f"no readable caption grouping for speech at {span[0]['start']}s "
                f"under {max_words} words/{max_chars} chars, {min_duration}s minimum "
                f"and {max_cps or 'unlimited'} chars/s; inspect the word timings "
                "or speech pace, do not invent times or extend through a pause"
            )
        index = 0
        while index < count:
            index, caption = choices[index]
            captions.append(caption)
    return captions


def _timestamp(seconds: float) -> str:
    total_milliseconds = int(round(seconds * 1000))
    hours, remaining_milliseconds = divmod(total_milliseconds, 3_600_000)
    minutes, remaining_milliseconds = divmod(remaining_milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(remaining_milliseconds, 1000)
    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},"
        f"{milliseconds:03d}"
    )


def to_srt(captions: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"{index}\n{_timestamp(caption['start'])} --> "
        f"{_timestamp(caption['end'])}\n{caption['text']}\n"
        for index, caption in enumerate(captions, start=1)
    )


def _words_faster(
    path: Path,
    model_size: str,
    *,
    language: str | None = None,
) -> list[dict[str, Any]]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8", local_files_only=True)
    # vad_filter drops music/room-tone stretches instead of hallucinating words
    # over them; condition_on_previous_text=False stops one bad segment from
    # dragging the rest of the transcript out of sync (the classic caption
    # drift). beam_size=5 recovers words a greedy pass swallows.
    segments, _info = model.transcribe(
        str(path),
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
        beam_size=5,
        language=language,
    )
    words: list[dict[str, Any]] = []
    for segment in segments:
        for word in segment.words or []:
            words.append(
                {
                    "word": str(word.word).strip(),
                    "start": float(word.start),
                    "end": float(word.end),
                }
            )
    return words


def _speech_only(path: Path) -> Path | None:
    """Voice-band copy of a MIXED track (video with music + SFX).

    Whisper loses words and drifts when a bed and diegetic SFX sit under the
    narration. Band-passing to the voice range and levelling first recovers
    most of them. Returns None when ffmpeg is unavailable — callers fall back
    to the original file.
    """
    import shutil
    import subprocess
    import tempfile

    if shutil.which("ffmpeg") is None:
        return None
    target = Path(tempfile.mkdtemp(prefix="caps_")) / "speech.wav"
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-vn",
        "-af",
        "highpass=f=180,lowpass=f=3800,dynaudnorm=f=250:g=15",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(target),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        shutil.rmtree(target.parent)
        return None
    if target.is_file() and target.stat().st_size > 0:
        return target
    shutil.rmtree(target.parent)
    return None


def get_words(
    path: Path,
    model_size: str,
    *,
    language: str | None = None,
    mixed_input: bool = False,
) -> tuple[list[dict[str, Any]], str]:
    source = path
    if mixed_input:
        cleaned = _speech_only(path)
        if cleaned is not None:
            source = cleaned
            print("(band-passed the mixed track before STT)", file=sys.stderr)
    try:
        return _words_faster(source, model_size, language=language), "faster-whisper"
    finally:
        if source != path:
            import shutil
            shutil.rmtree(source.parent)


def _load_blocks(sidecar_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
    blocks = payload.get("per_block")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("assembly sidecar has no per_block array")
    timed = [
        block
        for block in blocks
        if isinstance(block, dict)
        and isinstance(block.get("voice"), str)
        and block["voice"]
        and float(block.get("speech_s") or 0) > 0
    ]
    if not timed:
        raise ValueError(
            "assembly sidecar carries no voiced blocks (song mode has no narration "
            "to caption)"
        )
    for block in timed:
        if "speech_abs_s" not in block:
            raise ValueError(
                "assembly sidecar predates speech_abs_s — re-run the assembler "
                "so captions can be timed from the clean voice files"
            )
    return timed


def words_from_blocks(
    blocks: list[dict[str, Any]],
    voice_dir: Path,
    model_size: str,
    *,
    language: str | None = None,
) -> list[dict[str, Any]]:
    """Time words on the CLEAN per-block voice files, then shift into the
    finished timeline: t_final = speech_abs_s + (t_word - lead_silence_s).

    This is the accurate path: no music or SFX under the narration, and the
    offsets come from the assembler's own centring math instead of being
    re-estimated from the mix.
    """
    groups: list[dict[str, Any]] = []
    for block in blocks:
        voice_path = voice_dir / str(block["voice"])
        if not voice_path.is_file():
            raise ValueError(f"voice file missing for block {block.get('n')}: {voice_path}")
        offset = float(block["speech_abs_s"])
        lead = float(block.get("lead_silence_s") or 0.0)
        block_words = _words_faster(voice_path, model_size, language=language)
        if not block_words:
            raise ValueError(
                f"no words transcribed for block {block.get('n')} ({voice_path.name})"
            )
        shifted: list[dict[str, Any]] = []
        for word in block_words:
            start = offset + (float(word["start"]) - lead)
            end = offset + (float(word["end"]) - lead)
            shifted.append(
                {
                    "word": word["word"],
                    "start": round(max(start, 0.0), 3),
                    "end": round(max(end, start + 0.01), 3),
                }
            )
        shifted.sort(key=lambda word: float(word["start"]))
        speech_seconds = float(block.get("speech_s") or 0.0)
        speech_end = (
            offset + speech_seconds
            if speech_seconds > 0
            else float(shifted[-1]["end"])
        )
        groups.append(
            {
                "n": block.get("n"),
                "words": shifted,
                "speech_start": round(offset, 3),
                "speech_end": round(max(speech_end, float(shifted[-1]["end"])), 3),
            }
        )
    return groups


def align_blocks_to_script(
    groups: list[dict[str, Any]],
    rows: list[list[str]],
    *,
    minimum_similarity: float,
) -> tuple[list[dict[str, Any]], float]:
    """Align the authored text ONE BLOCK AT A TIME, inside that block's window.

    Aligning the whole timeline at once lets a missing opener borrow the silence
    between two blocks, so the caption fires before the speech. Per block, an
    interpolated span is clamped to `[speech_start, speech_end]` of the block that
    actually contains those words.
    """
    aligned: list[dict[str, Any]] = []
    weighted_similarity = 0.0
    token_count = 0
    worst_similarity = 1.0
    worst_block: Any = None
    if len(groups) != len(rows):
        raise ValueError("script and audio block counts differ")
    for group, tokens in zip(groups, rows):
        if not tokens:
            raise ValueError(f"block {group['n']} has no authored narration")
        try:
            block_aligned, block_similarity = align_words_to_script(
                group["words"],
                tokens,
                minimum_similarity=minimum_similarity,
                span_floor=float(group["speech_start"]),
                span_ceiling=float(group["speech_end"]),
            )
        except ValueError as error:
            raise ValueError(f"block {group['n']}: {error}") from error
        aligned.extend(block_aligned)
        weighted_similarity += block_similarity * len(tokens)
        token_count += len(tokens)
        if block_similarity < worst_similarity:
            worst_similarity = block_similarity
            worst_block = group["n"]
    if worst_block is not None and worst_similarity < 0.9:
        print(
            f"WARN: block {worst_block} matched only {worst_similarity:.2%} of its "
            "authored line — that block's word timings are partly interpolated "
            "(they stay inside its own speech window). Consider --model medium.",
            file=sys.stderr,
        )
    return aligned, (weighted_similarity / token_count if token_count else 1.0)


def _resolve_script_path(explicit_path: Path | None) -> Path | None:
    if explicit_path is not None:
        return explicit_path
    default_path = Path("script_manifest.json")
    return default_path if default_path.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--srt", type=Path)
    parser.add_argument(
        "--script",
        type=Path,
        help=(
            "Authored script manifest. Defaults to ./script_manifest.json "
            "when present."
        ),
    )
    parser.add_argument(
        "--per-block",
        type=Path,
        help=(
            "final.mp4.assembly.json — time the words on the CLEAN per-block "
            "voice files and shift them by the assembler's own offsets. The "
            "accurate path: no music/SFX under the narration."
        ),
    )
    parser.add_argument(
        "--voice-dir",
        type=Path,
        default=Path("."),
        help="Directory holding the voiceNN.wav files named in the sidecar.",
    )
    parser.add_argument(
        "--language",
        help="Language hint (e.g. en, ru). Stops the STT guessing on short takes.",
    )
    parser.add_argument(
        "--mixed",
        action="store_true",
        help=(
            "The input carries music/SFX under the speech — band-pass to the "
            "voice range before STT. Implied when captioning a finished video."
        ),
    )
    parser.add_argument("--max-words", type=int, default=5)
    parser.add_argument("--max-chars", type=int, default=32)
    parser.add_argument("--max-gap", type=float, default=0.4)
    parser.add_argument(
        "--min-duration", type=float, default=0.0,
        help="Minimum readable cue seconds; regroup using word timings (0 disables).",
    )
    parser.add_argument(
        "--max-cps", type=float, default=0.0,
        help="Maximum characters per second per cue (0 disables).",
    )
    parser.add_argument("--model", default="small")
    parser.add_argument("--minimum-similarity", type=float, default=0.75)
    arguments = parser.parse_args()

    groups: list[dict[str, Any]] | None = None
    if arguments.per_block is not None:
        try:
            blocks = _load_blocks(arguments.per_block)
            groups = words_from_blocks(
                blocks,
                arguments.voice_dir,
                arguments.model,
                language=arguments.language,
            )
            words = [word for group in groups for word in group["words"]]
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"ERROR: per-block timing failed: {error}", file=sys.stderr)
            return 1
        provider = "faster-whisper/per-block"
    else:
        words, provider = get_words(
            arguments.audio,
            arguments.model,
            language=arguments.language,
            mixed_input=arguments.mixed,
        )

    script_path = _resolve_script_path(arguments.script)
    similarity: float | None = None
    if script_path is not None:
        try:
            rows = _load_authored_rows(script_path)
            if groups is not None and len(rows) == len(groups):
                # Per-block: each line is aligned inside its own speech window.
                words, similarity = align_blocks_to_script(
                    groups,
                    rows,
                    minimum_similarity=arguments.minimum_similarity,
                )
            else:
                if groups is not None:
                    raise ValueError("script and audio block counts differ")
                words, similarity = align_words_to_script(
                    words,
                    [token for row in rows for token in row],
                    minimum_similarity=arguments.minimum_similarity,
                )
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"ERROR: authored caption alignment failed: {error}", file=sys.stderr)
            return 1
        if similarity is not None and similarity < 0.9:
            print(
                f"WARN: the STT only matched {similarity:.2%} of the authored script — "
                "wording is correct (taken from the manifest) but some timings are "
                "interpolated. Prefer --per-block on clean voice files, or a larger "
                "--model, before shipping.",
                file=sys.stderr,
            )

    try:
        captions = group_captions(
            words,
            max_words=arguments.max_words,
            max_gap=arguments.max_gap,
            max_chars=arguments.max_chars,
            min_duration=arguments.min_duration,
            max_cps=arguments.max_cps,
        )
    except ValueError as error:
        print(f"ERROR: caption grouping failed: {error}", file=sys.stderr)
        return 1

    # Coverage report: every timed word must survive into a caption, and a
    # suspiciously thin transcript (words per second of covered speech) means
    # the STT swallowed words — the caller must not ship that silently.
    caption_words = sum(len(str(caption["text"]).split()) for caption in captions)
    span = (
        float(captions[-1]["end"]) - float(captions[0]["start"]) if captions else 0.0
    )
    density = caption_words / span if span > 0 else 0.0
    if caption_words != len(words):
        print(
            f"ERROR: {len(words)} timed words but {caption_words} made it into "
            "captions — refusing to write a lossy caption file.",
            file=sys.stderr,
        )
        return 1
    if script_path is None and span > 5 and density < 1.6:
        print(
            f"WARN: only {density:.2f} words/second over {span:.1f}s — the STT likely "
            "dropped words. Re-run with --model medium (and --language), or pass "
            "--script/--per-block, before burning.",
            file=sys.stderr,
        )

    print(
        f"provider={provider} words={len(words)} captions={len(captions)} "
        f"caption_words={caption_words} density={density:.2f}/s "
        f"script_aligned={script_path is not None} similarity={similarity}",
        file=sys.stderr,
    )

    output = {
        "words": words,
        "captions": captions,
        "script_aligned": script_path is not None,
        "similarity": similarity,
        "timed_words": len(words),
        "caption_words": caption_words,
        "words_per_second": round(density, 2),
        "provider": provider,
    }
    serialized_output = json.dumps(output, indent=2, ensure_ascii=False)
    print(serialized_output)
    if arguments.json is not None:
        arguments.json.write_text(serialized_output, encoding="utf-8")
    if arguments.srt is not None:
        arguments.srt.write_text(to_srt(captions), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
