#!/usr/bin/env python3
"""Ten premium illuminated signage designs, rendered at dusk.

Each design is a real, specifiable sign — a fabrication brief, not a picture.
The artwork is drawn in millimetres in `sig_*` functions; the lighting rig
(bloom, halo, spill, wall-wash) is described alongside it so the render and the
manufacture agree.

Two rules the compositor obeys, because ignoring them is what makes a mock-up
look like a sticker:

  * **The artwork's aspect ratio matches the quad's.** A square artwork warped
    into a tall quad squashes every letter; so each board is built at the size
    of its actual mounting face.
  * **Light is added, never painted.** Halos, rims and spills are screened onto
    the scene, so they brighten what is behind them instead of covering it.

Output: signage/premium/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import layout  # noqa: E402
import insitu  # noqa: E402
import lighting as L  # noqa: E402
from layout import Page, text_width  # noqa: E402

OUT = ROOT / "signage" / "premium"
SCENES = ROOT / "assets" / "signage-scenes"
LOGO = ROOT / "assets" / "brand" / "logo-mark-transparent.png"

PHONE = "+263 772 856 852"
WEB = "vonletsecurity.co.zw"
EMAIL = "info@vonletsecurity.co.zw"
ADDR = "9 Blatherwick Road, Queensdale, Harare"
STRAP = "PROTECTION. WITHOUT COMPROMISE."

INK_DARK = "#05080e"       # near-black sign body
PAPER = "#f7f5f0"          # warm white letters
GOLD = "#facc15"


# ---------------------------------------------------------------------------
# type helpers
# ---------------------------------------------------------------------------
def fit(v, role, size, max_w, tr=0.0, floor=3.0):
    while size > floor and text_width(v, role, size, tr) > max_w:
        size *= 0.97
    return size


def draw(p, x, y, v, role, size, colour, tr=0.0, max_w=None, align="left", width=None):
    if max_w:
        size = fit(v, role, size, max_w, tr)
    return p.text(x, y, v, role, size, colour, tr, align=align, width=width)


def kick(p, x, y, v, colour, size, tr=0.0, max_w=None, align="left", width=None):
    v = v.upper()
    if max_w:
        size = fit(v, "semi", size, max_w, tr)
    p.kicker(x, y, v, colour, size, tr, align=align, width=width)


def kick_right(p, right, y, v, colour, size, tr=0.0, max_w=None, left=0.0):
    v = v.upper()
    if max_w:
        size = fit(v, "semi", size, max_w, tr)
    p.kicker(left, y, v, colour, size, tr, align="right", width=right - left)


def board(page, scale):
    """Render a page and shrink it to compositing size."""
    art = page.render_to_image()
    return art.resize((max(1, int(art.width * scale)), max(1, int(art.height * scale))),
                      Image.LANCZOS)


def keyed(page, scale, key=(255, 0, 255)):
    """Render a page and knock a flat key colour out to transparency.

    Used for films and vinyls, where the substrate is the glass, not the print.
    """
    art = board(page, scale).convert("RGB")
    arr = np.asarray(art, dtype=np.int16)
    dist = np.abs(arr - np.array(key, dtype=np.int16)).sum(axis=2).astype(np.float32)
    alpha = np.clip((dist - 90.0) / 90.0, 0, 1)
    out = np.dstack([arr.astype(np.uint8), (alpha * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------------------
# mounting
# ---------------------------------------------------------------------------
def contact_shadow(night, quad, offset=(5, 9), blur=16, opacity=0.55, spread=0.02):
    """A soft shadow on the wall, so the panel has depth behind it."""
    return insitu.shadow(night, quad, offset=offset, blur=blur,
                         opacity=opacity, spread=spread)


def mount(night, face, thickness=7, dark=INK_DARK, ambient=0.10):
    """Fill a quad with a dark body and give it a visible return edge.

    The body is never flat black: a real panel picks up sky light along its top
    and falls away towards the bottom, which is what stops it reading as a
    hole cut in the photograph.
    """
    out = night
    top = min(p[1] for p in face)
    bottom = max(p[1] for p in face)
    h = max(1.0, bottom - top)

    body = Image.new("RGB", night.size, dark)
    yy = np.linspace(0, 1, night.size[1], dtype=np.float32)
    t = np.clip((yy - top) / h, 0, 1)
    gain = (1.0 + ambient * (1.0 - t) ** 1.6)[:, None, None]
    arr = np.asarray(body, dtype=np.float32) * gain
    body = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    body.putalpha(insitu.quad_mask(face, night.size, feather=0.6))
    out = Image.alpha_composite(out, body)

    if thickness:
        edge = [(x, y) for x, y in face]
        # right return
        r = [edge[1], (edge[1][0] + thickness, edge[1][1] + thickness),
             (edge[2][0] + thickness, edge[2][1] + thickness), edge[2]]
        # bottom return
        b = [(edge[3][0] + thickness, edge[3][1] + thickness),
             (edge[2][0] + thickness, edge[2][1] + thickness), edge[2], edge[3]]
        layer = Image.new("RGBA", night.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.polygon([tuple(p) for p in r], fill=(13, 18, 28, 255))
        d.polygon([tuple(p) for p in b], fill=(9, 13, 21, 255))
        layer = layer.filter(ImageFilter.GaussianBlur(0.4))
        out = Image.alpha_composite(out, layer)
    return out


def face_grade(canvas, face, top=1.10, bottom=0.86):
    """Rake the sign's own face: bright at the top, falling away at the foot."""
    top_y = min(p[1] for p in face)
    bot_y = max(p[1] for p in face)
    h = max(1.0, bot_y - top_y)
    yy = np.arange(canvas.size[1], dtype=np.float32)
    t = np.clip((yy - top_y) / h, 0, 1)
    gain = (top + (bottom - top) * t)[:, None, None]

    arr = np.asarray(canvas.convert("RGB"), dtype=np.float32) * gain
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def lit_face(canvas, art, face, mask_value=255, grade=(1.10, 0.86)):
    """Composite the artwork itself, clipped to the face.

    `grade` is the falloff down the face: (top gain, bottom gain). A backlit
    box is even; a face washed by spots from above is much brighter at the top.
    """
    warped = insitu.warp(art, face, canvas.size)
    if mask_value < 255:
        warped.putalpha(insitu.quad_mask(face, canvas.size, feather=0.5)
                        .point(lambda v: int(v * mask_value / 255)))
    else:
        warped.putalpha(insitu.quad_mask(face, canvas.size, feather=0.5))
    out = Image.alpha_composite(canvas, warped)
    if grade:
        mask = insitu.quad_mask(face, canvas.size, feather=1.2)
        graded = face_grade(out, face, grade[0], grade[1])
        out = Image.composite(graded, out, mask)
    return out


