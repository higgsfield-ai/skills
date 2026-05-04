# Assets

Brand and demo assets for the repo. Not loaded by skills at runtime — purely for the README, plugin manifests, and marketplace listings.

## Expected files

| File | Used by | Notes |
|---|---|---|
| `logo.png` | `.cursor-plugin/plugin.json` (`"logo": "assets/logo.png"`) | Cursor plugin display logo. **Add this — manifest currently references a missing file.** |
| `icon.png` | future plugin manifests, marketplace listings | Square icon, 256×256 or 512×512 |
| `banner.png` | `README.md` header (optional) | Wide banner image for the GitHub page |
| `demo-generate.gif` | `README.md` Skills section | Short loop showing `higgsfield-generate` end-to-end |
| `demo-soul.gif` | `README.md` | Short loop showing Soul training |
| `demo-product-photoshoot.gif` | `README.md` | Short loop showing a Pinterest-pin or hero-banner result |

## Conventions

- **Logos and icons** — PNG with transparency, square aspect for icons.
- **Demo GIFs** — under 2 MB each, 8–15 seconds, looped.
- **Banner** — 1280×320 or 1920×480 typical GitHub social-preview ratio.

## Brand sources

Pull from internal Higgsfield brand assets (Figma / brand kit) when adding here. Don't recreate from scratch.

## Known gaps

- `logo.png` missing — `.cursor-plugin/plugin.json` references it (line: `"logo": "assets/logo.png"`). Cursor will render a default placeholder until added.
- No demo GIFs in README yet.
