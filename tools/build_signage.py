#!/usr/bin/env python3
"""VONLET — SIGNAGE & RECEPTION KIT.

Every sign a security company actually has to make, drawn to scale in
millimetres so each file can go straight to a fabricator, a printer or a sign
shop. Each board is rendered at the resolution it needs — a 5.2 m reception wall
does not need 300 dpi, an 800 mm plaque does.

Modern edition. The kit is drawn on paper and stone rather than on navy: the
field is the material a fabricator is actually printing onto, type is set in ink
and the brand mustard is used as a graphic accent — a spine, a rule, a numeral —
never as text, because #facc15 on white sits at 1.9:1 and would be unreadable at
any distance. Where the accent has to be type it becomes #985c06, the same
mustard the website uses for small mark-up, which clears 5:1 on paper. Signal
red survives only where it is doing regulatory work: the warning boards and the
after-hours redirect.

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
from layout import Page, text_width  # noqa: E402

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
# tokens
# ---------------------------------------------------------------------------
PAPER = "#ffffff"        # the sheet the board is printed on
STONE = "#f1f3f5"        # secondary field: photograph beds, payload panels
TYPE = "#0b0f16"         # primary type, 19:1 on paper
TYPE_SOFT = "#2b3440"    # long body copy
MUTED = "#5f6a7a"        # captions and technical lines, 5.9:1 on paper
HAIR = "#cfd6dd"         # hairline structure
GOLD = "#facc15"         # brand mustard — fills and rules only, never type
GOLD_INK = "#985c06"     # mustard as type, 5.0:1 on paper
RED = "#c81a1a"          # regulation only: warnings, after-hours
RED_DEEP = "#9e1414"

# The safety vest is the one board that must stay high-visibility yellow; navy
# type on it is the strongest pairing available (12.4:1).
HIVIS = GOLD
HIVIS_TYPE = "#0b1030"


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


def label(page: Page, x, y, value, size, color=MUTED, tracking=0.24, max_w=None,
          align="left", width=None) -> None:
    """Letterspaced technical caption — the kit's smallest voice."""
    value = value.upper()
    if max_w:
        size = fit(value, "semi", size, max_w, tracking)
    page.kicker(x, y, value, color, size, tracking, align=align, width=width)


def label_right(page: Page, right, y, value, size, color=MUTED, tracking=0.24,
                max_w=None, left=0.0) -> None:
    value = value.upper()
    if max_w:
        size = fit(value, "semi", size, max_w, tracking)
    page.kicker(left, y, value, color, size, tracking,
                align="right", width=right - left)


def wrap_lines(value, width, size, role="body", track=0.0):
    """Dry-run the wrapper so a block can be measured before it is drawn."""
    lines, current = [], ""
    for word in value.split():
        trial = (current + " " + word).strip()
        if not current or text_width(trial, role, size, track) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def para(page: Page, x, y, width, value, size, leading, color=TYPE_SOFT):
    """Wrapped body copy, ragged right.

    The engine justifies by default, which is right for a magazine column and
    wrong for a sign: stretched word gaps read as damage at three metres.
    """
    return page.paragraph(x, y, width, value, "body", size, leading, color,
                          justify=False)


def hair(page: Page, x, y, w, color=HAIR, t=2.0) -> None:
    page.rule(x, y, w, t, color)


def vhair(page: Page, x, y, h, color=HAIR, t=2.0) -> None:
    page.vrule(x, y, h, t, color)


def spine(page: Page, side="left", w=18, color=GOLD) -> None:
    """The one structural accent: a solid edge the board is hung against."""
    W, H = page.width_mm, page.height_mm
    if side == "left":
        page.rect(0, 0, w, H, fill=color)
    elif side == "right":
        page.rect(W - w, 0, w, H, fill=color)
    elif side == "bottom":
        page.rect(0, H - w, W, w, fill=color)
    else:
        page.rect(0, 0, W, w, fill=color)


