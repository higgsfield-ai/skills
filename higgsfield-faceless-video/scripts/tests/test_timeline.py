#!/usr/bin/env python3
"""Check timed scene planning and generated frame binding."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, root / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    timeline = load("build_scene_timeline")
    binding = load("bind_scene_frame_results")
    script = {"beats": [{"n": 1, "phrase": "Seeds need water"},
                        {"n": 2, "phrase": "Leaves catch sunlight"}]}
    words = {"words": [{"word": word, "start": i * .8, "end": i * .8 + .6}
                       for i, word in enumerate("Seeds need water Leaves catch sunlight".split())]}
    plan = timeline.build_scene_manifest(script, words, 5.0, 5.0)
    frames = plan["frames"]
    assert frames and all(f["duration"] <= 1.5 for f in frames)
    results = {"results": [{"output_slot": f["output_slot"], "job_id": f"id-{f['n']}",
                            "result_url": f"https://example.test/{f['n']}.png", "status": "completed",
                            "params": {"medias": [{"role": "image", "data": {"type": "image_job",
                                       "id": f"id-{f['n']-1}"}}]}}
                           for f in frames]}
    bound = binding.bind_scene_frame_results(plan, [results])
    for previous, current in zip(bound["frames"], bound["frames"][1:]):
        if current["image_mode"] == "variation":
            assert current["reference_frame_job_id"] == previous["frame_job_id"]
    variation = next(i for i, f in enumerate(frames) if f["image_mode"] == "variation")
    incorrect = {"results": [dict(r) for r in results["results"]]}
    incorrect["results"][variation] = {**incorrect["results"][variation], "params": {"medias": []}}
    try:
        binding.bind_scene_frame_results(plan, [incorrect])
    except ValueError:
        pass
    else:
        raise AssertionError("unverified variation reference was accepted")
    try:
        binding.bind_scene_frame_results(plan, [{"results": results["results"][:-1]}])
    except ValueError:
        pass
    else:
        raise AssertionError("missing frame was accepted")
    try:
        timeline.build_scene_manifest(script, words, 5.0, 20.0)
    except ValueError:
        pass
    else:
        raise AssertionError("wrong duration was accepted")
    print("timeline alignment, frame binding and failure gates passed")


if __name__ == "__main__":
    main()
