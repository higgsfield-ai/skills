#!/usr/bin/env python3
"""Check duration and language-aware prompt validation."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "validate_song_prompt.py"
spec = importlib.util.spec_from_file_location("song", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
base = ("A full 1-minute song, 100 BPM, steady constant beat, 4/4, no tempo changes, "
        "8 syllables, one syllable per beat, beat one, 4-bar phrases, chorus repeats verbatim. ")
for language, line in (("en", "The little bird can sing today"),
                       ("ru", "На лугу растёт зелёный сад"),
                       ("ja", "春の風が吹いています")):
    result = module.validate(base + '"' + line + '"', duration_seconds=60, lyrics_language=language)
    assert result["valid"], result
    assert result["manual_meter_review_required"] == (language == "ja")
assert not module.validate_duration(90)["valid"]
assert not module.validate(base, duration_seconds=60)["valid"]
print("song duration, lyric and language checks passed")