def glow_over(canvas, layer, strength=0.7):
    """Screen a light layer so it brightens rather than covers."""
    return L.screen(canvas, layer, strength)


def clipped(canvas, layer, mask):
    """Screen a light layer only where `mask` allows it.

    A spot cone throws light on the sign and on nothing behind it; this is what
    keeps a wash from also lighting the sky.
    """
    out = layer.copy()
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    return L.screen(canvas, out, 1.0)


def backlit(canvas, art, quad, em, colour=(255, 243, 216), radius=46,
            strength=1.0, spread=2.6, core=None, spill=2.0):
    """Reverse-halo a set of letters off the dark backplate they stand on.

    The light source is behind the letter returns, so it lands on the panel
    face and in the gaps between letters — it does not float in the air behind
    the sign. The panel is composited first, then the halo is clipped to it
    (bleeding a little past the edge), then the letter faces go back on top so
    they stay crisp instead of being washed out by their own glow.
    """
    size = canvas.size
    panel = insitu.quad_mask(quad, size, feather=spill)

    halo = L.halo(em, radius, colour, strength, spread)
    halo.putalpha(ImageChops.multiply(halo.getchannel("A"), panel))
    out = glow_over(canvas, halo, 1.0)

    if core:
        c = L.halo(em, core, (255, 252, 244), 0.85, 1.3)
        c.putalpha(ImageChops.multiply(c.getchannel("A"), panel))
        out = glow_over(out, c, 1.0)

    lit = insitu.warp(art, quad, size)
    lit.putalpha(ImageChops.multiply(em, panel))
    return Image.alpha_composite(out, lit)


def finish(canvas, vignette=0.30, sharpen=True, noise=2.6):
    out = L.vignette(canvas, vignette) if vignette else canvas
    if sharpen:
        rgb = out.convert("RGB")
        sharp = rgb.filter(ImageFilter.UnsharpMask(radius=1.6, percent=52, threshold=3))
        out = sharp.convert("RGBA")
    if noise:
        out = L.grain(out, noise)
    return out


# ===========================================================================
# 01 — CHANNEL LETTER MONOLITH  2400 x 1200 mm
# ===========================================================================
def sig_channel_letters():
    p = Page(width_mm=2400, height_mm=1200, bleed_mm=0, background=INK_DARK)
    W, H = 2400, 1200
    p.rect(0, 0, W, 6, fill=GOLD)

    p.image(130, 120, 230, 230, LOGO, focus=(0.5, 0.5))
    draw(p, 410, 300, "VONLET", "cond-bold", 300, PAPER, 0.01, max_w=1860)
    kick(p, 420, 380, "SECURITY SERVICES", "#c9ced6", 84, 9, max_w=1200)

    p.rect(130, 520, 2140, 3, fill="#252d3c")
    draw(p, 130, 700, "PROTECTION.", "cond-bold", 176, PAPER, 0.01, max_w=2140)
    draw(p, 130, 860, "WITHOUT COMPROMISE.", "cond-bold", 176, GOLD, 0.01, max_w=2140)

    kick(p, 130, 1060, f"CONTROL ROOM  {PHONE}", "#8e98a6", 62, 7, max_w=1400)
    kick_right(p, W - 130, 1060, WEB, "#8e98a6", 62, 7, max_w=800)
    return p


def render_channel_letters():
    layout.set_dpi(46)
    art = board(sig_channel_letters(), 0.34)

    sc = insitu.scene(SCENES / "scene-lobby-wall.jpg")
    base = L.warm_bounce(L.dusk(sc, 0.24, (0.52, 0.60, 0.92), 0.010), 0.025)

    face = [(214, 148), (1000, 126), (1000, 498), (214, 526)]
    quad = insitu.subquad(face, 0.0, 0.05, 1.0, 0.95)

    out = contact_shadow(base, quad, offset=(7, 12), blur=20, opacity=0.66)
    out = mount(out, quad, thickness=7)
    out = lit_face(out, art, quad)

    em = L.emission(art, quad, base.size, threshold=150)
    out = backlit(out, art, quad, em, (255, 243, 218), 40, 1.25, 2.5, core=13)

    out = L.bloom(out, 208, 24, 0.52)
    out = L.spill_down(out, quad, 300, (255, 228, 184), 0.22)
    out = finish(out, 0.36)
    insitu.save(out, OUT / "01-channel-letters.png")
    print("  01  channel letters, halo-lit on a stone monolith")