def lockup(page: Page, x, y, size, ink=TYPE, sub=MUTED, max_w=None) -> float:
    """Shield plus the VONLET wordmark, set in `ink` for the surface it is on."""
    if max_w:
        size = min(size, max_w / 3.05)
    page.image(x, y, size, size, LOGO, focus=(0.5, 0.5))
    tx = x + size * 1.16
    wm = fit("VONLET", "cond-bold", size * 0.58, size * 2.2, 0.02)
    page.text(tx, y + size * 0.58, "VONLET", "cond-bold", wm, ink, 0.02)
    label(page, tx + size * 0.04, y + size * 0.84, "SECURITY SERVICES",
          size * 0.126, sub, size * 0.005, max_w=size * 2.1)
    return tx + text_width("VONLET", "cond-bold", wm, 0.02)


def tech(page: Page, ref, title, size=None, color=MUTED) -> None:
    """Technical caption along the bottom-left: reference, name, finished size."""
    W, H = page.width_mm, page.height_mm
    size = size or max(14.0, min(W, H) * 0.022)
    value = f"{ref}  ·  {title}  ·  {int(W)} × {int(H)} MM"
    label(page, W * 0.055, H - size * 1.9, value, size, color,
          tracking=0.2, max_w=W - W * 0.11)


# ---------------------------------------------------------------------------
# 01 — MAIN GATE PYLON  3600 x 2200 mm
# ---------------------------------------------------------------------------
def gate_pylon() -> Page:
    """White monolith, mustard spine, three things read from fifty metres."""
    p = Page(width_mm=3600, height_mm=2200, bleed_mm=40, background=PAPER)
    W, H = 3600, 2200
    spine(p, "left", 34, GOLD)

    lockup(p, 190, 180, 430, ink=TYPE, sub=MUTED, max_w=1500)
    hair(p, 190, 700, 1500, TYPE, 6)

    draw(p, 190, 1060, "SITE SECURED", "cond-bold", 300, TYPE, 0.01, max_w=2380)
    draw(p, 190, 1380, "BY VONLET", "cond-bold", 300, GOLD_INK, 0.01, max_w=2380)

    label(p, 196, 1560, "MANNED GUARDING  ·  ELECTRONIC SECURITY  ·  K-9",
          64, MUTED, 0.16, max_w=2300)
    label(p, 196, 1656, f"{ADDRESS_1}, {ADDRESS_2}  ·  {WEB}", 54, MUTED, 0.14,
          max_w=2400)

    # right rail: the capability list, set small against a hairline, so the
    # board is balanced without competing with the statement
    vhair(p, 2820, 180, 1180, HAIR, 3)
    for i, cap in enumerate(("MANNED GUARDING", "ELECTRONIC SECURITY",
                             "K-9 UNITS", "CASH IN TRANSIT")):
        label_right(p, W - 190, 330 + i * 168, cap, 66, MUTED, 0.18,
                    max_w=1010, left=2940)

    # the number, on the mustard plinth at the foot of the board
    band = H - 380
    p.rect(0, band, W, 300, fill=GOLD)
    label(p, 190, band + 78, "24-HOUR CONTROL ROOM", 62, TYPE, 0.2, max_w=1100)
    draw(p, 190, band + 250, PHONE, "cond-bold", 150, TYPE, 0.01, max_w=1900)
    label_right(p, W - 190, band + 250, "EMERGENCY · ANY HOUR", 56, TYPE, 0.18,
                max_w=1100, left=W * 0.55)

    # quiet footer rail
    hair(p, 0, H - 60, W, TYPE, 4)
    label(p, 190, H - 22, STRAP, 44, TYPE, 0.22, max_w=1300)
    label_right(p, W - 190, H - 22, "ZIMBABWE  ·  ZAMBIA", 44, MUTED, 0.22,
                max_w=900, left=W * 0.6)
    return p


# ---------------------------------------------------------------------------
# 02 — PEDESTRIAN GATE PLATE  2400 x 900 mm
# ---------------------------------------------------------------------------
def gate_plate() -> Page:
    p = Page(width_mm=2400, height_mm=900, bleed_mm=30, background=PAPER)
    W, H = 2400, 900
    spine(p, "left", 20, GOLD)

    lockup(p, 130, 170, 430, ink=TYPE, sub=MUTED, max_w=1180)
    hair(p, 130, 690, 1150, HAIR, 4)
    label(p, 136, 760, "AUTHORISED ENTRY ONLY", 74, GOLD_INK, 0.2, max_w=1150)

    vhair(p, 1500, 140, 620, HAIR, 3)
    rx, rw = 1620, 660
    label(p, rx, 214, "SIGN IN AT THE GATEHOUSE", 58, MUTED, 0.18, max_w=rw)
    draw(p, rx, 400, "ALL VISITORS", "cond-bold", 128, TYPE, 0.01, max_w=rw)
    draw(p, rx, 540, "MUST REPORT", "cond-bold", 128, TYPE, 0.01, max_w=rw)
    hair(p, rx, 604, rw, TYPE, 5)
    label(p, rx, 672, "VEHICLES SUBJECT TO SEARCH", 54, MUTED, 0.16, max_w=rw)
    label(p, rx, 748, "SITE CLOSED 18:00 — 06:00", 50, MUTED, 0.16, max_w=rw)
    return p


