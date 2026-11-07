#!/usr/bin/env python3
"""Exercise picture, song, edit and presenter assembly with local fixtures."""
import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*args, check=True):
    return subprocess.run(args, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_script(name, *args, check=True):
    return run("bash", str(SCRIPTS / name), *(str(arg) for arg in args), check=check)


def duration(path):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=nw=1:nk=1", str(path)).stdout)


def color(path, second):
    output = run("ffmpeg", "-v", "error", "-ss", str(second), "-i", str(path),
                 "-frames:v", "1", "-vf", "scale=1:1", "-pix_fmt", "rgb24", "-f", "rawvideo", "-").stdout
    return tuple(output[:3])


SCRIPTS = Path(__file__).resolve().parents[1]


def main():
    for tool in ("bash", "ffmpeg", "ffprobe", "python3"):
        if not shutil.which(tool):
            raise RuntimeError(f"missing {tool}")
    with tempfile.TemporaryDirectory(prefix="faceless-modes-") as tmp:
        p = Path(tmp)
        clip, source, song = p / "clip.mp4", p / "source.mp4", p / "song.wav"
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=10",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=10", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(clip))
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=red:size=320x180:rate=24:duration=30",
            "-f", "lavfi", "-i", "sine=frequency=220:duration=30", "-t", "30", "-c:v", "libx264", "-c:a", "aac", str(source))
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=330:duration=60",
            "-af", "volume=3", "-ar", "24000", str(song))
        manifest = p / "clips.txt"
        manifest.write_text((str(clip) + "\n") * 6)
        result = p / "song.mp4"
        run_script("assemble_final.sh", "--out", result, "--blocks", 6, "--manifest", manifest, "--song", song)
        assert abs(duration(result) - 60) < 0.2
        negative = run_script("assemble_final.sh", "--out", p / "bad-song.mp4", "--blocks", 5,
                              "--manifest", manifest, "--song", song, check=False)
        assert negative.returncode != 0

        dialogue = p / "dialogue01.wav"
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=400:duration=8.2",
            "-af", "adelay=1000:all=1,apad", "-t", "10", str(dialogue))
        talking_script = p / "talking.json"
        talking_script.write_text(json.dumps({"talking_characters": True, "blocks": [{"block_kind": "dialogue"}]}))
        talking_out = p / "talking.mp4"
        assert run_script("assemble_final.sh", "--out", talking_out, "--blocks", 1,
                          "--script", talking_script, "--allow-mismatch", clip, dialogue, check=False).returncode != 0
        (p / "script.lock").write_text(json.dumps({"narration_sha256": hashlib.sha256(b"").hexdigest(),
                                                   "block_count": 1, "duration_seconds": 10}))
        run_script("assemble_final.sh", "--out", talking_out, "--blocks", 1,
                   "--script", talking_script, "--allow-mismatch", clip, dialogue)
        timing = json.loads(Path(str(talking_out) + ".assembly.json").read_text())["per_block"][0]
        assert abs(timing["speech_abs_s"] - 1.0) < 0.15, timing
        assert timing["voice"] == "dialogue01.wav", timing
        muted_out = p / "talking-muted.mp4"
        run_script("assemble_final.sh", "--out", muted_out, "--blocks", 1, "--sfx-vol", 0,
                   "--script", talking_script, "--allow-mismatch", clip, dialogue)
        def audio_bytes(path):
            return run("ffmpeg", "-v", "error", "-i", str(path), "-vn", "-f", "s16le", "-").stdout
        assert audio_bytes(talking_out) == audio_bytes(muted_out), "dialogue clip audio was mixed twice"
        (p / "script.lock").unlink()
        soft = p / "soft.wav"
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=300:duration=7.5", "-af", "volume=3", str(soft))
        assert run_script("assemble_final.sh", "--out", p / "soft.mp4", "--blocks", 1,
                          "--allow-mismatch", clip, soft, check=False).returncode != 0
        accepted = run_script("assemble_final.sh", "--out", p / "soft.mp4", "--blocks", 1,
                              "--accept-soft-blocks", "1", "--allow-mismatch", clip, soft, check=False)
        assert b"accepted retried voice 1" in accepted.stderr
        voice = p / "voice.wav"
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=300:duration=8.8", str(voice))
        frames = []
        for i in range(1, 9):
            frame = p / f"frame{i:03}.png"
            run("ffmpeg", "-v", "error", "-y", "-ss", str(i), "-i", str(clip), "-frames:v", "1", str(frame))
            frames.append(frame)
        pictures = p / "frames.txt"
        pictures.write_text("".join(f"{frame} 1.1\n" for frame in frames))
        stills = p / "stills.mp4"
        run_script("assemble_slides.sh", "--out", stills, "--audio", voice, "--blocks", 8, "--manifest", pictures)
        assert abs(duration(stills) - 8.8) < 0.3
        pictures.write_text("".join(f"{frames[0]} 1.1\n" for _ in frames))
        assert run_script("assemble_slides.sh", "--out", p / "bad-stills.mp4", "--audio", voice,
                          "--blocks", 8, "--manifest", pictures, check=False).returncode != 0

        patch = p / "patch.mp4"
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=blue:size=320x180:rate=24:duration=10",
            "-f", "lavfi", "-i", "sine=frequency=330:duration=10", "-t", "10", "-c:v", "libx264", "-c:a", "aac", str(patch))
        patches = p / "patches.json"
        patches.write_text(json.dumps([{"start_seconds": 10, "end_seconds": 20, "patch_video": str(patch)}]))
        edited = p / "edited.mp4"
        run_script("assemble_partial_edit.sh", "--source", source, "--source-seconds", 30,
                   "--requested-seconds", 30, "--manifest", patches, "--out", edited)
        assert abs(duration(edited) - 30) < 0.2
        assert color(edited, 5)[0] > 200 and color(edited, 15)[2] > 200 and color(edited, 25)[0] > 200
        patches.write_text(json.dumps([{"start_seconds": 5, "end_seconds": 15, "patch_video": str(patch)}]))
        assert run_script("assemble_partial_edit.sh", "--source", source, "--source-seconds", 30,
                          "--requested-seconds", 30, "--manifest", patches, "--out", p / "bad-edit.mp4", check=False).returncode != 0

        if "--skip-presenter" not in sys.argv:
            talk = p / "talk.mp4"
            run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=green:s=320x480:r=24:d=10",
                "-f", "lavfi", "-i", "sine=frequency=220:duration=10", "-filter_complex",
                "[0:v]drawbox=x=110:y=100:w=100:h=320:color=red:t=fill[v]", "-map", "[v]", "-map", "1:a",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(talk))
            reference = p / "reference.png"
            run("ffmpeg", "-v", "error", "-y", "-i", str(talk), "-frames:v", "1", str(reference))
            assert run_script("trim_static_head.sh", talk, p / "frozen.mp4", reference, check=False).returncode != 0
            composite = p / "presenter.mp4"
            run_script("presenter_composite.sh", clip, talk, composite, "--style", "cutout")
            assert json.loads(Path(str(composite) + ".qc.json").read_text())["result"] == "PASS"
            assert (p / "presenter_voice.wav").exists()
    print("picture, song and edit fixtures passed" + ("; presenter skipped" if "--skip-presenter" in sys.argv else "; presenter passed"))


if __name__ == "__main__":
    main()
