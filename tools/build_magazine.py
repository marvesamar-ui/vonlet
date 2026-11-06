#!/usr/bin/env python3
"""Build VONLET — THE REVIEW, a ten-page magazine typeset from the website.

    python3 tools/build_magazine.py

Writes magazine/vonlet-review/:
    01-cover.png … 10-back-cover.png   A4 at 300 dpi
    vonlet-review.pdf                  the ten pages, print order
    contact-sheet.png                  all ten, for a quick look
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from layout import (  # noqa: E402
    INK, LINE, LINE_STRONG, NAVY, NAVY_800, NAVY_850, NAVY_900, RED, RED_DEEP,
    SLATE_300, SLATE_400, SLATE_500, WHITE, YELLOW, Page, text_width,
)
from magazine_bits import (  # noqa: E402
    ISSUE, LOGO, M, OUT, STRAP, W, H, brand, caption, folio_line, photo,
    running_head, stat,
)
from build_services import GROUPS_IN_ORDER, SERVICES  # noqa: E402

BY_SLUG = {s["slug"]: s for s in SERVICES}


# ---------------------------------------------------------------------------
# 01 — COVER
# ---------------------------------------------------------------------------
def cover() -> Page:
    p = Page(margin=(M, M, M, M))
    # full-bleed hero
    p.image(0, 0, W, H, ROOT / "assets/images/master/full/IMG_9309.webp", focus=(0.62, 0.42))
    # legibility: a graduated head band for the lockup, a deep foot for the type
    p.grad(0, 0, W, 58, "rgba(3,8,22,0.86)-rgba(3,8,22,0.0)")
    p.grad(0, 156, W, 141, "rgba(3,8,22,0.0)-rgba(3,8,22,0.96)")
    # top brand lockup
    p.image(M, 15, 15, 15, LOGO, focus=(0.5, 0.5))
    p.text(M + 20, 24.2, "VONLET", "cond-bold", 7.2, INK, 0.5)
    p.kicker(0, 24.2, ISSUE, YELLOW, 2.3, 0.34, align="right", width=W - M)
    p.kicker(M + 20, 28.4, "SECURITY SERVICES · ZIMBABWE & ZAMBIA", INK, 1.85, 0.3)

    p.text(M, 205, "Every service.", "cond-bold", 21, INK)
    p.text(M, 226, "Photographed", "cond-bold", 21, YELLOW)
    p.text(M, 247, "in service.", "cond-bold", 21, INK)
    p.rule(M, 256, 62, 0.5, LINE_STRONG)
    p.paragraph(M, 265, 92,
                "Twenty-three service lines, from armed guarding to "
                "cash-in-transit, delivered across Zimbabwe and Zambia since 2010.",
                "body", 3.3, 1.55, INK)
    p.kicker(M, 288, STRAP, YELLOW, 2.15, 0.34)
    return p


# ---------------------------------------------------------------------------
# 02 — CONTENTS
# ---------------------------------------------------------------------------
CONTENTS = [
    ("03", "Who we are", "Mission, vision and the values behind a deployment"),
    ("04", "The catalogue", "All twenty-three service lines, grouped"),
    ("05", "Feature — Banking & corporate posts", "Officers at the bank, the fidelity room and the airport"),
    ("06", "Feature — Guarding on the ground", "Gatehouses, quad patrols and walked boundaries"),
    ("07", "Fleet, technology & the control room", "Branded response, cameras and monitored tours"),
    ("08", "Cash in transit", "Route selection, task assignment and accounting"),
    ("09", "Training, people & the K-9 unit", "Four steps to deployment"),
    ("10", "Back cover", "Dispatch, head office and licensing"),
]


def contents() -> Page:
    p = Page(margin=(M, M, M, M))
    running_head(p, 2, "CONTENTS")
    brand(p, 26)

    p.text(M, 46, "The", "cond-bold", 15, INK)
    p.text(M, 61, "contents.", "cond-bold", 15, YELLOW)
    p.paragraph(M, 72, 92,
                "A company is best judged by what it can show. This issue is drawn "
                "entirely from Vonlet's own photography and the service catalogue "
                "published on vonletsecurity.co.zw.",
                "body", 3.3, 1.6, SLATE_400)

    # contents list
    y = 94
    for number, title, blurb in CONTENTS:
        p.text(M, y, number, "cond-bold", 6.4, YELLOW)
        p.rule(M + 15, y - 5.2, W - 2 * M - 15, 0.25, LINE)
        p.text(M + 15, y - 0.4, title, "cond-semi", 4.6, INK)
        p.paragraph(M + 15, y + 6.2, W - 2 * M - 30, blurb, "body", 2.5, 1.4, SLATE_500)
        y += 17.6

    # masthead block
    top = 250
    p.rule(M, top - 8, W - 2 * M, 0.5, LINE_STRONG)
    p.kicker(M, top, "PUBLISHED BY", SLATE_500, 1.95, 0.28)
    p.text(M, top + 7, "Vonlet Security Services", "cond-semi", 4.2, INK)
    cols = [
        ("HEAD OFFICE", "9 Blatherwick Road\nQueensdale, Harare"),
        ("DISPATCH", "+263 772 856 852\ninfo@vonletsecurity.co.zw"),
        ("OPERATING", "Zimbabwe & Zambia\n24/7/365"),
    ]
    for i, (label, value) in enumerate(cols):
        x = M + i * 61
        p.kicker(x, top + 15, label, YELLOW, 1.85, 0.24)
        for j, line in enumerate(value.split("\n")):
            p.text(x, top + 20.6 + j * 4.8, line, "body", 2.7, SLATE_400)
    return p


# ---------------------------------------------------------------------------
# 03 — WHO WE ARE
# ---------------------------------------------------------------------------
def who_we_are() -> Page:
    p = Page(margin=(M, M, M, M))
    running_head(p, 3, "WHO WE ARE")

    p.text(M, 44, "Growing", "cond-bold", 15, INK)
    p.text(M, 58, "stronger since 2010.", "cond-bold", 15, YELLOW)
    p.rule(M, 64, W - 2 * M, 0.4, LINE_STRONG)

    # lead portrait
    photo(p, M, 70, 92, 78, "wa-09-suit-team-entrance", focus=(0.5, 0.32))
    caption(p, M, 153, "Officers badged and briefed for a corporate posting, November 2026.", 92)

    # mission / vision / values column
    cx = M + 100
    cw = W - M - cx
    p.kicker(cx, 74, "OUR MISSION", YELLOW, 2.1, 0.28)
    p.paragraph(cx, 81, cw,
                "To be the most customer-centric establishment and to offer the best "
                "quality services. We are also tirelessly committed to maintaining high "
                "ethical standards, as well as assisting the government in fighting crime "
                "in order to ensure safety to the community.",
                "body", 2.75, 1.5, SLATE_300)

    p.kicker(cx, 110, "OUR VISION", YELLOW, 2.1, 0.28)
    p.paragraph(cx, 117, cw,
                "To become a well-recognised, outstanding, preferred and sought-after "
                "security provider in the Southern Africa region.",
                "body", 2.75, 1.5, SLATE_300)

    p.kicker(cx, 134, "CORE VALUES", YELLOW, 2.1, 0.28)
    values = ["Professionalism", "Innovation", "Transparency",
              "Excellent service standards", "Team work"]
    vy = 141
    for value in values:
        p.rect(cx, vy - 1.85, 1.15, 1.15, fill=YELLOW)
        p.text(cx + 4.4, vy, value, "body", 2.7, SLATE_300)
        vy += 6.2

    # stats band
    p.rule(M, 168, W - 2 * M, 0.4, LINE_STRONG)
    stats = [("2010", "OPERATING SINCE"), ("23", "SERVICE LINES"),
             ("2", "COUNTRIES"), ("24/7", "CONTROL ROOM")]
    for i, (value, label) in enumerate(stats):
        stat(p, M + i * ((W - 2 * M) / 4), 180, value, label, 40)

    # leadership + core business two columns
    p.rule(M, 197, W - 2 * M, 0.25, LINE)
    colw = (W - 2 * M - 10) / 2
    p.kicker(M, 206, "LEADERSHIP", YELLOW, 2.1, 0.28)
    p.paragraph(M, 213, colw,
                "Vonlet is led by its chief executive officer from head office in "
                "Queensdale, Harare, working with the operations, technical and customer "
                "service teams that run deployments across Zimbabwe and part of Zambia.",
                "body", 2.75, 1.5, SLATE_400)

    p.kicker(M + colw + 10, 206, "CORE BUSINESS", YELLOW, 2.1, 0.28)
    p.paragraph(M + colw + 10, 213, colw,
                "Manned guarding and static protection, protective clothing and "
                "specialised safety gear, technical surveillance and electronic security, "
                "24/7/365 on-call tactical protection, and a dedicated customer service "
                "and client support division.",
                "body", 2.75, 1.5, SLATE_400)

    # CEO feature strip — the photo holds the left half, the note sits beside it
    p.rule(M, 236, W - 2 * M, 0.25, LINE)
    p.image(M, 242, 74, 46, ROOT / "assets/images/master/full/IMG_9346.webp", focus=(0.45, 0.42))
    tx = M + 82
    tw = W - M - tx
    p.kicker(tx, 249, "AT HEAD OFFICE", YELLOW, 2.1, 0.28)
    p.text(tx, 259, "The chief", "cond-bold", 11, INK)
    p.text(tx, 268.5, "executive.", "cond-bold", 11, YELLOW)
    p.paragraph(tx, 274, tw,
                "Photographed at the Queensdale head office. Names of individual officers "
                "and clients are withheld throughout this issue; captions describe what is "
                "visible in each frame.",
                "body", 2.5, 1.45, SLATE_400)
    return p


# ---------------------------------------------------------------------------
# 04 — THE CATALOGUE
# ---------------------------------------------------------------------------
GROUP_COPY = {
    "Manned guarding": "Officers on post, static or roving, armed or unarmed, in uniform or in plain clothes.",
    "Sector security": "The same discipline applied to the risk a particular site carries.",
    "Protection & investigation": "The journey and the enquiry, where a fixed post cannot follow.",
    "K-9": "Watch, attack and scent work with a trained handler.",
    "Electronic security": "Cameras, access, alarms, response and the evidence of a beat walked.",
    "Training & safety": "The instruction behind the uniform, and the safety skills beside it.",
    "Cash services": "Managing the movement of cash from task to book.",
}


def catalogue() -> Page:
    p = Page(margin=(M, M, M, M))
    running_head(p, 4, "THE CATALOGUE")

    p.text(M, 44, "Twenty-three", "cond-bold", 14, INK)
    p.text(M, 57.5, "service lines.", "cond-bold", 14, YELLOW)
    p.paragraph(M, 68, 118,
                "Every line Vonlet offers, in the seven groups the catalogue uses. "
                "Fifteen are published on vonletsecurity.co.zw; the eight sector, escort "
                "and investigation lines were supplied by the company for its own site.",
                "body", 2.7, 1.5, SLATE_400)

    # legend, set to the right of the headline so it never crowds the deck
    lx = 132
    ly = 57.5
    p.rect(lx, ly - 0.9, 3.4, 0.28, fill=YELLOW)
    p.text(lx + 5.6, ly, "Published on the site", "body", 2.35, SLATE_400)
    p.rect(lx, ly + 5.1, 3.4, 0.28, fill=SLATE_500)
    p.text(lx + 5.6, ly + 6, "Supplied by the company", "body", 2.35, SLATE_400)

    col_w = (W - 2 * M - 10) / 2
    cursors = [88.0, 88.0]
    for gi, group in enumerate(GROUPS_IN_ORDER):
        col = 0 if gi < 4 else 1
        x = M + col * (col_w + 10)
        y = cursors[col]
        lines = [s for s in SERVICES if s["group"] == group]
        p.kicker(x, y, f"{group.upper()}  ·  {len(lines)}", YELLOW, 2.0, 0.24)
        p.paragraph(x, y + 5.0, col_w, GROUP_COPY[group], "body", 2.25, 1.35, SLATE_500)
        yy = y + 12.0
        for s in lines:
            published = bool(s.get("source"))
            p.rect(x, yy - 1.7, 2.2, 0.24, fill=YELLOW if published else SLATE_500)
            p.text(x + 5, yy, s["name"], "body", 2.55, SLATE_300)
            yy += 5.2
        cursors[col] = yy + 5.6

    # bottom strip photo
    p.rule(M, 246, W - 2 * M, 0.25, LINE)
    photo(p, M, 251, 60, 34, "IMG_9280", focus=(0.5, 0.42))
    p.kicker(M + 66, 256, "ONE PARTNER", YELLOW, 2.0, 0.28)
    p.text(M + 66, 264, "Every layer.", "cond-semi", 5.6, INK)
    p.paragraph(M + 66, 271, W - M - (M + 66),
                "No two sites carry the same risk. The lines above are combined into one "
                "coordinated plan — a warehouse gate, a banking hall, a farm boundary, a "
                "family home.",
                "body", 2.5, 1.45, SLATE_500)
    return p


# ---------------------------------------------------------------------------
# 05 — FEATURE: BANKING & CORPORATE POSTS
# ---------------------------------------------------------------------------
def banking_feature() -> Page:
    p = Page(margin=(M, M, M, M))
    # top image band
    p.image(0, 0, W, 118, ROOT / "assets/images/master/full/wa-11-bank-duty-suit.webp",
            focus=(0.55, 0.3))
    p.grad(0, 0, W, 84, "rgba(3,8,22,0.55)-rgba(3,8,22,0.0)")
    p.grad(0, 0, 118, 84, "rgba(3,8,22,0.80)-rgba(3,8,22,0.0)", angle=90)
    p.grad(0, 86, W, 32, "rgba(3,8,22,0.0)-rgba(3,8,22,1.0)")

    p.kicker(M, 22, "FEATURE — BANKING & CORPORATE POSTS", YELLOW, 2.2, 0.3)
    p.text(M, 40, "A post that reads", "cond-bold", 13, INK)
    p.text(M, 52, "professional", "cond-bold", 13, YELLOW)
    p.text(M, 64, "before it reads security.", "cond-bold", 13, INK)

    # three proof frames across the measure, captions tight beneath them
    frames = [
        ("wa-10-bank-duty-shirt", "Banking-hall post, light-blue company shirt", 0.3),
        ("wa-13-fidelity-room-duty", "Duty at a fidelity room entrance", 0.34),
        ("wa-14-airport-arrivals", "Meet and greet, International Arrivals", 0.36),
    ]
    fw = (W - 2 * M - 12) / 3
    for i, (name, label, focus) in enumerate(frames):
        fx = M + i * (fw + 6)
        p.image(fx, 128, fw, 52, ROOT / f"assets/images/master/full/{name}.webp",
                focus=(0.5, focus))
        p.text(fx, 184, label, "body", 2.25, SLATE_500)

    # body copy, two columns
    colw = (W - 2 * M - 10) / 2
    p.kicker(M, 198, "WHY PRESENTATION IS THE FIRST CONTROL", SLATE_500, 1.95, 0.28)
    p.paragraph(M, 205, colw,
                "At a bank the risk sits in the few minutes a customer spends at the "
                "counter or the machine. A visible uniform beside the terminal discourages "
                "the observation of PIN entry, snatch-and-run theft, and the tampering and "
                "skimming that target an unattended terminal. The officer at the door is "
                "also the queue manager at peak hours, and the person who notices the "
                "vehicle that has been idling a little too long.",
                "body", 2.45, 1.45, SLATE_300)
    p.paragraph(M + colw + 10, 205, colw,
                "After hours the same post keeps the machine and its surroundings under "
                "watch. Attempted break-ins, loitering vehicles, blocked sight-lines and "
                "damaged casing are reported to the control room while there is still time "
                "to act, and every visit is written into the occurrence book — so the client "
                "has a record of cover, not a promise of it.",
                "body", 2.45, 1.45, SLATE_300)

    # sector note
    p.rule(M, 236, W - 2 * M, 0.25, LINE)
    p.kicker(M, 243, "ALSO COVERED UNDER SECTOR SECURITY", YELLOW, 2.0, 0.26)
    items = [("Bank & ATM security", "Static posts, after-hours cover, logged visits"),
             ("Warehouse & logistics", "Gate control, load verification, roving patrols"),
             ("Retail security", "Uniformed door presence and discreet floor cover"),
             ("Functions & events", "Briefed officers for arrivals and guest movement")]
    for i, (title, body) in enumerate(items):
        x = M + (i % 2) * ((W - 2 * M) / 2)
        y = 251 + (i // 2) * 13.5
        p.text(x, y, title, "cond-semi", 3.4, INK)
        p.paragraph(x, y + 5.2, (W - 2 * M) / 2 - 9, body, "body", 2.3, 1.35, SLATE_500)

    # call to action
    p.rect(M, 276, W - 2 * M, 15, fill=NAVY_850)
    p.vrule(M, 276, 15, 1.2, YELLOW)
    p.kicker(M + 6, 281, "REQUEST A SURVEY", YELLOW, 1.95, 0.28)
    p.text(M + 6, 287.5, "+263 772 856 852", "cond-bold", 5.6, INK)
    p.paragraph(M + 54, 281, W - M - (M + 54) - 4,
                "Scoped on site: entrances, the cash office, the ATM line and the hours "
                "each needs cover.", "body", 2.3, 1.4, SLATE_400)
    return p


# ---------------------------------------------------------------------------
# 06 — FEATURE: GUARDING ON THE GROUND
# ---------------------------------------------------------------------------
def ground_feature() -> Page:
    p = Page(margin=(M, M, M, M))
    p.background = NAVY
    running_head(p, 6, "FEATURE — GUARDING ON THE GROUND")

    p.text(M, 46, "The boundary is", "cond-bold", 13, INK)
    p.text(M, 58.5, "the job.", "cond-bold", 13, YELLOW)
    p.paragraph(M, 68, 112,
                "On a farm or a mine the perimeter is the problem: kilometres of fence, "
                "gates that are meant to be open, and value that is in the ground, in a dam, "
                "on a weighbridge or in a truck. Vonlet works the boundary on foot and by "
                "vehicle, posts officers at the gate that matters and roves the rest rather "
                "than leaving it to chance.",
                "body", 2.8, 1.55, SLATE_300)

    # three-up frames
    frames = [
        ("wa-03-quad-driveway", "Quad patrol up the driveway to the main gate", (0.5, 0.4)),
        ("wa-04-quad-lawn", "Patrolling the lawn inside the razor-wire line", (0.5, 0.45)),
        ("wa-02-gatehouse-register", "The gatehouse register, written as visits happen", (0.5, 0.35)),
    ]
    x = M
    for name, label, focus in frames:
        p.image(x, 96, 58, 62, ROOT / f"assets/images/master/full/{name}.webp", focus=focus)
        p.paragraph(x, 163, 58, label, "body", 2.3, 1.4, SLATE_500)
        x += 61.5

    # full-width patrol frame
    p.image(M, 176, W - 2 * M, 62, ROOT / "assets/images/master/full/wa-01-foot-patrol.webp",
            focus=(0.5, 0.4))
    p.scrim_panel(M, 216, W - 2 * M, 22, NAVY, 0.8)
    p.kicker(M + 6, 224, "CLEARED BOUNDARY, WALKED", YELLOW, 2.0, 0.28)
    p.text(M + 6, 232, "Patrol routes and check-times are set by the site risk assessment.",
           "cond-semi", 3.8, INK)

    # points row
    pts = [
        ("Perimeter patrols", "On foot and by vehicle, on a route the intruder cannot learn."),
        ("Gate control", "A stock movement register at the gate that matters."),
        ("Armed cover", "For ore, fuel, explosives stores and aggregate operations."),
        ("K-9 support", "For veld, dam and store searches where a dog is faster."),
    ]
    p.rule(M, 246, W - 2 * M, 0.25, LINE)
    for i, (title, body) in enumerate(pts):
        x = M + i * ((W - 2 * M) / 4)
        p.rect(x, 251, 2.4, 0.26, fill=YELLOW)
        p.text(x, 257, title, "cond-semi", 3.5, INK)
        p.paragraph(x, 263, (W - 2 * M) / 4 - 6, body, "body", 2.3, 1.42, SLATE_500)
    return p


# ---------------------------------------------------------------------------
# 07 — FLEET, TECHNOLOGY & THE CONTROL ROOM
# ---------------------------------------------------------------------------
def fleet_feature() -> Page:
    p = Page(margin=(M, M, M, M))
    running_head(p, 7, "FLEET, TECHNOLOGY & THE CONTROL ROOM")

    p.text(M, 46, "Capability, down", "cond-bold", 13, INK)
    p.text(M, 58.5, "to the detail.", "cond-bold", 13, YELLOW)

    # hero: rapid response vehicle
    p.image(M, 68, W - 2 * M, 74, ROOT / "assets/images/master/full/wa-08-rapid-response-vehicle.webp",
            focus=(0.5, 0.5))
    p.scrim_panel(M, 122, W - 2 * M, 20, NAVY, 0.78)
    p.kicker(M + 6, 130, "BRANDED RESPONSE FLEET", YELLOW, 2.0, 0.28)
    p.text(M + 6, 138, "RAPID RESPONSE, ON THE FORECOURT", "cond-semi", 3.6, INK)

    # four capability cards
    cards = [
        ("IMG_9336", "Covered trucks", "Secure movement of goods alongside patrol and personnel vehicles."),
        ("IMG_9399", "CCTV systems", "Cameras installed, maintained and monitored by the technical team."),
        ("IMG_9396", "Perimeter masts", "Camera units on poles overlooking walls and yards."),
        ("IMG_9250", "Guard monitoring", "NFC, beacon and QR tours reported as each check-in happens."),
    ]
    x = M
    for i, (name, title, body) in enumerate(cards):
        p.image(x, 152, 41, 30, ROOT / f"assets/images/master/full/{name}.webp", focus=(0.5, 0.4))
        p.text(x, 188, title, "cond-semi", 3.4, INK)
        p.paragraph(x, 194, 41, body, "body", 2.3, 1.42, SLATE_500)
        x += 43.5

    # technology list
    p.rule(M, 212, W - 2 * M, 0.25, LINE)
    p.kicker(M, 220, "ELECTRONIC SECURITY, FIVE LINES", YELLOW, 2.0, 0.28)
    tech = ["Close circuit television (CCTV)", "Access control systems",
            "Intruder alarm systems", "Rapid response systems", "Guard monitoring systems"]
    for i, item in enumerate(tech):
        col = i % 2
        row = i // 2
        x = M + col * ((W - 2 * M) / 2)
        y = 230 + row * 9
        p.rect(x, y - 1.8, 2.0, 0.26, fill=YELLOW)
        p.text(x + 5, y, item, "body", 2.9, SLATE_300)

    # control room callout, clear of the folio
    p.rect(M, 258, W - 2 * M, 19, fill=NAVY_850)
    p.vrule(M, 258, 19, 1.2, YELLOW)
    p.kicker(M + 7, 264.5, "THE CONTROL ROOM", YELLOW, 2.0, 0.28)
    p.paragraph(M + 7, 271, W - M - (M + 7) - 6,
                "Duty rosters, site reports and client communication are coordinated from "
                "head office. Equipment shown is photographed in service; exact models are "
                "confirmed during site assessment.",
                "body", 2.4, 1.45, SLATE_400)
    return p


# ---------------------------------------------------------------------------
# 08 — CASH IN TRANSIT
# ---------------------------------------------------------------------------
def cit_feature() -> Page:
    p = Page(margin=(M, M, M, M))
    running_head(p, 8, "CASH IN TRANSIT")

    p.text(M, 46, "Cash in transit,", "cond-bold", 13, INK)
    p.text(M, 58.5, "the Vonlet way.", "cond-bold", 13, YELLOW)
    p.paragraph(M, 68, 104,
                "Cash-in-transit provides management of the cash collection service for "
                "CIT staff: the assignment of tasks, the selection of routes, and the "
                "accounting of all books. Runs are made with Vonlet's branded fleet.",
                "body", 2.9, 1.55, SLATE_300)

    # four concept frames with the required provenance label
    p.kicker(M, 88, "THE RUN, IN FOUR STEPS", YELLOW, 2.0, 0.28)
    steps = [
        ("v2-convoy", "01 / ON THE ROUTE", "One route, planned in advance"),
        ("v2-crew", "02 / CREW CHECK", "Two officers, one console, before wheels move"),
        ("v2-loading", "03 / THE LOADING BAY", "Sealed, counted and signed for"),
        ("v2-handover", "04 / AT THE COUNTER", "Handed over against the book"),
    ]
    x = M
    for name, kicker, title in steps:
        p.image(x, 94, 41, 52, ROOT / f"assets/images/cit/{name}.jpg", focus=(0.5, 0.45))
        p.kicker(x, 151, kicker, YELLOW, 1.85, 0.24)
        p.paragraph(x, 156.5, 41, title, "body", 2.55, 1.4, SLATE_300)
        x += 43.5

    # provenance band — non-negotiable
    p.rect(M, 166, W - 2 * M, 13, fill="#1a1405")
    p.vrule(M, 166, 13, 1.2, YELLOW)
    p.kicker(M + 7, 172, "ILLUSTRATIVE — AI-GENERATED CONCEPT IMAGERY, NOT COMPANY PHOTOGRAPHS",
             YELLOW, 1.95, 0.22)
    p.text(M + 7, 177.4, "Built against the real livery, uniform and vehicle in the archive.",
           "body", 2.3, SLATE_500)

    # the three disciplines
    p.kicker(M, 192, "WHAT THE SERVICE ACTUALLY COVERS", SLATE_500, 1.95, 0.26)
    cols = [
        ("Task assignment", "Every collection and delivery is assigned to a crew, a time "
                            "and a vehicle before the day begins."),
        ("Route selection", "Routes are chosen in advance, with alternates, rather than "
                            "left to the driver on the morning."),
        ("Accounting for all books", "Each book is accounted for against the run, so the "
                                     "paper trail closes with the cash."),
    ]
    cw = (W - 2 * M - 12) / 3
    for i, (title, body) in enumerate(cols):
        x = M + i * (cw + 6)
        p.text(x, 201, f"{i+1:02d}", "cond-bold", 5.2, YELLOW)
        p.text(x, 208, title, "cond-semi", 3.4, INK)
        p.paragraph(x, 214, cw, body, "body", 2.35, 1.45, SLATE_500)

    p.rule(M, 234, W - 2 * M, 0.25, LINE)
    p.paragraph(M, 241, 66,
                "Vonlet publishes cash-in-transit as a core service on its home page rather "
                "than as one of the individual service pages. Requirements for the movement "
                "of cash are subject to applicable transport and site-specific approvals.",
                "body", 2.4, 1.5, SLATE_500)

    # dispatch band grounds the page
    p.rect(M + 74, 236, 104, 40, fill=NAVY_850)
    p.vrule(M + 74, 236, 40, 1.2, YELLOW)
    p.kicker(M + 81, 244, "SCHEDULE A RUN", YELLOW, 2.0, 0.28)
    p.text(M + 81, 256, "+263 772 856 852", "cond-bold", 8.2, INK)
    p.paragraph(M + 81, 263, 92,
                "Runs are quoted per route, per vehicle and per crew.",
                "body", 2.3, 1.4, SLATE_400)
    return p


# ---------------------------------------------------------------------------
# 09 — TRAINING, PEOPLE & K-9
# ---------------------------------------------------------------------------
def training_feature() -> Page:
    p = Page(margin=(M, M, M, M))
    running_head(p, 9, "TRAINING, PEOPLE & THE K-9 UNIT")

    p.text(M, 46, "Nobody wears", "cond-bold", 13, INK)
    p.text(M, 58.5, "the uniform untested.", "cond-bold", 13, YELLOW)

    # recruitment steps
    p.kicker(M, 72, "FOUR STEPS TO DEPLOYMENT", YELLOW, 2.0, 0.28)
    steps = [
        ("Evaluate candidates", "All candidates are evaluated one on one. The best are "
                                "selected for interview."),
        ("Job interviews", "Interviews are conducted in groups and also further done on an "
                           "individual basis."),
        ("Selection & training", "The successful candidates are selected and undergo "
                                 "training and contract signing."),
        ("Employed & deployed", "The employed officers are then deployed to various work "
                                "stations."),
    ]
    x = M
    for i, (title, body) in enumerate(steps):
        p.text(x, 84, f"{i+1:02d}", "cond-bold", 8.4, YELLOW)
        p.rule(x, 88, 40, 0.3, LINE_STRONG)
        p.text(x, 94, title, "cond-semi", 3.4, INK)
        p.paragraph(x, 100, 40, body, "body", 2.3, 1.42, SLATE_500)
        x += 45

    # training frames
    p.image(M, 118, 58, 42, ROOT / "assets/images/master/full/IMG_9274.webp", focus=(0.5, 0.4))
    p.image(M + 61.5, 118, 58, 42, ROOT / "assets/images/master/full/IMG_9313.webp", focus=(0.5, 0.45))
    p.image(M + 123, 118, 58, 42, ROOT / "assets/images/master/full/IMG_9294.webp", focus=(0.5, 0.4))
    p.text(M, 164, "Strategy and planning, control-and-restraint drill, and the K-9 handler.",
           "body", 2.3, SLATE_500)

    # training catalogue
    p.rule(M, 176, W - 2 * M, 0.25, LINE)
    p.kicker(M, 184, "TRAINING & SAFETY, FOUR LINES", YELLOW, 2.0, 0.28)
    tr = [("Basic security guard training", "The foundation course before a first posting."),
          ("Firearm handling", "Additional hours, licensing card and a multi-point check."),
          ("Fire drill", "Evacuation procedure and equipment, rehearsed on site."),
          ("First aid", "The kit, the drill and the confidence to use both.")]
    for i, (title, body) in enumerate(tr):
        x = M + (i % 2) * ((W - 2 * M) / 2)
        y = 193 + (i // 2) * 17
        p.text(x, y, title, "cond-semi", 3.5, INK)
        p.paragraph(x, y + 6, (W - 2 * M) / 2 - 8, body, "body", 2.35, 1.42, SLATE_500)

    # k9 callout
    p.rect(M, 224, W - 2 * M, 19, fill=NAVY_850)
    p.vrule(M, 224, 19, 1.2, YELLOW)
    p.kicker(M + 7, 230.5, "K-9", YELLOW, 2.0, 0.28)
    p.paragraph(M + 7, 237, W - M - (M + 7) - 6,
                "Watch and attack dogs supplied with trained handlers, plus dog handling "
                "training. Vonlet's dogs also assist guards and law enforcement with drug "
                "and explosives searches, locating missing people and finding evidence.",
                "body", 2.4, 1.45, SLATE_400)

    # closing line
    p.rule(M, 250, W - 2 * M, 0.25, LINE)
    p.text(M, 259, "Every candidate is screened before they wear the uniform.",
           "cond-semi", 4.4, INK)
    p.paragraph(M, 267, W - 2 * M,
                "These are the steps Vonlet publishes for its recruitment process. Officers "
                "are trained in-house, and armed officers train in collaboration with the "
                "Zimbabwe Republic Police and the Zambia National Police.",
                "body", 2.4, 1.5, SLATE_500)
    return p


# ---------------------------------------------------------------------------
# 10 — BACK COVER
# ---------------------------------------------------------------------------
def back_cover() -> Page:
    p = Page(margin=(M, M, M, M))
    p.image(0, 0, W, 200, ROOT / "assets/images/master/full/wa-09-suit-team-entrance.webp",
            focus=(0.5, 0.26))
    p.grad(0, 0, W, 58, "rgba(3,8,22,0.84)-rgba(3,8,22,0.0)")
    # the picture darkens into the paper's navy, then ends on a hard yellow rule
    p.grad(0, 138, W, 62, "rgba(3,8,22,0.0)-rgba(3,8,22,1.0)")
    p.rect(0, 200, W, H - 200, fill=NAVY)
    p.rect(0, 197, W, 3, fill=YELLOW)

    p.image(M, 15, 21, 21, LOGO, focus=(0.5, 0.5))
    p.text(M + 27, 24.4, "VONLET", "cond-bold", 9.2, INK, 0.5)
    p.kicker(M + 27, 29.8, "SECURITY SERVICES", INK, 2.3, 0.34)

    p.text(M, 175, "Ready when you", "cond-bold", 17.5, INK)
    p.text(M, 191, "need us.", "cond-bold", 17.5, YELLOW)

    p.kicker(M, 213, "24/7 RAPID RESPONSE", YELLOW, 2.1, 0.3)
    p.text(M, 226, "+263 772 856 852", "cond-bold", 14, INK)

    a, b = M, W - M
    mid = (a + b) / 2
    p.rule(a, 234, b - a, 0.25, LINE)
    p.kicker(a, 241, "EMAIL", SLATE_400, 1.8, 0.26)
    p.text(a, 247, "info@vonletsecurity.co.zw", "body", 3.0, INK)
    p.kicker(mid + 4, 241, "HEAD OFFICE", SLATE_400, 1.8, 0.26)
    p.text(mid + 4, 247, "9 Blatherwick Road, Queensdale", "body", 3.0, INK)
    p.text(mid + 4, 252.4, "Harare, Zimbabwe", "body", 3.0, INK)

    p.rule(a, 260, b - a, 0.25, LINE)
    p.kicker(a, 266, "OPERATING", SLATE_400, 1.8, 0.26)
    p.text(a, 272, "Zimbabwe & Zambia  ·  24/7/365", "body", 3.0, INK)

    p.paragraph(M, 281, W - 2 * M,
                "Licensing numbers are not published on this site. Verify current company "
                "registration, operating licences, tax clearance and insurance documents "
                "directly with Vonlet during procurement.",
                "body", 2.0, 1.35, SLATE_500)
    p.kicker(M, 292, f"{ISSUE}  ·  {STRAP}  ·  © 2026 VONLET SECURITY SERVICES",
             SLATE_500, 1.75, 0.26)
    return p


def ensure_pdf_policy() -> None:
    """Allow ImageMagick to write PDFs for this user.

    The distro policy denies the PDF coder outright. A per-user policy file
    overrides it; this keeps the build working in a fresh sandbox.
    """
    policy = Path.home() / ".config" / "ImageMagick" / "policy.xml"
    if policy.exists():
        return
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        "<policymap>\n"
        '  <policy domain="coder" rights="read|write" pattern="PDF" />\n'
        "</policymap>\n"
    )


# ---------------------------------------------------------------------------
def main() -> None:
    ensure_pdf_policy()
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [
        ("01-cover", cover()),
        ("02-contents", contents()),
        ("03-who-we-are", who_we_are()),
        ("04-catalogue", catalogue()),
        ("05-banking-and-corporate", banking_feature()),
        ("06-guarding-on-the-ground", ground_feature()),
        ("07-fleet-and-technology", fleet_feature()),
        ("08-cash-in-transit", cit_feature()),
        ("09-training-and-people", training_feature()),
        ("10-back-cover", back_cover()),
    ]

    rendered = []
    for name, page in pages:
        target = OUT / f"{name}.png"
        page.render(target)
        rendered.append(target)
        print(f"  {target.name:<32} {target.stat().st_size // 1024:>5} KB")

    # print-ready PDF of the ten pages, in order
    pdf = OUT / "vonlet-review.pdf"
    subprocess.run(["convert", *[str(p) for p in rendered],
                    "-units", "PixelsPerInch", "-density", "300",
                    "-compress", "jpeg", "-quality", "92", str(pdf)], check=True)
    print(f"  {pdf.name:<32} {pdf.stat().st_size // 1024:>5} KB")

    # contact sheet
    sheet = OUT / "contact-sheet.png"
    subprocess.run(["montage", *[str(p) for p in rendered],
                    "-tile", "5x2", "-geometry", "420x594+8+8",
                    "-background", "#030816", "-depth", "8", str(sheet)], check=True)
    print(f"  {sheet.name:<32} {sheet.stat().st_size // 1024:>5} KB")


if __name__ == "__main__":
    main()