# ===========================================================================
# 02 — FRAMED EDGE-LIT BLADE  1000 x 480 mm
# ===========================================================================
def sig_acrylic_blade():
    # 1640 x 800 mm: the aperture of the bracket it hangs in
    p = Page(width_mm=1640, height_mm=800, bleed_mm=0, background="#0b0f18")
    W, H = 1640, 800

    p.image(70, 130, 250, 250, LOGO, focus=(0.5, 0.5))
    draw(p, 360, 330, "VONLET", "cond-bold", 210, "#ffffff", 0.02, max_w=740)
    kick(p, 370, 396, "SECURITY SERVICES", "#ffd977", 46, 6, max_w=700)

    p.rect(70, 500, 1500, 3, fill="#2b3444")

    kick(p, 70, 600, "24 HOURS  ·  CONTROL ROOM", "#c6ccd6", 46, 7, max_w=900)
    draw(p, 70, 730, PHONE, "cond-bold", 116, "#ffffff", 0.01, max_w=900)

    kick_right(p, W - 70, 600, "HARARE  ·  ZAMBIA", "#8f99a7", 40, 7, max_w=520, left=1000)
    kick_right(p, W - 70, 730, WEB, "#8f99a7", 44, 6, max_w=520, left=900)
    return p


def render_acrylic_blade():
    layout.set_dpi(72)
    art = board(sig_acrylic_blade(), 0.42)

    sc = insitu.scene(SCENES / "scene-blade-wall.jpg")
    base = L.dusk(sc, 0.155, (0.43, 0.52, 0.94), 0.008)
    base = L.warm_bounce(base, 0.05)

    # the inner opening of the cantilevered bracket, measured off the plate:
    # top rail inner face y=175, bottom rail inner face y=375, left stile x=507
    quad = [(507, 176), (914, 175), (914, 374), (507, 375)]

    out = contact_shadow(base, quad, offset=(3, 6), blur=10, opacity=0.5, spread=0.01)
    out = mount(out, quad, thickness=0)
    out = lit_face(out, art, quad)

    # edge-lit acrylic: the cut edges carry the light
    m = insitu.quad_mask(quad, base.size, feather=0.4)
    rim = L.acrylic_edge_glow(m, (255, 250, 233), 2.2, 2.0)
    out = glow_over(out, rim, 0.95)
    out = glow_over(out, L.halo(rim.getchannel("A"), 24, (255, 238, 202), 1.0, 2.2), 0.5)

    out = L.bloom(out, 202, 22, 0.50)
    # the panel spills onto the bracket arm and the wall it is bolted to
    out = L.pool(out, (1030, 300), 260, (255, 230, 190), 0.14, squash=1.6)
    out = L.pool(out, (700, 430), 380, (255, 226, 182), 0.07, squash=0.5)
    out = finish(out, 0.42)
    insitu.save(out, OUT / "02-acrylic-blade.png")
    print("  02  framed edge-lit acrylic blade")


# ===========================================================================
# 03 — LED HALO RECEPTION / EXTERIOR WALL  3800 x 1700 mm
# ===========================================================================
def sig_halo_wall():
    p = Page(width_mm=3800, height_mm=1700, bleed_mm=0, background="#0b1018")
    W, H = 3800, 1700
    p.image(180, 150, 400, 400, LOGO, focus=(0.5, 0.5))
    draw(p, 660, 400, "VONLET", "cond-bold", 400, PAPER, 0.01, max_w=2400)
    kick(p, 680, 540, "SECURITY SERVICES", "#b9bfca", 108, 12, max_w=1500)
    p.rect(180, 780, 3440, 3, fill="#2b3646")
    draw(p, 180, 1030, "PROTECTION,", "cond-bold", 200, PAPER, 0.01, max_w=3440)
    draw(p, 180, 1235, "WITHOUT COMPROMISE.", "cond-bold", 200, GOLD, 0.01, max_w=3440)
    kick(p, 180, 1480, f"{ADDR}   ·   {PHONE}", "#8d97a5", 70, 7, max_w=2400)
    return p


def render_halo_wall():
    layout.set_dpi(32)
    art = board(sig_halo_wall(), 0.34)

    sc = insitu.scene(SCENES / "scene-night-wall.jpg")
    base = L.dusk(sc, 0.60, (0.58, 0.66, 0.97), 0.010)

    # the big dark render wall, clear of the uplight at its foot
    quad = [(452, 240), (952, 240), (952, 458), (452, 458)]

    out = contact_shadow(base, quad, offset=(5, 9), blur=16, opacity=0.45, spread=0.015)
    out = mount(out, quad, thickness=9)
    out = lit_face(out, art, quad)

    em = L.emission(art, quad, base.size, threshold=160)
    out = backlit(out, art, quad, em, (255, 242, 214), 44, 1.15, 2.8, core=14)

    # a backlit panel also leaks around its own edges onto the wall behind
    panel = insitu.quad_mask(quad, base.size, feather=1.0)
    ring = ImageChops.subtract(panel.filter(ImageFilter.GaussianBlur(7)),
                               panel.filter(ImageFilter.GaussianBlur(2.5)))
    out = glow_over(out, L.halo(ring, 26, (255, 238, 200), 1.0, 2.0), 0.55)

    out = L.bloom(out, 204, 30, 0.50)
    out = L.pool(out, (700, 630), 420, (255, 226, 176), 0.30, squash=0.40)
    out = finish(out, 0.38)
    insitu.save(out, OUT / "03-halo-wall.png")
    print("  03  LED halo wall, backlit mark on rendered stone")


