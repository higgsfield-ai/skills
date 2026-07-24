# App cover + OG image (3:2, Higgsfield brand style)

Produce launch covers that could sit NEXT TO the official Higgsfield covers
without looking like a knock-off. This is the image behind `og_image_url` and
the marketplace card. Also use it when the user directly asks for a "cover",
"кавер", "обложка", "OG image", "launch cover" or "thumbnail" for a product,
model, feature or app announcement.

## The one rule that makes or breaks this skill

**The image model NEVER renders text. Not the title, not the wordmark, not
labels, not UI. It renders ONLY the scene.** Every glyph on the cover is drawn
by `compose_cover.py` from the bundled Inter font — that is why the type is
identical and crisp on every cover, like the official ones. If a generated
scene comes back with lettering in it, the candidate is DEAD. Regenerate with
"no text, no letters, no logos, no captions" appended.

Division of labor:

- **The image model** → one vivid full-bleed scene (people, product, world).
  Nothing else. (`higgsfield generate create`.)
- **`image_background_remover`** → subject cutout for the capsule break-out.
- **`compose_cover.py`** → capsule, frame, dots, wordmark, TITLE, CTA pill,
  scrim, break-out compositing. All geometry and typography. Text is ALWAYS the
  topmost layer.

**Outputs** (one compose run makes all three, same pixels/scene in each):

| file | what | use |
|---|---|---|
| `<slug>_cover.png` | full-bleed 3:2 scene + type lockup | marketplace / `marketplace_cover_url` |
| `<slug>_og.png` | frame + stadium capsule + corner dots | OG / `og_image_url` |
| `<slug>_og_wide.png` | same, 1.91:1 | Twitter/FB link cards |

## What an official cover looks like (internalize before prompting)

1. **A big, vivid, energetic scene with STORY DENSITY.** Saturated color,
   strong art direction, subject filling 55–75 % of the frame — and the frame
   is FULL: 2–4 supporting story props/layers around the subject. Never a dim
   empty room, never a lone subject floating on a bare seamless, never a "moody
   teal void". One person on an empty backdrop reads as AI slop even when
   bright — stage a world, not a portrait.
2. **One structured type lockup**, left-anchored or centered: the real
   Higgsfield wordmark (bundled squiggle glyph + "Higgsfield", drawn
   automatically by the script) → HUGE display-caps title (2 lines max; aim for
   the official scale — the title is the loudest thing on the cover) →
   `( Available now at higgsfield.ai )` pill. NO tagline — the reference lockup
   is wordmark → title → CTA, three rows, nothing else. Tight, aligned, flat
   white. It reads as ONE unit, not scattered captions.
3. **Text is the LAST layer — always.** The full lockup renders on top of
   everything; the subject NEVER covers a letter. Type may sit over the
   subject's body/props — keep it OFF the face: position with `--block-x/y` so
   the title crosses shoulders, arms or background, not eyes/mouth.
4. **The capsule variant**: solid frame color from the approved palette,
   stadium-shaped window, 4 corner dots — and with `--cutout` the subject
   BREAKS OUT of the capsule onto the frame. That pop-out is the whole point of
   the cutout.

Hard bans (non-negotiable): acid lime/yellow `#D9FF2E`-family frames or text
(the script blocks them), 3D/chrome/beveled/gradient lettering, watermarks,
borders inside the art, model-rendered UI panels, any MODEL-rendered
squiggle/logo (the real glyph is bundled and pasted by code — never ask the
model to draw it).

## Workflow

### 1. Brief

You need: the **product/feature name** (exact spelling — the script renders it
as the title), a **scene concept**, and a **typography treatment**. For an app
build, derive the name from `og_title` and the scene from what the app does.

**Keep `og_title` SHORT — at most 3–4 words, ideally ONE** (`Lumen`,
`PixelForge`, `Recipe Vault`): it is the feed-card title, the browser tab
title, and the dominant cover text. Put the pitch in `og_description`, never in
`og_title`.

Decide:

- **slug** (`dreamcut`), **title** (`DreamCut` — break long names with `\n`),
  CTA (default stands). NO tagline unless the user explicitly hands you one.
- **Scene concept** — the creative leap. Take the product's core verb and stage
  it as a physical, photographable moment with humor or spectacle (Higgsfield
  covers are witty, not corporate). "AI video editor" → an editor mid-leap
  slicing a giant ribbon of film with chrome scissors in a bright studio.
  "Skill marketplace" → a tiny craftsman forging a glowing card. Never settle
  for "person looks at hologram UI".
- **Route**: humans/lifestyle/fashion → PHOTO (a Soul model). Product/3D/
  illustrated world, no humans → GRAPHIC (`gpt_image_2`). Default PHOTO in
  doubt. Run `higgsfield model list` if unsure which job types are available.

### 2. Scene prompt doctrine (both routes)

Build the prompt from these blocks, in order:

1. Subject + action, concrete and physical ("a film editor in a bold red
   bomber jacket mid-leap, cutting a giant arc of 35mm film with oversized
   chrome scissors").
2. **World + props (story density)**: name 2–4 supporting elements that fill
   the frame around the subject. Add "no readable screens" whenever
   screens/props could sprout text.
3. **Scale + placement**: "waist-up, subject fills two thirds of the frame,
   positioned right-of-center" — and reserve the block side: "soft open
   negative space upper-left on a warm white wall". Negative space = a real
   surface (wall, sky, backdrop), NOT a black void.
4. Palette, committed and saturated: name 2–3 colors. Avoid lime/acid
   yellow-green.
5. Light + lens: "bright soft key with punchy shadows, low wide angle,
   commercial editorial grade".
6. Always end with: "no text, no letters, no logos, no captions, no UI".

**Reference the scene mood.** Pass 1–2 hosted scene refs that match the
intended mood as repeated `--image` flags (the CLI auto-imports http(s) URLs) —
they carry grade/energy only; never let a ref's content leak into the concept.
Hosted at `https://static.higgsfield.ai/website-builder/app-cover-generator/refs/`:

| ref file | mood |
|---|---|
| `scene-stadium-action.jpg` | epic sports spectacle, golden hour |
| `scene-studio-fashion.jpg` | clean bright studio, bold single color |
| `scene-epic-film.jpg` | cinematic blockbuster scale |
| `scene-glow-portrait.jpg` | neon/beauty glow portrait |
| `scene-street-lifestyle.jpg` | sunny UGC lifestyle |
| `scene-office-banana.jpg` / `scene-office-slapstick.jpg` | office comedy |
| `scene-comedy-absurd.jpg` | staged absurdist studio humor |
| `scene-beauty-product.jpg` | glossy product macro |
| `scene-cozy-ugc.jpg` | warm handheld authenticity |
| `scene-painterly-epic.jpg` | painterly fantasy |

**PHOTO route** — a Soul model (`soul_cinematic`, or a cleaner
fashion/studio Soul), `--aspect_ratio 3:2 --quality 2k --count 2`, with 1–2
scene refs as `--image`.

**GRAPHIC route** — `gpt_image_2 --aspect_ratio 3:2 --quality high
--resolution 2k --count 2`. Same prompt doctrine; style words like "glossy 3D
render / claymation diorama / painterly still" replace the lens block.

```bash
higgsfield generate create gpt_image_2 \
  --aspect_ratio 3:2 --quality high --resolution 2k --count 2 \
  --image https://static.higgsfield.ai/website-builder/app-cover-generator/refs/scene-epic-film.jpg \
  --prompt "<scene prompt — ends with: no text, no letters, no logos, no captions, no UI>" \
  --wait
```

### 3. Judge the scenes BEFORE composing

Look at both candidates. Kill a candidate if ANY of: text/letters appeared;
subject under ~50 % of frame; palette washed-out or muddy; the reserved
negative space is missing (no room for the lockup); anatomy/prop glitches; "AI
slop" tells (waxy skin, melted hands, gibberish objects). If both die, fix the
prompt (usually: more concrete action, harder scale words, brighter palette)
and regenerate — do not compose a weak scene. Compose is free; generations are
not.

If the winning scene is under ~1500 px wide, upscale it first
(`higgsfield generate create bytedance_image_upscale --image <url> --wait`) —
the script refuses art below 1500 px.

### 4. Break-out pass (whenever there is a clear subject)

Run `image_background_remover` on the winning scene and download the cutout PNG
— it must be the SAME image, subject isolated with alpha:

```bash
higgsfield generate create image_background_remover \
  --image <winning_scene_url_or_id> --wait
```

Pass the cutout as `--cutout`: on the framed OG variants the subject then
BREAKS OUT of the stadium capsule onto the frame color instead of being
amputated by the window edge (the official pop-out look). The window shrink is
ADAPTIVE — it only kicks in when the subject actually reaches the window's
top/side edges; a subject sitting fully inside keeps the full scene, no fat
frame ring. The cutout MUST come from the same job as `--art` or it silently
misaligns.

### 5. Compose

Write `compose_cover.py` from the block at the END of this document to your
workspace verbatim, then run it (needs Pillow — `pip install pillow` if
missing; the script fetches the Inter font + wordmark glyph from the hosted
asset base on first run and caches them):

```bash
python3 compose_cover.py \
  --art scene.png --cutout cutout.png \
  --title "DreamCut" \
  --title-width 0.48 \
  --anchor left --block-x 0.07 --block-y 0.30 \
  --frame-color "#D23B2E" \
  --out-cover dreamcut_cover.png --out-og dreamcut_og.png \
  --out-og-wide dreamcut_og_wide.png
```

**ONE typeface, hardcoded.** Inter — the title face on the reference cover —
renders everything: wordmark, title, CTA. There is no font flag. A different
face is a manual edit, not a skill feature.

**All type is flat white — no shadows.** Legibility comes from scene contrast
(dark negative space) and the scrim, not effects.

**Frame color** (approved palette): pick FROM the scene's palette with contrast
— bright scene → deep frame (`deep-navy #243A5E`, `signal-red #D23B2E`, `olive
#7A7D3C`); dark scene → light frame (`sky-blue #A9CFF4`, `peach #F7DDB9`, `cream
#F1EEE6`, `dusty-rose #E7B7B0`, `warm-gray #D6D3CE`). Echoing an accent already
in the scene (red jacket → signal-red) looks intentional; a random pastel does
not. Lime is BLOCKED by the script — do not `--force-frame-color` around it.

**Block placement**: `--anchor left --block-x 0.07` with the subject on the
right (or mirror it); `--anchor center` only for symmetric hero scenes.
`--block-y` so the title sits on the subject's torso band (0.26–0.38 usually).
`--scrim 60-110` depending on how busy the art is behind the block. On framed
outputs the whole lockup is clamped INSIDE the capsule automatically — text
never touches the frame.

### 6. Final check + deliver — the side-by-side gate

Open your `_og.png` NEXT TO the official covers at
`https://static.higgsfield.ai/website-builder/app-cover-generator/layout/layout-hooks.jpg`
and `.../layout/layout-stadium.jpg` and honestly answer: **"If these were in
the same folder, does mine look like the intern made it?"** Concretely verify:

- [ ] scene is vivid + dense — no dead darkness, subject dominates
- [ ] lockup reads as one designed unit; title huge (≥ 3× wordmark height)
- [ ] text is the topmost layer, fully legible, off the face; on OG the subject
      breaks out of the capsule (no window amputation)
- [ ] zero model-rendered text anywhere in the art
- [ ] frame color from palette, correct contrast, dots visible
- [ ] no lime, no 3D text, no squiggle, no watermarks
- [ ] art ≥ 1500 px wide (script enforces)

If any box fails — fix and re-run.

### 7. Deliver / wire into the app

- **Standalone cover request**: show all three files to the user and save them
  to their folder if one is connected.
- **App/website build (the publish gate)**: upload the cover + OG with
  `higgsfield upload create` and set the returned durable URLs in
  `app/src/app-meta.json`: `<slug>_og.png` → `og_image_url`, `<slug>_cover.png`
  → `marketplace_cover_url`. Commit before running `higgsfield website publish`.

If the text (drawn by the script) ever needs adjusting, it is a compose-flag
change (`--title`, `--block-x/y`, `--title-width`), never a regeneration — the
model never touched the text.

## Deviations

User-driven only (they may override colors, layout, CTA, partner lockups,
tagline — note that lime still requires their explicit insistence, use
`--force-frame-color`). On errors: font/glyph won't fetch → check network to
the hosted asset base (override with `$COVER_ASSET_BASE`); Pillow missing →
`pip install pillow`; generation refusals → rework the prompt content, keep the
structure. The brand system is the default, not a cage.

## compose_cover.py (write this file verbatim, then run it)

```python
#!/usr/bin/env python3
"""Build Higgsfield-style covers from one full-bleed SCENE image (no text on it).

The image model renders ONLY the scene. ALL typography is drawn here as ONE
structured lockup block, matching the official covers:

        Higgsfield                 <- wordmark (small)
        DREAMCUT                   <- title (huge caps)
        ( Available now at … )     <- CTA pill
(NO tagline by default — the reference lockup has none; --tagline exists
only for an explicit user request.)

Break-out: pass --cutout (subject with alpha from remove_background, same
size as the scene) and on the framed OG variants the subject pops OUT of the
stadium capsule onto the frame color instead of being clipped by the window.
Text is ALWAYS the last (topmost) layer — the subject never covers a letter.

The stadium capsule, frame and corner dots are code too. Outputs:
  --out-cover   full-bleed scene + lockup (marketplace cover)
  --out-og      frame + capsule + dots + lockup, same ratio as the art (3:2)
  --out-og-wide the 1.91:1 social-card variant

ONE typeface: Inter (the title face on the reference cover) renders
EVERYTHING — wordmark, title, CTA. No other font ships in the bundle.

All type is FLAT white. No shadows, no outlines, no gradients — ever.
On framed outputs the whole lockup is clamped INSIDE the stadium capsule
(rounded ends included) — text never touches the frame.

Only Pillow required.

ASSETS: the font + logo glyph are NOT bundled — they are fetched once from the
hosted asset base and cached locally (~/.cache/higgsfield-cover, override with
$COVER_ASSET_CACHE). Point at a different host with $COVER_ASSET_BASE.
"""
import argparse
import colorsys
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ALLOWED_FRAMES = {
    "sky-blue": "#A9CFF4",
    "peach": "#F7DDB9",
    "olive": "#7A7D3C",
    "warm-gray": "#D6D3CE",
    "dusty-rose": "#E7B7B0",
    "deep-navy": "#243A5E",
    "signal-red": "#D23B2E",
    "cream": "#F1EEE6",
}
DEFAULT_FRAME = ALLOWED_FRAMES["sky-blue"]
CTA_DEFAULT = "Available now at higgsfield.ai"
# ONE font. Inter Bold — the title face on the reference cover.
BRAND_FONT = "Inter-Variable.ttf"

# Hosted asset base (font + logo). Override with $COVER_ASSET_BASE. The two
# assets live at <base>/fonts/Inter-Variable.ttf and <base>/logo/hf-glyph.png.
ASSET_BASE = os.environ.get(
    "COVER_ASSET_BASE",
    "https://static.higgsfield.ai/website-builder/app-cover-generator",
).rstrip("/")


def cache_dir():
    d = os.environ.get(
        "COVER_ASSET_CACHE",
        os.path.join(os.path.expanduser("~"), ".cache", "higgsfield-cover"),
    )
    os.makedirs(d, exist_ok=True)
    return d


def ensure_asset(rel_path):
    """Return a local path to a hosted asset, downloading + caching on first use.
    rel_path is relative to ASSET_BASE, e.g. 'fonts/Inter-Variable.ttf'."""
    local = os.path.join(cache_dir(), os.path.basename(rel_path))
    if os.path.exists(local) and os.path.getsize(local) > 0:
        return local
    url = f"{ASSET_BASE}/{rel_path}"
    try:
        # A browser-ish User-Agent — some CDNs/WAFs 403 the default urllib UA.
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted host)
            data = r.read()
        with open(local, "wb") as f:
            f.write(data)
        return local
    except Exception as e:  # pragma: no cover - network/host failure
        print(f"WARNING: could not fetch asset {url}: {e}", file=sys.stderr)
        return None


def hex_rgb(s):
    c = s.lstrip("#")
    if len(c) != 6:
        sys.exit(f"bad hex color: {s}")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def check_frame_color(rgb, force):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    if 40 / 360 <= h <= 160 / 360 and s > 0.55 and v > 0.55:
        msg = ("frame color %02X%02X%02X is in the BANNED acid lime/yellow band. "
               "Allowed: %s" %
               (*rgb, ", ".join(f"{k} {v}" for k, v in ALLOWED_FRAMES.items())))
        if force:
            print("WARNING:", msg)
        else:
            sys.exit("ERROR: " + msg)


def luminance(rgb):
    r, g, b = (c / 255 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def brand_font(px, weight):
    """Inter at the given weight (opsz pinned for display). The ONLY typeface."""
    path = ensure_asset(f"fonts/{BRAND_FONT}")
    if path is None:
        return ImageFont.load_default(px)
    try:
        f = ImageFont.truetype(path, px)
        try:
            f.set_variation_by_axes([32, weight])
        except Exception:
            pass
        return f
    except Exception:
        return ImageFont.load_default(px)


def measure(d, text, font):
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    return x1 - x0, y1 - y0, x0, y0


class Lockup:
    """One structured type block: wordmark / title lines / tagline / CTA pill."""

    def __init__(self, a, W, H):
        self.a = a
        probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        lines = [ln.strip() for part in a.title.split("\\n")
                 for ln in part.split("\n") if ln.strip()]
        if a.title_caps == "upper":
            lines = [ln.upper() for ln in lines]
        self.title_lines = lines

        # Size the title so its longest line fills the width budget…
        budget = W * a.title_width
        px = round(H * 0.5)
        f = brand_font(px, 700)
        w = max(measure(probe, ln, f)[0] for ln in self.title_lines)
        px = max(24, round(px * budget / max(1, w)))
        # …capped by line height and by total available width at the anchor.
        px = min(px, round(H * a.title_max_h))
        avail = W * (0.94 - a.block_x) if a.anchor == "left" else W * 0.88
        f = brand_font(px, 700)
        w = max(measure(probe, ln, f)[0] for ln in self.title_lines)
        if w > avail:
            px = round(px * avail / w)
        self.title_px = px
        self.f_title = brand_font(px, 700)

        glyph_path = ensure_asset("logo/hf-glyph.png")
        self.glyph = (Image.open(glyph_path).convert("RGBA")
                      if glyph_path and os.path.exists(glyph_path) else None)
        self.f_word = brand_font(max(16, round(px * 0.26)), 650)
        self.f_tag = brand_font(max(14, round(px * 0.20)), 500)
        self.f_cta = brand_font(max(13, round(px * 0.17)), 500)
        self.cta_pad_y = round(px * 0.14)
        self.cta_pad_x = round(px * 0.30)

        def rows_for(names):
            rows = []
            if "word" in names and a.wordmark:
                rows.append(("word", a.wordmark, self.f_word, 0))
            if "title" in names:
                for i, ln in enumerate(self.title_lines):
                    gap = round(px * (0.30 if (i == 0 and a.wordmark) else 0.10 if i else 0))
                    rows.append(("title", ln, self.f_title, gap))
            if "tag" in names and a.tagline:
                rows.append(("tag", a.tagline, self.f_tag, round(px * 0.26)))
            if "cta" in names and a.cta:
                rows.append(("cta", a.cta, self.f_cta, round(px * 0.30)))
            out = []
            for kind, text, font, gap in rows:
                tw, th, ox, oy = measure(probe, text, font)
                if kind == "cta":
                    tw += 2 * self.cta_pad_x
                    th += 2 * self.cta_pad_y
                if kind == "word" and self.glyph is not None:
                    gh = round(th * 1.3)
                    tw += round(gh * self.glyph.width / self.glyph.height) \
                        + round(th * 0.45)
                    th = max(th, gh)
                out.append([kind, text, font, gap, tw, th, ox, oy])
            return out

        self.rows = rows_for(("word", "title", "tag", "cta"))
        self.width = max(r[4] for r in self.rows)
        self.height = sum(r[3] + r[5] for r in self.rows)

    def origin(self, W, H, window=None):
        a = self.a
        bx = round(W * a.block_x)
        by = round(H * a.block_y)
        if a.anchor == "center":
            bx -= self.width // 2
        bx = max(round(W * 0.05), min(bx, W - self.width - round(W * 0.05)))
        by = max(round(H * 0.07), min(by, H - self.height - round(H * 0.075)))
        if window:
            # Framed variant: the WHOLE block must sit inside the stadium
            # capsule, including its rounded ends — never on/over the frame.
            wx0, wy0, wx1, wy1 = window
            r = (wy1 - wy0) / 2
            cy = (wy0 + wy1) / 2
            pad = round(W * 0.015)
            by = max(wy0 + pad, min(by, wy1 - self.height - pad))
            for _ in range(3):
                dy = max(abs(by - cy), abs(by + self.height - cy))
                dx = r - (max(r * r - dy * dy, 0.0)) ** 0.5
                lo = round(wx0 + dx) + pad
                hi = round(wx1 - dx) - pad - self.width
                bx = max(lo, min(bx, max(lo, hi)))
                by = max(wy0 + pad, min(by, wy1 - self.height - pad))
        return bx, by

    def render(self, im, cutout=None, window=None):
        """Layer order: scene -> scrim -> subject cutout -> ALL text LAST.

        The cutout's only job is the capsule break-out on the framed OG
        variants (the subject pops over the frame like the official covers).
        Text is always the topmost layer and never hidden by the subject."""
        a = self.a
        W, H = im.size
        bx, by = self.origin(W, H, window)
        base = im.convert("RGBA")

        if a.scrim > 0:
            scr = Image.new("L", (W, H), 0)
            pad = round(self.title_px * 0.8)
            ImageDraw.Draw(scr).rounded_rectangle(
                (bx - pad, by - pad, bx + self.width + pad, by + self.height + pad),
                radius=pad, fill=a.scrim)
            scr = scr.filter(ImageFilter.GaussianBlur(pad))
            base.alpha_composite(
                Image.composite(Image.new("RGBA", (W, H), (8, 8, 12, 255)),
                                Image.new("RGBA", (W, H), (0, 0, 0, 0)), scr))

        white = (255, 255, 255, 255)

        def draw_rows(target, kinds):
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            y = by
            for kind, text, font, gap, tw, th, ox, oy in self.rows:
                y += gap
                if kind not in kinds:
                    y += th
                    continue
                x = bx if a.anchor == "left" else bx + (self.width - tw) // 2
                if kind == "cta":
                    ss = 4
                    tile = Image.new("RGBA", (tw * ss, th * ss), (0, 0, 0, 0))
                    td = ImageDraw.Draw(tile)
                    td.rounded_rectangle((0, 0, tw * ss - 1, th * ss - 1),
                                         radius=th * ss // 2, fill=(15, 15, 18, 135),
                                         outline=(255, 255, 255, 115), width=ss)
                    layer.alpha_composite(tile.resize((tw, th), Image.LANCZOS), (x, y))
                    d.text((x + self.cta_pad_x - ox, y + self.cta_pad_y - oy),
                           text, font=font, fill=white)
                elif kind == "word" and self.glyph is not None:
                    twt, tht, oxt, oyt = measure(d, text, font)
                    gh = round(tht * 1.3)
                    gw = round(gh * self.glyph.width / self.glyph.height)
                    tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
                    tile.alpha_composite(
                        self.glyph.resize((gw, gh), Image.LANCZOS), (0, (th - gh) // 2))
                    ImageDraw.Draw(tile).text(
                        (gw + round(tht * 0.45) - oxt, (th - tht) // 2 - oyt),
                        text, font=font, fill=white)
                    layer.alpha_composite(tile, (x, y))
                else:
                    d.text((x - ox, y - oy), text, font=font, fill=white)
                y += th
            target.alpha_composite(layer)

        if cutout is not None:
            base.alpha_composite(cutout.convert("RGBA"))
        draw_rows(base, {"title", "word", "tag", "cta"})
        return base.convert("RGB")


def stadium_mask(size, box):
    W, H = size
    ss = 4 if max(W, H) <= 1800 else 2
    big = Image.new("L", (W * ss, H * ss), 0)
    r = (box[3] - box[1]) // 2
    ImageDraw.Draw(big).rounded_rectangle([v * ss for v in box],
                                          radius=r * ss, fill=255)
    return big.resize((W, H), Image.LANCZOS)


def draw_dots(im, dot_rgb):
    W, H = im.size
    dr = max(3, round(W * 0.008))
    ox, oy = round(W * 0.028), round(H * 0.045)
    ss = 4
    tile = Image.new("RGBA", (dr * 2 * ss, dr * 2 * ss), (0, 0, 0, 0))
    ImageDraw.Draw(tile).ellipse((0, 0, dr * 2 * ss - 1, dr * 2 * ss - 1),
                                 fill=(*dot_rgb, 255))
    tile = tile.resize((dr * 2, dr * 2), Image.LANCZOS)
    for cx in (ox, W - ox):
        for cy in (oy, H - oy):
            im.paste(tile, (cx - dr, cy - dr), tile)


def crop_box_for(size, ratio):
    w, h = size
    if w / h > ratio:
        nw = round(h * ratio)
        x = (w - nw) // 2
        return (x, 0, x + nw, h)
    nh = round(w / ratio)
    y = (h - nh) // 2
    return (0, y, w, y + nh)


def touches_edges(piece, band_h, band_w):
    """True if the subject plate has meaningful alpha in the top or side
    bands of the window — i.e. the subject actually reaches the capsule
    edge and a breakout is possible."""
    alpha = piece.getchannel("A")
    w, h = alpha.size
    for bbox in (
        (0, 0, w, max(1, band_h)),          # top band
        (0, 0, max(1, band_w), h),          # left band
        (w - max(1, band_w), 0, w, h),      # right band
    ):
        region = alpha.crop(bbox)
        hist = region.histogram()
        solid = sum(hist[128:])
        if solid > 0.005 * (region.width * region.height):
            return True
    return False


def build_framed(art, cutout, canvas_ratio, a, frame_rgb, dot_rgb):
    W = art.width
    H = round(W / canvas_ratio)
    mx, my = round(W * a.margin_x), round(H * a.margin_y)
    box = (mx, my, W - mx, H - my)
    bw, bh = box[2] - box[0], box[3] - box[1]
    cb = crop_box_for(art.size, bw / bh)

    scene = Image.new("RGB", (W, H), frame_rgb)
    scene.paste(art.crop(cb).resize((bw, bh), Image.LANCZOS), (box[0], box[1]))

    cut = None
    mask_box = box
    if cutout is not None:
        # UNCLIPPED on purpose: the subject breaks out of the capsule onto the
        # frame (official look — Cinema Studio 4's boot + ball over the green).
        cut = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        piece = cutout.crop(cb).resize((bw, bh), Image.LANCZOS)
        cut.paste(piece, (box[0], box[1]), piece)
        # ADAPTIVE window shrink: only if the subject actually reaches the
        # window's top/side edges does the window pull in (top + sides,
        # bottom stays flush) so the full-size plate pops over the capsule
        # with zero ghosting. Otherwise the window keeps the full scene —
        # no wasted frame ring.
        ins = round(bh * a.pop_inset)
        if ins > 0 and touches_edges(piece, round(bh * 0.06), round(bw * 0.04)):
            mask_box = (box[0] + ins, box[1] + ins, box[2] - ins, box[3])

    mask = stadium_mask((W, H), mask_box)
    out = Image.composite(scene, Image.new("RGB", (W, H), frame_rgb), mask)
    if not a.no_dots:
        draw_dots(out, dot_rgb)
    return Lockup(a, W, H).render(out, cut, window=mask_box)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--art", required=True, help="full-bleed SCENE image, no text on it")
    p.add_argument("--cutout", help="subject-with-alpha PNG aligned to --art "
                                    "(remove_background output); pops out of the OG capsule")
    p.add_argument("--title", required=True, help=r"product name; '\n' splits lines")
    p.add_argument("--title-caps", choices=["upper", "keep"], default="upper")
    p.add_argument("--title-width", type=float, default=0.52,
                   help="longest title line as fraction of canvas width (0.35-0.62)")
    p.add_argument("--title-max-h", type=float, default=0.26)
    p.add_argument("--wordmark", default="Higgsfield", help="'' to disable")
    p.add_argument("--tagline", default="")
    p.add_argument("--cta", default=CTA_DEFAULT, help="'' to disable")
    p.add_argument("--anchor", choices=["left", "center"], default="left")
    p.add_argument("--block-x", type=float, default=0.07)
    p.add_argument("--block-y", type=float, default=0.28)
    p.add_argument("--scrim", type=int, default=90,
                   help="0-255 soft dark scrim behind the block (0 = off)")
    p.add_argument("--out-cover")
    p.add_argument("--out-og")
    p.add_argument("--out-og-wide")
    p.add_argument("--frame-color", default=DEFAULT_FRAME)
    p.add_argument("--force-frame-color", action="store_true")
    p.add_argument("--dot-color", default="auto")
    p.add_argument("--no-dots", action="store_true")
    p.add_argument("--margin-x", type=float, default=0.045)
    p.add_argument("--margin-y", type=float, default=0.055)
    p.add_argument("--pop-inset", type=float, default=0.03,
                   help="with --cutout: shrink the capsule window by this "
                        "fraction of its height (top/sides) so the subject "
                        "plate pops over the edge — applied ONLY when the "
                        "subject actually reaches the window edge; 0 disables")
    p.add_argument("--min-width", type=int, default=1500)
    a = p.parse_args()

    if not (a.out_cover or a.out_og or a.out_og_wide):
        sys.exit("nothing to do: pass --out-cover / --out-og / --out-og-wide")

    frame_rgb = hex_rgb(a.frame_color)
    check_frame_color(frame_rgb, a.force_frame_color)
    dot_rgb = ((26, 26, 26) if luminance(frame_rgb) > 0.55 else (255, 255, 255)) \
        if a.dot_color == "auto" else hex_rgb(a.dot_color)

    art = Image.open(a.art).convert("RGB")
    if art.width < a.min_width:
        sys.exit(f"ERROR: art is {art.width}px wide (< {a.min_width}). Upscale "
                 f"first — do not ship a soft cover.")
    cutout = None
    if a.cutout:
        cutout = Image.open(a.cutout).convert("RGBA")
        if cutout.size != art.size:
            cutout = cutout.resize(art.size, Image.LANCZOS)

    if a.out_cover:
        out = Lockup(a, art.width, art.height).render(art, cutout)
        out.save(a.out_cover)
        print(f"cover    {a.out_cover} {out.size[0]}x{out.size[1]}")

    if a.out_og:
        out = build_framed(art, cutout, art.width / art.height, a, frame_rgb, dot_rgb)
        out.save(a.out_og)
        print(f"og       {a.out_og} {out.size[0]}x{out.size[1]} frame={a.frame_color}")

    if a.out_og_wide:
        out = build_framed(art, cutout, 1.91, a, frame_rgb, dot_rgb)
        out.save(a.out_og_wide)
        print(f"og-wide  {a.out_og_wide} {out.size[0]}x{out.size[1]} frame={a.frame_color}")


if __name__ == "__main__":
    main()
```
