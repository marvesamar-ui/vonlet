#!/usr/bin/env python3
"""Stamp a content hash onto the stylesheet and script URLs.

`<link href="styles.css">` gives a browser nothing to invalidate: after a CSS
change a visitor can pair fresh HTML with a stale stylesheet, and the page
renders half-dressed — which is exactly what a new component looks like when
its rules never arrive.

This rewrites the reference in every page to `styles.css?v=<hash of the file>`,
so the URL changes whenever the CSS does and stays identical when it does not.
Run it after `build_services.py` (which rebuilds services.html from index.html)
and after `build_gallery.py`; it is a rewrite, not a build, and is safe to run
any number of times.

    python3 tools/stamp_assets.py
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ("index.html", "services.html", "archive.html")
ASSETS = ("styles.css", "main.js")


def digest(name: str) -> str:
    """A short fingerprint of the file's bytes."""
    payload = (ROOT / name).read_bytes()
    return hashlib.sha256(payload).hexdigest()[:8]


def stamp(markup: str, name: str, version: str) -> str:
    """Point every reference to `name` at `name?v=version`."""
    pattern = re.compile(
        r'(?P<attr>href|src)="' + re.escape(name) + r'(?:\?v=[0-9a-f]+)?"'
    )
    return pattern.sub(lambda m: f'{m.group("attr")}="{name}?v={version}"', markup)


def main() -> None:
    versions = {name: digest(name) for name in ASSETS}
    for name, version in versions.items():
        print(f"  {name:<12} v={version}")

    for page in PAGES:
        path = ROOT / page
        before = path.read_text(encoding="utf-8")
        after = before
        for name, version in versions.items():
            after = stamp(after, name, version)
        if after == before:
            print(f"  {page:<14} unchanged")
            continue
        path.write_text(after, encoding="utf-8")
        print(f"  {page:<14} stamped")

    missing = []
    for page in PAGES:
        markup = (ROOT / page).read_text(encoding="utf-8")
        for name in ASSETS:
            if f'{name}?v={versions[name]}' not in markup:
                missing.append(f"{page} -> {name}")
    if missing:
        raise SystemExit("Reference not stamped: " + ", ".join(missing))


if __name__ == "__main__":
    main()