# ===========================================================================
# 04 — LIGHTBOX TOTEM  1200 x 2240 mm  (backlit fabric)
# ===========================================================================
def sig_totem():
    """A gate lightbox is read from a car at 15 m, so it carries type, not copy.

    The face is 1200 mm wide; at that width anything smaller than ~110 mm
    disappears from the roadside. So: three words, one rule, one number.
    """
    p = Page(width_mm=1200, height_mm=2240, bleed_mm=0, background=PAPER)
    W, H = 1200, 2240

    # head
    p.image(80, 92, 210, 210, LOGO, focus=(0.5, 0.5))
    draw(p, 320, 210, "VONLET", "cond-bold", 168, "#0a0f1a", 0.01, max_w=790)
    kick(p, 326, 282, "SECURITY SERVICES", "#3f4757", 46, 7, max_w=780)

    p.rect(80, 400, W - 160, 6, fill="#c9ccd2")

    draw(p, 80, 610, "MANNED", "cond-bold", 268, "#0a0f1a", 0.01, max_w=1040)
    draw(p, 80, 868, "GUARDING", "cond-bold", 268, "#0a0f1a", 0.01, max_w=1040)
    draw(p, 80, 1126, "24 HOURS", "cond-bold", 268, "#b31212", 0.01, max_w=1040)

    p.rect(80, 1236, 420, 16, fill=GOLD)

    kick(p, 80, 1338, "HARARE  ·  ZIMBABWE  ·  ZAMBIA", "#3f4757", 48, 8, max_w=1040)

    # the number is the reason the sign exists: give it the lower third
    kick(p, 80, 1478, "CONTROL ROOM  24/7", "#5d6675", 44, 9, max_w=1040)
    draw(p, 80, 1660, "+263 772", "cond-bold", 172, "#0a0f1a", 0.01, max_w=1040)
    draw(p, 80, 1806, "856 852", "cond-bold", 172, "#0a0f1a", 0.01, max_w=1040)

    p.rect(0, H - 190, W, 190, fill="#0a0f1a")
    p.rect(80, H - 190, 260, 14, fill=GOLD)
    kick(p, 80, H - 96, "VONLET SECURITY  EST. 2010", "#d5dae2", 42, 6, max_w=1040)
    return p


def render_totem():
    layout.set_dpi(58)
    art = board(sig_totem(), 0.34)

    sc = insitu.scene(SCENES / "scene-pylon-dusk.jpg")
    night = L.dusk(sc, 0.72, (0.56, 0.64, 0.96), 0.010)

    face = [(855, 194), (1073, 143), (1073, 553), (853, 549)]
    quad = insitu.subquad(face, 0.03, 0.012, 0.97, 0.988)

    out = contact_shadow(night, quad, offset=(6, 6), blur=13, opacity=0.55, spread=0.01)
    out = mount(out, quad, thickness=10)

    # a lightbox is a uniform emitter: fill it warm, then lay the print over
    panel = Image.new("RGBA", night.size, (255, 246, 228, 255))
    panel.putalpha(insitu.quad_mask(quad, night.size, feather=0.5)
                   .point(lambda v: int(v * 0.97)))
    out = Image.alpha_composite(out, panel)
    out = lit_face(out, art, quad, mask_value=250)

    out = L.bloom(out, 226, 30, 0.55)
    out = L.pool(out, (960, 600), 420, (255, 238, 200), 0.30, squash=0.42)
    out = L.pool(out, (960, 470), 260, (255, 244, 216), 0.18, squash=1.0)
    out = finish(out, 0.30)
    insitu.save(out, OUT / "04-lightbox-totem.png")
    print("  04  backlit fabric lightbox totem")


# ===========================================================================
# 05 — BRUSHED METAL PLATE  3000 x 1000 mm  (two downlights)
# ===========================================================================
def sig_metal_plate():
    p = Page(width_mm=3000, height_mm=1000, bleed_mm=0, background="#c9ccd2")
    W, H = 3000, 1000
    draw(p, 0, 430, "VONLET", "cond-bold", 300, "#1b212a", 0.03, align="center", width=W)
    kick(p, 0, 512, "SECURITY SERVICES", "#4a515c", 78, 12, align="center", width=W)
    p.rect(W / 2 - 240, 592, 480, 5, fill="#b31212")
    kick(p, 0, 712, "ZIMBABWE   ·   ZAMBIA   ·   EST. 2010", "#3c434d", 56, 8,
         align="center", width=W)
    return p