# ---------------------------------------------------------------------------
# 03–05 — WARNING BOARDS  600 x 450 mm
# ---------------------------------------------------------------------------
def _pict_camera(p, x, y, colour):
    """A CCTV camera in profile: housing, lens barrel, bracket, mount plate."""
    p.rect(x + 4, y + 14, 42, 26, fill=colour)          # housing
    p.rect(x + 46, y + 19, 14, 16, fill=colour)         # lens barrel
    p.rect(x + 52, y + 23, 6, 8, fill=PAPER)            # lens face
    p.rect(x + 18, y + 6, 7, 8, fill=colour)            # stem
    p.rect(x + 6, y + 1, 30, 5, fill=colour)            # mount plate


def _pict_dog(p, x, y, colour):
    """A handler and a K-9 side by side, both standing."""
    p.rect(x + 4, y - 2, 10, 10, fill=colour)           # handler head
    p.rect(x + 6, y + 10, 6, 36, fill=colour)           # handler body
    p.rect(x + 2, y + 18, 16, 4, fill=colour)           # leading arm
    p.rect(x + 20, y + 24, 28, 14, fill=colour)         # dog barrel
    p.rect(x + 44, y + 12, 13, 12, fill=colour)         # dog head
    p.rect(x + 44, y + 5, 5, 8, fill=colour)            # ear
    p.rect(x + 24, y + 38, 4, 13, fill=colour)          # forelegs
    p.rect(x + 40, y + 38, 4, 13, fill=colour)          # hind legs
    p.rect(x + 18, y + 20, 7, 4, fill=colour)           # tail


def _pict_vehicle(p, x, y, colour):
    """A vehicle in elevation, a barrier arm down across the lane."""
    p.rect(x + 2, y + 20, 62, 18, fill=colour)          # body
    p.rect(x + 34, y + 8, 24, 14, fill=colour)          # cab
    p.rect(x + 8, y + 40, 12, 8, fill=colour)           # wheels
    p.rect(x + 46, y + 40, 12, 8, fill=colour)
    p.rect(x + 68, y + 2, 5, 46, fill=colour)           # barrier post
    p.rect(x + 14, y + 6, 54, 4, fill=colour)           # barrier arm


