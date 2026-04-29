# Soul Troubleshooting

## `Minimum Basic plan required`

Soul training needs a paid plan. Tell the user to upgrade.

## `Training failed`

Common causes:

- Too few photos (<5) or too uniform.
- Heavy occlusion (sunglasses, hats).
- Group photos confusing identity.
- Upload type mismatch (must be image uploads, not video).

Action: ask user to swap in better photos, retrain.

## `Session expired`

`hf auth login`.

## Slow training

Default timeout is 30m. If still in progress: `hf soul wait <id> --timeout 60m`.
