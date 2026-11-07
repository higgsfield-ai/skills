#!/usr/bin/env python3
"""Bind generated image job provenance to a deterministic scene timeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _is_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _job_id(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _result_url(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    for candidate in (
        value.get("url"),
        value.get("result_url"),
        value.get("preview"),
        value.get("output_url"),
    ):
        if _is_http_url(candidate):
            return candidate
    result = value.get("result")
    if isinstance(result, dict):
        return _result_url(result)
    return None


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    records: list[dict[str, Any]] = []
    for field in (
        "frames",
        "requests",
        "results",
        "generation_provenance",
    ):
        value = payload.get(field)
        if isinstance(value, list):
            records.extend(item for item in value if isinstance(item, dict))
    return records


def _frame_results(payloads: list[Any]) -> dict[str, dict[str, Any]]:
    job_urls: dict[str, str] = {}
    job_references: dict[str, list[str]] = {}
    slots: dict[str, dict[str, Any]] = {}
    records = [record for payload in payloads for record in _records(payload)]
    for record in records:
        job_id = _job_id(record.get("job_id") or record.get("id"))
        url = _result_url(record)
        if job_id is not None and url is not None and record.get("status") == "completed":
            job_urls[job_id] = url
            params = record.get("params")
            if isinstance(params, dict) and isinstance(params.get("medias"), list):
                job_references[job_id] = [
                    media["data"]["id"] for media in params["medias"]
                    if isinstance(media, dict) and media.get("role") == "image"
                    and isinstance(media.get("data"), dict)
                    and media["data"].get("type") == "image_job"
                    and isinstance(media["data"].get("id"), str)
                ]

    for record in records:
        output_slot = record.get("output_slot")
        if not isinstance(output_slot, str) or not output_slot.strip():
            continue
        job_ids = record.get("job_ids")
        job_id = _job_id(record.get("job_id") or record.get("id"))
        if job_id is None and isinstance(job_ids, list) and len(job_ids) == 1:
            job_id = _job_id(job_ids[0])
        url = _result_url(record) or (job_urls.get(job_id) if job_id else None)
        if job_id is not None and url is not None and job_urls.get(job_id) == url:
            slots[output_slot.strip()] = {"job_id": job_id, "url": url,
                                          "reference_job_ids": job_references.get(job_id, [])}
    return slots


def bind_scene_frame_results(
    manifest: dict[str, Any],
    payloads: list[Any],
) -> dict[str, Any]:
    frames = manifest.get("frames")
    if manifest.get("manifest_version") != 2 or not isinstance(frames, list):
        raise ValueError("scene manifest must contain manifest_version 2 frames")
    results = _frame_results(payloads)
    bound_frames: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for index, raw_frame in enumerate(frames, start=1):
        if not isinstance(raw_frame, dict):
            raise ValueError(f"frame {index} must be an object")
        output_slot = raw_frame.get("output_slot")
        if output_slot != f"frame-{index:03d}":
            raise ValueError(f"frame {index} output_slot is invalid")
        result = results.get(output_slot)
        if result is None:
            raise ValueError(
                f"frame {index} has no completed job_id/url result for {output_slot}"
            )
        frame = {
            **raw_frame,
            "frame_job_id": result["job_id"],
            "frame_url": result["url"],
        }
        if frame.get("image_mode") == "variation":
            if previous is None:
                raise ValueError("the first frame cannot be a variation")
            if frame.get("reference_output_slot") != previous.get("output_slot"):
                raise ValueError(
                    f"frame {index} reference_output_slot must point to frame {index - 1}"
                )
            if previous["frame_job_id"] not in result["reference_job_ids"]:
                raise ValueError(
                    f"frame {index} job receipt does not reference the previous image job; "
                    "pass that job ID to generation and include the completed job receipt"
                )
            frame["reference_frame_job_id"] = previous["frame_job_id"]
            frame["reference_frame_url"] = previous["frame_url"]
        else:
            frame.pop("reference_frame_job_id", None)
            frame.pop("reference_frame_url", None)
        bound_frames.append(frame)
        previous = frame
    return {**manifest, "frames": bound_frames}


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--results", required=True, action="append", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    manifest = json.loads(arguments.manifest.read_text(encoding="utf-8"))
    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in arguments.results
    ]
    bound = bind_scene_frame_results(manifest, payloads)
    temporary = arguments.out.with_suffix(arguments.out.suffix + ".tmp")
    temporary.write_text(
        json.dumps(bound, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(arguments.out)
    print(json.dumps({"valid": True, "frames": len(bound["frames"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
