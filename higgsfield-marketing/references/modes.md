# Modes

`--mode` for `marketing_studio_video`. Pick by ad style.

| Mode | Best for |
|---|---|
| `ugc` | Default. Casual, organic-feel content from a presenter. |
| `ugc_how_to` | Tutorial / explainer. "Here's how to use this." |
| `ugc_unboxing` | Unboxing reveal. "Just got this in the mail." |
| `product_showcase` | Clean product highlight, polished. |
| `product_review` | Presenter giving opinion on the product. |
| `tv_spot` | Broadcast-style commercial. Higher production. |
| `wild_card` | Experimental, model picks vibe. |
| `ugc_virtual_try_on` | Person trying on clothing/accessories. |
| `virtual_try_on` | Same but more polished, model-driven. |

Default: `ugc`.

## Picking flow

- "Looks like a real person filmed it on phone" → `ugc` family
- "Polished broadcast feel" → `tv_spot`
- "Show the product itself, less presenter" → `product_showcase`
- "Try clothing on a model" → `virtual_try_on`
