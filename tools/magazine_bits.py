#!/usr/bin/env python3
"""VONLET — THE REVIEW. A ten-page company magazine, typeset from the website.

Every word in this issue is drawn from the site itself: the services catalogue,
the company profile, the recruitment process, the photography captions and the
published rates. Nothing is invented, and the provenance labels the site uses
for client-supplied and generated imagery are carried through — the
cash-in-transit spread states plainly that its images are illustrations.

Build:  python3 tools/build_magazine.py
Output: magazine/vonlet-review/  (10 A4 PNGs + PDF + contact sheet)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from layout import (  # noqa: E402
    INK, LINE, LINE_STRONG, NAVY, NAVY_800, NAVY_850, NAVY_900, RED, RED_DEEP,
    SLATE_300, SLATE_400, SLATE_500, WHITE, YELLOW, Page, mm, text_width,
)
from build_services import GROUPS_IN_ORDER, SERVICES  # noqa: E402

OUT = ROOT / "magazine" / "vonlet-review"
IMG = ROOT / "assets" / "images"
# Untouched master files. The site's own `full/`, `cards/`, `cit/` and `concept/`
# folders carry the on-page watermark; the magazine is printed from these
# clean copies so no watermark is baked into the press artwork.
FULL = IMG / "master" / "full"
CARDS = IMG / "cards"
LOGO = ROOT / "assets" / "brand" / "logo-mark-transparent.png"

W, H = 210, 297          # A4 portrait, mm
M = 16                   # page margin, mm

ISSUE = "ISSUE 01 — NOVEMBER 2026"
STRAP = "PROTECTION. WITHOUT COMPROMISE."


# ---------------------------------------------------------------------------
# shared furniture
# ---------------------------------------------------------------------------
def brand(page: Page, y: float, color=None, mark=True, size=4.2) -> None:
    """Shield + wordmark, top-left of the text area.

    `color` defaults to the palette's ink, resolved at call time: a default of
    `INK` would bind the dark edition's off-white when this module is imported
    and keep it, invisibly, through a light build.
    """
    color = INK if color is None else color
    x = M
    if mark:
        page._add("image", dict(x=x, y=y - size * 1.05, w=size * 1.1, h=size * 1.1,
                                path=str(LOGO), focus=(0.5, 0.5), scrim=None,
                                scrim_angle="bottom", border=None))
        x += size * 1.55
    page.text(x, y, "VONLET", "cond-bold", size * 1.28, color, 0.35)
    x += text_width("VONLET", "cond-bold", size * 1.28, 0.35) + 2.2
    page.kicker(x, y, "SECURITY SERVICES", SLATE_500, size * 0.52, 0.34)


def running_head(page: Page, number: int, section: str) -> None:
    l, r = M, W - M
    top = 9
    page.rule(l, top + 2.4, r - l, 0.25, LINE)
    page.kicker(l, top, section, SLATE_500, 2.1, 0.3)
    page.kicker(r - 46, top, ISSUE, SLATE_500, 2.1, 0.26)
    folio_line(page, number)


def folio_line(page: Page, number: int) -> None:
    l, r = M, W - M
    base = H - 11
    page.rule(l, base - 5.6, r - l, 0.25, LINE)
    page.kicker(l, base, "VONLET SECURITY — THE REVIEW", SLATE_500, 2.0, 0.28)
    page.text(l, base, f"{number:02d}", "cond-bold", 3.6, YELLOW, align="right", width=r - l)


def caption(page: Page, x, y, value, width=None, color=None, size=2.35,
            tick=True) -> float:
    """Small caption under a photograph, with a tick on the first line."""
    color = SLATE_500 if color is None else color
    text_x = x
    if tick:
        page.rect(x, y - size * 0.74, 3.0, 0.26, fill=YELLOW)
        text_x = x + 5.0
        width = (width or 60) - 5.0
    return page.paragraph(text_x, y, width or 55, value, "body", size, 1.4, color)


def photo(page: Page, x, y, w, h, name, focus=(0.5, 0.5), scrim=False, border=True) -> None:
    path = FULL / f"{name}.webp"
    if not path.exists():
        path = ROOT / "assets" / "images" / name
    page.image(x, y, w, h, path, focus=focus, scrim=None,
               border=(LINE if border else None))


def stat(page: Page, x, y, value, label, width=30, value_size=11) -> None:
    page.text(x, y, value, "cond-bold", value_size, YELLOW)
    page.kicker(x, y + 4.4, label, SLATE_500, 1.95, 0.22)


# ---------------------------------------------------------------------------
# palettes
# ---------------------------------------------------------------------------
# The issue is typeset once and can be bound to more than one palette. Some
# pages are photographic and would be identical in either theme (the cover and
# back cover are images under a scrim); the rest are type on the page field.
#
# The rules a light palette has to obey are not simply inverted:
#   * the page field is paper, so "white" type is unusable — text anchors on a
#     near-black ink instead;
#   * the site's #facc15 fails against white at every weight and size, so the
#     accent is darkened to a mustard that still reads as the same hue family;
#   * section tints become a light warm grey rather than a lifted navy, because
#     a navy tint on white reads as a printing error;
#   * scrims stay dark. A scrim exists to put light type on a photograph, and a
#     paper-coloured scrim over a photograph is a wash, not a scrim.
THEMES: dict[str, dict[str, str]] = {
    "dark": {},  # the module defaults, below
    "light": {
        "INK": "#0b0f16",          # near-black type on paper
        "PAPER": "#ffffff",
        "NAVY": "#ffffff",         # page field
        "NAVY_900": "#f4f5f7",     # tint panels
        "NAVY_850": "#f4f5f7",     # callout bands
        "NAVY_800": "#e9ebef",
        "LINE": "#dfe3e8",
        "LINE_STRONG": "#b9c0c9",
        "SLATE_300": "#2b3440",    # body copy
        "SLATE_400": "#46505e",
        "SLATE_500": "#6b7280",
        "YELLOW": "#a16207",       # mustard: the brand hue, darkened to read
        "WHITE": "#ffffff",
        "RED": "#c81a1a",
        "RED_DEEP": "#9e1414",
        "SCRIM": "255,255,255",    # unused on paper; kept for symmetry
        "SHADOW": "rgba(11,15,22,",
    },
}

# Names rebound for a light build. NAVY* are the page field and its tints, so a
# theme swap has to move them together with the type colours.
_PALETTE_NAMES = (
    "INK", "NAVY", "NAVY_800", "NAVY_850", "NAVY_900", "LINE", "LINE_STRONG",
    "SLATE_300", "SLATE_400", "SLATE_500", "RED", "RED_DEEP", "YELLOW", "WHITE",
)


def apply_theme(theme: str) -> None:
    """Rebind the palette names in this module and in build_magazine.

    Done by rebinding module globals rather than by threading a palette object
    through ten page functions: the page layouts already read these names, and
    a build is a single-theme run from start to finish, so there is no point at
    which two palettes need to coexist inside one page.
    """
    if theme not in THEMES:
        raise SystemExit(f"unknown theme: {theme} (choose from {', '.join(THEMES)})")
    values = THEMES[theme]

    # `python3 tools/build_magazine.py` runs the builder as __main__, so a plain
    # `import build_magazine` would load a second copy and rebind that one while
    # the copy actually drawing the pages stayed dark.
    import build_magazine

    # Every loaded module that declares itself themed. Running the builder as a
    # script puts the palette in `__main__`, so importing it again by name would
    # rebind an unused copy while the pages kept the original colours.
    targets, seen = [], set()
    for module in [build_magazine, *list(sys.modules.values())]:
        if module is None or not getattr(module, "_THEMED", False):
            continue
        if id(module) in seen:
            continue
        seen.add(id(module))
        targets.append(module)

    for name in _PALETTE_NAMES:
        value = values.get(name)
        if value is None:
            continue
        globals()[name] = value
        for target in targets:
            setattr(target, name, value)

    for target in targets:
        setattr(target, "THEME", theme)
