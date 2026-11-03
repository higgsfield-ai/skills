#!/usr/bin/env python3
"""Missing numpy/Pillow must be reported as a setup problem, not as a bad talking clip."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]


def main():
    for tool in ("bash", "ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"missing {tool}")
    with tempfile.TemporaryDirectory(prefix="faceless-deps-") as tmp:
        p = Path(tmp)
        # A python3 that runs without site-packages, so numpy and PIL cannot be imported.
        shim_dir = p / "bin"
        shim_dir.mkdir()
        shim = shim_dir / "python3"
        shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -I -S "$@"\n')
        shim.chmod(0o755)
        env = dict(os.environ, PATH=f"{shim_dir}{os.pathsep}{os.environ['PATH']}")

        clip, talk = p / "clip.mp4", p / "talk.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=2",
                        "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-shortest", str(clip)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=green:s=320x480:r=24:d=3",
                        "-f", "lavfi", "-i", "sine=frequency=220:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-shortest", str(talk)], check=True)

        res = subprocess.run(["bash", str(SCRIPTS / "presenter_composite.sh"), str(clip), str(talk),
                              str(p / "out.mp4"), "--style", "cutout"], env=env, capture_output=True, text=True)
        assert res.returncode == 2, (res.returncode, res.stderr)
        assert "numpy and PIL" in res.stderr, res.stderr
        assert "regenerate" not in res.stderr, res.stderr
        assert not (p / "out.mp4").exists()

        res = subprocess.run(["bash", str(SCRIPTS / "trim_static_head.sh"), str(talk), str(p / "trim.mp4")],
                             env=env, capture_output=True, text=True)
        assert res.returncode == 2, (res.returncode, res.stderr)
        assert "numpy" in res.stderr and "Traceback" not in res.stderr, res.stderr
    print("missing numpy/Pillow is reported as a setup error")


if __name__ == "__main__":
    main()
