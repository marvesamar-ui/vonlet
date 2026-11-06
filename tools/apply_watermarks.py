#!/usr/bin/env python3
"""Brand every photograph on the website with the Vonlet shield.

The mark is drawn into the **top-right** corner of each site image. The bottom
corners are deliberately avoided: the service cards carry the category badge at
the top-left and the open-button at the bottom-right, the archive tiles carry an
index at the top-right and an expand control at the bottom-right, and the
concept cards run a provenance label across the bottom-left. The upper right is
the one corner that stays clear everywhere, so the mark reads the same on every
card, tile and gallery frame.

Each image gets both a light and a dark copy of the shield, chosen from the mean
luminance of the corner it lands in, so the mark never disappears into a pale
sky or a white van.

The site's own folders are branded in place. `assets/images/print-src/` holds
untouched masters so the magazine can print without a watermark in the artwork.

Usage:
    python3 tools/apply_watermarks.py            # brand the site images
    python3 tools/apply_watermarks.py --preview  # write proofs to /tmp only
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"
WA = ROOT / "assets" / "brand" / "wa"
MASTER = IMAGES / "master"

# Folders that are rendered on the site, and so carry the mark.
SITE_FOLDERS = ["cards", "cit", "concept", "full", "thumbs"]

# Share of the image's short edge the mark occupies, and its inset.
MARK_RATIO = 0.115
INSET_RATIO = 0.032
MIN_MARK = 34
MIN_INSET = 8

# The shield is always the real, full-colour mark — recolouring it loses the
# brand. Legibility comes from a plate behind it, which darkens or lightens
# according to what the photograph is doing underneath.
MARK_ALPHA = 0.96
PLATE_ON_LIGHT = 0.52
PLATE_ON_DARK = 0.30


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def build_mark() -> Path:
    """Render the shield once at high resolution, straight from the site logo."""
    WA.mkdir(parents=True, exist_ok=True)
    mark = WA / "mark.png"
    run(["convert", str(ROOT / "assets/brand/logo-mark-transparent.png"),
         "-resize", "512x512",
         "-channel", "A", "-evaluate", "multiply", f"{MARK_ALPHA}", "+channel",
         "-depth", "8", str(mark)])
    return mark


def corner_luminance(path: Path, mark_w: int, inset: int, fw: int, fh: int) -> float:
    """Mean luminance (0-255) of the region the mark will cover."""
    x = max(0, fw - inset - mark_w)
    y = inset
    w = min(mark_w, fw - x)
    h = min(mark_w, fh - y)
    out = subprocess.check_output(
        ["convert", str(path), "-crop", f"{w}x{h}+{x}+{y}", "+repage",
         "-colorspace", "Gray", "-format", "%[fx:mean*255]", "info:"],
        text=True,
    )
    return float(out.strip())


def watermark(path: Path, mark_src: Path, out: Path) -> str:
    fmt = subprocess.check_output(
        ["identify", "-format", "%w %h %m", str(path)], text=True
    ).split()
    fw, fh = int(fmt[0]), int(fmt[1])
    kind = fmt[2]

    short = min(fw, fh)
    mark_w = max(MIN_MARK, int(round(short * MARK_RATIO)))
    inset = max(MIN_INSET, int(round(short * INSET_RATIO)))

    # how hard the plate has to work depends on how bright the corner is
    lum = corner_luminance(path, mark_w, inset, fw, fh)
    plate_alpha = PLATE_ON_LIGHT if lum >= 132 else PLATE_ON_DARK
    tone = "dark-plate" if lum >= 132 else "light-plate"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        mark = tmp / "mark.png"
        run(["convert", str(mark_src), "-resize", f"{mark_w}x", "-depth", "8", str(mark)])

        # a soft dark plate behind the mark so it holds on any background,
        # floated clear of the image edge rather than cropped by it
        pad = max(4, int(round(mark_w * 0.17)))
        pw = mark_w + pad * 2
        plate = tmp / "plate.png"
        run(["convert", "-size", f"{pw}x{pw}", "xc:none",
             "-fill", f"rgba(3,8,22,{plate_alpha})",
             "-draw", f"roundrectangle 0,0 {pw-1},{pw-1} {int(pw*0.26)},{int(pw*0.26)}",
             "-blur", "0x1.2", str(plate)])

        # PNG intermediate keeps alpha; the coder is chosen at the end.
        base = tmp / "base.png"
        run(["convert", str(path), "-depth", "8", str(base)])

        px = fw - pw - inset
        py = inset
        args = [str(base),
                str(plate), "-geometry", f"+{px}+{py}", "-compose", "over", "-composite",
                str(mark), "-geometry", f"+{px + pad}+{py + pad}", "-compose", "over",
                "-composite"]
        if kind == "JPEG":
            args += ["-quality", "86", "-sampling-factor", "4:2:0", str(out)]
        elif kind == "WEBP":
            args += ["-quality", "82", "-define", "webp:method=6", str(out)]
        else:
            args += ["-depth", "8", str(out)]
        run(["convert", *args])
    return tone


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="write proofs to /tmp, do not touch the site")
    args = ap.parse_args()

    mark = build_mark()

    # Keep a private, unbranded master of every site image so the operation is
    # idempotent and reversible.
    if not MASTER.exists():
        MASTER.mkdir(parents=True)
        for folder in SITE_FOLDERS:
            src_dir = IMAGES / folder
            if not src_dir.is_dir():
                continue
            dest_dir = MASTER / folder
            dest_dir.mkdir(exist_ok=True)
            for f in src_dir.iterdir():
                if not f.is_file():
                    continue
                dest = dest_dir / f.name
                # Never let a smaller render replace a larger master. `full/` and
                # `thumbs/` share filenames, and getting this wrong silently
                # downgrades the magazine's print sources.
                if dest.exists():
                    continue
                dest.write_bytes(f.read_bytes())
        print(f"  masters saved to {MASTER.relative_to(ROOT)}")

    total, tones = 0, {"light-plate": 0, "dark-plate": 0}
    for folder in SITE_FOLDERS:
        src_root = MASTER / folder
        if not src_root.is_dir():
            continue
        for master in sorted(src_root.iterdir()):
            if not master.is_file():
                continue
            target = Path("/tmp/wm-preview") / folder / master.name if args.preview \
                else IMAGES / folder / master.name
            target.parent.mkdir(parents=True, exist_ok=True)
            tone = watermark(master, mark, target)
            tones[tone] += 1
            total += 1
        print(f"  {folder:<9} {len(list(src_root.iterdir())):>3} images branded")

    print(f"  {total} images · {tones['dark-plate']} on a dark plate · "
          f"{tones['light-plate']} on a light plate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
