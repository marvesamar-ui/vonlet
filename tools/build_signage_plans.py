#!/usr/bin/env python3
"""Signage plans: technical elevations of the key boards in millimetres.

These are the drawings a fabricator or shopfitter works from — the board at its
true proportion, dimensioned, with the material, fixing and installation height
called out. Rendered in the same type and colour as the boards themselves, so
they read as one set with the artwork.

Output: signage/plans/
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import layout  # noqa: E402
from layout import (  # noqa: E402
    INK, LINE_STRONG, NAVY, NAVY_850, RED, SLATE_300, SLATE_400, SLATE_500,
    YELLOW, Page, text_width,
)

OUT = ROOT / "signage" / "plans"
LOGO = ROOT / "assets" / "brand" / "logo-mark-transparent.png"

PAPER = "#0b1220"          # drawing sheet
GRID = "#141d2e"
DIM = "#7f8ea3"            # dimension lines
NOTE = SLATE_400


def fit(value, role, size, max_w, tracking=0.0, floor=3.0):
    while size > floor and text_width(value, role, size, tracking) > max_w:
        size *= 0.97
    return size


def txt(p, x, y, value, role, size, color, tracking=0.0, max_w=None):
    if max_w:
        size = fit(value, role, size, max_w, tracking)
    return p.text(x, y, value, role, size, color, tracking)


def kick(p, x, y, value, color, size, tracking=0.0, max_w=None):
    value = value.upper()
    if max_w:
        size = fit(value, "semi", size, max_w, tracking)
    p.kicker(x, y, value, color, size, tracking)


# ---------------------------------------------------------------------------
def sheet(width, height, title, subtitle, sheet_no, scale_note):
    """A drawing sheet: title block, border, grid."""
    p = Page(width_mm=width, height_mm=height, bleed_mm=0, background=PAPER)
    W, H = width, height

    # drawing frame
    m = 14
    p.rect(m, m, W - 2 * m, H - 2 * m, stroke=LINE_STRONG, stroke_w=0.35)

    # faint grid for scale readability
    step = 20
    x = m + step
    while x < W - m:
        p.vrule(x, m, H - 2 * m, 0.08, GRID)
        x += step
    y = m + step
    while y < H - m:
        p.rule(m, y, W - 2 * m, 0.08, GRID)
        y += step

    # title block along the foot
    tb_h = 26
    p.rect(m, H - m - tb_h, W - 2 * m, tb_h, fill=NAVY_850)
    p.vrule(m, H - m - tb_h, tb_h, 1.4, YELLOW)
    p.image(m + 6, H - m - tb_h + 5, 16, 16, LOGO, focus=(0.5, 0.5))
    txt(p, m + 27, H - m - tb_h + 12.5, "VONLET", "cond-bold", 7.4, INK, 0.02)
    kick(p, m + 27.4, H - m - tb_h + 18.5, "SIGNAGE", SLATE_500, 2.4, 0.3)

    txt(p, m + 62, H - m - tb_h + 12, title, "cond-semi", 6.2, INK, 0.0,
        max_w=W - m - 62 - 62)
    kick(p, m + 62, H - m - tb_h + 18.4, subtitle, SLATE_500, 2.4, 0.26,
         max_w=W - m - 62 - 62)
    kick(p, W - m - 6, H - m - tb_h + 12, sheet_no, YELLOW, 3.0, 0.3,
         max_w=42)
    kick(p, W - m - 6, H - m - tb_h + 18.4, scale_note, SLATE_500, 2.3, 0.24,
         max_w=52)
    return p


def dim_h(p, x1, x2, y, label, above=True):
    """Horizontal dimension line with ticks and a centred label."""
    p.rule(x1, y, x2 - x1, 0.2, DIM)
    p.vrule(x1, y - 1.6, 3.2, 0.2, DIM)
    p.vrule(x2, y - 1.6, 3.2, 0.2, DIM)
    label = label.upper()
    size = 2.5
    w = text_width(label, "semi", size, 0.22)
    cx = (x1 + x2) / 2 - w / 2
    p.rect(cx - 1.6, y - (1.0 if above else -0.2), w + 3.2, 3.0, fill=PAPER)
    p.kicker(cx, y + (2.2 if above else 1.0), label, DIM, size, 0.22)


def dim_v(p, y1, y2, x, label):
    p.vrule(x, y1, y2 - y1, 0.2, DIM)
    p.rule(x - 1.6, y1, 3.2, 0.2, DIM)
    p.rule(x - 1.6, y2, 3.2, 0.2, DIM)
    label = label.upper()
    size = 2.5
    w = text_width(label, "semi", size, 0.22)
    cy = (y1 + y2) / 2
    p.rect(x - w / 2 - 1.2, cy - 1.0, w + 2.4, 3.2, fill=PAPER)
    p.kicker(x - w / 2, cy + 2.2, label, DIM, size, 0.22)


def callout(p, x, y, num, text_value, width, anchor_x=None, anchor_y=None):
    """Numbered note with a leader line back to the drawing."""
    if anchor_x is not None:
        p.rule(min(x, anchor_x), anchor_y if anchor_y is not None else y - 1.2,
               abs(x - anchor_x), 0.15, DIM)
    p.rect(x, y - 3.0, 5.2, 5.2, fill=YELLOW)
    p.text(x + 0.9, y + 0.5, str(num), "cond-bold", 3.4, NAVY)
    # `width` is the text column, measured from the note's own left edge —
    # the badge and its gap sit outside it
    p.paragraph(x + 8, y, width - 8, text_value, "body", 2.5, 1.4, NOTE)


# ---------------------------------------------------------------------------
# plan 01 — gate pylon
# ---------------------------------------------------------------------------
def plan_pylon():
    p = sheet(420, 297, "GATE PYLON", "ELEVATION  ·  FREE-STANDING MONOLITH",
              "PLAN 01", "1 : 20 AT A3")
    # board face, centred, at roughly 1:20 for a 3600 x 2200 panel
    bw, bh = 236, 144
    bx, by = 26, 44

    p.rect(bx, by, bw, bh, fill=NAVY)
    # simplified artwork: bands
    p.rect(bx, by, bw, 4.2, fill=YELLOW)
    p.image(bx + 8, by + 14, 30, 30, LOGO, focus=(0.5, 0.5))
    txt(p, bx + 42, by + 26, "VONLET", "cond-bold", 17, INK, 0.02, max_w=120)
    kick(p, bx + 42.6, by + 33, "SECURITY SERVICES", SLATE_300, 4.6, 0.4, max_w=110)
    p.rect(bx + 8, by + 44, 90, 0.6, YELLOW)
    txt(p, bx + 8, by + 66, "SITE SECURED", "cond-bold", 13, INK, 0.01, max_w=180)
    txt(p, bx + 8, by + 82, "BY VONLET", "cond-bold", 13, YELLOW, 0.01, max_w=180)
    kick(p, bx + 8, by + 95, "MANNED GUARDING · ELECTRONIC SECURITY · K-9",
         SLATE_400, 3.0, 0.28, max_w=250)
    kick(p, bx + 8, by + 102, "9 BLATHERWICK ROAD, QUEENSDALE, HARARE · VONLETSECURITY.CO.ZW",
         SLATE_500, 2.7, 0.22, max_w=250)
    # the yellow number band
    p.rect(bx, by + bh - 19.8, bw, 13, fill=YELLOW)
    kick(p, bx + 8, by + bh - 14, "24-HOUR CONTROL ROOM", NAVY, 3.4, 0.3, max_w=80)
    txt(p, bx + 8, by + bh - 8.4, "+263 772 856 852", "cond-bold", 6.6, NAVY, 0.01,
        max_w=110)
    p.rect(bx, by + bh - 6.8, bw, 6.8, fill=RED)
    kick(p, bx + 8, by + bh - 3.2, "PROTECTION. WITHOUT COMPROMISE.", INK, 3.0, 0.28,
         max_w=170)

    # dimensions
    dim_h(p, bx, bx + bw, by + bh + 14, "3600 MM (FINISHED)")
    dim_v(p, by, by + bh, bx - 10, "2200 MM")
    dim_v(p, by + bh, by + bh + 12, bx + bw + 10, "120 MM PLINTH")

    # callouts to the right
    cx = bx + bw + 14
    callout(p, cx, 52, 1, "3.6 x 2.2 m face. 9 mm ACM panel, matte laminated, "
                          "UV-stable ink. Navy #030816 with #facc15 and #e61919 bands.", 116)
    callout(p, cx, 78, 2, "Panel on a welded 40 x 40 mm steel frame, 4 mm leaves, "
                          "galvanised and painted. Frame bolted to a 1:2:4 concrete plinth.", 116)
    callout(p, cx, 108, 3, "Plinth 120 mm above finished ground, 3800 x 700 mm, cast in "
                           "situ with M16 cast-in anchors.", 116)
    callout(p, cx, 134, 4, "Base edge to finished ground: 120 mm. Set the foot of the "
                           "panel 1800 mm back from the carriageway edge.", 116)
    callout(p, cx, 162, 5, "Two 12 V LED floods on the underside of the top rail, "
                           "aimed down the face, for after-dark legibility.", 116)
    callout(p, cx, 188, 6, "Coating to hold specification for 8 years minimum in "
                           "Zimbabwe UV. Touch-up kit supplied with the installation.", 116)

    # scale bar
    sx, sy = bx, 250
    kick(p, sx, sy - 5, "SCALE BAR", SLATE_500, 2.3, 0.26)
    for i in range(4):
        p.rect(sx + i * 22, sy, 22, 3.4, fill=INK if i % 2 == 0 else SLATE_500)
    kick(p, sx, sy + 7.6, "0", SLATE_500, 2.2, 0.2)
    kick(p, sx + 22 * 4 - 8, sy + 7.6, "2 M", SLATE_500, 2.2, 0.2)
    return p


# ---------------------------------------------------------------------------
# plan 02 — reception wall
# ---------------------------------------------------------------------------
def plan_reception():
    p = sheet(420, 297, "RECEPTION WALL", "ELEVATION  ·  BEHIND THE DESK",
              "PLAN 02", "1 : 25 AT A3")
    bw, bh = 272, 138
    bx, by = 26, 46

    p.rect(bx, by, bw, bh, fill=NAVY)
    p.rect(bx, by, bw, 1.8, fill=YELLOW)

    # brand field
    p.image(bx + 12, by + 14, 34, 34, LOGO, focus=(0.5, 0.5))
    txt(p, bx + 12, by + 62, "VONLET", "cond-bold", 18, INK, 0.02, max_w=150)
    kick(p, bx + 12.6, by + 69, "SECURITY SERVICES", SLATE_300, 5.0, 0.4, max_w=140)
    p.rect(bx + 12, by + 74, 140, 0.6, YELLOW)
    txt(p, bx + 12, by + 91, "PROTECTION.", "cond-bold", 11.0, INK, 0.01, max_w=160)
    txt(p, bx + 12, by + 103, "WITHOUT", "cond-bold", 11.0, YELLOW, 0.01, max_w=160)
    txt(p, bx + 12, by + 115, "COMPROMISE.", "cond-bold", 11.0, INK, 0.01, max_w=160)

    # photo + right column
    px = bx + 150
    p.image(px, by + 14, 56, 32, ROOT / "assets/images/master/full/wa-09-suit-team-entrance.webp",
            focus=(0.5, 0.28))
    p.vrule(px - 8, by + 14, 118, 0.5, LINE_STRONG)
    kick(p, px, by + 56, "WELCOME TO VONLET", YELLOW, 3.2, 0.3, max_w=112)
    txt(p, px, by + 67, "Sign in at", "cond-bold", 8.2, INK, 0.01, max_w=112)
    txt(p, px, by + 77, "reception.", "cond-bold", 8.2, YELLOW, 0.01, max_w=112)
    p.paragraph(px, by + 84, 112,
                "All visitors report to reception and are issued a visitor pass.",
                "body", 2.8, 1.4, SLATE_300)
    kick(p, px, by + 103, "CONTROL ROOM · 24 HOURS", SLATE_500, 2.4, 0.24, max_w=112)
    txt(p, px, by + 110, "+263 772 856 852", "body", 3.8, INK, 0, max_w=112)

    p.rect(bx, by + bh - 9, bw, 9, fill=RED)
    kick(p, bx + 12, by + bh - 4, "+263 772 856 852   ·   VONLETSECURITY.CO.ZW",
         INK, 3.0, 0.26, max_w=240)

    dim_h(p, bx, bx + bw, by + bh + 14, "5200 MM (FINISHED)")
    dim_v(p, by, by + bh, bx - 10, "2400 MM")

    cx = bx + bw + 14
    callout(p, cx, 56, 1, "5.2 x 2.4 m. Matte vinyl applied to 5 mm foamex, fixed "
                          "with a concealed French cleat.", 96)
    callout(p, cx, 100, 2, "Centre the board on the desk: 1500 mm to its centre, "
                           "1100 mm clear above the desk top.", 96)
    callout(p, cx, 144, 3, "Matte laminate throughout — a lit lobby must not throw "
                           "reflections into a visitor's eyes.", 96)
    callout(p, cx, 188, 4, "Photo area at 300 dpi minimum. Supply a sharpen-corrected "
                           "file with the vinyl.", 96)

    sx, sy = bx, 250
    kick(p, sx, sy - 5, "SCALE BAR", SLATE_500, 2.3, 0.26)
    for i in range(4):
        p.rect(sx + i * 22, sy, 22, 3.4, fill=INK if i % 2 == 0 else SLATE_500)
    kick(p, sx, sy + 7.6, "0", SLATE_500, 2.2, 0.2)
    kick(p, sx + 22 * 4 - 8, sy + 7.6, "2 M", SLATE_500, 2.2, 0.2)
    return p


# ---------------------------------------------------------------------------
# plan 03 — warning boards, with the mounting key
# ---------------------------------------------------------------------------
def plan_warning():
    p = sheet(420, 297, "WARNING BOARDS", "ELEVATION  ·  MOUNTING  ·  THREE-BOARD SET",
              "PLAN 03", "1 : 5 AT A3")
    w, h = 168, 126
    xs = [26, 26 + w + 20, 26 + 2 * (w + 20)]
    by = 46
    labels = [("CCTV IN OPERATION", "CAMERAS · MONITORED 24/7", YELLOW),
              ("GUARD DOGS ON PATROL", "DO NOT APPROACH THE ANIMALS", RED),
              ("VEHICLES SUBJECT TO SEARCH", "BY ORDER OF SITE MANAGEMENT", YELLOW)]
    for x, (title, foot, accent) in zip(xs, labels):
        p.rect(x, by, w, h, fill=NAVY)
        p.rect(x, by, w, 9, fill=RED)
        kick(p, x + 5, by + 6.4, "VONLET SECURITY", INK, 4.2, 0.4, max_w=w - 10)
        p.rect(x + 5, by + 14, 24, 24, fill=accent)
        p.text(x + 5, by + 62, "TITLE", "semi", 2.2, SLATE_500, 0.3)
        lines = title.split(" ", 1)
        txt(p, x + 5, by + 78, lines[0], "cond-bold", 9.4, INK, 0.01, max_w=w - 10)
        txt(p, x + 5, by + 90, lines[1] if len(lines) > 1 else "", "cond-bold", 9.4,
            INK, 0.01, max_w=w - 10)
        p.paragraph(x + 5, by + 98, w - 10,
                    "Body copy is set in Barlow at 21 mm cap height for a 4 m read.",
                    "body", 3.0, 1.35, SLATE_400)
        p.rule(x + 5, by + h - 12, w - 10, 0.3, LINE_STRONG)
        kick(p, x + 5, by + h - 5, foot, accent, 2.8, 0.26, max_w=w - 10)

        dim_h(p, x, x + w, by + h + 10, "600 MM")
        dim_v(p, by, by + h, x - 6, "450 MM")

    # mounting key as a section
    sy = 214
    kick(p, 26, sy, "MOUNTING KEY  ·  SECTION AT A-A", YELLOW, 3.2, 0.3)
    p.rule(26, sy + 4, 368, 0.3, LINE_STRONG)
    # wall
    p.rect(26, sy + 14, 10, 46, fill="#25324a")
    kick(p, 26, sy + 66, "WALL", SLATE_500, 2.2, 0.24)
    # board
    p.rect(42, sy + 18, 7, 38, fill=NAVY)
    p.vrule(42, sy + 18, 38, 0.6, YELLOW)
    kick(p, 42, sy + 66, "3 MM ACM", SLATE_500, 2.2, 0.24)
    # standoffs
    for yy in (sy + 24, sy + 50):
        p.rect(36, yy, 6, 5, fill=SLATE_400)
    kick(p, 33, sy + 78, "25 MM ALUMINIUM STAND-OFF, FOUR PER BOARD", SLATE_400, 2.4, 0.24)

    notes = [
        "3 mm aluminium composite, matte laminated, edges sealed.",
        "Four 25 mm stand-offs per board; drill to the plug pattern supplied.",
        "Centre line at 1500 mm above finished ground for standing read.",
        "Use a hammer-fix anchor into brick or concrete; never into render alone.",
    ]
    for i, n in enumerate(notes, 1):
        p.text(196, sy + 16 + (i - 1) * 13, f"{i:02d}", "cond-bold", 3.6, YELLOW)
        p.paragraph(206, sy + 16 + (i - 1) * 13, 186, n, "body", 2.7, 1.35, NOTE)
    return p


PLANS = [
    ("01-gate-pylon-plan", plan_pylon, 130),
    ("02-reception-wall-plan", plan_reception, 130),
    ("03-warning-boards-plan", plan_warning, 150),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn, dpi in PLANS:
        layout.set_dpi(dpi)
        page = fn()
        target = OUT / f"{name}.png"
        page.render(target)
        print(f"  {name:<28} {int(page.width_mm)} x {int(page.height_mm)} mm"
              f"   {target.stat().st_size // 1024:>5} KB")


if __name__ == "__main__":
    main()
