#!/usr/bin/env python3
"""Validate the requested song duration and prompt."""

from __future__ import annotations

import argparse
import json
import re
import sys

MAX_PROMPT_CHARS = 2048
ALLOWED_BPM = {100, 112}
TARGET_SYLLABLES = 8
ALLOWED_DURATION_SECONDS = frozenset({60, 120})

REQUIRED_CLAUSES: tuple[tuple[str, str], ...] = (
    (r"steady|constant", "state that the beat is STEADY AND CONSTANT from first second to last"),
    (r"\b4/4\b", "state the simple 4/4 metre"),
    (r"no\s+tempo\s+changes?", 'state "NO tempo changes"'),
    (r"8\s+syllables|eight\s+syllables", "state the 8-syllable line law"),
    (r"one\s+syllable\s+per\s+beat", 'state "one syllable per beat"'),
    (r"beat\s+one", "state that every line starts on beat one of its bar"),
    (r"4-?bar|four-?bar", "state the 4-bar phrase law"),
    (r"chorus", "name the chorus sections"),
    (r"verbatim|repeat", "state that the chorus repeats verbatim"),
)

BANNED_TEMPO = (
    "bridge",
    "slow down",
    "slowdown",
    "speed up",
    "speedup",
    "ritardando",
    "accelerando",
    "tempo change",
    "key change",
    "breakdown",
    "half-time",
    "double-time",
    "drop",
)
BANNED_GROOVE = (
    "four-on-the-floor",
    "four on the floor",
    "syncopation",
    "syncopated",
    "swung",
    "shuffle groove",
)

VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.IGNORECASE)
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)


def _syllables(word: str) -> int:
    """Cheap English syllable estimate — good enough to catch a wandering line."""
    word = word.lower().strip("'")
    if not word:
        return 0
    groups = VOWEL_GROUPS.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1 and not word.endswith(("le", "ee", "ye")):
        count -= 1
    return max(1, count)


def _line_syllables(line: str) -> int:
    return sum(_syllables(word) for word in WORD.findall(line))


def _lyric_lines(prompt: str) -> list[str]:
    lines: list[str] = []
    for quoted in re.findall(r'"([^"]{10,})"', prompt):
        for part in re.split(r"\s*(?:/|\||\n)\s*", quoted):
            part = part.strip(" ,.;:!?-")
            if len(WORD.findall(part)) >= 3 or (not any(c.isspace() for c in part) and sum(c.isalpha() for c in part) >= 4):
                lines.append(part)
    return lines


NEGATED = re.compile(
    r"\bno\s+(?:tempo\s+changes?|key\s+changes?|slow\s?downs?|speed\s?ups?|breakdowns?|drops?|bridges?)",
    re.IGNORECASE,
)
SYLLABLE_TOLERANCE = 1
MAX_OFF_METER_SHARE = 0.25
GROSS_SYLLABLE_MISS = 4


def validate_duration(duration_seconds: int) -> dict:
    valid = type(duration_seconds) is int and duration_seconds in ALLOWED_DURATION_SECONDS
    return {
        "valid": valid,
        "duration_seconds": duration_seconds,
        "errors": [] if valid else [
            "Song mode supports only 60 or 120 seconds. Keep the original requested "
            "duration; ask for a supported length when clarification is available, "
            "otherwise stop and explain the unsupported duration. Do not generate a shorter song."
        ],
    }


