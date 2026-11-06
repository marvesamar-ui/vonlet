# VONLET SECURITY — THE REVIEW · LIGHT EDITION

Issue 01 · November 2026 · the same ten pages as the dark edition, typeset
against a light palette.

This folder is generated. Do not edit the PNGs or the PDF; edit the layouts in
`tools/build_magazine.py` and rebuild.

```bash
python3 tools/build_magazine.py --theme light
```

## What this edition is

Same copy, same photographs, same grid, same page count as
`magazine/vonlet-review/`. Only the palette differs:

| | Dark edition | Light edition |
| --- | --- | --- |
| Page field | navy `#030816` | white `#ffffff` |
| Display and body type | `#f8fafc` | `#0b0f16` |
| Secondary type | `#94a3b8` | `#46505e` |
| Accent | `#facc15` | mustard `#a16207` |
| Callout bands | navy `#07142b` | warm grey `#f4f5f7` |
| Rules | `#1e293b` | `#dfe3e8` |

## The four rules that do not simply invert

- **Type anchors on the ink.** White type is unavailable on paper, so the light
  edition sets in near-black.
- **The accent darkens.** The site's `#facc15` is invisible against white at any
  size or weight; `#a16207` keeps the hue and carries the emphasis.
- **Section tints become warm grey.** A lifted navy on white reads as a
  misprint, not a panel.
- **Scrims stay dark.** The cover, the back cover and the two panels over the
  patrol and fleet photographs are dark in both editions, with light type on
  them in both, because a scrim's job is legibility over a photograph rather
  than matching the page. See `ON_DARK` in `tools/build_magazine.py`.

The page-8 provenance band keeps a tinted ground in both editions — deep amber
on navy, pale amber on white — because it is a warning.

## Files

`01-cover.png` … `10-back-cover.png` (A4 at 300 dpi, 216 × 303 mm with bleed),
`vonlet-review.pdf` (ten pages in reading order) and `contact-sheet.png`.

Provenance, accuracy and licensing notes are identical to the dark edition and
are documented in `../vonlet-review/README.md`.
