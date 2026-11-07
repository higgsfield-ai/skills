#!/usr/bin/env python3
"""Exercise assembly using generated local fixtures; no account is required."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(*args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs)


def main():
    for tool in ("ffmpeg", "ffprobe", "bash"):
        if not shutil.which(tool):
            raise RuntimeError(f"missing {tool}")
    script = Path(__file__).resolve().parents[1] / "assemble_blocks.sh"
    with tempfile.TemporaryDirectory(prefix="faceless-test-") as temp:
        folder = Path(temp)
        for index, duration in [(1, 8.8), (2, 4.2)]:
            run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc2=size=320x180:rate=24:duration=10", "-c:v", "libx264",
                "-pix_fmt", "yuv420p", str(folder / f"clip{index:02}.mp4"))
            run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                f"sine=frequency=220:duration={duration}", "-ar", "24000",
                str(folder / f"voice{index:02}.wav"))
        checker = script.parent / "check_voice.sh"
        run("bash", str(checker), str(folder / "voice01.wav"), "10")
        wrong_window = subprocess.run(["bash", str(checker), str(folder / "voice02.wav"), "10"], capture_output=True)
        assert wrong_window.returncode != 0
        output = folder / "final.mp4"
        pairs = [str(folder / f"{kind}{index:02}.{extension}")
                 for index in (1, 2) for kind, extension in (("clip", "mp4"), ("voice", "wav"))]
        result = run("bash", str(script), "--out", str(output), "--last-seconds", "5", *pairs)
        assert "mixes numbers" not in result.stderr
        duration = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "default=nw=1:nk=1", str(output)).stdout)
        assert abs(duration - 15) < 0.2, duration
        receipt = json.loads(Path(str(output) + ".assembly.json").read_text())
        assert receipt["blocks"] == 2 and receipt["total_s"] == 15
        failed = subprocess.run(["bash", str(script), "--out", str(folder / "invalid.mp4"),
                                 pairs[0], pairs[3]], capture_output=True, text=True)
        assert failed.returncode != 0 and "DURATION GATE FAILED" in failed.stderr
        assert not (folder / "invalid.mp4").exists()
    print("assembly: ordered pairs, short final block and duration gate passed")


if __name__ == "__main__":
    main()