def validate(
    prompt: str,
    *,
    duration_seconds: int,
    target_syllables: int = TARGET_SYLLABLES,
    lyrics_language: str = "en",
) -> dict:
    errors = validate_duration(duration_seconds)["errors"]
    lowered = prompt.casefold()
    scannable = NEGATED.sub(" ", lowered)

    declared_minutes = re.search(r"\ba full (\d+)-minute\b", lowered)
    if declared_minutes is None or int(declared_minutes.group(1)) * 60 != duration_seconds:
        errors.append(
            "Start the song prompt with 'A full 1-minute' or 'A full 2-minute' "
            "matching the original requested duration; do not replace it with a shorter length"
        )

    if len(prompt) > MAX_PROMPT_CHARS:
        errors.append(
            f"prompt is {len(prompt)} characters, over the {MAX_PROMPT_CHARS} limit — "
            "trim instrument adjectives first, never the meter laws or the lyrics"
        )

    bpm_values = {int(value) for value in re.findall(r"(\d{2,3})\s*bpm", lowered)}
    if not bpm_values:
        errors.append("no BPM stated — name one constant tempo (100 gentle / 112 dance-along)")
    elif len(bpm_values) > 1:
        errors.append(
            "more than one BPM in the prompt ("
            + ", ".join(str(value) for value in sorted(bpm_values))
            + ") — one constant tempo only"
        )
    elif not bpm_values <= ALLOWED_BPM:
        errors.append(
            f"BPM {bpm_values.pop()} is untested — use 100 (gentle) or 112 (dance-along)"
        )

    for pattern, message in REQUIRED_CLAUSES:
        if not re.search(pattern, lowered):
            errors.append(f"missing clause: {message}")

    for phrase in BANNED_TEMPO:
        if phrase in scannable:
            errors.append(
                f'banned tempo word "{phrase}" — dynamics come from orchestration '
                "(fuller final chorus, extra claps), never from tempo"
            )
    for phrase in BANNED_GROOVE:
        if phrase in scannable:
            errors.append(
                f'banned groove jargon "{phrase}" — describe claps and instruments plainly'
            )

    lyrics = _lyric_lines(prompt)
    if not lyrics:
        errors.append("no quoted lyric lines found — the verses and chorus go in the prompt")
    elif lyrics_language in {"en", "ru"}:
        count_line = _line_syllables if lyrics_language == "en" else lambda line: len(re.findall(r"[аеёиоуыэюя]", line.casefold()))
        off = [
            f'"{line}" ({count_line(line)})'
            for line in lyrics
            if abs(count_line(line) - target_syllables) > SYLLABLE_TOLERANCE
        ]
        gross = [
            f'"{line}" ({count_line(line)})'
            for line in lyrics
            if abs(count_line(line) - target_syllables) >= GROSS_SYLLABLE_MISS
        ]
        if gross:
            errors.append(
                f"lyric line(s) nowhere near the {target_syllables}-syllable meter — they "
                "cannot land one syllable per beat: "
                + "; ".join(gross[:6])
                + (" …" if len(gross) > 6 else "")
            )
        elif len(off) > max(1, int(len(lyrics) * MAX_OFF_METER_SHARE)):
            errors.append(
                f"{len(off)} of {len(lyrics)} lyric lines miss the {target_syllables}-syllable "
                "meter by two or more — the wandering meter is what makes the beat sound "
                "broken; rewrite them: "
                + "; ".join(off[:6])
                + (" …" if len(off) > 6 else "")
            )

    return {
        "valid": not errors,
        "duration_seconds": duration_seconds,
        "characters": len(prompt),
        "bpm": sorted(bpm_values),
        "lyric_lines": len(lyrics),
        "manual_meter_review_required": lyrics_language not in {"en", "ru"},
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration-seconds", type=int, required=True,
                        help="original requested duration, exactly 60 or 120 seconds")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prompt", help="file holding the song prompt")
    mode.add_argument("--duration-only", action="store_true",
                      help="check the request before writing lyrics or generating assets")
    parser.add_argument("--syllables", type=int, default=TARGET_SYLLABLES)
    parser.add_argument("--lyrics-language", default="en", help="ISO language code; other languages require manual meter review")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_duration(args.duration_seconds)
    if result["valid"] and not args.duration_only:
        with open(args.prompt, encoding="utf-8") as handle:
            prompt = handle.read()
        result = validate(prompt, duration_seconds=args.duration_seconds,
                          target_syllables=args.syllables, lyrics_language=args.lyrics_language.casefold())
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"valid: {result['valid']}  duration seconds: {result['duration_seconds']}")
        if "characters" in result:
            print(f"chars: {result['characters']}  bpm: {result['bpm']}  "
                  f"lyric lines: {result['lyric_lines']}")
        if result.get("manual_meter_review_required"):
            print("Manual lyric meter review required for this language.")
        for error in result["errors"]:
            print(f"  - {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
