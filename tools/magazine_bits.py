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
def brand(page: Page, y: float, color=INK, mark=True, size=4.2) -> None:
    """Shield + wordmark, top-left of the text area."""
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


def caption(page: Page, x, y, value, width=None, color=SLATE_500, size=2.35,
            tick=True) -> float:
    """Small caption under a photograph, with a yellow tick on the first line."""
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