def render_metal_plate():
    layout.set_dpi(44)
    art = board(sig_metal_plate(), 0.34)

    sc = insitu.scene(SCENES / "scene-reception-desk.jpg")
    base = L.warm_bounce(L.dusk(sc, 0.17, (0.54, 0.62, 0.94), 0.008), 0.018)

    # the wall above the reception desk, between the ceiling slot and the desk top
    face = [(300, 118), (980, 114), (980, 330), (300, 334)]
    quad = insitu.subquad(face, 0.008, 0.04, 0.992, 0.96)

    out = contact_shadow(base, quad, offset=(3, 8), blur=12, opacity=0.55, spread=0.008)

    # the plate is brushed stainless; it is not a light source, so it stays dark
    # and only picks up what the ceiling washers give it
    metal = L.brushed_metal(base.size, (56, 61, 70), 0.30)
    metal.putalpha(insitu.quad_mask(quad, base.size, feather=0.6))
    out = Image.alpha_composite(out, metal)

    # the graphics are dark etch-filled type on that metal. The ink mask must
    # be warped into the same quad, not resized to the canvas.
    ink = art.convert("L").point(lambda v: 255 if v < 190 else 0)
    ink = ink.filter(ImageFilter.GaussianBlur(0.6))
    ink_quad = insitu.warp(ink.convert("RGBA"), quad, base.size).convert("L")
    ink_quad = ImageChops.multiply(ink_quad, insitu.quad_mask(quad, base.size, feather=0.6))

    ink_layer = Image.new("RGBA", base.size, (18, 22, 29, 255))
    ink_layer.putalpha(ink_quad)
    out = Image.alpha_composite(out, ink_layer)

    # two ceiling washers rake the plate from above
    out = L.wash(out, (280, 100, 360, 260), 90, (255, 240, 210), 0.19, 0.85)
    out = L.wash(out, (650, 98, 360, 260), 90, (255, 240, 210), 0.17, 0.85)
    out = L.fixture(out, (470, 104), 6, (255, 248, 230), 0.72)
    out = L.fixture(out, (820, 102), 6, (255, 248, 230), 0.72)
    out = L.pool(out, (640, 372), 380, (255, 238, 206), 0.16, squash=0.5)
    out = L.bloom(out, 222, 20, 0.22)
    out = finish(out, 0.30)
    insitu.save(out, OUT / "05-metal-plate.png")
    print("  05  brushed metal plate, wall-washed")


# ===========================================================================
# 06 — NEON-LINE GATE TOTEM  900 x 1740 mm
# ===========================================================================
def sig_neon_totem():
    p = Page(width_mm=900, height_mm=1740, bleed_mm=0, background="#05070d")
    W, H = 900, 1740
    p.rect(34, 34, W - 68, H - 68, stroke=GOLD, stroke_w=4)

    p.image(W / 2 - 130, 130, 260, 260, LOGO, focus=(0.5, 0.5))
    draw(p, 0, 560, "VONLET", "cond-bold", 158, "#fff8e6", 0.05, align="center", width=W)
    p.rect(190, 610, W - 380, 3, fill=GOLD)
    kick(p, 0, 700, "SECURITY SERVICES", "#ffd75e", 44, 10, align="center", width=W)
    draw(p, 0, 860, "SITE", "cond-bold", 132, "#fff8e6", 0.04, align="center", width=W)
    draw(p, 0, 990, "SECURED", "cond-bold", 132, "#fff8e6", 0.04, align="center", width=W)
    draw(p, 0, 1180, PHONE, "cond-bold", 74, "#ffd75e", 0.02, align="center", width=W)

    p.rect(150, 1330, W - 300, 1, fill="#4a4126")
    kick(p, 0, 1420, "MANNED GUARDING  ·  24 HOURS", "#b99b52", 30, 4,
         align="center", width=W)
    kick(p, 0, 1500, "ACCESS CONTROL", "#b99b52", 30, 4, align="center", width=W)
    return p


def render_neon_totem():
    layout.set_dpi(64)
    art = board(sig_neon_totem(), 0.34)

    sc = insitu.scene(SCENES / "scene-gate-pillar.jpg")
    night = L.warm_bounce(L.dusk(sc, 0.26, (0.47, 0.57, 0.94), 0.046), 0.028)

    face = [(218, 80), (512, 118), (512, 600), (224, 640)]
    quad = insitu.subquad(face, 0.14, 0.10, 0.86, 0.90)

    out = contact_shadow(night, quad, offset=(4, 6), blur=11, opacity=0.5, spread=0.02)
    out = mount(out, quad, thickness=7)
    out = lit_face(out, art, quad)

    em = L.emission(art, quad, night.size, threshold=120)
    out = glow_over(out, L.halo(em, 46, (255, 206, 96), 1.0, 2.9), 1.0)
    out = glow_over(out, L.halo(em, 16, (255, 232, 168), 1.0, 1.5), 0.8)

    out = L.bloom(out, 172, 30, 1.0, passes=4)
    out = L.pool(out, (300, 720), 300, (255, 206, 96), 0.34, squash=0.5)
    out = L.pool(out, (330, 120), 250, (255, 214, 128), 0.15, squash=0.7)
    out = finish(out, 0.44)
    insitu.save(out, OUT / "06-neon-gate-totem.png")
    print("  06  neon-line gate totem")


# ===========================================================================
# 07 — DOWNLIT PYLON  3000 x 2080 mm  (two spots on a top arm)
# ===========================================================================
def sig_illuminated_pylon():
    p = Page(width_mm=3000, height_mm=2080, bleed_mm=0, background="#0a0e16")
    W, H = 3000, 2080

    p.image(180, 200, 300, 300, LOGO, focus=(0.5, 0.5))
    draw(p, 540, 420, "VONLET", "cond-bold", 290, "#f2f0ea", 0.01, max_w=2100)
    kick(p, 552, 512, "SECURITY SERVICES", "#aab2be", 88, 10, max_w=1600)
    p.rect(180, 700, 2640, 3, fill="#252d3b")

    draw(p, 180, 940, "SITE SECURED", "cond-bold", 250, "#f2f0ea", 0.01, max_w=2640)
    draw(p, 180, 1180, "BY VONLET", "cond-bold", 250, GOLD, 0.01, max_w=2640)

    kick(p, 180, 1420, "MANNED GUARDING   ·   MOBILE PATROL   ·   24 HOURS",
         "#8d97a5", 56, 6, max_w=2640)

    p.rect(180, 1560, 2640, 2, fill="#222a37")
    kick(p, 180, 1690, "CONTROL ROOM", "#9aa4b2", 50, 6, max_w=1200)
    draw(p, 180, 1840, PHONE, "cond-bold", 150, "#f2f0ea", 0.01, max_w=1600)
    kick_right(p, W - 180, 1840, WEB, "#9aa4b2", 54, 5, max_w=1100, left=1900)
    return p


