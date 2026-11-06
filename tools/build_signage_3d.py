#!/usr/bin/env python3
"""Photorealistic in-situ renders of the signage: the boards on real walls.

The flat artwork in `signage/` is what a fabricator prints. This script answers
the other question a client asks — "what will that look like on the wall?" — by
compositing each board into a real scene with true perspective, wall-matched
lighting and panel thickness.

Output: signage/insitu/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import layout  # noqa: E402
import insitu  # noqa: E402
from layout import (  # noqa: E402
    INK, LINE, LINE_STRONG, NAVY, NAVY_800, NAVY_850, NAVY_900, RED, SLATE_300,
    SLATE_400, SLATE_500, WHITE, YELLOW, Page, text_width,
)

OUT = ROOT / "signage" / "insitu"
SCENES = ROOT / "assets" / "signage-scenes"
BRAND = ROOT / "assets" / "brand"
LOGO = BRAND / "logo-mark-transparent.png"

PHONE = "+263 772 856 852"
EMAIL = "info@vonletsecurity.co.zw"
WEB = "vonletsecurity.co.zw"
ADDRESS_1 = "9 Blatherwick Road"
ADDRESS_2 = "Queensdale, Harare"
STRAP = "PROTECTION. WITHOUT COMPROMISE."


def fit(value, role, size, max_w, tracking=0.0, floor=4.0):
    while size > floor and text_width(value, role, size, tracking) > max_w:
        size *= 0.97
    return size


def draw(p, x, y, value, role, size, color, tracking=0.0, max_w=None):
    if max_w:
        size = fit(value, role, size, max_w, tracking)
    return p.text(x, y, value, role, size, color, tracking)


def kick(p, x, y, value, color, size, tracking=0.0, max_w=None):
    value = value.upper()
    if max_w:
        size = fit(value, "semi", size, max_w, tracking)
    p.kicker(x, y, value, color, size, tracking)


# ---------------------------------------------------------------------------
# PORTRAIT ENTRANCE SIGN — 1600 x 2400 mm, for the gate pillar
# ---------------------------------------------------------------------------
def entrance_portrait():
    p = Page(width_mm=1600, height_mm=2400, bleed_mm=20, background=NAVY)
    W, H = 1600, 2400

    # yellow head band with the lockup
    p.rect(0, 0, W, 400, fill=YELLOW)
    p.image(96, 100, 210, 210, LOGO, focus=(0.5, 0.5))
    draw(p, 340, 250, "VONLET", "cond-bold", 150, NAVY, 0.01, max_w=1120)
    kick(p, 348, 322, "SECURITY SERVICES", NAVY, 40, 4, max_w=1080)

    # the statement
    draw(p, 96, 620, "SITE SECURED", "cond-bold", 150, INK, 0.01, max_w=1400)
    draw(p, 96, 780, "BY VONLET", "cond-bold", 150, YELLOW, 0.01, max_w=1400)
    p.rect(96, 860, 900, 10, fill=RED)

    kick(p, 96, 960, "MANNED GUARDING  ·  24 HOURS", SLATE_400, 44, 4, max_w=1400)
    kick(p, 96, 1040, "ACCESS CONTROL IN OPERATION", SLATE_400, 44, 4, max_w=1400)

    # the team photograph, full bleed to the sign edges
    p.image(0, 1180, W, 900, ROOT / "assets/images/master/full/wa-09-suit-team-entrance.webp",
            focus=(0.5, 0.26))
    kick(p, 96, 2150, "OFFICERS BADGED FOR A CORPORATE POSTING", SLATE_500, 34, 3, max_w=1400)

    # the number
    p.rect(0, H - 240, W, 240, fill=RED)
    kick(p, 96, H - 168, "CONTROL ROOM  ·  24 HOURS", INK, 40, 4, max_w=1400)
    draw(p, 96, H - 74, PHONE, "cond-bold", 108, INK, 0.01, max_w=1400)
    return p


def board_image(page_fn, dpi, scale=0.30):
    """Render a page to a downsized RGBA board ready for compositing."""
    layout.set_dpi(dpi)
    b = page_fn().render_to_image()
    return b.resize((max(2, int(b.width * scale)), max(2, int(b.height * scale))),
                    Image.LANCZOS)


# ---------------------------------------------------------------------------
# the jobs
#
# Each entry: output name, scene, board function, render dpi, the quad the board
# sits in, and the physical treatment. Quads were measured off each scene's
# silhouette (columns sampled for the top edge, rows for the base), then inset
# so the board sits within the wall rather than over its edges.
# ---------------------------------------------------------------------------
JOBS = []


def job(name, scene_file, board_fn, dpi, face, inset=(0.0, 0.0, 0.0, 0.0),
        scale=0.30, material="acm", depth=10.0, depth_angle=190.0,
        top="#cfcdc4", side="#8f8d86", light=0.40, shadow=(6, 5),
        shadow_blur=7, shadow_opacity=0.40, texture=0.05, scuff=0.12,
        tint=None, note=""):
    JOBS.append(dict(name=name, scene=scene_file, board=board_fn, dpi=dpi,
                     face=face, inset=inset, scale=scale, material=material,
                     depth=depth, depth_angle=depth_angle, top=top, side=side,
                     light=light, shadow=shadow, shadow_blur=shadow_blur,
                     shadow_opacity=shadow_opacity, texture=texture,
                     scuff=scuff, tint=tint, note=note))


def build_jobs():
    import build_signage as flat

    # --- 01: the 3.6 x 2.2 m pylon panel on the free-standing monolith -------
    # Camera left of the panel, so its top and bottom edges rise to the right.
    job("01-gate-pylon", "scene-pylon.jpg", flat.gate_pylon, 26,
        [(727, 259), (1132, 214), (1132, 495), (727, 500)],
        inset=(0.035, 0.045, 0.965, 0.955), scale=0.34,
        depth=9, depth_angle=190, light=0.30, shadow=(6, 5), shadow_blur=7,
        shadow_opacity=0.36,
        note="3.6 x 2.2 m pylon panel, 9 mm ACM on a steel frame")

    # --- 02: portrait entrance sign inset into the concrete gate pillar ------
    job("02-gate-pillar-entrance", "scene-gate-pillar.jpg", entrance_portrait, 46,
        [(218, 80), (512, 118), (512, 600), (224, 640)],
        inset=(0.085, 0.075, 0.915, 0.90), scale=0.30,
        depth=12, depth_angle=196, light=0.42, shadow=(7, 4), shadow_blur=7,
        shadow_opacity=0.42, scuff=0.14,
        top="#c2bfb6", side="#8a8880",
        note="1600 x 2400 mm panel, fixed to the pillar face")

    # --- 03: the reception wall, applied to the lobby wall ------------------
    job("03-reception-wall", "scene-lobby-wall.jpg", flat.reception_wall, 26,
        [(214, 148), (1000, 126), (1000, 498), (214, 526)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.34,
        depth=7, depth_angle=180, light=0.20, shadow=(5, 4), shadow_blur=9,
        shadow_opacity=0.30, texture=0.04, scuff=0.05,
        top="#f2ece2", side="#c9c2b6",
        note="5.2 x 2.4 m vinyl on 5 mm foamex, applied to the wall")

    # --- 04: reception desk fascia -----------------------------------------
    job("04-reception-desk", "scene-reception-desk.jpg", flat.reception_desk, 60,
        [(540, 392), (940, 404), (940, 592), (540, 588)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.34,
        depth=6, depth_angle=100, light=0.26, shadow=(3, 4), shadow_blur=6,
        shadow_opacity=0.34, texture=0.04, scuff=0.06,
        top="#d8c9b4", side="#a2907a",
        note="2.4 x 1.1 m fascia panel on the desk front")

    # --- 05: warning board on an exterior wall -----------------------------
    job("05-warning-cctv", "scene-exterior-wall.jpg", flat.warning_cctv, 150,
        [(392, 300), (562, 300), (562, 428), (392, 428)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.42,
        depth=4, depth_angle=175, light=0.34, shadow=(4, 5), shadow_blur=5,
        shadow_opacity=0.42, texture=0.05, scuff=0.10,
        top="#e8e0d2", side="#bdb5a6",
        note="600 x 450 mm, 3 mm ACM")

    # --- 06: notice board, portrait, same wall -----------------------------
    job("06-notice-board", "scene-exterior-wall.jpg", flat.notice_board, 90,
        [(660, 246), (782, 246), (782, 428), (660, 428)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.42,
        depth=4, depth_angle=175, light=0.34, shadow=(4, 5), shadow_blur=5,
        shadow_opacity=0.42, texture=0.05, scuff=0.10,
        top="#e8e0d2", side="#bdb5a6",
        note="800 x 1100 mm, 3 mm ACM")

    # --- 07: company plaque with a real edge -------------------------------
    job("07-company-plaque", "scene-exterior-wall.jpg", flat.company_plaque, 150,
        [(858, 300), (972, 302), (972, 378), (858, 376)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.42,
        depth=7, depth_angle=172, light=0.34, shadow=(5, 6), shadow_blur=6,
        shadow_opacity=0.46, texture=0.04, scuff=0.06,
        top="#efe7d9", side="#a89e8c",
        note="600 x 400 mm brushed plaque, 12 mm stand-off")

    # --- 08: wayfinding, mounted low at a doorway --------------------------
    job("08-wayfinding", "scene-exterior-wall.jpg", flat.wayfinding, 100,
        [(300, 330), (556, 330), (556, 415), (300, 415)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.42,
        depth=4, depth_angle=175, light=0.34, shadow=(4, 5), shadow_blur=5,
        shadow_opacity=0.40, texture=0.05, scuff=0.10,
        top="#e8e0d2", side="#bdb5a6",
        note="900 x 300 mm directional panel")

    # --- 09: A-frame standing on the paving -------------------------------
    job("09-a-frame", "scene-exterior-wall.jpg", flat.a_frame, 90,
        [(248, 596), (386, 596), (386, 726), (248, 726)],
        inset=(0.0, 0.0, 1.0, 1.0), scale=0.42,
        depth=11, depth_angle=8, light=0.30, shadow=(16, 10), shadow_blur=13,
        shadow_opacity=0.62, texture=0.04, scuff=0.14,
        top="#d8d2c6", side="#8d8madd".replace("madd", "87a"),
        note="700 x 1000 mm A-frame, double-sided")


def render_all():
    OUT.mkdir(parents=True, exist_ok=True)
    for j in JOBS:
        board = board_image(j["board"], j["dpi"], j["scale"])
        sc = insitu.scene(SCENES / j["scene"])
        quad = insitu.subquad(j["face"], j["inset"][0], j["inset"][1],
                              j["inset"][2], j["inset"][3])
        out = insitu.place(
            sc, board, quad,
            shadow_offset=j["shadow"], shadow_blur=j["shadow_blur"],
            shadow_opacity=j["shadow_opacity"], light_strength=j["light"],
            depth=j["depth"], depth_angle=j["depth_angle"],
            top_colour=j["top"], side_colour=j["side"],
            texture=j["texture"], scuff_amount=j["scuff"], tint=j["tint"],
        )
        insitu.save(out, OUT / f"{j['name']}.jpg")
        print(f"  {j['name']:<26} {j['note']}")


if __name__ == "__main__":
    build_jobs()
    render_all()
    print(f"  {len(JOBS)} scene renders")
