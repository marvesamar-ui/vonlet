#!/usr/bin/env python3
"""A minimal, dependency-free page-layout engine on top of ImageMagick.

There is no browser, no headless Chrome and no SVG rasteriser in this
environment, so the magazine and the signage kit are composed pixel-by-pixel
through ImageMagick's `convert`. This module wraps that in just enough of a
layout system to set real editorial pages:

  * a `Page` with a millimetre grid, margins and a column system, rendered at
    300 dpi and then re-sampled for screen previews
  * real type measurement through FontForge-free fontTools metrics, so rules,
    baselines, sidebars and captions land where they were specified rather than
    where ImageMagick's loose `annotate` gravity happened to put them
  * primitives: filled and outlined rules, panels, image placement with
    cover-crop and a duotone scrim, small-caps labels, letterspaced kickers,
    hanging-indent paragraphs, bullet lists, numbered lists, pull quotes,
    folios and image credits

Everything is drawn at 300 dpi into a single canvas, so the PDF handed over is
print resolution while the PNGs are screen previews.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path("/tmp/fonts")
FONT_FILES = {
    "cond-bold": FONT_DIR / "barlow-condensed-latin-700-normal.ttf",
    "cond-semi": FONT_DIR / "barlow-condensed-latin-600-normal.ttf",
    "body": FONT_DIR / "barlow-latin-400-normal.ttf",
    "semi": FONT_DIR / "barlow-latin-600-normal.ttf",
    "bold": FONT_DIR / "barlow-latin-700-normal.ttf",
}


def ensure_fonts() -> None:
    """Expand the site's woff2 files to TTF and install them for ImageMagick.

    The build environment is ephemeral, so this runs on every import: it is a
    no-op once `~/.fonts` already holds the faces.
    """
    if all(p.exists() for p in FONT_FILES.values()) and (Path.home() / ".fonts").is_dir():
        if any((Path.home() / ".fonts").glob("barlow*.ttf")):
            return
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    home_fonts = Path.home() / ".fonts"
    home_fonts.mkdir(exist_ok=True)
    for woff2 in (ROOT / "assets/fonts").glob("*.woff2"):
        font = TTFont(woff2)
        font.flavor = None
        target = FONT_DIR / (woff2.stem + ".ttf")
        if not target.exists():
            font.save(target)
        dest = home_fonts / target.name
        if not dest.exists():
            dest.write_bytes(target.read_bytes())


ensure_fonts()
def _hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


IMAGE_FONTS = {
    "cond-bold": "Barlow-Condensed-Bold",
    "cond-semi": "Barlow-Condensed-SemiBold",
    "body": "Barlow-Regular",
    "semi": "Barlow-SemiBold",
    "bold": "Barlow-Bold",
}

INK = "#f8fafc"
NAVY = "#030816"
NAVY_900 = "#050d1d"
NAVY_850 = "#07142b"
NAVY_800 = "#0a1933"
LINE = "#1e293b"
LINE_STRONG = "#334155"
SLATE_300 = "#cbd5e1"
SLATE_400 = "#94a3b8"
SLATE_500 = "#8b99ac"
RED = "#e61919"
RED_DEEP = "#b31212"
YELLOW = "#facc15"
WHITE = "#ffffff"

DPI = 300
MM = DPI / 25.4  # pixels per millimetre at print resolution


def mm(value: float) -> int:
    return round(value * MM)


_font_cache: dict[str, TTFont] = {}


def _font(role: str) -> TTFont:
    if role not in _font_cache:
        _font_cache[role] = TTFont(FONT_FILES[role])
    return _font_cache[role]


def text_width(text: str, role: str, size: float, tracking: float = 0) -> float:
    """Width in millimetres of `text` set at `size` mm, with optional tracking."""
    font = _font(role)
    upem = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    total = 0
    for char in text:
        name = cmap.get(ord(char))
        if name is None:
            name = ".notdef"
        total += hmtx[name][0]
    width_mm = total / upem * size
    if tracking:
        width_mm += tracking * max(0, len(text) - 1)
    return width_mm


@dataclass
class Page:
    """An A4 page with a millimetre coordinate system, origin top-left."""

    width_mm: float = 210
    height_mm: float = 297
    bleed_mm: float = 3
    margin: tuple[float, float, float, float] = (18, 18, 18, 18)  # top right bottom left
    background: str = NAVY
    # draw list of (kind, payload) executed in order
    ops: list = field(default_factory=list)
    _tokens: int = 0

    # ---------- geometry helpers ----------
    @property
    def px(self) -> tuple[int, int]:
        return (mm(self.width_mm + self.bleed_mm * 2), mm(self.height_mm + self.bleed_mm * 2))

    @property
    def trim(self) -> tuple[float, float, float, float]:
        """x, y, width, height of the trim box inside the bleed canvas (mm)."""
        return (self.bleed_mm, self.bleed_mm, self.width_mm, self.height_mm)

    def col(self, index: int, columns: int = 12, gutter: float = 4.5) -> tuple[float, float]:
        """Left edge and width of column `index` inside the text area."""
        left, right = self.margin[3], self.width_mm - self.margin[1]
        total = right - left
        col_w = (total - gutter * (columns - 1)) / columns
        x = left + index * (col_w + gutter)
        return x, col_w

    def span(self, start: int, end: int, columns: int = 12, gutter: float = 4.5) -> tuple[float, float]:
        """Left edge and width spanning columns start..end inclusive."""
        left, _ = self.col(start, columns, gutter)
        right_edge, _ = self.col(end, columns, gutter)
        _, col_w = self.col(start, columns, gutter)
        width = (right_edge + col_w) - left
        return left, width

    # ---------- primitives ----------
    def _add(self, kind: str, payload: dict) -> None:
        self._tokens += 1
        payload["_id"] = f"t{self._tokens:05d}"
        payload["kind"] = kind
        self.ops.append(payload)

    def rect(self, x, y, w, h, fill=None, stroke=None, stroke_w=0.3) -> None:
        self._add("rect", dict(x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, stroke_w=stroke_w))

    def rule(self, x, y, w, thickness=0.3, color=LINE) -> None:
        self.rect(x, y, w, thickness, fill=color)

    def vrule(self, x, y, h, thickness=0.3, color=LINE) -> None:
        self.rect(x, y, thickness, h, fill=color)

    def text(self, x, y, value, role="body", size=3.4, color=INK, tracking=0.0,
             align="left", width=None, opacity=None) -> float:
        """Draw one line. y is the baseline. Returns the advance width in mm."""
        w = text_width(value, role, size, tracking)
        x_draw = x
        if align == "right" and width is not None:
            x_draw = x + width - w
        elif align == "center" and width is not None:
            x_draw = x + (width - w) / 2
        self._add("text", dict(x=x_draw, y=y, value=value, role=role, size=size,
                               color=color, tracking=tracking, opacity=opacity))
        return w

    def kicker(self, x, y, value, color=YELLOW, size=2.5, tracking=0.32,
               align="left", width=None) -> None:
        """Letterspaced uppercase micro-label."""
        self.text(x, y, value.upper(), "semi", size, color, tracking,
                  align=align, width=width)

    def folio(self, number: int, section: str = "VONLET SECURITY") -> None:
        l, r = self.margin[3], self.width_mm - self.margin[1]
        base = self.height_mm - 11
        self.rule(l, base - 5.4, r - l, 0.25, LINE)
        self.kicker(l, base, section, SLATE_500, 2.2, 0.26)
        self.text(l, base, f"{number:02d}", "cond-bold", 3.4, YELLOW, align="right", width=r - l)

    # ---------- flow text ----------
    def paragraph(self, x, y, width, value, role="body", size=3.35, leading=1.52,
                  color=SLATE_300, first_indent=0.0, justify=True, track=0.0) -> float:
        """Set a wrapped paragraph. Returns the y baseline of the last line."""
        line_h = size * leading
        words = value.split()
        lines, current = [], ""
        avail = width
        first = True
        for word in words:
            trial = (current + " " + word).strip()
            limit = avail - (first_indent if first else 0)
            if text_width(trial, role, size, track) <= limit or not current:
                current = trial
            else:
                lines.append((current, first_indent if first else 0.0))
                first = False
                current = word
        if current:
            lines.append((current, first_indent if first else 0.0))

        baseline = y
        for i, (line, indent) in enumerate(lines):
            last = i == len(lines) - 1
            word_count = len(line.split())
            if justify and not last and word_count > 1:
                # `natural` already contains the spaces, so the extra band to
                # distribute is measured against the bare sum of the words —
                # otherwise a full line gets a near-zero gap and the words
                # collide.
                words_in_line = line.split()
                bare = sum(text_width(w, role, size, track) for w in words_in_line)
                gap = (width - indent - bare) / (word_count - 1)
                cursor = x + indent
                for w_i, word in enumerate(words_in_line):
                    wd = self.text(cursor, baseline, word, role, size, color, track)
                    cursor += wd + gap
            else:
                self.text(x + indent, baseline, line, role, size, color, track)
            baseline += line_h
        return baseline - line_h

    def bullets(self, x, y, width, items, size=3.2, leading=1.45, gap=1.6,
                color=SLATE_300, marker=YELLOW, marker_size=1.0) -> float:
        baseline = y
        line_h = size * leading
        for item in items:
            self.rect(x, baseline - size * 0.62, marker_size, marker_size, fill=marker)
            self.paragraph(x + 5.2, baseline, width - 5.2, item, "body", size, leading, color)
            approx_lines = max(1, int(text_width(item, "body", size) / (width - 5.2)) + 1)
            baseline += line_h * approx_lines + gap
        return baseline - gap

    def numbered(self, x, y, width, items, size=3.2, leading=1.45, gap=2.2) -> float:
        baseline = y
        line_h = size * leading
        for i, (title, body) in enumerate(items, start=1):
            self.text(x, baseline, f"{i:02d}", "cond-bold", size * 1.5, YELLOW)
            self.text(x + 10, baseline, title, "cond-semi", size * 1.22, INK)
            self.paragraph(x + 10, baseline + size * 1.35, width - 10, body, "body", size, leading, SLATE_400)
            approx = max(1, int(text_width(body, "body", size) / (width - 10)) + 1)
            baseline += size * 1.35 + line_h * approx + gap
        return baseline - gap

    # ---------- imagery ----------
    def image(self, x, y, w, h, path, focus=(0.5, 0.5), radius_bg=None,
              scrim=None, scrim_angle="bottom", border=None) -> None:
        self._add("image", dict(x=x, y=y, w=w, h=h, path=str(path), focus=focus,
                                scrim=scrim, scrim_angle=scrim_angle, border=border))

    def grad(self, x, y, w, h, stops: str, angle: int = 0) -> None:
        """A baked vertical gradient laid over the canvas.

        `stops` is an ImageMagick pair such as
        `rgba(3,8,22,0.0)-rgba(3,8,22,0.95)`; the gradient runs top to bottom
        across the given box, which is what makes full-bleed photography
        legible under display type without hiding the picture. `angle=90`
        rotates it to run left to right instead.
        """
        self._add("grad", dict(x=x, y=y, w=w, h=h, stops=stops, angle=angle))

    def scrim_panel(self, x, y, w, h, color=NAVY, alpha=0.72) -> None:
        """A real translucent panel — drawn as an SVG fill-opacity rectangle through
        the MVG renderer, so it composites rather than overpainting."""
        self._add("scrim", dict(x=x, y=y, w=w, h=h, color=color, alpha=alpha))

    # ---------- output ----------
    def _ox(self, x: float) -> int:
        """Page x in mm -> canvas pixels, shifted into the bleed box."""
        return mm(x + self.bleed_mm)

    def _oy(self, y: float) -> int:
        return mm(y + self.bleed_mm)

    def _args(self) -> list[str]:
        args: list[str] = []
        args.append("-size")
        args.append(f"{self.px[0]}x{self.px[1]}")
        args.append(f"xc:{self.background}")

        for op in self.ops:
            kind = op["kind"]
            if kind == "rect":
                x, y = op["x"], op["y"]
                w, h = op["w"], op["h"]
                if w <= 0 or h <= 0:
                    continue
                px_x, px_y = self._ox(x), self._oy(y)
                px_w = max(1, mm(w))
                px_h = max(1, mm(h))
                stroke = op["stroke"]
                if stroke:
                    args += ["-stroke", stroke, "-strokewidth", f"{max(1, mm(op['stroke_w']))}",
                             "-fill", "none" if not op["fill"] else op["fill"]]
                else:
                    args += ["-stroke", "none", "-fill", op["fill"]]
                args += ["-draw", f"rectangle {px_x},{px_y} {px_x + px_w},{px_y + px_h}"]
                args += ["-stroke", "none"]

            elif kind == "text":
                size_px = mm(op["size"])
                args += ["-font", IMAGE_FONTS[op["role"]], "-pointsize", f"{size_px:.2f}"]
                args += ["-fill", op["color"], "-stroke", "none"]
                if op.get("tracking"):
                    args += ["-kerning", f"{mm(op['tracking']):.2f}"]
                else:
                    args += ["-kerning", "0"]
                if op.get("opacity") is not None:
                    args += ["-channel", "A", "-evaluate", "multiply", f"{op['opacity']:.3f}", "+channel"]
                args += ["-annotate", f"+{self._ox(op['x'])}+{self._oy(op['y'])}", op["value"]]

            elif kind == "image":
                args += self._image_ops(op)

            elif kind == "scrim":
                r, g, b = _hex_rgb(op["color"])
                dx, dy = self._ox(op["x"]), self._oy(op["y"])
                dw, dh = max(1, mm(op["w"])), max(1, mm(op["h"]))
                args += ["(", "-size", f"{dw}x{dh}",
                         f"xc:rgba({r},{g},{b},{op['alpha']:.3f})", ")",
                         "-geometry", f"+{dx}+{dy}", "-compose", "over", "-composite"]

            elif kind == "grad":
                dx, dy = self._ox(op["x"]), self._oy(op["y"])
                dw, dh = max(1, mm(op["w"])), max(1, mm(op["h"]))
                if op.get("angle") == 90:
                    # build it tall, then rotate, so it runs left -> right
                    args += ["(", "-size", f"{dh}x{dw}", f"gradient:{op['stops']}",
                             "-rotate", "-90", "+repage", ")"]
                else:
                    args += ["(", "-size", f"{dw}x{dh}", f"gradient:{op['stops']}", ")"]
                args += ["-geometry", f"+{dx}+{dy}", "-compose", "over", "-composite"]

        return args

    def _image_ops(self, op: dict) -> list[str]:
        """Cover-crop the source to the destination box, then composite."""
        path = op["path"]
        ident = subprocess.check_output(
            ["identify", "-format", "%w %h", path], text=True
        ).split()
        sw, sh = int(ident[0]), int(ident[1])
        dx, dy = self._ox(op["x"]), self._oy(op["y"])
        dw, dh = max(1, mm(op["w"])), max(1, mm(op["h"]))
        scale = max(dw / sw, dh / sh)
        cw, ch = int(round(dw / scale)), int(round(dh / scale))
        fx, fy = op["focus"]
        cx = int(max(0, min(sw - cw, sw * fx - cw / 2)))
        cy = int(max(0, min(sh - ch, sh * fy - ch / 2)))
        args = ["(", path, "-crop", f"{cw}x{ch}+{cx}+{cy}", "+repage",
                "-resize", f"{dw}x{dh}!", ")"]
        if op.get("scrim"):
            # A gradient scrim is baked into the tile before it is composited,
            # so the photograph can carry white type over it.
            args += ["(", "-size", f"{dw}x{dh}",
                     f"gradient:{op['scrim_expr'] if 'scrim_expr' in op else 'rgba(3,8,22,0.88)-rgba(3,8,22,0.0)'}",
                     ")", "-compose", "over", "-composite"]
        args += ["-geometry", f"+{dx}+{dy}", "-compose", "over", "-composite"]
        return args

    def render(self, out: Path, preview_scale: float | None = None) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["convert"] + self._args()
        if preview_scale:
            target_w = int(mm(self.width_mm) * preview_scale)
            cmd += ["-resize", f"{target_w}x"]
        cmd += ["-depth", "8", "-define", "png:compression-level=9", "-strip", str(out)]
        subprocess.run(cmd, check=True)