def render_illuminated_pylon():
    layout.set_dpi(40)
    art = board(sig_illuminated_pylon(), 0.32)

    sc = insitu.scene(SCENES / "scene-pylon.jpg")
    night = L.warm_bounce(L.dusk(sc, 0.16, (0.48, 0.57, 0.92), 0.012), 0.02)

    face = [(727, 259), (1132, 214), (1132, 495), (727, 500)]
    quad = insitu.subquad(face, 0.012, 0.02, 0.988, 0.985)

    out = contact_shadow(night, quad, offset=(5, 7), blur=12, opacity=0.5, spread=0.012)
    out = mount(out, quad, thickness=6)
    # spots on a top arm: a strong rake, bright at the head, falling to the foot
    out = lit_face(out, art, quad, grade=(2.35, 0.88))

    # two spot heads stand on an arm above the face and rake down across it.
    # Light cannot pass through a sign, so the cones are clipped to the panel.
    panel = insitu.quad_mask(quad, night.size, feather=1.6)

    cone_l = L.pool_layer(out.size, (748, 250), 250, (255, 248, 228), 1.15, squash=1.5)
    cone_r = L.pool_layer(out.size, (1112, 240), 250, (255, 248, 228), 0.98, squash=1.5)
    rake = L.wash_layer(out.size, (726, 228, 210, 274), 90, (255, 243, 214), 0.85, 0.45)

    for layer in (cone_l, cone_r, rake):
        out = clipped(out, layer, panel)

    # the heads themselves sit on the top edge, clear of the panel
    out = L.fixture(out, (748, 226), 5, (255, 250, 236), 1.0)
    out = L.fixture(out, (1112, 218), 5, (255, 250, 236), 1.0)

    out = L.bloom(out, 198, 26, 0.55)
    out = L.spill_down(out, quad, 330, (255, 232, 192), 0.30)
    out = finish(out, 0.42)
    insitu.save(out, OUT / "07-illuminated-pylon.png")
    print("  07  downlit pylon with two spot heads")


# ===========================================================================
# 08 — FROSTED WINDOW FILM  2600 x 1670 mm  (after hours, lit from inside)
# ===========================================================================
def sig_window_film():
    """Two frosted manifest bands; the key colour is the clear glass between."""
    W, H = 2600, 1670
    p = Page(width_mm=W, height_mm=H, bleed_mm=0, background="#ff00ff")

    # upper band: the lockup, set dark so it reads as ink on frosted vinyl
    p.rect(0, 0, W, 430, fill="#fbf7ee")
    p.image(120, 96, 210, 210, LOGO, focus=(0.5, 0.5))
    draw(p, 390, 310, "VONLET", "cond-bold", 230, "#0a0f1a", 0.01, max_w=1200)
    kick(p, 398, 372, "SECURITY SERVICES", "#39404d", 62, 8, max_w=1000)
    kick_right(p, W - 120, 300, "HARARE  ·  ZAMBIA", "#39404d", 54, 8, max_w=800,
               left=1500)

    # lower band: the after-hours instruction
    p.rect(0, 1180, W, 490, fill="#fbf7ee")
    draw(p, 120, 1340, "RECEPTION CLOSED", "cond-bold", 130, "#0a0f1a", 0.01, max_w=1100)
    draw(p, 120, 1450, "USE THE GATE", "cond-bold", 130, "#b31212", 0.01, max_w=1100)

    kick(p, 1440, 1330, "CONTROL ROOM  ·  24 HOURS", "#39404d", 48, 6, max_w=1050)
    draw(p, 1440, 1440, PHONE, "cond-bold", 104, "#0a0f1a", 0.01, max_w=1050)
    kick(p, 1440, 1530, WEB, "#39404d", 44, 5, max_w=900)
    return p