def _warning(title_lines, note, footer, accent=GOLD_INK, pict=None):
    p = Page(width_mm=600, height_mm=450, bleed_mm=15, background=PAPER)
    W, H = 600, 450

    # regulation rail: red stays on the warning boards and nowhere else
    p.rect(0, 0, W, 12, fill=RED)
    label(p, 40, 52, "VONLET SECURITY  ·  SITE NOTICE", 18, MUTED, 0.22,
          max_w=W - 80)

    # framed pictogram, drawn in ink so it survives a two-colour print
    p.rect(40, 78, 84, 84, fill=None, stroke=HAIR, stroke_w=1.6)
    if pict:
        pict(p, 52, 96, TYPE)

    y = 226
    for line in title_lines:
        size = fit(line, "cond-bold", 50, W - 80, 0.01)
        draw(p, 40, y, line, "cond-bold", size, TYPE, 0.01)
        y += size * 1.06

    # The footer is anchored to the trim, so the note is sized to the room that
    # is actually left between the title and the hairline rather than guessed.
    hair(p, 40, H - 62, W - 80, HAIR, 2.4)
    label(p, 40, H - 28, footer, 18, accent, 0.18, max_w=W - 80)

    top, limit, size = y + 22, H - 84, 17.0
    while size > 12 and top + (len(wrap_lines(note, W - 80, size)) - 1) * size * 1.36 > limit:
        size -= 0.5
    para(p, 40, top, W - 80, note, size, 1.36, TYPE_SOFT)
    return p


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
    """The hero wall: a quiet brand field left, the practical side right."""
    p = Page(width_mm=5200, height_mm=2400, bleed_mm=50, background=PAPER)
    W, H = 5200, 2400
    p.rect(0, 0, W, 18, fill=GOLD)

    # --- left: brand field -------------------------------------------------
    lockup(p, 300, 240, 520, ink=TYPE, sub=MUTED, max_w=2500)
    hair(p, 300, 1000, 2500, TYPE, 6)

    for i, (line, colour) in enumerate([("PROTECTION.", TYPE),
                                        ("WITHOUT", GOLD_INK),
                                        ("COMPROMISE.", TYPE)]):
        size = fit(line, "cond-bold", 210, 2620, 0.01)
        p.text(300, 1320 + i * (size * 1.06), line, "cond-bold", size,
               colour, 0.01)

    hair(p, 300, 2060, 2500, HAIR, 3)
    label(p, 306, 2130, "MANNED GUARDING  ·  CASH IN TRANSIT  ·  ELECTRONIC SECURITY",
          50, MUTED, 0.16, max_w=2500)

    # --- right: the practical side ----------------------------------------
    vhair(p, 3060, 240, 1830, HAIR, 4)

    rx, rw = 3220, 1580
    p.image(rx, 240, rw, 720,
            ROOT / "assets/images/master/full/wa-09-suit-team-entrance.webp",
            focus=(0.5, 0.24))
    label(p, rx, 1030, "OFFICERS BADGED FOR A CORPORATE POSTING", 44, MUTED,
          0.16, max_w=rw)

    draw(p, rx, 1210, "SIGN IN AT", "cond-bold", 140, TYPE, 0.01, max_w=rw)
    draw(p, rx, 1350, "RECEPTION", "cond-bold", 140, GOLD_INK, 0.01, max_w=rw)
    para(p, rx, 1430, rw,
         "All visitors report to reception and are issued a visitor pass. "
         "Officers will direct you to your appointment.", 46, 1.4, TYPE_SOFT)

    rows = [("CONTROL ROOM  ·  24 HOURS", PHONE),
            ("EMAIL", EMAIL),
            ("HEAD OFFICE", f"{ADDRESS_1}, {ADDRESS_2}")]
    y = 1690
    for name, value in rows:
        hair(p, rx, y - 54, rw, HAIR, 2.4)
        label(p, rx, y, name, 40, MUTED, 0.18, max_w=rw)
        draw(p, rx, y + 80, value, "body", 54, TYPE, 0.0, max_w=rw)
        y += 186

    p.rect(0, H - 104, W, 14, fill=GOLD)
    label(p, 300, H - 44, f"{PHONE}   ·   {WEB}", 50, MUTED, 0.18, max_w=2400)
    label_right(p, W - 300, H - 44, "ZIMBABWE  ·  ZAMBIA", 50, MUTED, 0.18,
                max_w=900, left=W * 0.6)
    return p


# ---------------------------------------------------------------------------
# 07 — RECEPTION DESK FRONT  2400 x 1100 mm
# ---------------------------------------------------------------------------
def reception_desk() -> Page:
    p = Page(width_mm=2400, height_mm=1100, bleed_mm=30, background=PAPER)
    W, H = 2400, 1100
    spine(p, "left", 22, GOLD)

    lockup(p, 120, 250, 360, ink=TYPE, sub=MUTED, max_w=1150)
    hair(p, 120, 720, 1120, TYPE, 5)
    draw(p, 120, 900, "RECEPTION", "cond-bold", 120, TYPE, 0.02, max_w=1120)

    vhair(p, 1420, 200, 700, HAIR, 3)
    rx, rw = 1520, 740
    label(p, rx, 274, "PLEASE WAIT TO BE SEEN", 52, MUTED, 0.18, max_w=rw)
    draw(p, rx, 460, "A HOST WILL", "cond-bold", 108, TYPE, 0.01, max_w=rw)
    draw(p, rx, 590, "COLLECT YOU", "cond-bold", 108, GOLD_INK, 0.01, max_w=rw)
    hair(p, rx, 650, rw, HAIR, 3)
    para(p, rx, 726, rw, "Visitor passes must be worn at all times while on site.",
         44, 1.36, TYPE_SOFT)
    return p


