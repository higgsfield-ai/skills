#!/usr/bin/env python3
"""Validate fully-animated faceless script gates before generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


WORD_PATTERN = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*", re.UNICODE)
TTS_WRAPPER_PATTERN = re.compile(r"^\s*\[|\[\s*00:\d{2}(?::\d{2})?-", re.UNICODE)
ARC_ROLES = {"hook", "build", "turn", "payoff"}

DEFAULT_WORD_BUDGET = (20, 23)
DURATION_RETRY_WORD_MIN = 17
SPEECH_TARGET_WINDOW = (7.8, 9.5)
SPEECH_HARD_WINDOW = (7.2, 9.5)
WORD_BUDGETS = {"kids": (17, 21)}   # a child needs room to follow, so Kids sits one

MAX_SENTENCES_PER_LINE = 2
SENTENCE_SPLIT_PATTERN = re.compile(r"[.!?]+(?:\s|$)", re.UNICODE)

DIGIT_PATTERN = re.compile(r"\d", re.UNICODE)

DIALOGUE_WORD_BUDGET = (16, 22)
BLOCK_KINDS = {"narration", "dialogue"}
MAX_DIALOGUE_SPEAKERS = 2

FILLER_PATTERN = re.compile(
    r"\b(?:you\s+know|y'?know|i\s+mean|sort\s+of|kinda|basically|um+|uh+|erm)\b",
    re.IGNORECASE | re.UNICODE,
)

REPEAT_WINDOW = 6
REPEAT_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "did", "do",
    "does", "for", "from", "had", "has", "have", "he", "her", "here", "his",
    "how", "i", "if", "in", "into", "is", "it", "its", "just", "me", "my", "no",
    "not", "of", "on", "one", "or", "our", "out", "over", "she", "so", "than",
    "that", "the", "their", "them", "then", "there", "these", "they", "this",
    "those", "to", "up", "was", "we", "were", "what", "when", "why", "will",
    "with", "would", "you", "your",
}


SHARED_PHRASE_WORDS = 5
MAX_REPORTED_SHARED_PHRASES = 6

SHOT_SIZE_VOCABULARY = {
    "ecu": "ECU",
    "xcu": "ECU",
    "extreme close-up": "ECU",
    "close-up": "CU",
    "closeup": "CU",
    "cu": "CU",
    "macro": "MACRO",
    "detail": "DETAIL",
    "insert": "DETAIL",
    "medium": "MEDIUM",
    "mid": "MEDIUM",
    "ms": "MEDIUM",
    "ots": "OTS",
    "over-the-shoulder": "OTS",
    "two-shot": "TWO-SHOT",
    "wide": "WIDE",
    "full-spread": "WIDE",
    "full spread": "WIDE",
    "establishing": "WIDE",
    "master": "WIDE",
    "overhead": "TOP",
    "top-down": "TOP",
    "aerial": "TOP",
}
ESTABLISHING_SHOT_SIZES = {"WIDE", "TOP"}
SHOT_SIZE_LEAD_CHARACTERS = 48
SHARED_SHOT_WORDS = 8
NEAR_BLOCK_DISTANCE = 3
HOOK_SENTENCE_WORDS = 8
HOOK_SENTENCE_GENRES = {"education", "history"}
_SHOT_SIZE_PATTERN = re.compile(
    "|".join(
        rf"\b{re.escape(key)}\b"
        for key in sorted(SHOT_SIZE_VOCABULARY, key=len, reverse=True)
    ),
    re.IGNORECASE,
)


NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
    "billion", "trillion", "first", "second", "third", "fourth", "fifth", "sixth",
    "seventh", "eighth", "ninth", "tenth", "half", "quarter", "dozen",
}


def _word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def _normalised_words(text: str) -> list[str]:
    return [token.casefold() for token in WORD_PATTERN.findall(text)]


def _longest_shared_run(left: list[str], right: list[str]) -> list[str]:
    """Longest verbatim word run present in both lines."""
    best_end = 0
    best_length = 0
    previous = [0] * (len(right) + 1)
    for left_index in range(1, len(left) + 1):
        current = [0] * (len(right) + 1)
        for right_index in range(1, len(right) + 1):
            if left[left_index - 1] == right[right_index - 1]:
                current[right_index] = previous[right_index - 1] + 1
                if current[right_index] > best_length:
                    best_length = current[right_index]
                    best_end = left_index
        previous = current
    if best_length < SHARED_PHRASE_WORDS:
        return []
    return left[best_end - best_length : best_end]


def _shot_size(text: str) -> str | None:
    """Canonical framing size of a shot, read from the head of its description."""
    match = _SHOT_SIZE_PATTERN.search(text[:SHOT_SIZE_LEAD_CHARACTERS])
    if match is None:
        return None
    return SHOT_SIZE_VOCABULARY[match.group(0).casefold()]


def _first_sentence(text: str) -> str:
    parts = [part for part in SENTENCE_SPLIT_PATTERN.split(text.strip()) if part.strip()]
    return parts[0] if parts else text.strip()


def _narration_digest(script: Any) -> str:
    """Digest of the narration only, so formatting is free and words are locked."""
    blocks = script.get("blocks") if isinstance(script, dict) else None
    lines = []
    if isinstance(blocks, list):
        for block in blocks:
            line = block.get("vo_line") if isinstance(block, dict) else None
            lines.append(" ".join(_normalised_words(line if isinstance(line, str) else "")))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _script_lock(script: Any, duration_seconds: float) -> dict[str, Any]:
    blocks = script.get("blocks") if isinstance(script, dict) else None
    return {
        "narration_sha256": _narration_digest(script),
        "block_count": len(blocks) if isinstance(blocks, list) else 0,
        "duration_seconds": duration_seconds,
    }


def _sentence_count(text: str) -> int:
    parts = [part for part in SENTENCE_SPLIT_PATTERN.split(text.strip()) if part.strip()]
    return max(1, len(parts))


def _filler_hits(text: str) -> list[str]:
    seen: list[str] = []
    for match in FILLER_PATTERN.finditer(text):
        phrase = " ".join(match.group(0).split()).casefold()
        if phrase not in seen:
            seen.append(phrase)
    return seen


def _near_repeats(text: str) -> list[str]:
    tokens = [token.casefold() for token in WORD_PATTERN.findall(text)]
    repeats: list[str] = []
    for index, token in enumerate(tokens):
        if token in REPEAT_STOPWORDS or token in NUMBER_WORDS or len(token) < 3:
            continue
        if token in tokens[index + 1 : index + REPEAT_WINDOW] and token not in repeats:
            repeats.append(token)
    return repeats


def _is_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate(
    script: dict,
    duration_seconds: float,
    word_budget: tuple[int, int] | None = None,
    duration_retry_blocks: set[int] | None = None,
) -> dict:
    errors: list[str] = []
    invalid_blocks: list[dict[str, Any]] = []
    if not isinstance(script, dict):
        return {
            "valid": False,
            "errors": ["script must be an object"],
            "invalid_blocks": [],
        }

    duration_retry_blocks = duration_retry_blocks or set()
    genre = script.get("genre")
    if genre not in {"education", "history", "kids", "storytelling"}:
        errors.append(
            "genre must be education, history, kids, or storytelling"
        )

    talking_characters = script.get("talking_characters", False)
    if not isinstance(talking_characters, bool):
        errors.append("talking_characters must be a boolean")
        talking_characters = False
    if talking_characters and genre != "kids":
        errors.append("talking_characters is a Kids-only direction")

    expected_blocks = math.ceil(duration_seconds / 10)
    blocks = script.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        return {
            "valid": False,
            "errors": [*errors, "script must contain a non-empty blocks array"],
            "invalid_blocks": [],
        }
    if len(blocks) != expected_blocks:
        errors.append(
            f"block count {len(blocks)} does not match expected {expected_blocks}"
        )
    unknown_retry_blocks = sorted(
        block for block in duration_retry_blocks if block > len(blocks)
    )
    if unknown_retry_blocks:
        errors.append(
            "duration retry blocks do not exist: "
            + ", ".join(str(block) for block in unknown_retry_blocks)
        )

    through_line = script.get("through_line")
    if not isinstance(through_line, dict):
        errors.append("through_line must be an object")
        through_line = {}
    for field in ("name", "asset", "progression", "resolution"):
        value = through_line.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"through_line.{field} is required")
    through_line_asset = through_line.get("asset")

    cast = script.get("cast")
    cast_members: list[tuple[str, str]] = []
    if not isinstance(cast, list):
        errors.append(
            "cast must be an array of {name, asset} — the characters Phase 2 generated; "
            "use [] only for a video with no characters"
        )
    else:
        for position, member in enumerate(cast, start=1):
            if not isinstance(member, dict):
                errors.append(f"cast[{position}] must be an object with name and asset")
                continue
            name = member.get("name")
            asset = member.get("asset")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"cast[{position}].name is required")
            if not isinstance(asset, str) or not asset.strip():
                errors.append(f"cast[{position}].asset is required")
            if isinstance(name, str) and name.strip() and isinstance(asset, str) and asset.strip():
                cast_members.append((name.strip(), asset.strip()))

    arc = script.get("arc")
    errors_before_arc = len(errors)
    if not isinstance(arc, dict):
        errors.append("arc must be an object")
        arc = {}
    if arc.get("hook") != 1:
        errors.append("arc.hook must be block 1")
    if arc.get("payoff") != expected_blocks:
        errors.append(f"arc.payoff must be block {expected_blocks}")
    if expected_blocks >= 3 and not isinstance(arc.get("turn"), int):
        errors.append("arc.turn must name the turn block")
    if not isinstance(arc.get("build"), list):
        errors.append("arc.build must be an array of build block numbers")
    if len(errors) > errors_before_arc:
        build_blocks = [
            index
            for index, block in enumerate(blocks, start=1)
            if isinstance(block, dict) and block.get("arc_role") == "build"
        ]
        errors.append(
            "expected arc shape, block numbers as integers and nothing else: "
            '{"hook": 1, "build": '
            + json.dumps(build_blocks or [2])
            + ', "turn": <block number>, "payoff": '
            + str(expected_blocks)
            + "} — there are no hook_block/build_blocks/turn_block keys and no prose "
            "in these fields; the arc text belongs in the blocks themselves"
        )

    sources = script.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be an array")
    elif any(not _is_http_url(source) for source in sources):
        errors.append("sources must contain only absolute HTTP URLs")
    elif genre in {"education", "history"} and not sources:
        errors.append("factual Education and History scripts require source URLs")

    expected_shot_count = 4 if genre == "kids" else 5
    locations: list[str | None] = []
    arc_roles: list[str | None] = []
    narration_lines: list[tuple[int, list[str]]] = []
    block_shot_sizes: list[tuple[int, str | None]] = []
    block_shot_texts: list[tuple[int, int, list[str]]] = []
    block_sizes_by_number: dict[int, tuple[str | None, ...]] = {}
    block_renders: list[tuple[int, str, tuple[str, ...]]] = []
    for index, raw_block in enumerate(blocks, start=1):
        if not isinstance(raw_block, dict):
            invalid_blocks.append(
                {"n": index, "errors": ["block must be an object"]}
            )
            locations.append(None)
            arc_roles.append(None)
            continue

        block_errors: list[str] = []
        if raw_block.get("n") != index:
            block_errors.append(f"n must be {index}")

        voice_line = raw_block.get("vo_line")
        word_count = _word_count(voice_line) if isinstance(voice_line, str) else 0
        if isinstance(voice_line, str) and voice_line.strip():
            narration_lines.append((index, _normalised_words(voice_line)))
        if not isinstance(voice_line, str) or not voice_line.strip():
            block_errors.append("vo_line is required")
        elif TTS_WRAPPER_PATTERN.search(voice_line):
            block_errors.append(
                "vo_line must contain authored narration only, without "
                "TTS delivery instructions or timecodes"
            )
        block_duration_seconds = 10.0
        if index == expected_blocks and duration_seconds % 10:
            block_duration_seconds = duration_seconds % 10

        block_kind = raw_block.get("block_kind")
        if talking_characters:
            expected_kind = "narration" if index % 2 else "dialogue"
            if block_kind is None:
                block_errors.append(
                    f"block_kind is required on a talking_characters run "
                    f"(expected '{expected_kind}')"
                )
            elif block_kind not in BLOCK_KINDS:
                block_errors.append("block_kind must be narration or dialogue")
            elif block_kind != expected_kind:
                block_errors.append(
                    f"block_kind must alternate: block {index} must be "
                    f"'{expected_kind}'"
                )
            speakers = raw_block.get("speakers")
            if block_kind == "dialogue":
                if not isinstance(speakers, list) or not speakers:
                    block_errors.append(
                        "a dialogue block must name its speakers (1-2 characters)"
                    )
                elif len(speakers) > MAX_DIALOGUE_SPEAKERS:
                    block_errors.append(
                        f"a dialogue block takes at most {MAX_DIALOGUE_SPEAKERS} "
                        "speaking characters"
                    )
            elif speakers:
                block_errors.append(
                    "a narration block has no on-screen speakers — the narrator is "
                    "off screen and every mouth stays closed"
                )
        elif block_kind is not None:
            block_errors.append(
                "block_kind belongs to talking_characters runs only"
            )

        if talking_characters and block_kind == "dialogue":
            budget_minimum, budget_maximum = DIALOGUE_WORD_BUDGET
        elif word_budget is not None:
            budget_minimum, budget_maximum = word_budget
        else:
            budget_minimum, budget_maximum = WORD_BUDGETS.get(
                genre if isinstance(genre, str) else "",
                DEFAULT_WORD_BUDGET,
            )
        if index in duration_retry_blocks:
            budget_minimum = min(budget_minimum, DURATION_RETRY_WORD_MIN)
        minimum_words = max(1, math.floor(budget_minimum * block_duration_seconds / 10))
        maximum_words = max(
            minimum_words, math.ceil(budget_maximum * block_duration_seconds / 10)
        )
        if (
            isinstance(voice_line, str)
            and voice_line.strip()
            and not minimum_words <= word_count <= maximum_words
        ):
            block_errors.append(
                f"vo_line must contain {minimum_words}-{maximum_words} words"
            )
        if isinstance(voice_line, str) and voice_line.strip():
            filler = _filler_hits(voice_line)
            if filler:
                block_errors.append(
                    "vo_line must not use conversational filler: "
                    + ", ".join(f'"{phrase}"' for phrase in filler)
                    + " — reach the word count with content, not padding"
                )
            sentences = _sentence_count(voice_line)
            if sentences > MAX_SENTENCES_PER_LINE:
                block_errors.append(
                    f"vo_line packs {sentences} sentences into one block — keep it to "
                    f"{MAX_SENTENCES_PER_LINE}; every extra period costs ~0.7s of dead "
                    "air and the voice rushes the words to compensate"
                )
            if DIGIT_PATTERN.search(voice_line):
                block_errors.append(
                    "vo_line contains digits — write numbers, dates and years as words "
                    '("nineteen seventy-seven"), they are spoken longer than written'
                )
            repeats = _near_repeats(voice_line)
            if repeats:
                block_errors.append(
                    "vo_line repeats "
                    + ", ".join(f'"{token}"' for token in repeats)
                    + f" within {REPEAT_WINDOW} words — stacked epithets read as "
                    "padding; keep one modifier per thing"
                )

        arc_role = raw_block.get("arc_role")
        if arc_role not in ARC_ROLES:
            block_errors.append("arc_role must be hook, build, turn, or payoff")
            arc_roles.append(None)
        else:
            arc_roles.append(arc_role)

        location = raw_block.get("location")
        if not isinstance(location, str) or not location.strip():
            block_errors.append("location is required")
            locations.append(None)
        else:
            locations.append(location.strip())

        through_line_state = raw_block.get("through_line_state")
        if not isinstance(through_line_state, str) or not through_line_state.strip():
            block_errors.append("through_line_state is required")

        shots = raw_block.get("shots")
        if not isinstance(shots, list) or len(shots) != expected_shot_count:
            block_errors.append(
                f"shots must contain exactly {expected_shot_count} entries"
            )
        elif any(not isinstance(shot, str) or not shot.strip() for shot in shots):
            block_errors.append("every shot must be a non-empty string")
        else:
            sizes: list[str | None] = []
            for shot_index, shot in enumerate(shots, start=1):
                size = _shot_size(shot)
                sizes.append(size)
                if size is None:
                    block_errors.append(
                        f"shot {shot_index} does not open with a framing size — start it "
                        "with one of WIDE / FULL-SPREAD / OVERHEAD / MEDIUM / OTS / CU / "
                        "ECU / MACRO / DETAIL, as in 'CU: the slat railing, dotted airflow "
                        "lines drifting past'"
                    )
                elif size == "OTS" and "shoulder" not in shot.casefold():
                    block_errors.append(
                        f"shot {shot_index} is an OTS but names no shoulder — an OTS needs "
                        "a visible character whose shoulder or head sits in the foreground; "
                        "over an object or a diagram it is just a medium shot"
                    )
            for shot_index in range(1, len(sizes)):
                previous, current = sizes[shot_index - 1], sizes[shot_index]
                if previous is not None and previous == current:
                    block_errors.append(
                        f"shots {shot_index} and {shot_index + 1} are both {current} — "
                        "every shot differs in SIZE and ANGLE from its neighbour, or the "
                        "block reads as one held plate"
                    )
            block_shot_sizes.append((index, sizes[0] if sizes else None))
            block_sizes_by_number[index] = tuple(sizes)
            for shot_index, shot in enumerate(shots, start=1):
                block_shot_texts.append((index, shot_index, _normalised_words(shot)))

        assets_used = raw_block.get("assets_used")
        if not isinstance(assets_used, list) or not assets_used:
            block_errors.append("assets_used must be a non-empty array")
        else:
            if len(assets_used) > 7:
                block_errors.append("assets_used must contain at most 7 entries")
            if (
                isinstance(through_line_asset, str)
                and through_line_asset not in assets_used
            ):
                block_errors.append(
                    "assets_used must include through_line.asset in every block"
                )
            block_tokens = set(_normalised_words(voice_line if isinstance(voice_line, str) else ""))
            for shot in shots if isinstance(shots, list) else []:
                if isinstance(shot, str):
                    block_tokens.update(_normalised_words(shot))
            for member_name, member_asset in cast_members:
                member_tokens = set(_normalised_words(member_name))
                if not member_tokens or not member_tokens <= block_tokens:
                    continue
                if member_asset not in assets_used:
                    block_errors.append(
                        f"this block names {member_name} but assets_used does not carry "
                        f"{member_asset} — a named character without their asset is a new "
                        f"character, so attach it or take the name out of the block"
                    )
            if isinstance(location, str) and location:
                block_renders.append(
                    (
                        index,
                        location,
                        tuple(
                            str(asset)
                            for asset in assets_used
                            if asset != through_line_asset
                        ),
                    )
                )

        if block_errors:
            invalid_blocks.append(
                {
                    "n": raw_block.get("n", index),
                    "word_count": word_count,
                    "errors": block_errors,
                }
            )

    if arc_roles:
        if arc_roles[0] != "hook":
            errors.append("the first block arc_role must be hook")
        if arc_roles[-1] != "payoff":
            errors.append("the final block arc_role must be payoff")
        if expected_blocks >= 3 and "turn" not in arc_roles[1:-1]:
            errors.append("the arc must contain a turn before the payoff")
        if expected_blocks >= 4 and "build" not in arc_roles[1:-1]:
            errors.append("the arc must contain a build block")
        if isinstance(arc.get("turn"), int):
            turn_index = arc["turn"] - 1
            if (
                turn_index < 0
                or turn_index >= len(arc_roles)
                or arc_roles[turn_index] != "turn"
            ):
                errors.append("arc.turn must point to a block with arc_role turn")
        if isinstance(arc.get("build"), list):
            declared_build_blocks = arc["build"]
            actual_build_blocks = [
                index
                for index, role in enumerate(arc_roles, start=1)
                if role == "build"
            ]
            if declared_build_blocks != actual_build_blocks:
                errors.append(
                    "arc.build must exactly match blocks with arc_role build"
                )

    shared_phrase_pairs = 0
    for left_position in range(len(narration_lines)):
        left_number, left_words = narration_lines[left_position]
        for right_position in range(left_position + 1, len(narration_lines)):
            right_number, right_words = narration_lines[right_position]
            phrase = _longest_shared_run(left_words, right_words)
            if not phrase:
                continue
            shared_phrase_pairs += 1
            if shared_phrase_pairs <= MAX_REPORTED_SHARED_PHRASES:
                errors.append(
                    f"blocks {left_number} and {right_number} share the verbatim phrase "
                    f"'{' '.join(phrase)}' ({len(phrase)} words) — a line is never brought "
                    "up to the word budget by appending or reusing a sentence; rewrite the "
                    "short line with one more FACT and leave the other one alone"
                )
    if shared_phrase_pairs > MAX_REPORTED_SHARED_PHRASES:
        errors.append(
            f"{shared_phrase_pairs} block pairs share a verbatim phrase in total; the "
            f"first {MAX_REPORTED_SHARED_PHRASES} are listed above"
        )

    seen_locations: set[str] = set()
    first_size_by_block = dict(block_shot_sizes)
    for position, location in enumerate(locations):
        if not isinstance(location, str) or not location:
            continue
        opening_size = first_size_by_block.get(position + 1)
        if location in seen_locations and opening_size in ESTABLISHING_SHOT_SIZES:
            errors.append(
                f"block {position + 1} returns to location {location!r} and opens on "
                f"{opening_size} — only the FIRST block of a new location establishes it; "
                "a later block there opens on a fresh close, medium or coverage angle"
            )
        seen_locations.add(location)

    repeated_shots = 0
    for left_position in range(len(block_shot_texts)):
        left_block, left_index, left_words = block_shot_texts[left_position]
        for right_position in range(left_position + 1, len(block_shot_texts)):
            right_block, right_index, right_words = block_shot_texts[right_position]
            if left_block == right_block:
                continue
            phrase = _longest_shared_run(left_words, right_words)
            if len(phrase) < SHARED_SHOT_WORDS:
                continue
            repeated_shots += 1
            if repeated_shots <= MAX_REPORTED_SHARED_PHRASES:
                errors.append(
                    f"block {left_block} shot {left_index} and block {right_block} shot "
                    f"{right_index} share the verbatim phrase '{' '.join(phrase)}' "
                    f"({len(phrase)} words) — the same plate described twice is the same "
                    "plate; give the later block a different subject, size or angle"
                )
    if repeated_shots > MAX_REPORTED_SHARED_PHRASES:
        errors.append(
            f"{repeated_shots} shot pairs repeat a verbatim phrase in total; the first "
            f"{MAX_REPORTED_SHARED_PHRASES} are listed above"
        )

    for left_position in range(len(block_renders)):
        left_block, left_location, left_assets = block_renders[left_position]
        for right_position in range(left_position + 1, len(block_renders)):
            right_block, right_location, right_assets = block_renders[right_position]
            if left_location != right_location or left_assets != right_assets:
                continue
            distance = right_block - left_block
            same_sizes = block_sizes_by_number.get(left_block) == block_sizes_by_number.get(
                right_block
            )
            if distance > NEAR_BLOCK_DISTANCE and not same_sizes:
                continue
            listed = ", ".join(left_assets) if left_assets else "no assets beyond the through-line"
            reason = (
                f"only {distance} blocks apart"
                if distance <= NEAR_BLOCK_DISTANCE
                else "and the same framing sizes in the same order"
            )
            errors.append(
                f"blocks {left_block} and {right_block} render from the same inputs — "
                f"location {left_location!r} with the same assets in the same order "
                f"({listed}), {reason}. The narration differs but the clip will not: give "
                "the later block a different location, a different asset order, or a "
                "different set of framing sizes"
            )

    if genre in HOOK_SENTENCE_GENRES and narration_lines:
        hook_number, _ = narration_lines[0]
        first_line = blocks[0].get("vo_line") if isinstance(blocks[0], dict) else None
        if hook_number == 1 and isinstance(first_line, str) and first_line.strip():
            opening = _first_sentence(first_line)
            opening_words = _word_count(opening)
            if opening_words > HOOK_SENTENCE_WORDS:
                errors.append(
                    f"the cold open is {opening_words} words before its first full stop "
                    f"({opening.strip()!r}) — block 1 opens on a sentence of at most "
                    f"{HOOK_SENTENCE_WORDS} words, the raw fact stated flat, and only then "
                    "fills out to the block's word budget"
                )

    for index in range(2, len(locations)):
        current = locations[index]
        if current and current == locations[index - 1] == locations[index - 2]:
            errors.append(
                f"location {current!r} is used in more than 2 consecutive blocks"
            )

    return {
        "valid": not errors and not invalid_blocks,
        "expected_block_count": expected_blocks,
        "block_count": len(blocks),
        "errors": errors,
        "invalid_blocks": invalid_blocks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--duration-seconds", required=True, type=float)
    parser.add_argument("--words-min", type=int, default=None)
    parser.add_argument("--words-max", type=int, default=None)
    parser.add_argument(
        "--duration-retry-blocks",
        type=str,
        default="",
        help=(
            "Comma-separated block numbers measured above the 9.5s hard ceiling. "
            "Only those blocks may use the adaptive 17-word retry floor."
        ),
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=None,
        help=(
            "Where the script lock lives (default: script.lock beside --script). "
            "A passing run writes it; assemble_final.sh refuses to work with narration "
            "whose digest does not match it, which is what makes an edit after "
            "SCRIPT LOCK impossible instead of merely forbidden."
        ),
    )
    parser.add_argument(
        "--verify-lock",
        action="store_true",
        help=(
            "Only compare the narration against an existing lock and exit; no gates are "
            "run. This is the mode assemble_final.sh calls."
        ),
    )
    arguments = parser.parse_args()
    if arguments.duration_seconds <= 0:
        parser.error("--duration-seconds must be positive")

    word_budget = None
    if arguments.words_min is not None or arguments.words_max is not None:
        if arguments.words_min is None or arguments.words_max is None:
            parser.error("--words-min and --words-max go together")
        if arguments.words_min > arguments.words_max:
            parser.error("--words-min must not exceed --words-max")
        word_budget = (arguments.words_min, arguments.words_max)
    try:
        duration_retry_blocks = {
            int(item.strip())
            for item in arguments.duration_retry_blocks.split(",")
            if item.strip()
        }
    except ValueError:
        parser.error("--duration-retry-blocks contains integers only")
    if any(block < 1 for block in duration_retry_blocks):
        parser.error("--duration-retry-blocks uses 1-based block numbers")

    try:
        script = json.loads(arguments.script.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {"valid": False, "errors": [str(error)], "invalid_blocks": []},
                ensure_ascii=False,
            )
        )
        return 1

    lock_path = arguments.lock or arguments.script.with_name("script.lock")

    if arguments.verify_lock:
        expected = _script_lock(script, arguments.duration_seconds)
        try:
            recorded = json.loads(lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(
                json.dumps(
                    {
                        "lock_ok": False,
                        "errors": [
                            f"no usable script lock at {lock_path}: {error} — run "
                            "validate_motion_script.py on the manifest first"
                        ],
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        matches = all(recorded.get(key) == expected[key] for key in (
            "narration_sha256", "block_count", "duration_seconds"
        ))
        payload: dict[str, Any] = {
            "lock_ok": matches,
            "narration_sha256": expected["narration_sha256"],
            "locked_sha256": recorded.get("narration_sha256"),
        }
        if not matches:
            payload["errors"] = [
                "the narration, block count or duration no longer matches the locked "
                "script. Revalidate the script and regenerate any affected takes."
            ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if matches else 1

    result = _validate(
        script,
        arguments.duration_seconds,
        word_budget,
        duration_retry_blocks,
    )
    if result["valid"]:
        lock = _script_lock(script, arguments.duration_seconds)
        try:
            lock_path.write_text(
                json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            result["lock"] = {"path": str(lock_path), **lock}
        except OSError as error:
            result["valid"] = False
            result["errors"].append(f"could not write the script lock to {lock_path}: {error}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
