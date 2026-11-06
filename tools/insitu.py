#!/usr/bin/env python3
"""In-situ signage rendering: put a flat board onto a real wall, in perspective.

There is no 3D package and no GPU in this environment, so the renderer does the
three things that actually make a mock-up read as real:

  * **Perspective.** The board is mapped onto an arbitrary four-point quad with a
    true homography (solved with numpy, sampled with Pillow's bicubic
    transform), so it sits in the scene's vanishing geometry rather than being
    pasted on flat.
  * **Light.** A blurred luminance field is sampled from the patch of wall the
    board will cover, and the board's colour is modulated by it. A sign on a wall
    in shade is darker on its shaded side, which is the single biggest cue that
    lifts a composite out of "sticker on a photo".
  * **Depth.** Boards are not paper. `slab()` extrudes the quad along a direction
    and fills the side faces with a darker tone, giving a real edge thickness —
    a 3 mm ACM panel, a 60 mm illuminated box, a 110 mm projecting blade.

`shadow()` adds the contact shadow, `paper_texture()` adds the faint grain of a
printed substrate, and `scuff()` dirties the bottom edge where a real sign
collects dust.

Everything works in plain numpy/Pillow so it runs anywhere the rest of the
tooling runs.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter


# ---------------------------------------------------------------------------
# homography
# ---------------------------------------------------------------------------
def _homography(src: list[tuple[float, float]], dst: list[tuple[float, float]]) -> np.ndarray:
    """Solve H such that dst -> src, as Pillow's PERSPECTIVE wants."""
    A, b = [], []
    for (sx, sy), (dx, dy) in zip(src, dst):
        A.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        b.append(sx)
        A.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
        b.append(sy)
    h = np.linalg.solve(np.array(A, dtype=float), np.array(b, dtype=float))
    return np.append(h, 1.0).reshape(3, 3)


def warp(image: Image.Image, quad: list[tuple[float, float]],
         canvas_size: tuple[int, int]) -> Image.Image:
    """Map `image` onto `quad` inside a canvas of `canvas_size`.

    `quad` is TL, TR, BR, BL in canvas pixels. Returns RGBA the size of canvas.
    """
    w, h = image.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    # Pillow wants dst -> src coefficients
    coeffs = _homography(src, quad).flatten()[:8]
    warped = image.convert("RGBA").transform(
        canvas_size, Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC
    )
    return warped


def quad_mask(quad, canvas_size, feather=1.2) -> Image.Image:
    """Antialiased mask of the quad."""
    mask = Image.new("L", canvas_size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).polygon([tuple(p) for p in quad], fill=255)
    if feather:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    return mask


def subquad(face, u0, v0, u1, v1):
    """A sub-rectangle of a planar quad, in its own (u, v) space.

    Bilinear on the parent quad, which is exact at the corners and matches the
    perspective of a rectangle lying on that plane closely enough that a board
    inset into a wall keeps the wall's own geometry.
    """
    def at(u, v):
        tl, tr, br, bl = face
        x = ((1 - u) * (1 - v) * tl[0] + u * (1 - v) * tr[0]
             + u * v * br[0] + (1 - u) * v * bl[0])
        y = ((1 - u) * (1 - v) * tl[1] + u * (1 - v) * tr[1]
             + u * v * br[1] + (1 - u) * v * bl[1])
        return (x, y)
    return [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)]


# ---------------------------------------------------------------------------
# lighting
# ---------------------------------------------------------------------------
def luminance(canvas: Image.Image, blur: int = 48) -> np.ndarray:
    """Blurred 0-1 luminance field of a scene, used to light what sits on it."""
    g = np.asarray(canvas.convert("L").filter(ImageFilter.GaussianBlur(blur)),
                   dtype=np.float32) / 255.0
    return g