# ---------------------------------------------------------------------------
# 08 — AFTER-HOURS RECEPTION BOARD  1200 x 800 mm
# ---------------------------------------------------------------------------
def reception_after_hours() -> Page:
    p = Page(width_mm=1200, height_mm=800, bleed_mm=20, background=PAPER)
    W, H = 1200, 800
    p.rect(0, 0, W, 10, fill=RED)          # after-hours: the one red field
    lockup(p, 70, 70, 116, ink=TYPE, sub=MUTED, max_w=W - 140)
    hair(p, 70, 224, W - 140, HAIR, 2.4)

    label(p, 76, 292, "RECEPTION IS CLOSED", 36, RED, 0.2, max_w=W - 140)
    y = 372
    for line, colour in [("After hours, all", TYPE), ("entry is through", TYPE),
                         ("the security gate.", GOLD_INK)]:
        size = fit(line, "cond-bold", 60, W - 140, 0.01)
        p.text(70, y, line, "cond-bold", size, colour, 0.01)
        y += size * 1.04

    hair(p, 70, 610, W - 140, TYPE, 4)
    label(p, 76, 650, "CALL THE CONTROL ROOM", 26, MUTED, 0.2, max_w=500)
    draw(p, 70, 720, PHONE, "cond-bold", 60, TYPE, 0.01, max_w=W - 140)
    label(p, 76, 764, f"{EMAIL}   ·   {WEB}", 19, MUTED, 0.14, max_w=W - 140)
    return p


# ---------------------------------------------------------------------------
# 09 — VEHICLE LIVERY, DOOR PANEL  2200 x 900 mm
# ---------------------------------------------------------------------------
def vehicle_livery() -> Page:
    p = Page(width_mm=2200, height_mm=900, bleed_mm=25, background=PAPER)
    W, H = 2200, 900
    spine(p, "bottom", 16, GOLD)

    p.image(90, 170, 380, 380, LOGO, focus=(0.5, 0.5))
    draw(p, 540, 400, "VONLET", "cond-bold", 230, TYPE, 0.02, max_w=760)
    label(p, 556, 470, "SECURITY SERVICES", 64, MUTED, 0.2, max_w=740)
    hair(p, 540, 540, 700, GOLD, 8)
    draw(p, 540, 700, PHONE, "cond-bold", 108, TYPE, 0.01, max_w=760)

    vhair(p, 1330, 190, 470, HAIR, 3)
    rx, rw = 1420, W - 1420 - 90
    label(p, rx, 236, "RAPID RESPONSE  ·  24 HOURS", 52, GOLD_INK, 0.18, max_w=rw)
    label(p, rx, 330, WEB, 46, MUTED, 0.14, max_w=rw)
    label(p, rx, 410, EMAIL, 46, MUTED, 0.14, max_w=rw)
    label(p, rx, 490, f"{ADDRESS_1}, {ADDRESS_2}", 42, MUTED, 0.14, max_w=rw)
    return p


# ---------------------------------------------------------------------------
# 10 — NOTICE / INFORMATION BOARD  800 x 1100 mm
# ---------------------------------------------------------------------------
def notice_board() -> Page:
    p = Page(width_mm=800, height_mm=1100, bleed_mm=20, background=PAPER)
    W, H = 800, 1100
    p.rect(0, 0, W, 14, fill=GOLD)

    lockup(p, 62, 70, 96, ink=TYPE, sub=MUTED, max_w=W - 124)
    hair(p, 62, 250, W - 124, TYPE, 4)

    draw(p, 62, 340, "NOTICE TO", "cond-bold", 72, TYPE, 0.01, max_w=W - 124)
    draw(p, 62, 414, "ALL PERSONS", "cond-bold", 72, GOLD_INK, 0.01, max_w=W - 124)
    draw(p, 62, 488, "ON SITE", "cond-bold", 72, TYPE, 0.01, max_w=W - 124)

    rules = [
        "Report to the gatehouse or reception on arrival.",
        "Wear your visitor pass where it can be seen.",
        "No photography or recording without written approval.",
        "Vehicles, bags and personal effects may be searched.",
        "Follow the instructions of security officers at all times.",
    ]
    y = 566
    for i, rule in enumerate(rules, 1):
        p.text(62, y, f"{i:02d}", "cond-bold", 28, GOLD_INK)
        bottom = para(p, 128, y, W - 190, rule, 23, 1.32, TYPE_SOFT)
        if i < len(rules):
            hair(p, 62, bottom + 30, W - 124, HAIR, 2)
        y = bottom + 66

    hair(p, 62, H - 96, W - 124, TYPE, 3)
    label(p, 62, H - 48, f"CONTROL ROOM  {PHONE}", 21, MUTED, 0.18, max_w=W - 124)
    return p


