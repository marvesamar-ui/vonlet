#!/usr/bin/env python3
"""Light: emissive signage on a dark wall.

A premium sign is not a bright rectangle. It is a light source with physics —
a halo blooming onto the wall behind it, spill pooling on the floor, a face that
is brighter at its core than its edges, and a room that has gone dark around it.

Everything here composites in *additive* or *screen* space rather than painting
over, because that is what light does. Work in that space and a render reads as
photographic; paint a yellow rectangle and it reads as a sticker.

The pieces:

  * `dusk()`      grades a daylight scene to night, keeping sky and structure
  * `emission()`  the lit part of a sign as a mask, for a given panel quad
  * `halo()`      the bloom behind reverse-lit letters
  * `bloom()`     soft glow around anything bright, from the image itself
  * `pool()`      a radial spill of light on a surface
  * `wash()`      a linear gradient of light raking a wall
  * `fixture()`   a small point source — a downlight, an LED spot
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageChops, ImageFilter


# ---------------------------------------------------------------------------
# grading
# ---------------------------------------------------------------------------
def dusk(canvas: Image.Image, exposure: float = 0.34,
         tint: tuple[float, float, float] = (0.62, 0.70, 0.95),
         lift: float = 0.02) -> Image.Image:
    """Grade a daylight scene to night.

    The sky is handled separately: a real dusk sky is not the day sky
    multiplied down, it is a deep blue that still holds gradient, so it is
    tinted and lifted rather than crushed.
    """
    arr = np.asarray(canvas.convert("RGB"), dtype=np.float32) / 255.0
    arr = arr * exposure
    arr[..., 0] *= tint[0]
    arr[..., 1] *= tint[1]
    arr[..., 2] *= tint[2]
    # keep a little shadow detail so the scene does not go to mud
    arr = arr + lift * (1.0 - arr)
    arr = np.clip(arr, 0, 1)
    return Image.fromarray((arr * 255).astype(np.uint8), "RGB").convert("RGBA")


def warm_bounce(canvas: Image.Image, amount: float = 0.05) -> Image.Image:
    """A faint warm cast low in the frame, as if from a nearby lamp."""
    w, h = canvas.size
    ramp = np.linspace(0, 1, h, dtype=np.float32)[:, None] ** 2
    arr = np.asarray(canvas.convert("RGB"), dtype=np.float32) / 255.0
    warm = np.array([amount * 1.0, amount * 0.72, amount * 0.38], dtype=np.float32)
    arr = arr + ramp[..., None] * warm
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")


# ---------------------------------------------------------------------------
# emission
# ---------------------------------------------------------------------------
def emission(art: Image.Image, quad, canvas_size, threshold: int = 150) -> Image.Image:
    """Warp the bright parts of a sign artwork into canvas space, as a mask.

    Returns an L-mode image the size of the canvas where the lit elements are
    white. Anything dark in the artwork — a metal face, a matte background —
    emits nothing.
    """
    from insitu import warp
    g = art.convert("L").point(lambda v: 0 if v < threshold else
                               int(255 * (v - threshold) / max(1, 255 - threshold)))
    layer = Image.new("L", art.size, 0)
    layer.paste(g, (0, 0))
    warped = warp(layer.convert("RGBA"), quad, canvas_size).convert("L")
    mask = Image.new("L", canvas_size, 0)
    from insitu import quad_mask
    mask = ImageChops.multiply(warped, quad_mask(quad, canvas_size, feather=0))
    return mask


def halo(mask: Image.Image, radius: float, color=(255, 236, 200),
         strength: float = 1.0, spread: float = 1.0) -> Image.Image:
    """Coloured bloom from a mask, to be screened onto the wall behind.

    Light falls off continuously, so this sums blurs over a range of radii and
    then tone-maps the result. A single gaussian, or a clipped sum of two,
    plateaus into a flat grey blob the shape of the lettering; the tone map
    keeps the gradient alive all the way out to the skirt.
    """
    w, h = mask.size
    acc = None
    for i, r in enumerate((0.28, 0.7, 1.5, 3.2)):
        weight = (0.62, 0.30, 0.14, 0.06)[i]
        b = mask.filter(ImageFilter.GaussianBlur(max(0.4, radius * r * spread ** 0.5)))
        if acc is None:
            acc = np.asarray(b, dtype=np.float32) * weight
        else:
            acc += np.asarray(b, dtype=np.float32) * weight

    a = acc / 255.0 * strength
    a = a / (1.0 + a)      # soft knee: no flat topped plateau
    a = np.clip(a * 1.9, 0, 1)

    rgba = np.zeros((h, w, 4), dtype=np.float32)
    rgba[..., 0] = color[0] / 255.0
    rgba[..., 1] = color[1] / 255.0
    rgba[..., 2] = color[2] / 255.0
    rgba[..., 3] = a
    return Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")


def bloom(canvas: Image.Image, threshold: int = 205, radius: float = 26.0,
          strength: float = 0.75, passes: int = 3) -> Image.Image:
    """Screen a soft glow around whatever in the image is already bright."""
    rgb = canvas.convert("RGB")
    lum = rgb.convert("L")
    hot = lum.point(lambda v: max(0, v - threshold) * 255 // max(1, 255 - threshold))
    if not hot.getbbox():
        return canvas

    acc = None
    for i in range(passes):
        r = radius * (1.0 + i * 0.9)
        b = hot.filter(ImageFilter.GaussianBlur(r))
        b = b.point(lambda v, k=1.0 / (i + 1.6): int(v * k))
        acc = b if acc is None else ImageChops.add(acc, b)

    colour = Image.new("RGB", canvas.size, (255, 246, 226))
    glow = Image.composite(colour, Image.new("RGB", canvas.size, (0, 0, 0)), acc)
    glow = Image.eval(glow, lambda v: int(v * strength))
    out = ImageChops.screen(rgb, glow)
    return out.convert("RGBA")


# ---------------------------------------------------------------------------
# spill
# ---------------------------------------------------------------------------
def pool(canvas: Image.Image, centre, radius: float, color=(255, 226, 178),
         strength: float = 0.55, squash: float = 1.0, falloff: float = 2.2) -> Image.Image:
    """A radial pool of light on a surface, screened onto the frame."""
    layer = pool_layer(canvas.size, centre, radius, color, strength, squash, falloff)
    return screen(canvas, layer)


def pool_layer(size, centre, radius: float, color=(255, 226, 178),
               strength: float = 0.55, squash: float = 1.0,
               falloff: float = 2.2) -> Image.Image:
    """`pool()` as a light layer: colour in RGB, intensity in alpha.

    Returned as a layer rather than composited, so the caller can clip it to a
    surface — a spot cone that lands on a sign must not also light the sky.
    """
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xx - centre[0]) / radius
    dy = (yy - centre[1]) / (radius * squash)
    d = np.sqrt(dx * dx + dy * dy)
    a = np.clip(1.0 - d, 0, 1) ** falloff * strength

    rgba = np.zeros((h, w, 4), dtype=np.float32)
    rgba[..., 0] = color[0] / 255.0
    rgba[..., 1] = color[1] / 255.0
    rgba[..., 2] = color[2] / 255.0
    rgba[..., 3] = np.clip(a, 0, 1)
    return Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")


def wash(canvas: Image.Image, box, angle: float = 90, color=(255, 232, 190),
         strength: float = 0.5, softness: float = 0.65) -> Image.Image:
    """A linear raking wash of light across a region — a wall-washer."""
    layer = wash_layer(canvas.size, box, angle, color, strength, softness)
    return screen(canvas, layer)


def wash_layer(size, box, angle: float = 90, color=(255, 232, 190),
               strength: float = 0.5, softness: float = 0.65) -> Image.Image:
    """`wash()` as a light layer: colour in RGB, intensity in alpha.

    The falloff is feathered on all four sides, not just along the ramp: a
    wall-washer has a soft-edged cone, and a hard-edged rectangle of light is
    the single most obvious tell that a render was assembled in layers.
    """
    w, h = size
    x, y, bw, bh = [int(round(v)) for v in box]
    bw, bh = max(2, bw), max(2, bh)

    ramp_n = max(2, bh if angle == 90 else bw)
    ramp = np.linspace(1.0, 0.0, ramp_n, dtype=np.float32) ** (1.0 / max(0.05, softness))
    field = (np.tile(ramp[:, None], (1, bw)) if angle == 90
             else np.tile(ramp[None, :], (bh, 1))).astype(np.float32)

    def edge_taper(n, power=1.6):
        t = np.linspace(0.0, 1.0, n, dtype=np.float32)
        return np.clip(np.minimum(t, 1.0 - t) * 2.0, 0, 1) ** (1.0 / power)

    if angle == 90:
        field *= edge_taper(bw)[None, :]
        field *= np.clip(ramp * 2.2, 0, 1)[:, None]
    else:
        field *= edge_taper(bh)[:, None]
        field *= np.clip(ramp * 2.2, 0, 1)[None, :]

    tile = (np.clip(field, 0, 1) * 255.0 * strength).astype(np.uint8)
    alpha = Image.new("L", (w, h), 0)
    alpha.paste(Image.fromarray(tile, "L"), (x, y))

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0] = color[0]
    rgba[..., 1] = color[1]
    rgba[..., 2] = color[2]
    rgba[..., 3] = np.asarray(alpha)
    return Image.fromarray(rgba, "RGBA")


def fixture(canvas: Image.Image, centre, radius: float, color=(255, 240, 214),
            strength: float = 0.9, core: float = 0.34) -> Image.Image:
    """A small bright source: the LED itself, before its spill."""
    out = pool(canvas, centre, radius * 3.4, color, strength * 0.35, falloff=2.8)
    out = pool(out, centre, radius * 1.5, color, strength * 0.6, falloff=2.4)
    out = pool(out, centre, radius * core, color, strength, falloff=1.4)
    return out


def spill_down(canvas: Image.Image, quad_top, height: float,
               color=(255, 226, 178), strength: float = 0.4) -> Image.Image:
    """Light falling from the underside of a sign onto the surface below."""
    cx = (quad_top[0][0] + quad_top[1][0]) / 2
    y = max(p[1] for p in quad_top)
    return pool(canvas, (cx, y + height * 0.35), height,
                color, strength, squash=0.55, falloff=2.6)


# ---------------------------------------------------------------------------
# metal
# ---------------------------------------------------------------------------
def brushed_metal(size, base=(208, 212, 218), contrast=0.16,
                  seed=7) -> Image.Image:
    """A vertical satin gradient with faint horizontal brushing.

    Real signage faces are never one flat grey. A brushed stainless face reads
    as metal because it carries a soft vertical gradient plus fine horizontal
    streaks.
    """
    w, h = size
    rng = np.random.default_rng(seed)

    grad = np.linspace(1.0 + contrast, 1.0 - contrast, h, dtype=np.float32)[:, None]
    field = np.repeat(grad, w, axis=1)

    streak = rng.normal(0, 1, (h, 1)).astype(np.float32)
    streak = np.repeat(streak, w, axis=1)
    streak = np.asarray(Image.fromarray(((streak * 0.5 + 0.5) * 255).astype(np.uint8))
                        .filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0
    field = field * (1.0 + (streak - 0.5) * 0.10)

    arr = np.zeros((h, w, 3), dtype=np.float32)
    for i in range(3):
        arr[..., i] = np.clip(field * base[i] / 255.0, 0, 1)
    img = Image.fromarray((arr * 255).astype(np.uint8), "RGB")
    return img.convert("RGBA")


def metal_face(size, text_layers, base=(206, 210, 216), edge=(120, 126, 134)):
    """Metal cut to letter shapes, with a darker edge and a top highlight.

    `text_layers` is a list of (mask, offset) in the same pixel space as `size`.
    Returns RGBA with metal only where the masks are.
    """
    w, h = size
    mask = Image.new("L", size, 0)
    for m, off in text_layers:
        mask.paste(ImageChops.lighter(mask.crop((off[0], off[1],
                                                 off[0] + m.width, off[1] + m.height)), m),
                   (off[0], off[1]))

    metal = brushed_metal(size, base)
    # a raised letter catches light on its top edge and drops shadow below
    hi = mask.filter(ImageFilter.GaussianBlur(1.2))
    hi = ImageChops.subtract(hi, ImageChops.offset(mask, 0, 2))
    lo = mask.filter(ImageFilter.GaussianBlur(1.2))
    lo = ImageChops.subtract(lo, ImageChops.offset(mask, 0, -2))

    out = metal.copy()
    out.paste(Image.new("RGBA", size, edge + (255,)), (0, 0), lo)
    out.paste(Image.new("RGBA", size, (248, 250, 252, 255)), (0, 0),
              Image.eval(hi, lambda v: int(v * 0.55)))
    out.putalpha(mask)
    return out


def acrylic_edge_glow(panel_mask: Image.Image, color=(255, 250, 236),
                      strength: float = 1.0, radius: float = 3.0) -> Image.Image:
    """The bright rim an edge-lit acrylic panel shows along its cut edges."""
    edge = ImageChops.subtract(panel_mask.filter(ImageFilter.GaussianBlur(radius)),
                               panel_mask.filter(ImageFilter.GaussianBlur(0.2)))
    edge = Image.eval(edge, lambda v: int(v * strength))
    rgba = Image.new("RGBA", panel_mask.size, color + (0,))
    rgba.putalpha(edge)
    return rgba


def screen(canvas: Image.Image, layer: Image.Image,
           strength: float = 1.0) -> Image.Image:
    """Screen an RGBA light layer onto the canvas, weighted by its own alpha.

    `alpha_composite` replaces; light does not replace. This adds the layer in
    screen space so a halo brightens the wall behind it instead of painting a
    flat colour over it.
    """
    w, h = canvas.size
    rgb = canvas.convert("RGB")
    a = layer.getchannel("A")
    if strength != 1.0:
        a = a.point(lambda v: min(255, int(v * strength)))
    lit = Image.composite(layer.convert("RGB"), Image.new("RGB", (w, h), (0, 0, 0)), a)
    return ImageChops.screen(rgb, lit).convert("RGBA")


def vignette(canvas: Image.Image, amount: float = 0.42,
             power: float = 2.0) -> Image.Image:
    """Darken the corners. A night scene photographed on a wide lens falls off."""
    w, h = canvas.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xx - w / 2) / (w / 2)
    dy = (yy - h / 2) / (h / 2)
    d = np.sqrt(dx * dx + dy * dy) / 1.41421356
    fall = np.clip(1.0 - amount * d ** power, 0, 1).astype(np.float32)

    arr = np.asarray(canvas.convert("RGB"), dtype=np.float32) / 255.0
    arr *= fall[..., None]
    return Image.fromarray((arr * 255).astype(np.uint8), "RGB").convert("RGBA")


def grain(canvas: Image.Image, amount: float = 3.4, seed: int = 11,
          chroma: float = 0.5) -> Image.Image:
    """Add sensor noise.

    A composite with no noise reads as CGI, because every real photograph taken
    at dusk carries grain in the shadows. This is added after the grade, at the
    same amplitude across the frame, with a little chroma variance so it does
    not look like a single grey overlay.
    """
    rng = np.random.default_rng(seed)
    arr = np.asarray(canvas.convert("RGB"), dtype=np.float32)
    h, w = arr.shape[:2]
    luma = rng.normal(0, amount, (h, w)).astype(np.float32)
    for c in range(3):
        n = luma + rng.normal(0, amount * chroma, (h, w)).astype(np.float32)
        arr[..., c] = np.clip(arr[..., c] + n, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


def combine(base: Image.Image, *layers: Image.Image) -> Image.Image:
    """Composite a stack of RGBA light layers over a base."""
    out = base.convert("RGBA")
    for layer in layers:
        if layer is None:
            continue
        out = Image.alpha_composite(out, layer)
    return out
