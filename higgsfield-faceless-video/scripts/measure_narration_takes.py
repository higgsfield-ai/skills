#!/usr/bin/env python3
"""Measure per-block narration against its authored script."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

TARGET_MIN = 7.8
HARD_MIN = 7.2
HARD_MAX = 9.5
ADAPTIVE_WORD_MIN = 17
DEFAULT_WORD_MAX = 23


def _parse_blocks(value: str) -> set[int]:
    if not value.strip():
        return set()
    try:
        blocks = {int(item.strip()) for item in value.split(",") if item.strip()}
    except ValueError as error:
        raise argparse.ArgumentTypeError("block lists contain integers only") from error
    if any(block < 1 for block in blocks):
        raise argparse.ArgumentTypeError("block numbers start at 1")
    return blocks


def _default_metrics_script() -> Path:
    candidate = Path(__file__).resolve().with_name("speech_metrics.sh")
    if not candidate.is_file():
        raise FileNotFoundError("speech_metrics.sh is missing")
    return candidate


def _recommended_words(words: int, speech: float) -> int:
    if speech <= 0:
        return words
    if speech > HARD_MAX:
        target = round(words * 9.0 / speech)
        return max(ADAPTIVE_WORD_MIN, min(words - 1, target))
    if speech < HARD_MIN:
        target = math.ceil(words * 8.5 / speech)
        return min(DEFAULT_WORD_MAX, max(words + 1, target))
    return words


def _classify(metric: dict[str, Any], *, accept_soft: bool) -> tuple[str, bool]:
    speech = float(metric["speech"])
    pauses = int(metric.get("pauses", 0))
    rate = metric.get("rate")
    if pauses:
        return "pausey", False
    if speech > HARD_MAX:
        return "too_long", False
    if speech < HARD_MIN:
        return "too_short", False
    if rate == "RUSHED":
        return "rushed", False
    if rate == "SLOW":
        return "slow", False
    if speech < TARGET_MIN:
        return ("soft_pass" if accept_soft else "soft_retry"), accept_soft
    return "pass", True


def measure(
    script: dict[str, Any],
    voice_dir: Path,
    metrics_script: Path,
    *,
    accept_soft_blocks: set[int] | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    accept_soft_blocks = accept_soft_blocks or set()
    blocks = script.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("script must contain a non-empty blocks array")

    takes: list[dict[str, Any]] = []
    retry_blocks: list[int] = []
    overlong_blocks: list[int] = []
    for index, block in enumerate(blocks, start=1):
        if not isinstance(block, dict) or not isinstance(block.get("vo_line"), str):
            raise ValueError(f"block {index} has no vo_line")
        voice = voice_dir / f"voice{index:02d}.wav"
        if not voice.is_file():
            takes.append({"block": index, "state": "missing", "file": str(voice)})
            retry_blocks.append(index)
            continue

        completed = runner(
            [
                str(metrics_script),
                str(voice),
                "--text",
                block["vo_line"],
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[:500]
            raise RuntimeError(f"speech metrics failed for block {index}: {detail}")
        metric = json.loads(completed.stdout)
        state, accepted = _classify(
            metric, accept_soft=index in accept_soft_blocks
        )
        take = {"block": index, "state": state, **metric}
        if state in {"too_long", "too_short"}:
            take["recommended_words"] = _recommended_words(
                int(metric["words"]), float(metric["speech"])
            )
        takes.append(take)
        if not accepted:
            retry_blocks.append(index)
        if state == "too_long":
            overlong_blocks.append(index)

    result: dict[str, Any] = {
        "valid": not retry_blocks,
        "retry_blocks": retry_blocks,
        "overlong_blocks": overlong_blocks,
        "takes": takes,
    }
    if overlong_blocks:
        joined = ",".join(str(block) for block in overlong_blocks)
        result["revalidate_with"] = f"--duration-retry-blocks {joined}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--voice-dir", required=True, type=Path)
    parser.add_argument("--metrics-script", type=Path, default=None)
    parser.add_argument(
        "--accept-soft-blocks",
        type=_parse_blocks,
        default=set(),
        help="Comma-separated blocks already retried once in the 7.2-7.8s soft band",
    )
    arguments = parser.parse_args()
    try:
        script = json.loads(arguments.script.read_text(encoding="utf-8"))
        result = measure(
            script,
            arguments.voice_dir,
            arguments.metrics_script or _default_metrics_script(),
            accept_soft_blocks=arguments.accept_soft_blocks,
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