def render_window_film():
    layout.set_dpi(40)
    art = keyed(sig_window_film(), 0.34)

    sc = insitu.scene(SCENES / "scene-glassfront.jpg")
    night = L.dusk(sc, 0.74, (0.60, 0.68, 0.99), 0.008)

    quad = [(233, 209), (748, 209), (748, 538), (233, 538)]

    # the film sits on the inside face of the glass, so it is lit from behind
    warped = insitu.warp(art, quad, night.size)
    glass = insitu.quad_mask(quad, night.size, feather=0.6)
    warped.putalpha(ImageChops.multiply(warped.getchannel("A"), glass))
    out = Image.alpha_composite(night, warped)

    # the vinyl itself is translucent: it takes its brightness from the room
    lum = Image.new("L", night.size, 0)
    lum.paste(night.convert("L").filter(ImageFilter.GaussianBlur(9)), (0, 0))
    lit = Image.composite(Image.new("RGB", night.size, (255, 250, 240)),
                          Image.new("RGB", night.size, (0, 0, 0)),
                          warped.getchannel("A"))
    lit = ImageChops.multiply(lit, Image.merge("RGB", (lum, lum, lum)).point(lambda v: 120 + v // 2))
    out = ImageChops.screen(out.convert("RGB"), lit).convert("RGBA")

    out = L.bloom(out, 200, 26, 0.42)
    out = L.spill_down(out, quad, 120, (255, 236, 200), 0.24)
    out = L.pool(out, (490, 590), 340, (255, 238, 204), 0.16, squash=0.45)
    out = finish(out, 0.34)
    insitu.save(out, OUT / "08-window-vinyl.png")
    print("  08  frosted manifest film, lit from inside")


# ===========================================================================
# 09 — FASCIA LETTERS  4500 x 300 mm  (soffit-lit entrance)
# ===========================================================================
def sig_canopy():
    p = Page(width_mm=4500, height_mm=300, bleed_mm=0, background="#0b111b")
    W, H = 4500, 300
    draw(p, 0, 225, "VONLET", "cond-bold", 215, PAPER, 0.06, align="center", width=W)
    return p


def render_canopy():
    layout.set_dpi(46)
    art = board(sig_canopy(), 0.30)

    sc = insitu.scene(SCENES / "scene-canopy.jpg")
    night = L.dusk(sc, 0.66, (0.56, 0.65, 0.98), 0.010)

    face = [(218, 200), (1190, 200), (1190, 264), (218, 264)]
    quad = insitu.subquad(face, 0.005, 0.06, 0.995, 0.94)

    out = contact_shadow(night, quad, offset=(2, 5), blur=9, opacity=0.55, spread=0.0)
    out = mount(out, quad, thickness=3)
    out = lit_face(out, art, quad)

    em = L.emission(art, quad, night.size, threshold=150)
    out = glow_over(out, L.halo(em, 30, (255, 244, 220), 1.0, 2.4), 0.85)
    out = glow_over(out, L.halo(em, 12, (255, 250, 236), 1.0, 1.2), 0.5)

    out = L.bloom(out, 196, 22, 0.50)
    # the soffit above the doors picks up the letter glow and drops it on the step
    out = L.wash(out, (300, 264, 830, 110), 90, (255, 240, 208), 0.13, 0.8)
    out = L.pool(out, (700, 470), 470, (255, 234, 196), 0.21, squash=0.35)
    out = finish(out, 0.34)
    insitu.save(out, OUT / "09-canopy-letters.png")
    print("  09  fascia letters, soffit-lit entrance")


# ===========================================================================
# 10 — ILLUMINATED A-FRAME  700 x 1000 mm
# ===========================================================================
def sig_lit_a_frame():
    p = Page(width_mm=700, height_mm=1000, bleed_mm=0, background="#f6f3ec")
    W, H = 700, 1000
    p.image(W / 2 - 100, 70, 200, 200, LOGO, focus=(0.5, 0.5))
    draw(p, 0, 380, "VONLET", "cond-bold", 104, "#0a0f1a", 0.02, align="center", width=W)
    kick(p, 0, 424, "SECURITY SERVICES", "#414956", 30, 4, align="center", width=W)
    p.rect(150, 470, W - 300, 5, fill="#b31212")
    draw(p, 0, 570, "MANNED", "cond-bold", 84, "#b31212", 0.01, align="center", width=W)
    draw(p, 0, 652, "GUARDING", "cond-bold", 84, "#b31212", 0.01, align="center", width=W)
    draw(p, 0, 734, "24 HOURS", "cond-bold", 84, "#0a0f1a", 0.01, align="center", width=W)
    kick(p, 0, 806, "CONTROL ROOM", "#414956", 28, 3, align="center", width=W)
    draw(p, 0, 900, PHONE, "cond-bold", 56, "#0a0f1a", 0.01, align="center", width=W)
    return p


def _grad_poly(size, quad, top_rgb, bot_rgb):
    """A polygon filled with a vertical gradient, returned as an RGBA layer."""
    w, h = size
    ys = [p[1] for p in quad]
    y0, y1 = min(ys), max(ys)
    t = np.clip((np.arange(h, dtype=np.float32) - y0) / max(1.0, y1 - y0), 0, 1)[:, None, None]
    top = np.array(top_rgb, dtype=np.float32)[None, None, :]
    bot = np.array(bot_rgb, dtype=np.float32)[None, None, :]
    arr = np.repeat(top * (1 - t) + bot * t, w, axis=1)
    grad = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    grad.putalpha(insitu.quad_mask(quad, size, feather=0.5))
    return grad


def render_lit_a_frame():
    layout.set_dpi(86)
    art = board(sig_lit_a_frame(), 0.46)

    sc = insitu.scene(SCENES / "scene-exterior-wall.jpg")
    base = L.dusk(sc, 0.33, (0.50, 0.58, 0.95), 0.038)
    base = L.warm_bounce(base, 0.022)

    # On the block paving in the foreground, close to the camera so it has real
    # presence. A-frame leaves lean back, so the face is a keystone: narrower at
    # the hinge than at the feet. Feet at y=728.
    face = [(588, 452), (776, 448), (788, 724), (576, 728)]
    # the far leaf is turned almost edge-on and is in its own shade: a thin
    # graded sliver, not a second panel
    far = [(776, 448), (789, 457), (795, 728), (788, 724)]
    foot = [(574, 722), (790, 718), (792, 744), (572, 748)]

    out = Image.alpha_composite(base, _grad_poly(base.size, far, (62, 62, 66), (16, 17, 21)))

    # shadow thrown forward-left by the sky, not by the sign
    out = insitu.shadow(out, foot, offset=(16, 10), blur=16, opacity=0.62, spread=0.02)
    out = contact_shadow(out, face, offset=(18, 16), blur=20, opacity=0.52, spread=0.01)
    out = mount(out, face, thickness=0)

    panel = Image.new("RGBA", base.size, (255, 248, 234, 255))
    panel.putalpha(insitu.quad_mask(face, base.size, feather=0.5))
    out = Image.alpha_composite(out, panel)
    out = lit_face(out, art, face, mask_value=250, grade=(1.05, 0.92))

    frame = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.line([tuple(q) for q in face] + [face[0]], fill=(32, 36, 44, 255),
            width=5, joint="curve")
    fd.line([(776, 450), (789, 458)], fill=(104, 104, 108, 255), width=2)
    out = Image.alpha_composite(out, frame.filter(ImageFilter.GaussianBlur(0.35)))

    # the rubber foot rail, painted after the panel so it sits proud of it
    out = Image.alpha_composite(out, _grad_poly(base.size, foot, (30, 32, 38), (20, 22, 27)))

    out = L.pool(out, (682, 754), 190, (255, 240, 214), 0.20, squash=0.40, falloff=2.8)
    out = L.pool(out, (682, 700), 290, (255, 236, 206), 0.08, squash=0.62, falloff=2.2)
    out = L.pool(out, (676, 520), 340, (255, 238, 210), 0.055, squash=1.0, falloff=2.0)

    catch = Image.new("RGBA", base.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(catch)
    cd.line([(778, 470), (786, 726)], fill=(122, 116, 104, 255), width=2)
    out = Image.alpha_composite(out, catch.filter(ImageFilter.GaussianBlur(1.4)))
    out = L.bloom(out, 208, 22, 0.55)
    out = finish(out, 0.42)
    insitu.save(out, OUT / "10-lit-a-frame.png")
    print("  10  illuminated A-frame on the paving")


RENDERS = [
    ("01-channel-letters", sig_channel_letters, render_channel_letters,
     "CHANNEL LETTERS", "Halo-lit fabricated acrylic on a stone monolith", "01"),
    ("02-acrylic-blade", sig_acrylic_blade, render_acrylic_blade,
     "EDGE-LIT BLADE", "Framed acrylic blade, edge-lit", "02"),
    ("03-halo-wall", sig_halo_wall, render_halo_wall,
     "LED HALO WALL", "Backlit mark on rendered stone", "03"),
    ("04-lightbox-totem", sig_totem, render_totem,
     "LIGHTBOX TOTEM", "Backlit fabric totem, free-standing", "04"),
    ("05-metal-plate", sig_metal_plate, render_metal_plate,
     "METAL PLATE", "Brushed stainless, wall-washed", "05"),
    ("06-neon-gate-totem", sig_neon_totem, render_neon_totem,
     "NEON GATE TOTEM", "LED neon-line gate sign", "06"),
    ("07-illuminated-pylon", sig_illuminated_pylon, render_illuminated_pylon,
     "ILLUMINATED PYLON", "Downlit pylon face, 3.0 x 2.1 m", "07"),
    ("08-window-vinyl", sig_window_film, render_window_film,
     "WINDOW FILM", "Frosted manifest bands, lit from inside", "08"),
    ("09-canopy-letters", sig_canopy, render_canopy,
     "FASCIA LETTERS", "Signature entrance letters, soffit-lit", "09"),
    ("10-lit-a-frame", sig_lit_a_frame, render_lit_a_frame,
     "LIT A-FRAME", "Edge-lit pavement sign", "10"),
]


def contact_sheet():
    """The ten designs on one page, captioned like a presentation sheet."""
    from PIL import ImageFont

    W = 2000
    BG = (7, 9, 14)
    cols, rows = 2, 5
    gut, cap_h, top, foot = 34, 86, 236, 60
    cell_w = (W - 180 - gut) // cols
    cell_h = round(cell_w * 768 / 1408)
    H = top + rows * (cell_h + cap_h) + (rows - 1) * gut + foot

    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)

    bold = ImageFont.truetype(str(layout.FONT_FILES["cond-bold"]), 72)
    semi = ImageFont.truetype(str(layout.FONT_FILES["semi"]), 27)
    small = ImageFont.truetype(str(layout.FONT_FILES["semi"]), 22)

    # header
    d.text((90, 56), "VONLET SECURITY", font=bold, fill=(247, 245, 240))
    d.text((90, 142), "PREMIUM ILLUMINATED SIGNAGE", font=semi, fill=(250, 204, 21))
    d.line([(90, 192), (W - 90, 192)], fill=(38, 42, 52), width=2)
    d.text((W - 90, 86), "TEN DESIGNS  ·  DUSK", font=small, fill=(122, 130, 143), anchor="ra")
    d.text((W - 90, 120), "SIGNAGE / PREMIUM", font=small, fill=(122, 130, 143), anchor="ra")

    for i, (slug, _a, _r, title, sub, num) in enumerate(RENDERS):
        cx = 90 + (i % cols) * (cell_w + gut)
        cy = top + (i // cols) * (cell_h + cap_h + gut)
        shot = Image.open(OUT / f"{slug}.png").convert("RGB")
        shot = shot.resize((cell_w, cell_h), Image.LANCZOS)
        sheet.paste(shot, (cx, cy))
        d.text((cx, cy + cell_h + 20), f"{num}   {title}", font=semi, fill=(240, 240, 238))
        d.text((cx, cy + cell_h + 56), sub.upper(), font=small, fill=(122, 130, 143))

    return sheet


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:] or None
    for slug, _art_fn, render_fn, _title, _sub, _num in RENDERS:
        if only and slug not in only:
            continue
        render_fn()

    # A partial run must not overwrite the full contact sheet with its own subset.
    if only:
        return

    contact_sheet().save(OUT / "contact-sheet.png", optimize=True)


if __name__ == "__main__":
    main()