def light_board(board: Image.Image, scene_lum: np.ndarray, quad,
                canvas_size, strength: float = 0.55,
                tint: tuple[float, float, float] | None = None) -> Image.Image:
    """Modulate a warped board by the light falling on the wall behind it.

    `strength` is how much of the wall's own shading is transferred. A printed
    sign under diffuse daylight keeps most of its own colour, so this stays
    well under 1.0.
    """
    arr = np.asarray(board, dtype=np.float32) / 255.0
    mask = np.asarray(quad_mask(quad, canvas_size, feather=0)) > 127

    # normalise the wall's luminance so the average is unchanged: we want the
    # *variation* across the surface, not an overall darkening
    sampled = scene_lum.copy()
    mean = sampled[mask].mean() if mask.any() else 0.5
    gain = 1.0 + (sampled - mean) * strength
    gain = np.clip(gain, 0.55, 1.45)[..., None]

    arr[..., :3] = np.clip(arr[..., :3] * gain, 0, 1)

    if tint is not None:
        t = np.array(tint, dtype=np.float32)
        arr[..., :3] = arr[..., :3] * t

    out = (arr * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------------------
# depth: turn a flat quad into a slab with real edge thickness
# ---------------------------------------------------------------------------
def _offset_quad(quad, dx, dy):
    return [(x + dx, y + dy) for x, y in quad]


@dataclass
class Slab:
    """A panel with thickness, seen at an angle."""
    face: list[tuple[float, float]]          # TL TR BR BL of the front face
    depth: float = 10.0                      # extrusion in canvas pixels
    angle: float = 0.0                       # direction of extrusion, radians


def slab_faces(quad, depth, angle_deg):
    """Return (visible side polygons, top polygon) for an extruded panel.

    The extrusion runs away from the viewer. Sides that face away are not drawn,
    which is what keeps a thick sign from looking like a box of glass.
    """
    import math
    a = math.radians(angle_deg)
    dx, dy = math.cos(a) * depth, math.sin(a) * depth
    back = _offset_quad(quad, dx, dy)

    polys = {}
    # each edge of the face, paired with the same edge on the back
    for name, i, j in (("top", 0, 1), ("right", 1, 2), ("bottom", 2, 3), ("left", 3, 0)):
        p = [quad[i], quad[j], back[j], back[i]]
        polys[name] = p
    return polys, back


def draw_slab(canvas: Image.Image, quad, depth=10.0, angle_deg=0.0,
              side="#101826", top="#1b2536", shade=0.72):
    """Draw the extruded body of a panel behind where the face will go."""
    from PIL import ImageDraw
    polys, back = slab_faces(quad, depth, angle_deg)
    layer = canvas.copy()
    d = ImageDraw.Draw(layer)

    # decide which faces are visible from the extruded area: if the extrusion
    # goes right/down, the right and bottom faces are hidden behind the face
    import math
    a = math.radians(angle_deg)
    show_right = math.cos(a) > 0.15
    show_left = math.cos(a) < -0.15
    show_top = math.sin(a) > 0.15
    show_bottom = math.sin(a) < -0.15

    order = []
    if show_top:
        order.append(("top", top))
    if show_left:
        order.append(("left", side))
    if show_right:
        order.append(("right", side))
    if show_bottom:
        order.append(("bottom", side))

    for name, colour in order:
        d.polygon([tuple(p) for p in polys[name]], fill=colour)
    return layer


# ---------------------------------------------------------------------------
# shadow
# ---------------------------------------------------------------------------
def shadow(canvas: Image.Image, quad, offset=(6, 8), blur=14, opacity=0.42,
           spread=0) -> Image.Image:
    """A soft contact shadow cast by the panel onto the wall."""
    from PIL import ImageDraw
    w, h = canvas.size
    sh = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(sh)
    moved = _offset_quad(quad, *offset)
    if spread:
        cx = sum(p[0] for p in moved) / 4
        cy = sum(p[1] for p in moved) / 4
        moved = [(cx + (x - cx) * (1 + spread), cy + (y - cy) * (1 + spread))
                 for x, y in moved]
    d.polygon([tuple(p) for p in moved], fill=int(255 * opacity))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))

    out = canvas.convert("RGBA")
    dark = Image.new("RGBA", (w, h), (6, 10, 20, 0))
    dark.putalpha(sh)
    return Image.alpha_composite(out, dark)


# ---------------------------------------------------------------------------
# substrate
# ---------------------------------------------------------------------------
def paper_texture(board: Image.Image, amount=0.045, seed=3) -> Image.Image:
    """Faint grain so a flat print does not look like a vector graphic."""
    arr = np.asarray(board, dtype=np.float32) / 255.0
    rng = np.random.default_rng(seed)
    h, w = arr.shape[:2]
    noise = rng.normal(0, 1, (h, w)).astype(np.float32)
    # smooth it a little, then keep it low-frequency
    noise = np.asarray(Image.fromarray(((noise * 0.5 + 0.5) * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.8)), dtype=np.float32) / 255.0
    noise = (noise - 0.5) * 2
    arr[..., :3] = np.clip(arr[..., :3] + noise[..., None] * amount, 0, 1)
    return Image.fromarray((arr * 255).astype(np.uint8), "RGBA")


def scuff(board: Image.Image, amount=0.10) -> Image.Image:
    """Dust and wear along the bottom edge of a panel."""
    arr = np.asarray(board, dtype=np.float32) / 255.0
    h = arr.shape[0]
    band = max(4, int(h * 0.06))
    ramp = np.linspace(0, 1, band, dtype=np.float32)[:, None, None]
    arr[h - band:, :, :3] = arr[h - band:, :, :3] * (1 - amount * ramp) + \
        0.52 * amount * ramp
    return Image.fromarray((arr * 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------------------
# composite
# ---------------------------------------------------------------------------
def place(canvas: Image.Image, board: Image.Image, quad,
          shadow_offset=(7, 9), shadow_blur=14, shadow_opacity=0.4,
          light_strength=0.55, depth=None, depth_angle=0.0,
          top_colour="#1b2536", side_colour="#0d1420",
          texture=0.045, scuff_amount=0.10, tint=None) -> Image.Image:
    """Composite one board onto a scene.

    Order matters: shadow first (it falls on the wall), then the slab body, then
    the lit, textured face. Done any other way the shadow paints over the panel.
    """
    base = canvas.convert("RGBA")
    size = base.size

    base = shadow(base, quad, offset=shadow_offset, blur=shadow_blur,
                  opacity=shadow_opacity, spread=0.045 if depth else 0.02)

    if depth:
        base = draw_slab(base, quad, depth=depth, angle_deg=depth_angle,
                         side=side_colour, top=top_colour)

    face = paper_texture(board, amount=texture)
    if scuff_amount:
        face = scuff(face, amount=scuff_amount)

    warped = warp(face, quad, size)
    if light_strength:
        warped = light_board(warped, luminance(base), quad, size,
                             strength=light_strength, tint=tint)

    mask = quad_mask(quad, size, feather=1.1)
    warped.putalpha(mask)

    return Image.alpha_composite(base, warped)


def scene(path, size=None) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    if size:
        im = im.resize(size, Image.LANCZOS)
    return im


def save(canvas: Image.Image, path, quality=94) -> None:
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(p, quality=quality, subsampling=1)
