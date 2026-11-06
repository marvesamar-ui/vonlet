# VONLET SECURITY — THE REVIEW

Issue 01 · November 2026 · ten A4 pages, built entirely from the material already
on vonletsecurity.co.zw and in this repository's image archive.

## Files

| File | What it is |
| --- | --- |
| `01-cover.png` … `10-back-cover.png` | Individual pages, A4 at 300 dpi |
| `vonlet-review.pdf` | The ten pages in reading order, print-ready |
| `contact-sheet.png` | All ten pages at a glance |

Pages are **210 × 297 mm with 3 mm bleed** on every edge, so the PNGs measure
216 × 303 mm (2551 × 3579 px). Trim to the bleed box before commercial print.

## What is in the issue

1. **Cover** — armed-response officer, full bleed.
2. **Contents** — masthead, dispatch and head-office columns.
3. **Who we are** — mission, vision, five core values, the 2010/23/2/24-7 stat
   band, leadership and core business, and the chief executive's head-office
   photograph.
4. **The catalogue** — all twenty-three service lines in the seven groups the
   site uses, with a legend separating lines published on the site from lines
   supplied by the company for it.
5. **Feature — banking & corporate posts** — why presentation is the first
   control, with three post photographs and the sector lines that adjoin it.
6. **Feature — guarding on the ground** — a quad patrol, a cleared boundary and
   a gatehouse register.
7. **Fleet, technology & the control room** — the liveried response vehicle, the
   four carded capabilities and the five electronic-security lines.
8. **Cash in transit** — the four steps of a run, the three disciplines the site
   states (task assignment, route selection, accounting for all books) and the
   provenance band for its concept imagery.
9. **Training, people & the K-9 unit** — the site's four-step recruitment
   process, the four training lines and the K-9 note.
10. **Back cover** — rapid-response number, email, head office and operating
    territory, with the licensing caveat.

## Provenance and accuracy

- Every claim is drawn from the site. Where the site is silent — licensing and
  registration numbers, individual client names, model numbers of equipment —
  the issue says so rather than inventing detail.
- The cash-in-transit images are **AI-generated concept imagery**. The page
  carries a yellow band stating this, as the site's own archive does. They are
  not photographs of company operations.
- Names of individual officers and clients are withheld throughout; captions
  describe what is visible in each frame.

## Rebuilding

```bash
python3 tools/build_magazine.py
```

The build is self-contained. On first run `tools/layout.py` expands the site's
Barlow `woff2` files in `assets/fonts` to TTF and installs them into `~/.fonts`
so ImageMagick can set real type; after that it is a no-op. Output is written
back into this folder.

Requires ImageMagick 6 with an `~/.config/ImageMagick/policy.xml` that permits
the PDF coder for writing:

```xml
<policymap>
  <policy domain="coder" rights="read|write" pattern="PDF" />
</policymap>
```

## How the typesetting works

`tools/layout.py` is a small page-layout engine written for this job: a
millimetre grid with bleed, real glyph metrics from `fontTools` so paragraphs,
rules and captions land exactly where specified, and cover-cropped image
placement with gradient scrims. `tools/magazine_bits.py` holds the shared
furniture (running heads, folios, captions, stat blocks); `tools/build_magazine.py`
holds the ten page layouts.