# ---------------------------------------------------------------------------
# 11 — HI-VIS SAFETY VEST BACK PANEL  560 x 640 mm
# ---------------------------------------------------------------------------
def safety_vest() -> Page:
    """The one board that stays high-visibility: ink on the vest's own yellow."""
    p = Page(width_mm=560, height_mm=640, bleed_mm=10, background=HIVIS)
    W, H = 560, 640
    p.rect(0, 0, W, 10, fill=RED)
    p.rect(0, H - 10, W, 10, fill=RED)

    p.image(30, 44, 96, 96, LOGO, focus=(0.5, 0.5))
    draw(p, 144, 116, "VONLET", "cond-bold", 84, HIVIS_TYPE, 0.02, max_w=390)
    label(p, 148, 156, "SECURITY SERVICES", 21, HIVIS_TYPE, 0.2, max_w=380)
    p.rect(30, 190, 500, 4, fill=HIVIS_TYPE)

    label(p, 34, 250, "SECURITY", 38, HIVIS_TYPE, 0.18, max_w=480)
    draw(p, 30, 350, "ON DUTY", "cond-bold", 96, HIVIS_TYPE, 0.01, max_w=500)
    hair(p, 30, 384, 500, HIVIS_TYPE, 4)
    label(p, 34, 440, "24 HOUR CONTROL ROOM", 21, HIVIS_TYPE, 0.18, max_w=480)
    draw(p, 30, 520, PHONE, "cond-bold", 56, HIVIS_TYPE, 0.01, max_w=500)
    label(p, 34, 580, "AUTHORISED PERSONNEL ONLY", 20, HIVIS_TYPE, 0.18,
          max_w=500)
    return p


# ---------------------------------------------------------------------------
# 12 — SITE ID / COMPANY PLAQUE  600 x 400 mm
# ---------------------------------------------------------------------------
def company_plaque() -> Page:
    """A plaque reads as a plate: hairline frame, mark, then the practical lines."""
    p = Page(width_mm=600, height_mm=400, bleed_mm=12, background=PAPER)
    W, H = 600, 400
    p.rect(28, 28, W - 56, H - 56, fill=None, stroke=HAIR, stroke_w=1.4)
    p.rect(28, 28, 66, 5, fill=GOLD)

    p.image(56, 66, 92, 92, LOGO, focus=(0.5, 0.5))
    draw(p, 172, 122, "VONLET", "cond-bold", 68, TYPE, 0.02, max_w=370)
    label(p, 176, 160, "SECURITY SERVICES", 22, MUTED, 0.2, max_w=360)
    hair(p, 56, 196, W - 112, TYPE, 3)

    rows = [(PHONE, WEB), (ADDRESS_1, ADDRESS_2)]
    y = 244
    for left, right in rows:
        draw(p, 56, y, left, "body", 23, TYPE_SOFT, 0.0, max_w=250)
        draw(p, 306, y, right, "body", 23, TYPE_SOFT, 0.0, max_w=W - 330)
        y += 40
    label(p, 56, H - 46, STRAP, 16, MUTED, 0.2, max_w=W - 112)
    return p


# ---------------------------------------------------------------------------
# 13 — EVENT BACKDROP  3000 x 750 mm
# ---------------------------------------------------------------------------
def event_backdrop() -> Page:
    p = Page(width_mm=3000, height_mm=750, bleed_mm=30, background=PAPER)
    W, H = 3000, 750
    p.rect(0, H - 14, W, 14, fill=GOLD)

    lockup(p, 90, 170, 330, ink=TYPE, sub=MUTED, max_w=1400)
    vhair(p, 1400, 150, 400, HAIR, 3)

    tx, tw = 1520, 1390
    draw(p, tx, 300, "PROTECTION.", "cond-bold", 140, TYPE, 0.01, max_w=tw)
    draw(p, tx, 450, "WITHOUT COMPROMISE.", "cond-bold", 140, GOLD_INK, 0.01,
         max_w=tw)
    label(p, tx, 540, "MANNED GUARDING  ·  CASH IN TRANSIT", 44, MUTED, 0.16,
          max_w=tw)
    label(p, tx, 610, "ELECTRONIC SECURITY  ·  K-9  ·  TRAINING", 44, MUTED, 0.16,
          max_w=tw)
    return p


