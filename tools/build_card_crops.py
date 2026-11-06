#!/usr/bin/env python3
"""Generate the 16:10 card crop for every service line photograph.

The service showcase and the services page both show a photograph in a wide,
short box. `object-fit: cover` handles that for a landscape frame, but most of
the company's newest frames are 3:4 phone portraits of a standing officer —
cropping one of those to 16:10 with a centre anchor beheads the subject.

So each service line gets a dedicated card derivative, cropped once, here, at a
size the cards actually use:

    assets/images/cards/<slug>.webp   800 x 500, quality 76

`FOCUS` sets where the vertical centre of that crop sits, as a fraction of the
source height: 0.00 is the top edge, 1.00 the bottom. A standing officer's head
and chest — what the card is for — sit around a third of the way down the frame,
so portrait frames default to 0.34 and landscape frames to 0.46. Frames where
the subject is off-centre get an explicit entry.

Run after tools/process-wa-frames.sh and before tools/build_services.py:

    python3 tools/build_card_crops.py
    python3 tools/build_services.py
    python3 tools/build_services_gallery.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/images/cards"
WIDTH, HEIGHT = 800, 500

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_services import SERVICES  # noqa: E402

# slug -> zoom: crop a tighter window from the centre before the 16:10 resize.
# The boundary-patrol frame is a wide site shot with the officer in the middle
# distance; at full width he is a speck on a card.
ZOOM = {
    "farms-and-mines-security": (0.42, 0.44, 0.62),  # (width fraction, centre x, centre y)
}

# slug -> vertical centre of the card crop (0 = top, 1 = bottom)
FOCUS = {
    # Suited officers standing behind a bank / client frontage: keep badge + face.
    "bank-and-atm-security": 0.32,
    "secret-service": 0.30,
    "private-escorts": 0.34,
    "functions-security": 0.33,
    "farms-and-mines-security": 0.36,
    "warehouse-security": 0.42,
    "retail-security": 0.38,
    "residential-security": 0.40,
    # Equipment and detail frames: the middle band is the subject.
    "close-circuit-television-cctv": 0.48,
    "access-control-systems": 0.46,
    "intruder-alarm-systems": 0.44,
    "guard-monitoring-systems": 0.46,
    "cash-in-transit": 0.50,
    "fire-drill": 0.50,
    "first-aid": 0.50,
}


def dimensions(path: Path) -> tuple[int, int]:
    width, height = subprocess.check_output(
        ["identify", "-format", "%w %h", str(path)], text=True
    ).split()
    return int(width), int(height)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for service in SERVICES:
        source = ROOT / service["image"]
        if not source.exists():
            raise SystemExit(f"missing source for {service['slug']}: {source}")

        width, height = dimensions(source)
        focus = FOCUS.get(service["slug"], 0.34 if width / height < 0.95 else 0.46)

        if service["slug"] in ZOOM:
            fraction, cx, cy = ZOOM[service["slug"]]
            crop_w = round(width * fraction)
            crop_h = round(crop_w / (WIDTH / HEIGHT))
            left = max(0, min(width - crop_w, round(cx * width - crop_w / 2)))
            top = max(0, min(height - crop_h, round(cy * height - crop_h / 2)))
            geometry = f"{crop_w}x{crop_h}+{left}+{top}"
        else:
            # Crop a 16:10 window at the chosen focus, then let the resize do the rest.
            crop_h = min(height, round(width / (WIDTH / HEIGHT)))
            top = round(focus * height - crop_h / 2)
            top = max(0, min(height - crop_h, top))
            geometry = f"{width}x{crop_h}+0+{top}"

        target = OUT / f"{service['slug']}.webp"
        subprocess.run(
            [
                "convert", str(source),
                "-auto-orient",
                "-crop", geometry, "+repage",
                "-resize", f"{WIDTH}x{HEIGHT}^",
                "-gravity", "center", "-extent", f"{WIDTH}x{HEIGHT}",
                "-strip", "-quality", "76",
                str(target),
            ],
            check=True,
        )
        written += 1
        print(f"{service['slug']:<34} {width}x{height} -> 800x500 (focus {focus:.2f})")

    print(f"wrote {written} card crops to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
