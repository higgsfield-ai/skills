---
name: higgsfield-video-explainer
description: |
  Compatibility entry for the former video explainer skill. Use when: the user explicitly invokes higgsfield-video-explainer or continues its existing workflow. NOT for: new generic explainer requests, ads, single clips, or unrelated video edits.
metadata:
  version: "0.14.0"
  argument-hint: "[topic or source files] [duration] [language] [aspect ratio]"
allowed-tools: Bash
---

# Video explainer

Use the `higgsfield-faceless-video` skill for this request and select its illustrated explainer workflow. Preserve the user's inputs and choices. If that skill is not installed, ask the user to update or install the current Higgsfield skills package before generating any assets. Do not use `explainer_video` or `video_explainer`.