# ---------------------------------------------------------------------------
# 14 — FLOOR WAYFINDING  900 x 300 mm
# ---------------------------------------------------------------------------
def wayfinding() -> Page:
    p = Page(width_mm=900, height_mm=300, bleed_mm=15, background=PAPER)
    W, H = 900, 300
    spine(p, "left", 16, GOLD)

    p.image(56, 96, 96, 96, LOGO, focus=(0.5, 0.5))
    label(p, 52, 56, "VONLET SECURITY", 19, MUTED, 0.2, max_w=210)
    draw(p, 186, 168, "RECEPTION", "cond-bold", 74, TYPE, 0.02, max_w=430)
    label(p, 190, 236, "VISITORS SIGN IN HERE", 34, GOLD_INK, 0.16, max_w=430)

    # arrow, built from bars so it stays crisp at any size
    ay = H / 2
    p.rect(W - 214, ay - 8, 104, 16, fill=TYPE)
    p.rect(W - 122, ay - 30, 14, 60, fill=TYPE)
    p.rect(W - 138, ay - 15, 14, 30, fill=TYPE)
    return p


# ---------------------------------------------------------------------------
# 15 — A-FRAME / PAVEMENT SIGN  700 x 1000 mm
# ---------------------------------------------------------------------------
def a_frame() -> Page:
    p = Page(width_mm=700, height_mm=1000, bleed_mm=15, background=PAPER)
    W, H = 700, 1000
    p.rect(0, 0, W, 14, fill=GOLD)
    p.rect(0, H - 14, W, 14, fill=GOLD)

    p.image(W / 2 - 120, 96, 240, 240, LOGO, focus=(0.5, 0.5))
    draw(p, 0, 470, "VONLET", "cond-bold", 132, TYPE, 0.02,
         align="center", width=W)
    label(p, 0, 512, "SECURITY SERVICES", 34, MUTED, 0.22,
          align="center", width=W)
    p.rect(180, 560, W - 360, 4, fill=GOLD)

    draw(p, 0, 690, "MANNED", "cond-bold", 88, TYPE, 0.01, align="center",
         width=W)
    draw(p, 0, 776, "GUARDING", "cond-bold", 88, TYPE, 0.01, align="center",
         width=W)
    draw(p, 0, 862, "24 HOURS", "cond-bold", 88, GOLD_INK, 0.01, align="center",
         width=W)

    label(p, 0, 902, "CALL THE CONTROL ROOM", 26, MUTED, 0.22,
          align="center", width=W)
    draw(p, 0, 958, PHONE, "cond-bold", 50, TYPE, 0.01, align="center", width=W)
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

    # A partial run must not overwrite the full contact sheet with its own subset.
    if not rendered or args.only:
        return

    # The boards are metres wide at print resolution; shrink each to a proof tile
    # first, or montage exhausts ImageMagick's memory.
    thumbs = []
    for slug, _, _ in SIGNS:
        target = OUT / f"{slug}.png"
        thumb = OUT / f".thumb-{slug}.png"
        subprocess.run(["convert", str(target), "-resize", "420x420>", "-depth", "8",
                        "-bordercolor", "#c9d0d8", "-border", "1", str(thumb)],
                       check=True)
        thumbs.append(str(thumb))
    sheet = OUT / "contact-sheet.png"
    subprocess.run(["montage", *thumbs, "-tile", "4x", "-geometry", "420x420+10+10",
                    "-background", "#e9ecef", "-depth", "8", str(sheet)], check=True)
    for thumb in thumbs:
        Path(thumb).unlink(missing_ok=True)
    print(f"  {'contact-sheet':<28} {'':>16}   {sheet.stat().st_size // 1024:>5} KB")


if __name__ == "__main__":
    main()
