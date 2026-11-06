#!/usr/bin/env python3
"""VONLET — SIGNAGE & RECEPTION KIT.

Every sign a security company actually has to make, drawn to scale in
millimetres so each file can go straight to a fabricator, a printer or a sign
shop. Each board is rendered at the resolution it needs — a 5.2 m reception wall
does not need 300 dpi, an 800 mm plaque does.

Every string is measured with the real font metrics before it is placed, and
long lines are shrunk or wrapped to the column they belong to, so type can never
run into the next column.

Output: signage/  (one PNG per board, plus a contact sheet)

  python3 tools/build_signage.py
  python3 tools/build_signage.py --only 06-reception-wall
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import layout  # noqa: E402
from layout import (  # noqa: E402
    INK, LINE, LINE_STRONG, NAVY, NAVY_800, NAVY_850, NAVY_900, RED, RED_DEEP,
    SLATE_300, SLATE_400, SLATE_500, WHITE, YELLOW, Page, text_width,
)

OUT = ROOT / "signage"
BRAND = ROOT / "assets" / "brand"
LOGO = BRAND / "logo-mark-transparent.png"

PHONE = "+263 772 856 852"
EMAIL = "info@vonletsecurity.co.zw"
WEB = "vonletsecurity.co.zw"
ADDRESS_1 = "9 Blatherwick Road"
ADDRESS_2 = "Queensdale, Harare"
STRAP = "PROTECTION. WITHOUT COMPROMISE."


# ---------------------------------------------------------------------------
# measured type helpers
# ---------------------------------------------------------------------------
def fit(value: str, role: str, size: float, max_w: float, tracking: float = 0.0,
        floor: float = 5.0) -> float:
    """Shrink `size` until the string fits `max_w` millimetres."""
    while size > floor and text_width(value, role, size, tracking) > max_w:
        size *= 0.97
    return size


def draw(page: Page, x, y, value, role, size, color, tracking=0.0, max_w=None,
         align="left", width=None) -> float:
    """Draw one measured line, optionally fitted to a maximum width."""
    if max_w:
        size = fit(value, role, size, max_w, tracking)
    return page.text(x, y, value, role, size, color, tracking,
                     align=align, width=width)


def kick(page: Page, x, y, value, color, size, tracking=0.0, max_w=None,
         align="left", width=None) -> None:
    """Letterspaced label, fitted to a maximum width."""
    value = value.upper()
    if max_w:
        size = fit(value, "semi", size, max_w, tracking)
    page.kicker(x, y, value, color, size, tracking, align=align, width=width)


def draw_right(page: Page, right, y, value, role, size, color, tracking=0.0,
               max_w=None, left=0.0) -> float:
    """Right-align a line on `right`; `left` is where its column begins."""
    if max_w:
        size = fit(value, role, size, max_w, tracking)
    return page.text(left, y, value, role, size, color, tracking,
                     align="right", width=right - left)


def kick_right(page: Page, right, y, value, color, size, tracking=0.0,
               max_w=None, left=0.0) -> None:
    value = value.upper()
    if max_w:
        size = fit(value, "semi", size, max_w, tracking)
    page.kicker(left, y, value, color, size, tracking,
                align="right", width=right - left)


def para(page: Page, x, y, width, value, size, leading, color, max_lines=None):
    """Wrapped body copy. Returns the baseline of the last line."""
    return page.paragraph(x, y, width, value, "body", size, leading, color)


def hairline(page: Page, x, y, w, color=LINE_STRONG, t=2.0) -> None:
    page.rule(x, y, w, t, color)


# ---------------------------------------------------------------------------
# shared furniture
# ---------------------------------------------------------------------------
def shield(page: Page, x, y, size, wordmark=True, max_w=None) -> float:
    """Shield, and optionally the VONLET wordmark beside it.

    `max_w` caps the whole lockup so it cannot run into the next column; the
    shield shrinks with it.
    """
    if max_w:
        size = min(size, max_w / 3.05)
    page.image(x, y, size, size, LOGO, focus=(0.5, 0.5))
    if not wordmark:
        return x + size
    tx = x + size * 1.16
    wm_size = fit("VONLET", "cond-bold", size * 0.58, size * 2.2, 0.02)
    page.text(tx, y + size * 0.58, "VONLET", "cond-bold", wm_size, INK, 0.02)
    kick(page, tx + size * 0.04, y + size * 0.84, "SECURITY SERVICES",
         SLATE_400, size * 0.128, size * 0.006, max_w=size * 2.1)
    return tx + text_width("VONLET", "cond-bold", wm_size, 0.02)


def foot_band(page: Page, h, label_left, label_right, color=RED) -> None:
    """Solid strap along the bottom edge of a board."""
    W, H = page.width_mm, page.height_mm
    page.rect(0, H - h, W, h, fill=color)
    base = H - h / 2 + h * 0.13
    kick(page, W * 0.035, base, label_left, INK, h * 0.30, h * 0.03,
         max_w=W * 0.55)
    if label_right:
        kick_right(page, W * 0.965, base, label_right, INK, h * 0.30, h * 0.03,
                   max_w=W * 0.38, left=W * 0.5)


def top_rule(page: Page, h, colour=YELLOW) -> None:
    page.rect(0, 0, page.width_mm, h, fill=colour)


# ---------------------------------------------------------------------------
# 01 — MAIN GATE PYLON  3600 x 2200 mm
# ---------------------------------------------------------------------------
def gate_pylon() -> Page:
    """Full-width pylon: brand, statement, then the number in a yellow band.

    Read from fifty metres away, so it carries three things and nothing else.
    """
    p = Page(width_mm=3600, height_mm=2200, bleed_mm=40, background=NAVY)
    W, H = 3600, 2200

    # masthead
    p.rect(0, 0, W, 46, fill=YELLOW)
    p.image(170, 200, 520, 520, LOGO, focus=(0.5, 0.5))
    draw(p, 780, 560, "VONLET", "cond-bold", 320, INK, 0.02, max_w=1500)
    kick(p, 792, 700, "SECURITY SERVICES", SLATE_300, 96, 10, max_w=1100)
    hairline(p, 792, 760, 900, YELLOW, 12)

    # the statement
    draw(p, 170, 1030, "SITE SECURED", "cond-bold", 280, INK, 0.01, max_w=2100)
    draw(p, 170, 1300, "BY VONLET", "cond-bold", 280, YELLOW, 0.01, max_w=2100)

    kick(p, 170, 1440, "MANNED GUARDING  ·  ELECTRONIC SECURITY  ·  K-9",
         SLATE_400, 66, 8, max_w=2300)
    kick(p, 170, 1530, f"{ADDRESS_1}, {ADDRESS_2}  ·  {WEB}", SLATE_500, 60, 7,
         max_w=2400)

    # the number, on yellow, full width
    band_y = H - 430
    p.rect(0, band_y, W, 270, fill=YELLOW)
    kick(p, 170, band_y + 74, "24-HOUR CONTROL ROOM", NAVY, 68, 7, max_w=1000)
    draw(p, 170, band_y + 232, PHONE, "cond-bold", 132, NAVY, 0.01, max_w=1900)
    kick_right(p, W - 170, band_y + 232, "EMERGENCY · ANY HOUR", NAVY, 58, 6,
               max_w=1100)

    # licensing strip
    p.rect(0, H - 160, W, 160, fill=RED)
    kick(p, 170, H - 68, STRAP, INK, 68, 8, max_w=1500)
    kick_right(p, W - 170, H - 68, "ZIMBABWE  ·  ZAMBIA", INK, 68, 8, max_w=900)
    return p


# ---------------------------------------------------------------------------
# 02 — PEDESTRIAN GATE PLATE  2400 x 900 mm
# ---------------------------------------------------------------------------
def gate_plate() -> Page:
    p = Page(width_mm=2400, height_mm=900, bleed_mm=30, background=NAVY)
    W, H = 2400, 900
    p.rect(0, 0, 46, H, fill=YELLOW)
    shield(p, 130, 190, 500, max_w=1290)
    kick(p, 130, 730, "AUTHORISED ENTRY ONLY", YELLOW, 80, 8, max_w=1320)

    p.vrule(1520, 120, 660, 10, LINE_STRONG)
    rx, rw = 1620, 680
    kick(p, rx, 210, "SIGN IN AT THE GATEHOUSE", SLATE_300, 60, 6, max_w=rw)
    draw(p, rx, 360, "ALL VISITORS", "cond-bold", 132, INK, 0.01, max_w=rw)
    draw(p, rx, 500, "MUST REPORT", "cond-bold", 132, YELLOW, 0.01, max_w=rw)
    hairline(p, rx, 570, rw)
    kick(p, rx, 650, "VEHICLES SUBJECT TO SEARCH", SLATE_400, 56, 6, max_w=rw)
    kick(p, rx, 730, "SITE CLOSED 18:00 — 06:00", SLATE_500, 52, 5, max_w=rw)
    return p


# ---------------------------------------------------------------------------
# 03–05 — WARNING BOARDS  600 x 450 mm
# ---------------------------------------------------------------------------
def _warning(title_lines, note, footer, accent=YELLOW, pict=None):
    p = Page(width_mm=600, height_mm=450, bleed_mm=15, background=NAVY)
    W, H = 600, 450
    p.rect(0, 0, W, 36, fill=RED)
    kick(p, 36, 26, "VONLET SECURITY", INK, 20, 2.6, max_w=W - 72)

    # pictogram field
    p.rect(36, 62, 96, 96, fill=accent)
    if pict:
        pict(p)

    y = 200
    for line in title_lines:
        size = fit(line, "cond-bold", 56, W - 72, 0.01)
        draw(p, 36, y, line, "cond-bold", size, INK, 0.01)
        y += size * 1.12

    # body copy flows from the title block, footer sits under whatever it becomes
    body_size = 21
    bottom = para(p, 36, y + 14, W - 72, note, body_size, 1.32, SLATE_400)
    hairline(p, 36, bottom + 24, W - 72)
    kick(p, 36, bottom + 56, footer, accent, 18, 2.4, max_w=W - 72)
    return p


def _pict_camera(p):
    p.rect(50, 78, 52, 34, fill=NAVY)
    p.rect(102, 84, 18, 20, fill=NAVY)
    p.rect(62, 112, 8, 34, fill=NAVY)


def _pict_dog(p):
    p.rect(50, 78, 52, 34, fill=NAVY_900)
    p.rect(108, 78, 18, 34, fill=NAVY_900)


def _pict_vehicle(p):
    p.rect(50, 84, 68, 44, fill=NAVY)


def warning_cctv():
    return _warning(["CCTV IN", "OPERATION"],
                    "This site is monitored continuously. Recordings are retained "
                    "and may be used in the investigation of crime.",
                    "CAMERAS · MONITORED 24/7", pict=_pict_camera)


def warning_dogs():
    return _warning(["GUARD DOGS", "ON PATROL"],
                    "Do not enter unescorted. Handlers and dogs are deployed day "
                    "and night. Remain in your vehicle and wait to be received.",
                    "DO NOT APPROACH THE ANIMALS", accent=RED, pict=_pict_dog)


def warning_search():
    return _warning(["VEHICLES", "SUBJECT TO SEARCH"],
                    "All vehicles and personal effects entering or leaving this "
                    "site may be searched by a security officer.",
                    "BY ORDER OF SITE MANAGEMENT", pict=_pict_vehicle)


# ---------------------------------------------------------------------------
# 06 — RECEPTION WALL  5200 x 2400 mm
# ---------------------------------------------------------------------------
def reception_wall() -> Page:
    """The wall behind the reception desk at head office.

    Split 60/40: a quiet brand field on the left that a visitor reads while
    waiting, and the practical side on the right — the team, then how to sign in
    and who to call. Only four things compete for attention.
    """
    p = Page(width_mm=5200, height_mm=2400, bleed_mm=50, background=NAVY)
    W, H = 5200, 2400
    p.rect(0, 0, W, 34, fill=YELLOW)

    # --- left: the brand field ---------------------------------------------
    p.image(300, 250, 620, 620, LOGO, focus=(0.5, 0.5))
    draw(p, 300, 1120, "VONLET", "cond-bold", 330, INK, 0.02, max_w=2600)
    kick(p, 312, 1250, "SECURITY SERVICES", SLATE_300, 94, 11, max_w=2000)
    hairline(p, 300, 1330, 2680, YELLOW, 10)

    for i, (line, colour) in enumerate([("PROTECTION.", INK),
                                        ("WITHOUT", YELLOW),
                                        ("COMPROMISE.", INK)]):
        size = fit(line, "cond-bold", 200, 2680, 0.01)
        p.text(300, 1590 + i * (size * 1.08), line, "cond-bold", size,
               colour, 0.01)

    kick(p, 300, 2190, "MANNED GUARDING  ·  CASH IN TRANSIT  ·  ELECTRONIC SECURITY",
         SLATE_500, 52, 6, max_w=2680)

    # --- right: the practical side -----------------------------------------
    p.vrule(3100, 250, 1990, 10, LINE_STRONG)

    rx, rw = 3260, 1620
    p.image(rx, 250, rw, 760,
            ROOT / "assets/images/master/full/wa-09-suit-team-entrance.webp",
            focus=(0.5, 0.24))
    kick(p, rx, 1070, "OFFICERS BADGED FOR A CORPORATE POSTING", SLATE_500, 46, 5,
         max_w=rw)

    kick(p, rx, 1180, "WELCOME TO VONLET", YELLOW, 60, 7, max_w=rw)
    draw(p, rx, 1310, "Sign in at", "cond-bold", 132, INK, 0.01, max_w=rw)
    draw(p, rx, 1430, "reception.", "cond-bold", 132, YELLOW, 0.01, max_w=rw)
    para(p, rx, 1500, rw,
         "All visitors report to reception and are issued a visitor pass. "
         "Officers will direct you to your appointment.", 50, 1.38, SLATE_300)

    rows = [("CONTROL ROOM  ·  24 HOURS", PHONE),
            ("EMAIL", EMAIL),
            ("HEAD OFFICE", f"{ADDRESS_1}, {ADDRESS_2}")]
    y = 1700
    for label, value in rows:
        hairline(p, rx, y - 52, rw, LINE, 4)
        kick(p, rx, y, label, SLATE_500, 42, 5, max_w=rw)
        draw(p, rx, y + 82, value, "body", 56, INK, 0.0, max_w=rw)
        y += 190

    p.rect(0, H - 120, W, 120, fill=RED)
    kick(p, 300, H - 62, f"{PHONE}   ·   {WEB}", INK, 54, 6, max_w=2400)
    kick_right(p, W - 300, H - 62, "ZIMBABWE  ·  ZAMBIA", INK, 54, 6, max_w=900)
    return p


# ---------------------------------------------------------------------------
# 07 — RECEPTION DESK FRONT  2400 x 1100 mm
# ---------------------------------------------------------------------------
def reception_desk() -> Page:
    p = Page(width_mm=2400, height_mm=1100, bleed_mm=30, background=NAVY_900)
    W, H = 2400, 1100
    p.rect(0, 0, W, 24, fill=YELLOW)
    shield(p, 110, 300, 400)
    kick(p, 110, 810, "RECEPTION", YELLOW, 96, 9, max_w=900)

    p.vrule(1520, 180, 740, 8, LINE_STRONG)
    rx, rw = 1620, 700
    kick(p, rx, 280, "PLEASE WAIT TO BE SEEN", SLATE_300, 54, 5, max_w=rw)
    draw(p, rx, 440, "A HOST WILL", "cond-bold", 104, INK, 0.01, max_w=rw)
    draw(p, rx, 570, "COLLECT YOU", "cond-bold", 104, YELLOW, 0.01, max_w=rw)
    hairline(p, rx, 640, rw)
    para(p, rx, 720, rw, "Visitor passes must be worn at all times while on site.",
         44, 1.35, SLATE_400)
    return p


# ---------------------------------------------------------------------------
# 08 — AFTER-HOURS RECEPTION BOARD  1200 x 800 mm
# ---------------------------------------------------------------------------
def reception_after_hours() -> Page:
    p = Page(width_mm=1200, height_mm=800, bleed_mm=20, background=NAVY)
    W, H = 1200, 800
    p.rect(0, 0, W, 28, fill=RED)
    shield(p, 60, 74, 108)
    hairline(p, 60, 230, W - 120, LINE_STRONG, 4)

    kick(p, 60, 300, "RECEPTION IS CLOSED", YELLOW, 38, 4, max_w=W - 120)
    y = 360
    for line, colour in [("After hours, all", INK), ("entry is through", INK),
                         ("the security gate.", YELLOW)]:
        size = fit(line, "cond-bold", 58, W - 120, 0.01)
        p.text(60, y, line, "cond-bold", size, colour, 0.01)
        y += size * 1.06

    kick(p, 60, 610, "CALL THE CONTROL ROOM", SLATE_500, 24, 3, max_w=400)
    draw(p, 60, 680, PHONE, "cond-bold", 66, INK, 0.01, max_w=W - 120)
    kick(p, 60, 736, f"{EMAIL}  ·  {WEB}", SLATE_500, 20, 2.2, max_w=W - 120)
    return p


# ---------------------------------------------------------------------------
# 09 — VEHICLE LIVERY, DOOR PANEL  2200 x 900 mm
# ---------------------------------------------------------------------------
def vehicle_livery() -> Page:
    p = Page(width_mm=2200, height_mm=900, bleed_mm=25, background=WHITE)
    W, H = 2200, 900
    p.rect(0, 0, W, 110, fill=YELLOW)
    kick(p, 80, 76, "RAPID RESPONSE  ·  24 HOURS", NAVY, 56, 7, max_w=900)

    p.image(80, 210, 360, 360, LOGO, focus=(0.5, 0.5))
    draw(p, 470, 430, "VONLET", "cond-bold", 220, NAVY, 0.02, max_w=800)
    kick(p, 482, 530, "SECURITY SERVICES", SLATE_500, 70, 8, max_w=760)
    p.rect(470, 580, 560, 8, fill=RED)
    draw(p, 470, 760, PHONE, "cond-bold", 112, NAVY, 0.01, max_w=760)

    rx, rw = 1290, W - 1290 - 70
    draw(p, rx, 620, WEB, "body", 56, SLATE_500, 0.0, max_w=rw)
    draw(p, rx, 700, EMAIL, "body", 56, SLATE_500, 0.0, max_w=rw)
    draw(p, rx, 780, f"{ADDRESS_1}, {ADDRESS_2}", "body", 50, SLATE_500, 0.0,
         max_w=rw)
    p.rect(W - 10, 0, 10, H, fill=RED)
    return p


# ---------------------------------------------------------------------------
# 10 — NOTICE / INFORMATION BOARD  800 x 1100 mm
# ---------------------------------------------------------------------------
def notice_board() -> Page:
    p = Page(width_mm=800, height_mm=1100, bleed_mm=20, background=NAVY)
    W, H = 800, 1100
    p.rect(0, 0, W, 16, fill=YELLOW)
    p.rect(0, 16, W, 12, fill=RED)
    shield(p, 60, 66, 88)
    hairline(p, 60, 200, W - 120, LINE_STRONG, 3)

    draw(p, 60, 280, "NOTICE TO", "cond-bold", 70, INK, 0.01, max_w=W - 120)
    draw(p, 60, 350, "ALL PERSONS", "cond-bold", 70, YELLOW, 0.01, max_w=W - 120)
    draw(p, 60, 420, "ON SITE", "cond-bold", 70, INK, 0.01, max_w=W - 120)

    rules = [
        "Report to the gatehouse or reception on arrival.",
        "Wear your visitor pass where it can be seen.",
        "No photography or recording without written approval.",
        "Vehicles, bags and personal effects may be searched.",
        "Follow the instructions of security officers at all times.",
    ]
    # spread the list so it fills the board instead of leaving a third empty
    y = 500
    for i, rule in enumerate(rules, 1):
        p.text(60, y, f"{i:02d}", "cond-bold", 30, YELLOW)
        para(p, 122, y, W - 182, rule, 26, 1.34, SLATE_300)
        y += 104

    hairline(p, 60, H - 118, W - 120, LINE, 3)
    kick(p, 60, H - 70, f"CONTROL ROOM  {PHONE}", YELLOW, 22, 2.5, max_w=W - 120)
    return p


# ---------------------------------------------------------------------------
# 11 — HI-VIS SAFETY VEST BACK PANEL  560 x 640 mm
# ---------------------------------------------------------------------------
def safety_vest() -> Page:
    p = Page(width_mm=560, height_mm=640, bleed_mm=10, background=YELLOW)
    W, H = 560, 640
    p.rect(0, 0, W, 48, fill=RED)
    kick(p, 28, 33, "VONLET SECURITY", INK, 20, 2.6, max_w=W - 56)
    p.rect(0, H - 48, W, 48, fill=RED)

    draw(p, 28, 140, "VONLET", "cond-bold", 88, NAVY, 0.02, max_w=300)
    kick(p, 30, 178, "SECURITY SERVICES", NAVY, 22, 2.6, max_w=300)
    p.rect(28, 208, 260, 6, fill=RED)

    kick(p, 28, 262, "SECURITY", NAVY, 38, 4, max_w=320)
    draw(p, 28, 350, "ON DUTY", "cond-bold", 82, NAVY, 0.01, max_w=340)
    kick(p, 28, 406, "24 HOUR CONTROL ROOM", NAVY, 21, 2.4, max_w=340)
    draw(p, 28, 470, PHONE, "cond-bold", 50, NAVY, 0.01, max_w=340)

    p.image(392, 286, 120, 120, LOGO, focus=(0.5, 0.5))
    kick(p, 28, 556, "AUTHORISED PERSONNEL ONLY", NAVY, 20, 2.4, max_w=W - 56)
    return p


# ---------------------------------------------------------------------------
# 12 — SITE ID / COMPANY PLAQUE  600 x 400 mm
# ---------------------------------------------------------------------------
def company_plaque() -> Page:
    p = Page(width_mm=600, height_mm=400, bleed_mm=12, background=NAVY_900)
    W, H = 600, 400
    p.rect(0, 0, W, 16, fill=YELLOW)
    p.rect(0, H - 16, W, 16, fill=RED)

    p.image(36, 62, 104, 104, LOGO, focus=(0.5, 0.5))
    draw(p, 160, 130, "VONLET", "cond-bold", 74, INK, 0.02, max_w=380)
    kick(p, 166, 168, "SECURITY SERVICES", SLATE_400, 24, 2.8, max_w=380)
    hairline(p, 36, 202, W - 72, LINE_STRONG, 3)

    rows = [(PHONE, WEB), (ADDRESS_1, ADDRESS_2)]
    y = 252
    for left, right in rows:
        draw(p, 36, y, left, "body", 24, SLATE_300, 0.0, max_w=250)
        draw(p, 300, y, right, "body", 24, SLATE_300, 0.0, max_w=W - 336)
        y += 40
    kick(p, 36, H - 38, STRAP, SLATE_500, 17, 2.2, max_w=W - 72)
    return p


# ---------------------------------------------------------------------------
# 13 — EVENT BACKDROP  3000 x 750 mm
# ---------------------------------------------------------------------------
def event_backdrop() -> Page:
    p = Page(width_mm=3000, height_mm=750, bleed_mm=30, background=NAVY)
    W, H = 3000, 750
    p.rect(0, 0, W, 14, fill=RED)
    p.image(90, 180, 360, 360, LOGO, focus=(0.5, 0.5))
    draw(p, 500, 400, "VONLET", "cond-bold", 260, INK, 0.02, max_w=800)
    kick(p, 512, 500, "SECURITY SERVICES", SLATE_300, 74, 8, max_w=800)

    p.vrule(1420, 120, 470, 8, LINE_STRONG)
    tx, tw_ = 1540, 1350
    draw(p, tx, 300, "PROTECTION.", "cond-bold", 146, INK, 0.01, max_w=tw_)
    draw(p, tx, 450, "WITHOUT COMPROMISE.", "cond-bold", 146, YELLOW, 0.01, max_w=tw_)
    kick(p, tx, 545, "MANNED GUARDING  ·  CASH IN TRANSIT", SLATE_400, 48, 5, max_w=tw_)
    kick(p, tx, 615, "ELECTRONIC SECURITY  ·  K-9  ·  TRAINING", SLATE_400, 48, 5, max_w=tw_)

    p.rect(0, H - 92, W, 92, fill=RED)
    kick(p, 90, H - 34, f"{PHONE}   ·   {WEB}", INK, 50, 6, max_w=W - 180)
    return p


# ---------------------------------------------------------------------------
# 14 — FLOOR WAYFINDING  900 x 300 mm
# ---------------------------------------------------------------------------
def wayfinding() -> Page:
    p = Page(width_mm=900, height_mm=300, bleed_mm=15, background=NAVY_900)
    W, H = 900, 300
    p.rect(0, 0, 18, H, fill=YELLOW)
    p.image(56, 92, 108, 108, LOGO, focus=(0.5, 0.5))
    kick(p, 56, 58, "VONLET SECURITY", SLATE_500, 20, 2.4, max_w=220)
    draw(p, 200, 158, "RECEPTION", "cond-bold", 76, INK, 0.02, max_w=430)
    draw(p, 200, 224, "VISITORS SIGN IN HERE", "cond-bold", 44, YELLOW, 0.01,
         max_w=430)

    # arrow, built from bars
    ay = H / 2
    p.rect(W - 205, ay - 9, 110, 18, fill=YELLOW)
    p.rect(W - 108, ay - 34, 18, 68, fill=YELLOW)
    p.rect(W - 126, ay - 17, 18, 34, fill=YELLOW)
    return p


# ---------------------------------------------------------------------------
# 15 — A-FRAME / PAVEMENT SIGN  700 x 1000 mm
# ---------------------------------------------------------------------------
def a_frame() -> Page:
    p = Page(width_mm=700, height_mm=1000, bleed_mm=15, background=NAVY)
    W, H = 700, 1000
    p.rect(0, 0, W, 34, fill=YELLOW)
    p.rect(0, H - 20, W, 20, fill=RED)

    p.image(W / 2 - 130, 80, 260, 260, LOGO, focus=(0.5, 0.5))
    draw(p, 0, 440, "VONLET", "cond-bold", 132, INK, 0.02,
         align="center", width=W)
    kick(p, 0, 496, "SECURITY SERVICES", SLATE_300, 36, 4.5,
         align="center", width=W)
    p.rect(150, 546, W - 300, 5, fill=RED)

    draw(p, 0, 650, "MANNED", "cond-bold", 84, YELLOW, 0.01, align="center", width=W)
    draw(p, 0, 730, "GUARDING", "cond-bold", 84, YELLOW, 0.01, align="center", width=W)
    draw(p, 0, 810, "24 HOURS", "cond-bold", 84, INK, 0.01, align="center", width=W)

    kick(p, 0, 872, "CALL THE CONTROL ROOM", SLATE_400, 30, 3.4,
         align="center", width=W)
    draw(p, 0, 936, PHONE, "cond-bold", 54, INK, 0.01, align="center", width=W)
    return p


# ---------------------------------------------------------------------------
SIGNS = [
    ("01-gate-pylon", gate_pylon, 40),
    ("02-gate-plate", gate_plate, 60),
    ("03-warning-cctv", warning_cctv, 150),
    ("04-warning-dogs", warning_dogs, 150),
    ("05-warning-search", warning_search, 150),
    ("06-reception-wall", reception_wall, 26),
    ("07-reception-desk", reception_desk, 60),
    ("08-reception-after-hours", reception_after_hours, 90),
    ("09-vehicle-livery", vehicle_livery, 60),
    ("10-notice-board", notice_board, 90),
    ("11-hi-vis-vest", safety_vest, 110),
    ("12-company-plaque", company_plaque, 150),
    ("13-event-backdrop", event_backdrop, 30),
    ("14-wayfinding", wayfinding, 100),
    ("15-a-frame", a_frame, 90),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None, help="render only these slugs")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rendered = []
    for slug, fn, dpi in SIGNS:
        if args.only and slug not in args.only:
            continue
        layout.set_dpi(dpi)
        page = fn()
        target = OUT / f"{slug}.png"
        page.render(target)
        rendered.append((slug, target, int(page.width_mm), int(page.height_mm)))
        print(f"  {slug:<28} {rendered[-1][2]:>5} x {rendered[-1][3]:>4} mm"
              f"   {target.stat().st_size // 1024:>5} KB")

    if not rendered:
        return

    # The boards are metres wide at print resolution; shrink each to a proof tile
    # first, or montage exhausts ImageMagick's memory.
    thumbs = []
    for slug, target, _, _ in rendered:
        thumb = OUT / f".thumb-{slug}.png"
        subprocess.run(["convert", str(target), "-resize", "420x420>", "-depth", "8",
                        str(thumb)], check=True)
        thumbs.append(str(thumb))
    sheet = OUT / "contact-sheet.png"
    subprocess.run(["montage", *thumbs, "-tile", "4x", "-geometry", "420x420+10+10",
                    "-background", "#030816", "-depth", "8", str(sheet)], check=True)
    for thumb in thumbs:
        Path(thumb).unlink(missing_ok=True)
    print(f"  {'contact-sheet':<28} {'':>16}   {sheet.stat().st_size // 1024:>5} KB")


if __name__ == "__main__":
    main()
