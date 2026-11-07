#!/usr/bin/env python3
"""Check authored caption alignment without downloading a model."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "audio_to_captions.py"
spec = importlib.util.spec_from_file_location("captions", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
groups = [{"n": 1, "speech_start": 0, "speech_end": 2,
           "words": [{"word": "hello", "start": 0.1, "end": 0.5},
                     {"word": "world", "start": 0.6, "end": 1.0}]}]
aligned, score = module.align_blocks_to_script(groups, [["hello", "world"]], minimum_similarity=0.75)
assert score == 1.0 and [word["word"] for word in aligned] == ["hello", "world"]
try:
    module.align_blocks_to_script(groups, [], minimum_similarity=0.75)
except ValueError:
    pass
else:
    raise AssertionError("mismatched blocks were accepted")
print("captions: authored alignment and block count passed")
